import asyncio
from threading import Thread


def run_async(func, *args, **kwargs):
    """
    Runs a function asynchronously, usefull for when you are in an async context.

    Parameters
    ----------
    func
        function to call
    args
        args of function
    kwargs
        kwargs of function

    Returns
    -------
    A future for the call.

    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    if loop and loop.is_running():
        thread = _RunThread(func, args, kwargs)
        thread.start()
        thread.join()
        return thread.result
    else:
        return asyncio.run(func(*args, **kwargs))


class _RunThread(Thread):
    def __init__(self, func, args, kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.result = None
        super().__init__()

    def run(self):
        self.result = asyncio.run(self.func(*self.args, **self.kwargs))
