:: Run all scripts in the behavython env 
@REM call mamba activate behavython
@REM echo Running data_preparation...
@REM call python -m src.stage_1.run_stage_1
@REM echo Running derived data_preparation...
call python -m src.stage_2.run_stage_2
echo run plotting
call python -m src.stage_3.run_stage_3
pause All stages completed.