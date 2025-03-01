#!/bin/sh
get_current_directory() {
    current_file="${0}"
    echo "${current_file%/*}"
}
CWD=$(get_current_directory)
PID="${CWD}/user_data/pid"
PID_NO=$(cat $PID)

strace -p$PID_NO -s9999 -e write