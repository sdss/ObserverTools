#!/bin/bash
#
# $Id: find-ssh-agent.sh 143 2009-10-19 15:34:19Z bw55 $
#
# Look for an instance of ssh-agent running on the current host.
# If one exists, emit the environment variable settings needed to connect to
# that ssh-agent.
#
# Example (for csh):
#   eval `find-ssh-agent.sh`
#
# Example (for bash):
#   . find-ssh-agent.sh
#
if test ${SSH_AUTH_SOCK:-foo} = "foo"; then
    for dir in $(find /tmp -nowarn -type d -user ${USER} -name "ssh-*" 2>/dev/null)
    do
        pid=$(ls ${dir} | cut -d. -f2)
        foo=$(uname)
        if [[ ${foo:0:6} = "CYGWIN" ]]; then
            trypid=$(ps | grep ssh-agent | grep -v grep | awk '{print $1}')
            if [[ -z "$trypid" ]]; then
                procname='nope'
            else
                procname='ssh-agent'
            fi
        else
            #
            # The real ssh-agent process id is usually $pid + 1
            #
            trypid=$((${pid} + 1))
            procname=$(ps --format comm= ${trypid})
        fi
        if test "${procname}" == "ssh-agent"; then
            if test "${SHELL}" == "/bin/tcsh"; then
                echo "setenv SSH_AGENT_PID ${trypid};"
                echo "setenv SSH_AUTH_SOCK ${dir}/agent.${pid};"
            else
                export SSH_AGENT_PID=${trypid}
                export SSH_AUTH_SOCK=${dir}/agent.${pid}
            fi
            break
        fi
    done
fi
