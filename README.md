MuffinTrack
==========


Introduction
============

MuffinTrack is a text parser that enhances note files with organized, actionable objects in order to facilitate project management. The utility offers a simple, free framework for organizing project development from a stream-of-consciousness notes list into objects for "Questions to be answered", "Important notes to remember", and "Tasks to do". 

In tech, there is an expectation that engineers, support techs, administrators, etc. should be able to plan, organize, maintain communication, and execute end-to-end projects, sometimes with no assistance. The aim of this effort is to provide a utility for individuals who have not been trained as project managers to keep projects organized without hefty licensing costs or bulky software implementations.

Installation
============

MuffinTrack can be installed using the usual Python packaging tools.
Example:

`pip install MuffinTrack`

Using MuffinTrack
========================

1. Start with a .txt file of notes
```
 - End Users want to start utilizing project on Dec. 1
    - Needs to be fully functional before the Thanksgiving break
 - Cost center for project from Finance for ordering?
 - All equipment must be received for configuration by Oct. 1
 - Lyle is no longer on project team
 - Need to test configuration
 - Get director approval
```


2. Add prefixes to lines that need to be parsed. 
For lines that should become "Question" objects, prefix the line with "??". 
Important notes should have the prefix "!!". 
Task notes should have the prefix "++".
```
 - End Users want to start utilizing project on Dec. 1
    !! Needs to be fully functional before the Thanksgiving break
 ?? Cost center for project from Finance for ordering?
 !! All equipment must be received for configuration by Oct. 1
 - Lyle is no longer on project team
 ++ Need to test configuration
 ++ Get director approval
```


3. Run MuffinTrack as a CLI (`python3 -m MuffinTrack`). It will ask for the file path to the .txt file. MuffinTrack will parse the file, identifying the lines that need to be expanded into objects based on the prefixes found, and add those objects to the beginning of the file. Objects will be given a unique identifier that will trace back to the originating line so context for the object can easily be traced. The updated file will have a similar structure as the example below:
```
 ***Questions
 createDateTime: 2025-09-07 12:42:35.421960
 questionText:  Cost center for project from Finance for ordering?
 questionStatus: Open
 answer: None
 assignedId: 20250907Q1
 
 
 ***Important
 createDateTime: 2025-09-07 12:42:35.419175
 importantText:  Needs to be fully functional before the Thanksgiving break
 importantStatus: Active
 assignedId: 20250907I1

 createDateTime: 2025-09-07 12:42:35.422081
 importantText:  All equipment must be received for configuration by Oct. 1
 importantStatus: Active
 assignedId: 20250907I2


 ***Tasks
 createDateTime: 2025-09-07 12:42:35.422224
 taskText:  Need to test configuration
 taskStatus: To Do
 dueDate: None
 assignedId: 20250907T1

 createDateTime: 2025-09-07 12:42:35.422361
 taskText:  Get director approval
 taskStatus: To Do
 dueDate: None
 assignedId: 20250907T2

 ***Original Input
 - End Users want to start utilizing project on Dec. 1
     !! Needs to be fully functional before the Thanksgiving break [[20250907I1]]
 ?? Cost center for project from Finance for ordering? [[20250907Q1]]
 !! All equipment must be received for configuration by Oct. 1 [[20250907I2]]
 - Lyle is no longer on project team
 ++ Need to test configuration [[20250907T1]]
 ++ Get director approval [[20250907T2]]
```

4. Objects can be modified in any way and modifications will persist through repeated parsings. Subsequent notes can be added anywhere below the "***Original Input" header and the file can be reparsed to the same effect.


Additional Notes
===================
* No AI is used for this parser so content of the elements are not modified during processing
* If there is a parse failure, an error will be returned and the version of the file read in at runtime will be restored to the filepath



More resources
==============

* Package: https://pypi.org/project/MuffinTrack/
* Sources: https://github.com/jstz84/MuffinTrack
