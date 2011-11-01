"""
Monitor files and kill mod_wsgi processes if any files change

Details here -- http://code.google.com/p/modwsgi/wiki/ReloadingSourceCode#Restarting_Daemon_Processes

Added the ability to track directories
"""

import os
import sys
import time
import signal
import threading
import atexit
import Queue

_interval = 1.0
_times = {}
_files = []

_running = False
_queue = Queue.Queue()
_lock = threading.Lock()

def _restart(path):
    sys.stderr = open('/dev/null')
    _queue.put(True)
    prefix = 'monitor (pid=%d):' % os.getpid()
    print '%s Change detected to \'%s\'.' % (prefix, path)
    print '%s Triggering process restart.' % prefix
    os.kill(os.getpid(), signal.SIGINT)

def _modified(path):
    try:
        # If path doesn't denote a file and were previously
        # tracking it, then it has been removed or the file type
        # has changed so force a restart. If not previously
        # tracking the file then we can ignore it as probably
        # pseudo reference such as when file extracted from a
        # collection of modules contained in a zip file.

        if not os.path.isfile(path):
            return path in _times

        # Check for when file last modified.

        mtime = os.stat(path).st_mtime
        if path not in _times:
            _times[path] = mtime

        # Force restart when modification time has changed, even
        # if time now older, as that could indicate older file
        # has been restored.

        if mtime != _times[path]:
            return True
    except:
        # If any exception occured, likely that file has been
        # been removed just before stat(), so force a restart.

        return True

    return False

def _monitor():
    while 1:
        # Check modification times on all files in sys.modules.

        for module in sys.modules.values():
            if not hasattr(module, '__file__'):
                continue
            path = getattr(module, '__file__')
            if not path:
                continue
            if os.path.splitext(path)[1] in ['.pyc', '.pyo', '.pyd']:
                path = path[:-1]
            if _modified(path):
                return _restart(path)

        # Check modification times on files which have
        # specifically been registered for monitoring.

        for path in _files:
            if _modified(path):
                return _restart(path)

        # Go to sleep for specified interval.

        try:
            return _queue.get(timeout=_interval)
        except:
            pass

_thread = threading.Thread(target=_monitor)
_thread.setDaemon(True)

def _exiting():
    try:
        _queue.put(True)
    except:
        pass
    _thread.join()

atexit.register(_exiting)

def _get_files_from_dir(dir):
    basedir = dir
    subdirlist = []
    for item in os.listdir(dir):
        item_full_path = os.path.join(basedir, item)
        if os.path.isfile(item_full_path):
            if not item_full_path in _files:
                _files.append(item_full_path)
        else:
            subdirlist.append(item_full_path)
    for subdir in subdirlist:
        _get_files_from_dir(subdir)

def track(path):
    if os.path.isfile(path):
        if not path in _files:
            _files.append(path)
    else:
        _get_files_from_dir(path)

def start(interval=1.0):
    global _interval
    if interval < _interval:
        _interval = interval

    global _running
    _lock.acquire()
    if not _running:
        prefix = 'monitor (pid=%d):' % os.getpid()
        print >> sys.stderr, '%s Starting change monitor.' % prefix
        _running = True
        _thread.start()
    _lock.release()
