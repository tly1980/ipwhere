#!/bin/bash
export PYTHONPATH='./src' && src/ipwhere/app.py $1 ./data/inmemstore.pickle
