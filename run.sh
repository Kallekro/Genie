#!/usr/bin/env bash

SCRIPT=`realpath $0`
SCRIPTPATH=`dirname $SCRIPT`

python3 "${SCRIPTPATH}/src/genie.py" $@