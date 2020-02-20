#!/bin/bash

set -e

cmd="$@"

script_full_path=$(dirname "$0")
$script_full_path/wait_for.sh postgres 5432
#$script_full_path/wait_for.sh elasticsearch 9200

bash -c "$cmd"
