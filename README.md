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

1. Start with a .txt file of notes. Note: The MuffinTrack format is best utilized with a text-editor where matching text fields are highlighted when they are selected to easily visually scan through elements/ids 
```
 - End Users want to start utilizing project on Dec. 1
    - Needs to be fully functional before the Thanksgiving break
 - Cost center for project from Finance for ordering?
 - All equipment must be received for configuration by Oct. 1
 - Lyle is no longer on project team
 - Need to test configuration
 - Get director approval
```


2. Add formatting to lines that need to be parsed. 
For lines that should become "Question" objects, prefix the line with "??". 
Important notes should have the prefix "!!". 
Task notes should have the prefix "++".
Within a line that has a prefix listed above if "--" is found, the rest of the line will be considered a comment on the generated element

```
 - End Users want to start utilizing project on Dec. 1
    !! Needs to be fully functional before the Thanksgiving break
 ?? Cost center for project from Finance for ordering?
 !! All equipment must be received for configuration by Oct. 1 -- Per Director, call purchasing if it's not received by 9/25
 - Lyle is no longer on project team
 ++ Need to test configuration
 ++ Get director approval
```


3. Run MuffinTrack as a CLI (`python3 -m MuffinTrack`). It will ask for the file path to the .txt file. MuffinTrack will parse the file, identifying the lines that need to be expanded into objects based on the prefixes found, and add those objects to the beginning of the file. Objects will be given a unique identifier that will trace back to the originating line so context for the object can easily be traced. The updated file will have a similar structure as the example below:
```
***Questions
createDateTime: 2026-04-03 20:21:25.424320
text:  Cost center for project from Finance for ordering?
status: Open
answer: None
comments: None
relatedId: None
assignedId: 20260403Q1


***Important
createDateTime: 2026-04-03 20:21:25.424172
text:  Needs to be fully functional before the Thanksgiving break
status: Active
comments: None
relatedId: None
assignedId: 20260403I1

createDateTime: 2026-04-03 20:21:25.424416
text:  All equipment must be received for configuration by Oct. 1 
status: Active
comments:  Per Director, call purchasing if it's not received by 9/25
relatedId: None
assignedId: 20260403I2


***Tasks
createDateTime: 2026-04-03 20:21:25.424485
text:  Need to test configuration
status: To Do
dueDate: None
comments: None
relatedId: None
assignedId: 20260403T1

createDateTime: 2026-04-03 20:21:25.424548
text:  Get director approval
status: To Do
dueDate: None
comments: None
relatedId: None
assignedId: 20260403T2


***Original Input
 - End Users want to start utilizing project on Dec. 1
    !! Needs to be fully functional before the Thanksgiving break [[20260403I1]]
 ?? Cost center for project from Finance for ordering? [[20260403Q1]]
 !! All equipment must be received for configuration by Oct. 1 -- Per Director, call purchasing if it's not received by 9/25 [[20260403I2]]
 - Lyle is no longer on project team
 ++ Need to test configuration [[20260403T1]]
 ++ Get director approval [[20260403T2]]

```

4. Objects can be modified in any way and modifications will persist through repeated parsings. Subsequent notes can be added anywhere below the "***Original Input" header and the file can be reparsed to the same effect. The prefixes above can also be added in "text" or "comments" element fields to be parsed as a new element with a relatedId that is mapped to the original id (example below).

```
***Questions
createDateTime: 2026-03-29 12:29:24.469269
text:  Test Nested Question 01
status: Open
answer: None
comments: None
relatedId:  [[20260329T1]]
assignedId: 20260329Q1


***Important

***Tasks
createDateTime: 2026-03-29 11:11:06.229244
text:  Test Task 01
status: To Do
dueDate: None
comments: ?? Test Nested Question 01 [[20260329Q1]]
relatedId: None
assignedId: 20260329T1


***Original Input
++ Test Task 01 [[20260329T1]]
```


Additional Notes
===================
* Content of the elements are not modified during processing
* If there is a parse failure, an error will be returned and the version of the file read in at runtime will be restored to the filepath
* If an unsaved file is processed, the unsaved changes will be lost



More resources
==============

* Package: https://pypi.org/project/MuffinTrack/
* Sources: https://github.com/jstz84/MuffinTrack
