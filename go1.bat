@echo off
set repetitions=15
set savepath= exploration_ignore

START cmd /k python run.py -a age -o maximin --r %repetitions% -p %savepath%
START cmd /k python run.py -a gender -o maximin --r %repetitions% -p %savepath%
START cmd /k python run.py -a ethnicity -o maximin --r %repetitions% -p %savepath%

START cmd /k python run.py -a age -o speed --r %repetitions% -p %savepath%
START cmd /k python run.py -a gender -o speed --r %repetitions% -p %savepath%
START cmd /k python run.py -a ethnicity -o speed --r %repetitions% -p %savepath%

START cmd /k python run.py -a age -o rationality --r %repetitions% -p %savepath%
START cmd /k python run.py -a gender -o rationality --r %repetitions% -p %savepath%
START cmd /k python run.py -a ethnicity -o rationality --r %repetitions% -p %savepath%

START cmd /k python run.py -a age  --r %repetitions% -p %savepath%
START cmd /k python run.py -a gender  --r %repetitions% -p %savepath%
START cmd /k python run.py -a ethnicity  --r %repetitions% -p %savepath%

