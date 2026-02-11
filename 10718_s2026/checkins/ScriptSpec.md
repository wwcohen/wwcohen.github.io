# Script specifications

## Inputs

The input to the script is an input subdirectory name, a string
matching a date, and an output subdirectory name. The input
subdirectory will contain two files

* a .tsv file, which contains schedules for two days.  On each day,
  several groups of students will make short presentations.
* a submissions.zip file, exported from GradeScope, which contains
  * a directory of presentation materials
  * metadata for that directory which associates each presentation
  with a student.

There is a sample input subdirectory called 'test_data'.

## Behavior

The script is called prepare_presentations.py and when invoked it will
create an output directory which contains every presentation file
that will be needed on the given date, renamed as consistently as

DATE-STARTTIME-STUDENTNAME-ORIGINALFILENAME

So the files can be easily accessed during the presentation.

