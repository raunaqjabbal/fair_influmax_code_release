@echo off
set repetitions=15 

START cmd /k python run.py -a age -o maximin -r %repetitions%
START cmd /k python run.py -a gender -o maximin -r %repetitions%
START cmd /k python run.py -a ethnicity -o maximin -r %repetitions%

START cmd /k python run.py -a age -o speed -r %repetitions%
START cmd /k python run.py -a gender -o speed -r %repetitions%
START cmd /k python run.py -a ethnicity -o speed -r %repetitions%

START cmd /k python run.py -a age -o rationality -r %repetitions%
START cmd /k python run.py -a gender -o rationality -r %repetitions%
START cmd /k python run.py -a ethnicity -o rationality -r %repetitions%

START cmd /k python run.py -a age -r %repetitions%
START cmd /k python run.py -a gender -r %repetitions%
START cmd /k python run.py -a ethnicity -r %repetitions%
