# CS221CourseScheduling
Repository for the CS 221 course scheduling project

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
