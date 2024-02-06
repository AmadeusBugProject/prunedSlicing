# prunedSlicing
This is a proof of concept implementation of pruned slicing as discussed in our paper *"Pruning Boolean Expressions to Shorten Dynamic and Relevant Slices"* by Thomas Hirsch and Birgit Hofer.

## Example
A very simplistic usage example of our slicer is implemented in [slicing_demo.py](slicing_demo.py).

## Tracing and Slicing
Our python ast based tracer can be found in [ast_tree_tracer/trace.py](ast_tree_tracer/trace.py).
Our dynamic slicer and pruned slicer implementations are located in [slicing/slice.py](slicing/slice.py).

## Environment
For portability reasons we provide a minimal Conda environment in [environment.yml](environment.yml) and a [requirements.txt](requirements.txt).

## Test suite
The test suite uses the python library `timeout-decorator`, that relies on OS signal functionality only on *nix OS's to cancel tests exceeding a timeout value specified in [constants.py](constants.py).
The [test](test) package houses all tests.
Use `pytest` to run all tests in the package.
[conftest.py](test/conftest.py) contains the blacklisted tests and explanations and reasons for exclusion.

## Evaluation scripts
[evaluation/slice_benchmarks](evaluation/slice_benchmarks) contains the scripts calculating slices for all benchmark inputs.
The resulting slices and data can be found in [evaluation/data](evaluation/data).
Data analysis, evaluation, and creation of figures is performed by the scripts in [evaluation](evaluation).

## Refactory, Quix, and Tcas Benchmarks
The benchmarks code and inputs can be found in [benchmark](benchmark).

# Limitations

- Object orientation (tracing/slicing only relevant instances of the same class).
    If there are multiple instances of a class, and the user is only interested to slice for a variable that is connected to one of these instances, the tracing as it is now implemented does not distinguish the code that runs in a class method based on its caller.
- Lambdas
- Varargs in function calls
- Named args in function calls
- Single file tracing only
- Class variables (not tb. confused with instance variables) of a class are not supported
- Decorators (e.g. @staticmethod or @classmethod)
- globals statements are not supported
- Linebreaks in statements dont work
- Inheritance also not really supported
- Exception handling
- Nested functions
- Nested classes
- Imports are always included in sliced code (although they are not listed in the slice)
- Changes of parameters within function calls 

A listing for excluded keywords and constructs can be found in [ast_tree_tracer/transformer_utils.py::check_for_unsupported_constructs](ast_tree_tracer/transformer_utils.py)


