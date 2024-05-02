@echo off
set repetitions=30


START cmd /k python run.py -a age -o rationality -r %repetitions%
START cmd /k python run.py -a gender -o rationality -r %repetitions%
START cmd /k python run.py -a ethnicity -o rationality -r %repetitions%

START cmd /k python run.py -a age -r %repetitions%
START cmd /k python run.py -a gender -r %repetitions%
START cmd /k python run.py -a ethnicity -r %repetitions%
