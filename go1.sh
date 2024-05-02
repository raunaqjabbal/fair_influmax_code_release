#!/bin/bash

repetitions=30

gnome-terminal -- python run.py -a age -o maximin -r "$repetitions"
gnome-terminal -- python run.py -a gender -o maximin -r "$repetitions"
gnome-terminal -- python run.py -a ethnicity -o maximin -r "$repetitions"

gnome-terminal -- python run.py -a age -o speed -r "$repetitions"
gnome-terminal -- python run.py -a gender -o speed -r "$repetitions"
gnome-terminal -- python run.py -a ethnicity -o speed -r "$repetitions"
