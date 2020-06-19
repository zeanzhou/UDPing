# https://docs.microsoft.com/en-us/windows/console/setconsolectrlhandler

import sys
import signal

_console_ctrl_handlers = {}
def set_signal_handler(signal_handler):
    if sys.platform == 'win32':

        import ctypes
        from ctypes import windll, wintypes
        _HandlerRoutine = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.DWORD)
        windll.kernel32.SetConsoleCtrlHandler.argtypes =[_HandlerRoutine, wintypes.BOOL]
        windll.kernel32.SetConsoleCtrlHandler.restype  = wintypes.BOOL

        _win_signal_handler = _HandlerRoutine(signal_handler)
        if windll.kernel32.SetConsoleCtrlHandler(_win_signal_handler, True):  # True=Add, False=Remove
            _console_ctrl_handlers[signal_handler] = _win_signal_handler # save handler to avoid being gc-ed
        else:
            raise ctypes.WinError()
        
    else:
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)


## Example Handler

# For Windows: https://docs.microsoft.com/en-us/windows/console/handlerroutine
def example_signal_handler(signum, frame=None): # frame=None is for win
    if sys.platform == 'win32':
        if signum == signal.CTRL_C_EVENT:
            print("Ctrl-C detected!")
        else:
            print(f"Signal detected! {signum}")
        return 1 # if handled correctly, the handler should return 1, for win
    else:
        if signum == signal.SIGINT:
            print("Ctrl-C detected!")
        else:
            print(f"Signal detected! {signum}")
