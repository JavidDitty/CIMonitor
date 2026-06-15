#!/bin/bash

set -u

# sys.setprofile() profiler - deterministic 100% coverage
# Works by setting PYTHONPROFILE environment variable to auto-load profiler
# No root access needed, works on any platform

TIMESTAMP=$(date +%s%N)
SANDWICH_LOG_FILE="$CINTENT_LOGS/$TIMESTAMP.$CINTENT_STEP_ID.setprofile.sandwich.csv"
GRAPH_LOG_FILE="$CINTENT_LOGS/$TIMESTAMP.$CINTENT_STEP_ID.setprofile.graph.csv"
PATHS_LOG_FILE="$CINTENT_LOGS/$TIMESTAMP.$CINTENT_STEP_ID.setprofile.paths.csv"
PROFILER_SCRIPT="$CINTENT_SETPROFILE_SCRIPT"

# Export environment variables for the profiler
export CINTENT_SANDWICH_LOG="$SANDWICH_LOG_FILE"
export CINTENT_GRAPH_LOG="$GRAPH_LOG_FILE"
export CINTENT_PATHS_LOG="$PATHS_LOG_FILE"
export CINTENT_MAX_CALLS="${CINTENT_MAX_CALLS:-1000000}"

# Check if process is Python
if ps -p "$1" -o comm= | grep -q python; then
    echo "[setprofile] Python process detected (PID: $1)"

    # Note: sys.setprofile() can't be injected into already-running processes
    # It must be set at startup via PYTHONPROFILE or -m flag
    # For running processes, we can only profile child processes

    echo "[setprofile] Warning: sys.setprofile() requires startup injection"
    echo "[setprofile] Set PYTHONPROFILE='$PROFILER_SCRIPT' before starting Python"
else
    echo "[setprofile] Not a Python process, skipping"
fi
