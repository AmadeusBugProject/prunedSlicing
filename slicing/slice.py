import copy

from timeout_decorator import timeout_decorator

from constants import SLICING_TIMEOUT
from slicing.slicing_criteria_exception import SlicingCriteriaException
from slicing.slicing_exceptions import InconsistentExecutionTraceException, SlicingException
from helpers.Logger import Logger
import re

log = Logger(level=5)


def dumb_dynamic_slice(exec_trace):
    return set([x['lineno'] for x in exec_trace])


@timeout_decorator.timeout(SLICING_TIMEOUT)
def get_dynamic_slice(exec_trace, variable, line_number, parameters_in_slice=False):
    slicer = Slicer(parameters_in_slice, pruned_slice=False, relevant_slice=False)
    return slicer.get_slice_for(exec_trace, variable, line_number)

@timeout_decorator.timeout(SLICING_TIMEOUT)
def get_relevant_slice(exec_trace, variable, line_number, parameters_in_slice=False):
    slicer = Slicer(parameters_in_slice, pruned_slice=False, relevant_slice=True)
    return slicer.get_slice_for(exec_trace, variable, line_number)


@timeout_decorator.timeout(SLICING_TIMEOUT)
def get_pruned_slice(exec_trace, variable, line_number, parameters_in_slice=False):
    slicer = Slicer(parameters_in_slice, pruned_slice=True, relevant_slice=False)
    return slicer.get_slice_for(exec_trace, variable, line_number)

@timeout_decorator.timeout(SLICING_TIMEOUT)
def get_pruned_relevant_slice(exec_trace, variable, line_number, parameters_in_slice=False):
    slicer = Slicer(parameters_in_slice, pruned_slice=True, relevant_slice=True)
    return slicer.get_slice_for(exec_trace, variable, line_number)


