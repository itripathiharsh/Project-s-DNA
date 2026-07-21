import atexit
from concurrent.futures import ThreadPoolExecutor

# A global thread pool for CPU-bound or IO-bound operations that don't need a dedicated pool.
# We set max_workers to a reasonable default, for example 8.
_global_executor = ThreadPoolExecutor(max_workers=16)

def get_executor() -> ThreadPoolExecutor:
    return _global_executor

@atexit.register
def shutdown_executor():
    _global_executor.shutdown(wait=False)
