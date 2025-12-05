#!/bin/bash
# Cast3m calculator script for fz framework

# Check if castem2000 or cast3m is available
if command -v castem2000 &> /dev/null; then
    CAST3M_CMD="castem2000"
elif command -v cast3m &> /dev/null; then
    CAST3M_CMD="cast3m"
else
    echo "Error: Cast3m executable (castem2000 or cast3m) not found in PATH"
    exit 1
fi

# Process arguments
if [ -d "$1" ]; then
    # If directory is provided, cd into it
    cd "$1"
    DGIBI_FILE=$(ls *.dgibi 2>/dev/null | head -n 1)
    shift
elif [ $# -gt 0 ]; then
    # If files are provided, find the .dgibi file
    DGIBI_FILE=""
    for f in "$@"; do
        if [[ "$f" == *.dgibi ]]; then
            DGIBI_FILE="$f"
            break
        fi
    done
    if [ -z "$DGIBI_FILE" ]; then
        echo "Error: No .dgibi file found in input files"
        exit 1
    fi
    shift $#
else
    echo "Usage: $0 <file.dgibi or directory>"
    exit 2
fi

# Check if we found a .dgibi file
if [ -z "$DGIBI_FILE" ]; then
    echo "Error: No .dgibi file found"
    exit 1
fi

# Validate the .dgibi file path (basic validation)
if [[ ! "$DGIBI_FILE" =~ ^[a-zA-Z0-9./_-]+$ ]]; then
    echo "Error: Invalid characters in .dgibi filename"
    exit 1
fi

# Check if file exists and is readable
if [ ! -r "$DGIBI_FILE" ]; then
    echo "Error: Cannot read .dgibi file: $DGIBI_FILE"
    exit 1
fi

# Run Cast3m
# Redirect output to castem.out
$CAST3M_CMD "$DGIBI_FILE" > castem.out 2>&1

# Check exit status
exit_code=$?
if [ $exit_code -ne 0 ]; then
    echo "Error: Cast3m execution failed with exit code $exit_code"
    cat castem.out
    exit $exit_code
fi

exit 0
