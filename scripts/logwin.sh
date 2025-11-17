#!/usr/bin/env bash
# Usage: ./logwin.sh <pillar> "<task>" "<notes>"
DATE=$(date +%F)
PILLAR=$1
TASK=$2
NOTES=$3
echo "$DATE,$PILLAR,$TASK,$NOTES" >> $(git rev-parse --show-toplevel)/daily-log.csv
