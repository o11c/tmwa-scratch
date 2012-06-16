#!/bin/bash -e
##    {filename} - {description}
##
{prepend:##
{reparse:{include:{conf_dir}/{license}}}}

die() {{ echo "$@"; exit 1; }}

DIRNAME=$(dirname "$0")
BASENAME=$(basename "$0")
