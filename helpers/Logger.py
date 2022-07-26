import time
from helpers.TermColors import *

class Logger:
    VERBOSE = 0
    DEBUG = 1
    WARN = 2
    ERROR = 3
    STATUS = 4
    OFF = 5

    def __init__(self, level=2, log_file=None):
        self.level = level
        self.log_file = log_file

    def __out(self, message, level, color):
        if level >= self.level:
            print(color + time.ctime() + " " + message + CEND)
        if self.log_file:
            with open(self.log_file, "a") as fd:
                fd.write(time.ctime() + " " + message + "\n")

    def v(self, message):
        self.__out(message, Logger.VERBOSE, "")

    def d(self, message):
        self.__out(message, Logger.DEBUG, CBLUE)

    def w(self, message):
        self.__out(message, Logger.WARN, CYELLOW)

    def e(self, message):
        self.__out(message, Logger.ERROR, CRED)

    def s(self, message):
        self.__out(message, Logger.STATUS, CGREEN)

    def print_trace(self, trace):
        if self.level == 5:
            return
        for i, t in enumerate(trace):
            print('trace ' + str(i) + ' | ' + self.pretty_trace_line(t))

    content_colors = {'lineno': CGREEN, 'type': CBLUE, 'info': '', 'control_dep': CVIOLET, 'data_target': CYELLOW, 'data_dep': CBLUE2, 'class_range': CYELLOW, 'func_name': CGREEN2, 'bool_op': CWHITE}

    def pretty_trace_line(self, trace):
        if self.level == 5:
            return
        out = []
        for key in ['lineno', 'type', 'data_target', 'data_dep', 'control_dep', 'info', 'class_range', 'func_name', 'bool_op']:
            out.append(CBOLD + CRED + key + ': ' + CEND + self.content_colors[key] + str(trace[key]) + CEND + '\t')
        return ' '.join(out)

    def pretty_print_code(self, code):
        if self.level == 5:
            return
        print('\n')
        for i, line in enumerate(code.splitlines()):
            print(CBOLD + CGREEN + str(i + 1) + ':\t' + CEND + line)
        print('\n')

    def pretty_print_slice_criteria(self, line, variable):
        if self.level == 5:
            return
        print('\n' + CBOLD + CRED + 'Slicing criteria:' + CEND)
        print(CBOLD + CRED + 'lineno: ' + CEND + CGREEN + str(line) + CEND + '\t' + CBOLD + CRED + 'variable: ' + CEND + CBLUE + variable + CEND)
