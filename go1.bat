@echo off
set repetitions=30

START cmd /k python run.py -a age -o maximin -r %repetitions%
START cmd /k python run.py -a gender -o maximin -r %repetitions%
START cmd /k python run.py -a ethnicity -o maximin -r %repetitions%

START cmd /k python run.py -a age -o speed -r %repetitions%
START cmd /k python run.py -a gender -o speed -r %repetitions%
START cmd /k python run.py -a ethnicity -o speed -r %repetitions%

