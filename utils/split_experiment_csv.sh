#!/bin/bash

# Base folder
base="../csv/experiment1_adaptive_streaming_0908"

# Make sure target folders exist
mkdir -p "$base/baseline"
mkdir -p "$base/res_only"

# Move matching files
mv "$base"/*baseline*.csv "$base/baseline"/ 2>/dev/null
mv "$base"/*res_only*.csv "$base/res_only"/ 2>/dev/null

echo "Done. Baseline CSVs moved to $base/baseline, res_only CSVs moved to $base/res_only."
