#!/usr/bin/env python3
"""
Profile script using sys.setprofile() for deterministic 100% coverage profiling.
This is injected into the target Python process to capture all function calls.
"""

import sys
import os
import time
import atexit
import threading
import inspect

# Get configuration from environment
profile_log_file = os.environ.get('CINTENT_PROFILE_LOG')
function_log_file = os.environ.get('CINTENT_FUNCTIONS_LOG')
step_id = os.environ.get('CINTENT_STEP_ID', 'error')

_workspace = os.environ.get('GITHUB_WORKSPACE', '')
_extra = os.environ.get('CINTENT_PROJECT_PATHS', '')
_ws_prefixes = tuple(
    p for p in ([_workspace] + _extra.split(os.pathsep)) if p
)
def _is_workspace(filename: str) -> bool:
    return bool(_ws_prefixes) and filename.startswith(_ws_prefixes)

log_timestamp = int(time.time() * 1000000000) # nanoseconds
if not profile_log_file:
    log_dir = os.environ.get('CINTENT_LOGS', '/tmp')
    profile_log_file = f"{log_dir}/{log_timestamp}.{step_id}.setprofile.csv"
if not function_log_file:
    log_dir = os.environ.get('CINTENT_LOGS', '/tmp')
    function_log_file = f"{log_dir}/{log_timestamp}.{step_id}.setprofile.functions.csv"

# Open log files
profile_log = open(profile_log_file, 'w')
profile_log.write("timestamp_ns,event,function,filename,line\n")
profile_log.flush()
function_log = open(function_log_file, 'w')
function_log.write("name,path,line,is_external,code\n")
function_log.flush()

call_count = 0
function_count = 0
logged_functions = set()
max_calls = int(os.environ.get('CINTENT_MAX_CALLS', '1000000'))  # Limit to prevent huge files
is_shutting_down = False
write_lock = threading.Lock()

def profile_handler(frame, event, arg):
    """
    Profile handler called on every function call/return/exception.

    Events:
    - 'call': function is called
    - 'return': function is returning
    - 'c_call': C function is about to be called
    - 'c_return': C function has returned
    - 'c_exception': C function has raised an exception
    """
    global call_count
    global function_count
    global logged_functions

    if is_shutting_down:
        return

    # Limit total calls to prevent giant log files
    if call_count >= max_calls:
        return

    # Filter out profiler itself
    if 'setprofile_profiler' in frame.f_code.co_filename:
        return

    # Only log call and return events for Python functions
    if event in ('call', 'return'):
        with write_lock:
            is_external = _ws_prefixes and not _is_workspace(frame.f_code.co_filename)
            # if is_external:
            #     return
            if is_shutting_down:
                return
            if call_count >= max_calls:
                return
            call_count += 1

            timestamp_ns = int(time.time() * 1000000000)
            function = frame.f_code.co_name
            filename = frame.f_code.co_filename
            line = frame.f_lineno

            key = (function, filename, line)
            if event == 'call' and key not in logged_functions:
                try:
                    code = inspect.getsource(frame)
                except:
                    code = ''
                function_log.write(f"{function},{filename},{line},{is_external},{code}\n")
                logged_functions.add(key)
                function_count += 1
            profile_log.write(f"{timestamp_ns},{event},{function},{filename},{line}\n")

            # Flush periodically
            if call_count % 1000 == 0:
                profile_log.flush()
            if function_count % 100 == 0:
                function_log.flush()

def cleanup():
    """Cleanup on exit"""
    global is_shutting_down
    is_shutting_down = True
    threading.setprofile(None)
    sys.setprofile(None)
    with write_lock:
        profile_log.flush()
        profile_log.close()
        function_log.flush()
        function_log.close()
    print(f"[setprofile] Captured {function_count} functions to {function_log_file} and {call_count} calls to {profile_log_file}", file=sys.stderr)

# Register cleanup
atexit.register(cleanup)

# Install the profiler for the current thread and all future threads.
# Without threading.setprofile, framework worker threads (where callbacks
# often run) are invisible to this profiler.
threading.setprofile(profile_handler)
sys.setprofile(profile_handler)

print(f"[setprofile] Profiling enabled, logging functions to {function_log_file} and calls to {profile_log_file}", file=sys.stderr)
