#!/bin/bash

repetitions=30

gnome-terminal -- python run.py -a age -o rationality -r "$repetitions"
gnome-terminal -- python run.py -a gender -o rationality -r "$repetitions"
gnome-terminal -- python run.py -a ethnicity -o rationality -r "$repetitions"

gnome-terminal -- python run.py -a age -r "$repetitions"
gnome-terminal -- python run.py -a gender -r "$repetitions"
gnome-terminal -- python run.py -a ethnicity -r "$repetitions"