class Slicer:
    def __init__(self, parameters_in_slice, pruned_slice, relevant_slice):
        self.parameters_in_slice = parameters_in_slice
        self.pruned_slice = pruned_slice
        self.relevant_slice = relevant_slice
        self.slice = set()
                
    def get_slice_for(self, exec_trace, variable, line_number):
        self.slice = set()
        if line_number > max(d['lineno'] for d in exec_trace):
            msg = "Line number in slicing criterion " + str(line_number) \
                  + " is larger than the line numbers in the executed code (max: " \
                  + str(max(d['lineno'] for d in exec_trace)) + ")"
            raise SlicingCriteriaException(msg)
    
        slice_end_index = next((index for (index, d) in enumerate(reversed(exec_trace))
                                if d["lineno"] == line_number), None)
        slice_end_index = len(exec_trace) - 1 - slice_end_index
        while variable not in exec_trace[slice_end_index].get('data_target'):
            slice_end_index -= 1
            if slice_end_index < 0:
                msg = "Wrong slicing criterion: variable " + variable + ", line " + str(line_number)
                raise SlicingCriteriaException(msg)

        self.add_control_dependencies(exec_trace, slice_end_index)

        relevant_variables = set()
        relevant_variables.add(variable)
        
        slicing_crit_in_func = self.is_slicing_criteria_in_function(exec_trace, slice_end_index)
    
        if exec_trace[slice_end_index].get('type') in ['p_if_begin', 'p_else_begin', 'p_for_begin']:
            self.slice.add(exec_trace[slice_end_index].get('lineno'))
        relevant_variables, bool_ops_slice, codegen_param_removal = self.compute_slice(exec_trace, relevant_variables,
                                                                                       slice_end_index,
                                                                                       slicing_crit_in_func)
        if len(relevant_variables) > 0:
            log.s("Relevant variables: " + str(relevant_variables))
    
        return self.slice, bool_ops_slice, codegen_param_removal

    def add_control_dependencies(self, exec_trace, index):
        if exec_trace[index].get('control_dep') != 'module':
            regex = '(\d+): (\w+) '
            match = re.search(regex, exec_trace[index].get('control_dep'))
            control_lineno = int(match.group(1))
            self.slice.add(control_lineno)
            index = next((index for (index, d) in enumerate(exec_trace)
                                if d["lineno"] == control_lineno), None)
            self.add_control_dependencies(exec_trace, index)

    @staticmethod
    def get_p_call_before_index(exec_trace, p_func_def_idx):
        p_func_def = 1
        p_call_before = 0
        idx = p_func_def_idx-1
        while p_func_def > p_call_before:
            if exec_trace[idx].get('type') == 'p_func_def':
                p_func_def += 1
            elif exec_trace[idx].get('type') == 'p_call_before':
                p_call_before += 1
            idx -= 1
        return idx+1

    @staticmethod
    def is_slicing_criteria_in_function(exec_trace, index):
        p_func_def = 0
        p_call_after = 0
    
        while index > 0:
            if exec_trace[index].get('type') == 'p_func_def':
                p_func_def += 1
            elif exec_trace[index].get('type') == 'p_call_after':
                p_call_after += 1
            if p_func_def > p_call_after:
                return True
            index -= 1
        return False
    
    def compute_slice(self, exec_trace, relevant_variables, slice_end_index, within_function=False):
        bool_ops_slice = []
        func_param_removal = []
        while slice_end_index >= 0:
            line_info = exec_trace[slice_end_index]
            if line_info.get('type') in ['p_assignment', 'p_aug_assignment']:
                if len(line_info.get('data_target')) > 0 and len(line_info.get('data_dep')) > 0:  # creating an object
                    object_name = line_info.get('data_target')[0] + '.'
                    target_name = line_info.get('data_dep')[0]+'.'
                    new_relevant_variables = set()
                    for var in relevant_variables:
                        if object_name in var:
                            new_relevant_variables.add(var.replace(object_name, target_name))
                        else:
                            new_relevant_variables.add(var)
                    relevant_variables = new_relevant_variables
                intersect = relevant_variables.intersection(line_info.get('data_target'))
                if len(intersect) > 0:
                    self.slice.add(line_info.get('lineno'))

                    slice_end_index = self.add_control_statement(exec_trace, slice_end_index, slice_end_index)
                    relevant_variables = relevant_variables.difference(intersect)
                    relevant_variables = relevant_variables.union(line_info.get('data_dep'))
                slice_end_index -= 1
    
            elif line_info.get('type') in ['p_and_dyn', 'p_or_dyn']:
                intersect = relevant_variables.intersection(line_info.get('data_target'))
                if len(intersect) > 0:
                    self.slice.add(line_info.get('lineno'))
                    slice_end_index = self.add_control_statement(exec_trace, slice_end_index, slice_end_index)
                    relevant_variables = relevant_variables.difference(intersect)
                    if self.pruned_slice:
                        rel_var, rel_bool_ops = self.get_cond_relevant_variables(line_info)
                        relevant_variables = relevant_variables.union(rel_var)
                        bool_ops_slice.append(rel_bool_ops)
                    else:
                        relevant_variables = relevant_variables.union(line_info.get('data_dep'))
                        bool_ops_slice.append(copy.deepcopy(line_info['bool_op']))
                slice_end_index -= 1
    
            elif line_info.get('type') in ['p_and_stat', 'p_or_stat']:
                slice_end_index -= 1
            elif line_info.get('type') == 'p_call_after':
                slice_end_index, relevant_variables, rel_bool_ops, codegen_param_removal = self.get_function_slice(
                    exec_trace, slice_end_index, relevant_variables)
                bool_ops_slice.extend(rel_bool_ops)
                func_param_removal.extend(codegen_param_removal)
            elif line_info.get('type') == 'p_func_def':
                if within_function:
                    self.slice.add(line_info.get('lineno'))
                    p_call_before_idx = self.get_p_call_before_index(exec_trace, slice_end_index)
                    relevant_variables, changed, codegen_param_removal = self.get_parameter_assignment(line_info,
                                                                    exec_trace[p_call_before_idx], relevant_variables, needed=True)
                    func_param_removal.append(codegen_param_removal)
                slice_end_index -= 1
            elif line_info.get('type') == 'p_call_before':
                slice_end_index -= 1
            elif line_info.get('type') == 'p_class_def':
                lineno_range = line_info['class_range']
                lineno_range = [int(x) for x in lineno_range]
                lineno_range = set(range(lineno_range[0], lineno_range[1] + 1))
                if not lineno_range.isdisjoint(self.slice):
                    self.slice.add(line_info.get('lineno'))
                slice_end_index -= 1
            elif line_info.get('type') == 'p_pass':
                slice_end_index -= 1
            elif line_info.get('type') in ['p_if_end', 'p_for_end', 'p_while_end']:
                if line_info.get('lineno') in self.slice:
                    intersect = relevant_variables.intersection(line_info.get('data_target'))
                    relevant_variables = relevant_variables.difference(intersect)
                    relevant_variables = relevant_variables.union(line_info.get('data_dep'))
                slice_end_index -= 1
            elif line_info.get('type') in ['p_for_else_begin', 'p_while_else_begin']:
                if line_info.get('lineno') in self.slice:
                    intersect = relevant_variables.intersection(line_info.get('data_target'))
                    relevant_variables = relevant_variables.difference(intersect)
                    relevant_variables = relevant_variables.union(line_info.get('data_dep'))
                slice_end_index -= 1
            elif line_info.get('type') in ['p_if_begin', 'p_else_begin', 'p_for_begin', 'p_while_begin']:
                intersect = relevant_variables.intersection(line_info.get('data_target'))
                if line_info.get('lineno') in self.slice or len(intersect) > 0:
                    self.slice.add(line_info.get('lineno'))
                    relevant_variables = relevant_variables.difference(intersect)
                    relevant_variables = relevant_variables.union(line_info.get('data_dep'))

                    slice_end_index = self.add_control_statement(exec_trace, slice_end_index, slice_end_index)
    
                    if line_info.get('type') in ['p_for_begin', 'p_while_begin']:
                        break_and_continues, loop_end_index = self.get_break_continues_loop_end_index(exec_trace, slice_end_index, line_info.get('lineno'))
                        for item in break_and_continues:
                            self.slice.add(exec_trace[item].get('lineno'))
                            control_lineno = exec_trace[item].get('control_dep').split(':')[0]  #  adding if-statements that contain the condition for break/continue
                            highest_control_index = -1
                            if int(control_lineno) not in self.slice:
                                self.slice.add(int(control_lineno))
                                control_index = next((index for (index, d) in enumerate(reversed(exec_trace))
                                                        if d["lineno"] == int(control_lineno)), None)
                                control_index = len(exec_trace) - 1 - int(control_index)
                                highest_control_index = max(highest_control_index, control_index)
                            slice_end_index = max(highest_control_index+1, slice_end_index)
    
                slice_end_index -= 1
            elif line_info.get('type') == 'p_condition':
                # ToDo: here we have to add the relevant slicing code
                if self.relevant_slice:
                    if relevant_variables.intersection(line_info.get('pot_dep')):
                        if line_info.get('lineno') in self.slice:
                            slice_end_index -= 1
                            continue
                        self.slice.add(line_info.get('lineno'))
                        relevant_variables = relevant_variables.union(line_info.get('data_dep'))

                        cond_line_number = line_info.get('lineno')

                        # TODO dont go to last slice_end_index in the same line, but the next 'p_for_begin', 'p_while_begin', 'p_for_else_begin', 'p_while_else_begin'
                        # while(exec_trace[slice_end_index].get('lineno')==cond_line_number):
                        #     slice_end_index += 1
                        #     if slice_end_index >= len(exec_trace):
                        #         break
                        #     control_statement_line_info = exec_trace[slice_end_index]
                        # slice_end_index -= 1

                        original_slice_end_index = slice_end_index
                        while (exec_trace[slice_end_index].get('type') not in ['p_for_begin', 'p_while_begin',
                                                                               'p_for_else_begin', 'p_while_else_begin',
                                                                               'p_else_begin', 'p_if_begin']):

                            if exec_trace[slice_end_index].get('lineno') != cond_line_number:  # loop executed at least once
                                break
                            slice_end_index += 1
                            if slice_end_index >= len(exec_trace):
                                raise Exception("Exception while relevant slicing: slice_end_index >= len(exec_trace)")

                        if exec_trace[slice_end_index].get('lineno') != cond_line_number:  # loop executed at least once
                            slice_end_index = original_slice_end_index
                        else:
                            control_statement_line_info = exec_trace[slice_end_index]

                            if control_statement_line_info.get('type') in ['p_for_begin', 'p_while_begin', 'p_for_else_begin', 'p_while_else_begin']:
                                break_and_continues, loop_end_index = self.get_break_continues_loop_end_index(exec_trace, slice_end_index, control_statement_line_info.get('lineno'))
                                for item in break_and_continues:
                                    self.slice.add(exec_trace[item].get('lineno'))
                                    control_lineno = exec_trace[item].get('control_dep').split(':')[0]  # adding if-statements that contain the condition for break/continue
                                    highest_control_index = -1
                                    if int(control_lineno) not in self.slice:
                                        self.slice.add(int(control_lineno))
                                        control_index = next((index for (index, d) in enumerate(reversed(exec_trace))
                                                              if d["lineno"] == int(control_lineno)), None)
                                        control_index = len(exec_trace) - 1 - int(control_index)
                                        highest_control_index = max(highest_control_index, control_index)
                                    slice_end_index = max(highest_control_index + 1, slice_end_index)

                # End ToDo
                slice_end_index -= 1
            elif line_info.get('type') in ['p_else_end', 'p_for_else_end', 'p_while_else_end']:
                slice_end_index -= 1
            elif line_info.get('type') == 'p_return':  # we add returns in get_function_slice()
                slice_end_index -= 1
            elif line_info.get('type') in ['p_break', 'p_continue']:  # we add breaks and continues when we add the loop header
                slice_end_index -= 1
            else:
                msg = "Type " + line_info.get('type') + " not implemented!"
                raise NotImplementedError(msg)
        return relevant_variables, bool_ops_slice, func_param_removal

    @staticmethod
    def get_break_continues_loop_end_index(exec_trace, slice_index, line_no):
        line_loop_begin = exec_trace[slice_index].get('lineno')
        loop_begins = 1
        loop_ends = 0
        break_and_continues = set()
        index = slice_index+1
        loop_end_index = -1
        while index < len(exec_trace):
            if loop_ends == loop_begins and exec_trace[index].get('lineno') != line_loop_begin:  # exec_trace[index].get('type') not in ['p_for_begin', 'p_while_begin'] and
                break
            if exec_trace[index].get('type') in ['p_break', 'p_continue']:  # and loop_begins == loop_ends+1:
                break_and_continues.add(index)
            elif exec_trace[index].get('type') in ['p_for_begin', 'p_while_begin']:
                loop_begins += 1
            if exec_trace[index].get('type') in ['p_for_end', 'p_while_end', 'p_break', 'p_continue'] and exec_trace[index].get('lineno') == line_no:
                loop_end_index = index
                loop_ends += 1
            index += 1
        return break_and_continues, loop_end_index

    @staticmethod
    def get_cond_relevant_variables(line_info):
        # info = {'lineno': 5, 'type': 'p_and_dyn', 'info': "['a']=True and ['b']=True and ['c']=False => False", 'control_dep': 'module',
        #         'data_target': ['a and b and c'], 'data_dep': ['a', 'b', 'c'], 'class_range': [], 'func_name': '',
        #         'bool_op': {'op': 'and', 'result': False, 'executed_nodes': [
        #                                                   {'unparsed': 'a', 'data_dyn': ['a'], 'result': True},
        #                                                   {'unparsed': 'b', 'data_dyn': ['b'], 'result': True},
        #                                                   {'unparsed': 'c', 'data_dyn': ['c'], 'result': False}]}}
    
        bool_op = line_info['bool_op']
        result = bool_op['result']
        relevant_variables = set()
        cond_relevant_bool_op = copy.deepcopy(bool_op)
    
        if line_info.get('type') == 'p_and_dyn':
            if result:  # all params are true
                relevant_variables = line_info.get('data_dep')
            else:  # add params evaluating to false
                cond_relevant_bool_op['executed_nodes'] = []
                for param in bool_op['executed_nodes']:
                    if not param['result']:
                        relevant_variables.update(set(param['data_dyn'])) # update set since a single node can actually contain more than one data dep, eg (x > y and z)
                        cond_relevant_bool_op['executed_nodes'].append(param)
        elif line_info.get('type') == 'p_or_dyn':
            if result:  # add params evaluating to true
                cond_relevant_bool_op['executed_nodes'] = []
                for param in bool_op['executed_nodes']:
                    if param['result']:
                        relevant_variables.update(set(param['data_dyn']))
                        cond_relevant_bool_op['executed_nodes'].append(param)
            else:  # add all params
                relevant_variables = line_info.get('data_dep')
        else:
            mgs = "Conditional slicing for type "+line_info.get('type')+" not implemented!"
            raise(SlicingException(mgs))
    
        return relevant_variables, cond_relevant_bool_op

    @staticmethod
    def get_function_trace(exec_trace, function_end_index):
        if exec_trace[function_end_index].get('type') != 'p_call_after':
            msg = "getFunctionTrace(exec_trace, end_index) called with wrong arguments"
            raise InconsistentExecutionTraceException(msg)
        p_call_after = 1
        p_call_before = 0
        p_func_def_index = -1
        index = function_end_index-1
        while p_call_before < p_call_after:
            if exec_trace[index].get('type') == 'p_call_after':
                p_call_after += 1
            elif exec_trace[index].get('type') == 'p_call_before':
                p_call_before += 1
            elif exec_trace[index].get('type') == 'p_func_def' and p_call_after == 1 + p_call_before:
                p_func_def_index = index
            else:
                pass
            index -= 1
    
        before_function_index = index
        p_call_before_index = 0
        if p_func_def_index > 0:
            p_func_def_index = p_func_def_index-before_function_index-1
        function_exec_trace = exec_trace[index+1:function_end_index+1]
        # log.s("FUNCTION | before: " + str(index) + ", p_call_before: " + str(p_call_before_index) + ", p_func_def: "
        #       + str(p_func_def_index))
        # log.print_trace(function_exec_trace)
        return function_exec_trace, before_function_index, p_call_before_index, p_func_def_index

    def get_function_slice(self, exec_trace, slice_end_index, relevant_variables):
        slice_before_len = len(self.slice)
        exec_trace, before_function_index, p_call_before_idx, p_func_def_idx = Slicer.get_function_trace(exec_trace, slice_end_index)
        bool_ops_slice = []
        func_param_removal = []

        function_index = len(exec_trace)-1
        if exec_trace[function_index].get('type') != 'p_call_after':
            msg = "Lineno: " + str(exec_trace[function_index]) + " Expecting type 'p_call_after, but got " + \
                             exec_trace[function_index].get('type')
            raise InconsistentExecutionTraceException(msg)
        intersect = relevant_variables.intersection(exec_trace[function_index].get('data_target'))
        return_value_needed = True if len(intersect) > 0 else False
    
        object_relevant = False
        for item in exec_trace[function_index].get('data_target'):
            if '.' in item and item.split('.')[0] in relevant_variables:
                object_relevant = True
                break

        if p_func_def_idx == -1:  # call of build-in function
            if return_value_needed or object_relevant:
                self.slice.add(exec_trace[function_index].get('lineno'))
                function_index = self.add_control_statement(exec_trace, function_index, slice_end_index, p_call_before_idx)-1
                relevant_variables = relevant_variables.difference(exec_trace[ p_call_before_idx].get('data_target'))
                data_deps = exec_trace[ p_call_before_idx].get('data_dep')
                for data_dep in data_deps:
                    relevant_variables = relevant_variables.union(data_dep)
                if exec_trace[function_index].get('type') != 'p_call_before':   # parameter(s) of function call are functions
                    relevant_variables, rel_bool_op_slice, codegen_param_removal = self.compute_slice(exec_trace, relevant_variables, function_index)
                    func_param_removal.extend(codegen_param_removal)
                    bool_ops_slice.extend(rel_bool_op_slice)
    
                    # msg = "Lineno: " + str(exec_trace[function_index]) + " Expecting type 'p_call_before, but got " + \
                    #       exec_trace[function_index].get('type')
                    # raise InconsistentExecutionTraceException(msg)
    
            return before_function_index, relevant_variables, bool_ops_slice, func_param_removal
    
        # call of traced function
        if re.compile('\A[a-zA-Z_]\w*\.[a-zA-Z_]\w*').match(exec_trace[function_index].get('data_target')[0]):
            object_name = exec_trace[function_index].get('data_dep')[0][0]
        elif exec_trace[p_func_def_idx]['func_name'] == "__init__" and exec_trace[p_func_def_idx]['data_target'][0] == 'self':
            object_name = exec_trace[function_index].get('data_target')[0]
        else:
            object_name = None
    
        if return_value_needed:
            self.slice.add(exec_trace[function_index].get('lineno'))
            function_index -= 1
    
            if Slicer.is_constructor_func_def(exec_trace[p_func_def_idx]):
                locally_relevant, globally_relevant = Slicer.split_relevant_variables(relevant_variables, object_name, init=True)
                relevant_variables = globally_relevant
            elif exec_trace[function_index].get('type') != 'p_return':
                relevant_variables = relevant_variables.difference(intersect)
                locally_relevant, globally_relevant = Slicer.split_relevant_variables(relevant_variables, object_name)
                # function_index -= 1

                # msg = "Lineno: " + str(exec_trace[function_index]) + " Expecting type 'p_return, but got " + \
                #     exec_trace[function_index].get('type')
                # raise InconsistentExecutionTraceException(msg)
            else:
                self.slice.add(exec_trace[function_index].get('lineno'))
                relevant_variables = relevant_variables.difference(intersect)
                locally_relevant, globally_relevant = Slicer.split_relevant_variables(relevant_variables, object_name)
                relevant_variables = globally_relevant.union(exec_trace[function_index].get('data_dep'))

                function_index = self.add_control_statement(exec_trace, function_index, slice_end_index)-1
        else:
            locally_relevant, globally_relevant = Slicer.split_relevant_variables(relevant_variables, object_name)
            relevant_variables = globally_relevant
            function_index -= 1
    
        bool_ops_slice = []
        before_exec_trace, after_exec_trace = Slicer.split_function_trace(exec_trace, p_func_def_idx, function_index)
        relevant_variables, rel_bool_op_slice, codegen_param_removal = self.compute_slice(after_exec_trace, relevant_variables,
                                                                                          len(after_exec_trace) - 1)
        bool_ops_slice.extend(rel_bool_op_slice)
        func_param_removal.extend(codegen_param_removal)
    
        needed = len(self.slice) > slice_before_len or return_value_needed
        relevant_variables, changed, codegen_param_removal = self.get_parameter_assignment(exec_trace[p_func_def_idx],
                                                               exec_trace[p_call_before_idx], relevant_variables, needed)
        func_param_removal.append(codegen_param_removal)
    
        relevant_variables, rel_bool_op_slice, codegen_param_removal = self.compute_slice(before_exec_trace, relevant_variables,
                                                                                          len(before_exec_trace) - 1)
        bool_ops_slice.extend(rel_bool_op_slice)
        func_param_removal.extend(codegen_param_removal)
    
        if len(self.slice) > slice_before_len or return_value_needed:
            self.slice = self.slice.union({exec_trace[p_func_def_idx].get('lineno')})
            self.slice = self.slice.union({exec_trace[p_call_before_idx].get('lineno')})
    
        relevant_variables = relevant_variables.union(locally_relevant)
    
        if Slicer.is_constructor_func_def(exec_trace[p_func_def_idx]):
            relevant_variables = relevant_variables.difference(exec_trace[0].get('data_target'))
    
        return before_function_index, relevant_variables, bool_ops_slice, func_param_removal

    def add_control_statement(self, exec_trace, function_index, slice_end_index, p_call_before_idx=-1):
        if p_call_before_idx > -1:
            info = exec_trace[p_call_before_idx]
        else:
            info = exec_trace[function_index]
        if info.get('control_dep') != 'module':
            regex = '(\d+): (\w+) '
            match = re.search(regex, info.get('control_dep'))
            control_lineno = int(match.group(1))
            type = match.group(2)

            if control_lineno not in self.slice and type in ['p_while_begin', 'p_for_begin', 'p_if_begin',
                                                             'p_else_begin', 'p_for_else_begin', 'p_while_else_begin']:
                self.slice.add(control_lineno)
                # Todo: This is a quick and dirty hack which might result in an endless loop
                if type in ['p_for_begin', 'p_while_begin']:
                    _, loop_end_index = Slicer.get_break_continues_loop_end_index(exec_trace, function_index, control_lineno)
                    function_index = max(loop_end_index + 1, function_index)
        return function_index

    @staticmethod
    def is_constructor_func_def(trace):
        return trace['func_name'] == "__init__" and trace['data_target'][0] == 'self'

    @staticmethod
    def split_function_trace(exec_trace, p_func_def_index, function_index):
        exec_trace_before = exec_trace[0:p_func_def_index]
        exec_trace_after = exec_trace[p_func_def_index+1:function_index+1]
        return exec_trace_before, exec_trace_after

    @staticmethod
    def split_relevant_variables(relevant_variables, object_name, init=False):
        locally_relevant = set()
        globally_relevant = set()
        for variable in relevant_variables:
            if "." in variable:
                if object_name and object_name+'.' in variable:
                    globally_relevant.add(variable.replace(object_name+'.', 'self.'))
                else:
                    globally_relevant.add(variable)
            else:
                locally_relevant.add(variable)
        if init:
            globally_relevant.add(object_name)
            locally_relevant.remove(object_name)
        return locally_relevant, globally_relevant

    def get_parameter_assignment(self, formal_param, actual_param, relevant_variables, needed):
        actual_param_l = actual_param.copy()
        if formal_param.get('type') != 'p_func_def' or actual_param_l.get('type') != 'p_call_before':
            raise InconsistentExecutionTraceException("Expected 'p_func_def' and 'p_call_before' as types!")
        formal_params = formal_param.get('data_target')
    
        actual_params = actual_param_l.get('data_dep').copy()

        if self.parameters_in_slice and needed:
            relevant_variables = relevant_variables.difference(formal_params)
            for param in actual_params:
                relevant_variables = relevant_variables.union(param)
            return relevant_variables, True, {}

        formal_params_for_removal = formal_params.copy()
        if len(formal_params_for_removal) and formal_params_for_removal[0] == 'self':
            formal_params_for_removal = formal_params_for_removal[1:]
        idx_removed_in_code_gen = [formal_params_for_removal.index(x) for x in set(formal_params_for_removal).difference(relevant_variables)]
        origin_data_target = actual_param_l['data_target']
        origin_lineno = actual_param_l['lineno']
        func_name = formal_param['func_name']
        codegen_param_removal = {'lineno': origin_lineno, 'func_name': func_name, 'target': origin_data_target, 'remove_param_idx': idx_removed_in_code_gen}
    
        # changes data_dep of a constructor call to add itself to the data_dep as helper token.
        # before:
        # p_call_before	 data_target: ['Tcas(a)']	 data_dep: [['a']]
        # p_func_def	 data_target: ['self', 'x']	 data_dep: []
        #
        # after
        # p_call_before	 data_target: ['Tcas(a)']	 data_dep: [['Tcas(a)'], ['a']]
        # p_func_def	 data_target: ['self', 'x']	 data_dep: []
        #
        # to enable mapping of function definition to input parameters, and therefore map 'self' to 'Tcas(a)'
        if Slicer.is_constructor_func_def(formal_param):
            actual_params.insert(0, actual_param_l['data_target'])
        # end data_dep for constructor calls
    
        if len(formal_params) != len(actual_params):
            raise InconsistentExecutionTraceException("Parameter mismatch: " + str(formal_params) + " (formal parameter) " +
                                                      str(actual_params) + " (actual params)")
    
        changed = False
        for i, param in enumerate(formal_params):
            if param in relevant_variables:
                relevant_variables.remove(param)
                relevant_variables.update(actual_params[i])
                changed = True
        new_relevant_variables = set()
        for variable in relevant_variables:
            if 'self.' in variable:
                new_var_name = variable.replace('self.', actual_params[0][0]+'.')
                new_relevant_variables = new_relevant_variables.union({new_var_name})
                new_relevant_variables = new_relevant_variables.union({actual_params[0][0]})
            else:
                new_relevant_variables = new_relevant_variables.union({variable})
        return new_relevant_variables, changed, codegen_param_removal
