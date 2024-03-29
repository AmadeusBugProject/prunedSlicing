import pathlib

QUIX_TIMEOUT = 10
REFACTORY_TIMEOUT = 0.1

MAX_TRACE_LENGTH = 10**6
NUM_RUNS_TIMEIT = 50

CODE_CLEANUP_TIMEOUT = 1
TRACING_AUGMENTATION_TIMEOUT = 5
TRACING_TIMEOUT = 1
SLICING_TIMEOUT = 1
CODE_GEN_TIMEOUT = 1

# HW INFO

# AMD® Ryzen™ 7 Pro 3700U Processor (2.30 GHz, up to 4.00 GHz Max Boost, 4 Cores, 8 Threads, 4 MB Cache)
# 16 GB ram
# Debain 11
# Python 3.9

def root_dir():
    return str(pathlib.Path(__file__).parent) + '/'