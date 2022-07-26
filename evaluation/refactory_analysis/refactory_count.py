import glob
import shutil
import pandas

from benchmark.benchmark_root import benchmark_dir


def main():
    path = benchmark_dir() + '/refactory/data/'
    unique_code_snippets = {}
    all_py_files = glob.glob(path + '**/*.py', recursive=True)
    all_py_files.sort()
    duplicates = []
    for py_file in all_py_files:
        if '/duplicate/' in py_file:
            continue
        with open(py_file, 'r') as fd:
            pycode = fd.read().strip()

        if pycode in unique_code_snippets.keys():
            move_duplicate(py_file)
            duplicates.append({'first occurrence': unique_code_snippets[pycode].replace(path, ''), 'duplicate': py_file.replace(path, '')})
        else:
            unique_code_snippets.update({pycode: py_file})
    pandas.DataFrame(duplicates).to_csv(path + 'duplicates.csv')

    print(len(all_py_files))
    print(len(unique_code_snippets))


def move_duplicate(file_path):
    out_path = file_path.replace('/correct/', '/duplicate/').replace('/fail/', '/duplicate/').replace('/reference/', '/duplicate/').replace('/wrong/', '/duplicate/')
    shutil.move(file_path, out_path)

if __name__ == '__main__':
    main()