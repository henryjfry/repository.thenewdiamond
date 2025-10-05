from concurrent.futures import ThreadPoolExecutor, wait
from cocoscrapers.modules import log_utils

#Init global thread pool
tp = ThreadPoolExecutor(max_workers=10)

def run_and_wait(func, iterable):
#    for i in iterable:
#        tp.map(func,i)
#    results = tp.map(func,iterable)
#    return results
    futures = []
    for item in iterable:
        # Submit each task to the thread pool
        future = tp.submit(func, item)
        futures.append(future)
    # Wait for all tasks to complete
    wait(futures)

def run_and_wait_multi(func, iterable):
    results = tp.map(lambda args: func(*args),iterable)
    return results

def shutdown_executor():
    tp.shutdown(wait=True)
