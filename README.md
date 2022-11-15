# CS221CourseScheduling
Repository for the CS 221 course scheduling project.

```
$ python schedule_courses.py --help
usage: ScheduleCourses [-h] [-d DATA_DIRECTORY] [-p PROGRAM]
                       [-y YEARS [YEARS ...]]

Create a course schedule for a two year Stanford MS program.

optional arguments:
  -h, --help            show this help message and exit
  -d DATA_DIRECTORY, --data_directory DATA_DIRECTORY
                        The local directory where course data is stored.
                        Defaults to "data/".
  -p PROGRAM, --program PROGRAM
                        The degree program. Should be in {CS, EE, ICME}.
                        Defaults to "CS".
  -y YEARS [YEARS ...], --years YEARS [YEARS ...]
                        The program years. Each year should be formatted as
                        <YYYY>-<YYYY>. Defaults to "2021-2022 2022-2023".
```

## Running Course Scheduling
Example usage:
```
python schedule_courses.py -d course_data -p EE -y 2022-2023 2023-2024
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
