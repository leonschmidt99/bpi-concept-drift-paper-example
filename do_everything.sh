#!/bin/bash

echo "Generating the log..."
./gen_log.py ${1:-"6000"}

echo "Generating the relationship matrix..."
./gen_rel_matrix.py

echo "Generating the measures..."
./gen_measures.py ${2:-"10"}

echo "Evaluating the measures..."
./eval_measures.py ${3:-"400"}
