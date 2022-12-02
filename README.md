# CS221CourseScheduling
Repository for the CS 221 course scheduling project.

```
$ python schedule_courses.py --help
usage: ScheduleCourses [-h] [-d DATA_DIRECTORY] [-p PROGRAM]
                       [-y YEARS [YEARS ...]] [-mq MAX_QUARTER]
                       [-ms MAX_SUCCESSORS] [-m MODEL] [-c CONFIG_NAME]
                       [-v VERBOSE]

Create a course schedule for a two year Stanford MS program.

optional arguments:
  -h, --help            show this help message and exit
  -d DATA_DIRECTORY, --data_directory DATA_DIRECTORY
                        The local directory where course data is stored.
                        Defaults to "data/".
  -p PROGRAM, --program PROGRAM
                        The degree program. Should be in {CS, EE, CME}.
                        Defaults to "CS".
  -y YEARS [YEARS ...], --years YEARS [YEARS ...]
                        The program years. Each year should be formatted as
                        <YYYY>-<YYYY>. Defaults to "2021-2022 2022-2023".
  -mq MAX_QUARTER, --max_quarter MAX_QUARTER
                        The maximum number of quarters to graduate in.
  -ms MAX_SUCCESSORS, --max_successors MAX_SUCCESSORS
                        The maximum number of successors to return from
                        successors_and_cost.
  -m MODEL, --model MODEL
                        Whether to model the problem as a search problem or
                        CSP.
  -c CONFIG_NAME, --config_name CONFIG_NAME
                        The config filename corresponding to a student's
                        schedule requests.
  -v VERBOSE, --verbose VERBOSE
                        Whether to run UCS in verbose mode.
```

## Running Course Scheduling
Note that for both Search and CSP, the program can take >10 minutes to find a solution.

By default, `schedule_courses` uses the CSP model and the student profile found at `profile1.yaml`. To run this default case,
don't set any command line arguments:
```
python schedule_courses.py
```
You can change the student profile to anything in the `configs` folder by using the `--config_name` argument.

To run the Search model, use the `--model` argument:
```
python schedule_courses.py --model search
```

## Setup
Create conda environment and install requirements:
```sh
conda create --name course_scheduling python=3.7.13 -y
conda activate course_scheduling
pip install -r requirements.txt
```

### Pre-Commit
Please set up pre-commit before pushing to the repo. After setting it up, checks/auto-formatters will automatically run whenever you commit files. This will ensure that buggy code does not go into a remote branch and style is consistent across files. If you fail a check, you may need to fix the file, add, and commit it again.

Set up pre-commit hooks:
```sh
pre-commit install
```

(Optional) To run pre-commit on all files:
```sh
pre-commit run --all-files
```

### Testing
Run the following from the root of this directory to run all unit tests:
```sh
pytest tests/
```
or:
```sh
python -m pytest tests/
```
