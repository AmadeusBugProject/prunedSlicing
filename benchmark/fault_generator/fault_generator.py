import os

import pandas as pd

tcas = {'name': 'Tcas',
        'original_file': '../tcas/Tcas.py',
        'faults_file': '../tcas/faults.json',
        'faulty_versions_dir': '../tcas/faulty_versions/'}
triangle = {'name': 'Triangle',
            'original_file': '../triangle/Triangle.py',
            'faults_file': '../triangle/faults.json',
            'faulty_versions_dir': '../triangle/faulty_versions/'}
middle = {'name': 'Middle',
          'original_file': '../middle/Middle.py',
          'faults_file': '../middle/faults.json',
          'faulty_versions_dir': '../middle/faulty_versions/'}


def main():
    # analyze_and_create(tcas)
    analyze_and_create(triangle)
    # analyze_and_create(middle)


def analyze_and_create(series):

    print("******************** "+series.get('name')+" ********************")
    faults = pd.read_json(series.get('faults_file'), orient='index')
    analyze_faults(faults)
    create_faulty_files(series.get('name'), faults, series.get('original_file'), series.get('faulty_versions_dir'))
    print("**************************************************")


def create_faulty_files(name, faults, original_file, faulty_versions_dir):
    print("\nCREATING FAULTY VERSIONS")
    os.makedirs(faulty_versions_dir, exist_ok=True)
    with open(original_file, 'r') as original_file_reader:
        original_code = original_file_reader.readlines()
        for index, fault in faults.iterrows():
            if fault.get('duplicate') == True:
                print("IGNORING duplicate: "+index+" is "+fault.get('info'))
                continue
            if type(fault.get('info')) is str:
                print("IGNORING: "+index+" is "+fault.get('info'))
                continue
            faulty_code = original_code.copy()
            if type(fault.get('line')) is list:
                faulty_lines = fault.get('line')
                correct_code_lines = fault.get('correct')
                faulty_code_lines = fault.get('faulty')
            else:
                faulty_lines = [fault.get('line')]
                correct_code_lines = [fault.get('correct')]
                faulty_code_lines = [fault.get('faulty')]

            error = False

            for i in range(0, len(faulty_lines)):
                faulty_line = int(faulty_lines[i])
                faulty_code_line = faulty_code_lines[i]+"  # "+index+": "+fault.get('description')
                correct_code_line = correct_code_lines[i]
                if correct_code_line not in faulty_code[faulty_line-1]:
                    print("ERROR when creating "+index+": correct_code not in line "+str(faulty_line) +
                          " in original file!")
                    error = True
                    break
                faulty_code[faulty_line-1] = faulty_code[faulty_line-1].replace(correct_code_line, faulty_code_line)

            if not error:
                with open(faulty_versions_dir+name+'_'+index+'.py', 'w') as faulty_file:
                    faulty_file.writelines(faulty_code)


def analyze_faults(faults):
    if 'info' in faults.index.values:
        faults_cleaned = faults[faults['info'].apply(lambda x: not isinstance(x, str))]
        print('NOT BUGS:')
        not_bugs = faults[faults['info'].apply(lambda x: isinstance(x, str))]
        print(not_bugs[['line', 'info']].to_string())
    else:
        faults_cleaned = faults

    print('\nFAULT TYPES:')
    print(faults.description.value_counts())

    print("\nFAULTS SORTED AFTER CHANGED LINES:")
    single_faults = faults_cleaned[faults_cleaned['line'].apply(lambda x: isinstance(x, int))]
    double_faults = faults_cleaned[faults_cleaned['line'].apply(lambda x: isinstance(x, list))]
    single_faults_sorted = single_faults.sort_values('line')
    print(single_faults_sorted[['line', 'faulty']].to_string())
    double_faults_sorted = double_faults.sort_values('line')
    print(double_faults_sorted[['faulty', 'line']].to_string())


if __name__ == "__main__":
    main()
