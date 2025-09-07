from datetime import date,datetime
import os
import logging

class Question:
    def __init__(self,questionText,answer=None,assignedId=None):
        self.createDateTime = datetime.now()
        self.questionText = questionText
        self.questionStatus = 'Open'
        self.answer = answer
        self.idAbbrev = 'Q'
        self.assignedId = assignedId

class Task:
    def __init__(self,taskText,dueDate=None,assignedId=None):
        self.createDateTime = datetime.now()
        self.taskText = taskText
        self.taskStatus = 'To Do'
        self.dueDate = dueDate
        self.idAbbrev = 'T'
        self.assignedId = assignedId

class Important:
    def __init__(self,importantText,assignedId=None):
        self.createDateTime = datetime.now()
        self.importantText = importantText
        self.importantStatus = 'Active'
        self.idAbbrev = 'I'
        self.assignedId = assignedId

def defineLogging():
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.DEBUG)

    return None

def errorHandling(severity,messageToLog,originalFilePath=None,originalFileContent=None):
    if severity == 'Critical':
        logging.critical(messageToLog)
        logging.info('Parsing unable to complete. Restoring file to original state and ending program')

        with open(originalFilePath,"w") as restoreFileContent:
            restoreFileContent.writelines(originalFileContent)

        os._exit(1) # Exit immediately with an error status
    elif severity in ['Unhandled','Warning']:
        logging.warning(messageToLog)

def prefixLookup(prefixValue):

    prefixDict = {'??':'Question','!!':'Important','++':'Task'}

    if prefixValue in prefixDict.keys():
        PrefixName = prefixDict[prefixValue]
    else:
        PrefixName = None

    return PrefixName

def constructId(counterAsInt, shortDate,lineAbbrev):
    counterAsString = str(counterAsInt)

    constructedId = shortDate + lineAbbrev + counterAsString

    return constructedId

def generateId(dynamicLineAbbrev,existingList):
    currentDate = date.today()
    formattedDate = str(currentDate.strftime("%Y%m%d"))

    counter = 1

    generatedId = constructId(counter,formattedDate,dynamicLineAbbrev)

    with open(ExportFilePath, 'r') as exportFile:
        fileContent = exportFile.read()

        while generatedId in fileContent:

            counter = int(counter)

            counter += 1

            generatedId = constructId(counter,formattedDate,dynamicLineAbbrev)

    for existingInstances in existingList:
        if generatedId in existingInstances.values():
            counter = int(counter)

            counter += 1

            generatedId = constructId(counter,formattedDate,dynamicLineAbbrev)


    return generatedId

def printValue(printInstanceList,instanceType,existingData):

    HeaderPrefix = '***'
    HeaderSuffix = '\n'
    
    ImportantHeader = HeaderPrefix + 'Important' + HeaderSuffix
    TaskHeader = HeaderPrefix + 'Tasks' + HeaderSuffix
    OriginalInputHeader = HeaderPrefix + 'Original Input' + HeaderSuffix
    QuestionSectionList = [HeaderPrefix + 'Questions' + HeaderSuffix]
    ImportantSectionList = [HeaderSuffix + ImportantHeader]
    TaskSectionList = [HeaderSuffix + TaskHeader]

    match instanceType:
        case 'Q':
            ListToParse = QuestionSectionList
        case 'I':
            ListToParse = ImportantSectionList
        case 'T':
            ListToParse = TaskSectionList
        case _:
            MessageToSend = 'Instance Type {} not found (01)'.format(instanceType)
            errorHandling('Warning',MessageToSend)

    '''Format the objects to print'''
    for itemsToParse in printInstanceList:
        for key, value in itemsToParse.items():
            DetailToAdd = '{}: {}{}'.format(key,value,HeaderSuffix)
            if DetailToAdd.startswith('assignedId:'):
                ListToParse.append(DetailToAdd)
                ListToParse.append(HeaderSuffix)
            elif DetailToAdd != '' and not DetailToAdd.startswith('idAbbrev:'):
                ListToParse.append(DetailToAdd)
    
    if existingData == False:
        with open(ExportFilePath, "a+") as currentFileContent:
            currentFileContent.writelines(ListToParse)
    else:
        with open(ExportFilePath, "r+") as currentFileContent:
            readFileContent = currentFileContent.readlines()
            unupdatedFileContent = readFileContent

            importantHeaderIndex = readFileContent.index(ImportantHeader) - 2
            taskHeaderIndex = readFileContent.index(TaskHeader) - 2
            fileEndIndex = len(readFileContent) - 1
            
            '''On the first instance add for a file, the Original Content block will be present, but will be missing for subsequent executions'''
            try:         
                originalInputHeaderIndex = readFileContent.index(OriginalInputHeader)
                originalInputHeaderIndexToInsert = originalInputHeaderIndex -1

                '''Remove old original input from text'''
                while originalInputHeaderIndex <= fileEndIndex:
                    readFileContent.pop(originalInputHeaderIndex)

                    fileEndIndex = len(readFileContent) - 1

            except ValueError:
                originalInputHeaderIndex = fileEndIndex
                originalInputHeaderIndexToInsert = fileEndIndex


            '''If there are new elements to add to an existing elements section, add them to the index right before the next section starts. Increase the listed index value appropriately'''
            for details in ListToParse: 
                match instanceType:
                    case 'Q':
                        if HeaderPrefix not in details:
                            readFileContent.insert(importantHeaderIndex,details)

                        importantHeaderIndex += 1
                    case 'I':
                        if HeaderPrefix not in details:
                            readFileContent.insert(taskHeaderIndex,details)

                        taskHeaderIndex += 1
                    case 'T':
                        if HeaderPrefix not in details:
                            readFileContent.insert(originalInputHeaderIndexToInsert - 1,details)
                    case _:
                        MessageToSend = 'Instance Type {} not found (02)'.format(instanceType)
                        errorHandling('Warning',MessageToSend)
            
            try:               
                currentFileContent.truncate(0)
                currentFileContent.seek(0)
            except Exception as e:
                MessageToSend = 'Unable to truncate text due to error: {}'.format(e)
                errorHandling('Warning',MessageToSend)

            try:
                currentFileContent.writelines(readFileContent)
            except Exception as e:
                MessageToSend = 'Unable to add parsed lists due to error: {}'.format(e)
                errorHandling('Critical',MessageToSend,ExportFilePath,unupdatedFileContent)


def generateInstance(dynamicLineType,instanceText,questionList,importantList,taskList):

    match(dynamicLineType):
        case('Question'):

            NewQuestion = Question(questionText=instanceText,answer=None,assignedId=None)

            IdToReturn = generateId(NewQuestion.idAbbrev,questionList)

            NewQuestion.assignedId = IdToReturn

            questionList.append(NewQuestion.__dict__)

        case('Task'):

            NewTask = Task(taskText=instanceText,dueDate=None)

            IdToReturn = generateId(NewTask.idAbbrev,taskList)

            NewTask.assignedId = IdToReturn

            taskList.append(NewTask.__dict__)

        case('Important'):

            NewImportant = Important(importantText=instanceText)

            IdToReturn = generateId(NewImportant.idAbbrev,importantList)

            NewImportant.assignedId = IdToReturn

            importantList.append(NewImportant.__dict__)

        case _:
            print('Dynamic Line Type {} not found'.format(dynamicLineType))

            IdToReturn = None

    returnList = [IdToReturn,questionList,importantList,taskList]

    return returnList

def getContent(filePath):
    OriginalInput = '***Original Input\n'

    with open(filePath, "r+") as fileContent:
        fileDetails = fileContent.readlines()
        modifiedFileList = []
        listToParse = []
        fileChangeFlag = 0
        '''Used to restore the file back to its original state in the event of failure'''
        unchangedFileDetails = fileDetails

        questionInstanceList = []
        importantInstanceList = []
        taskInstanceList = []

        if OriginalInput in fileDetails:
            '''If file has been processed before, find and save the existing original input section'''
            ExistingData = True

            ExtractedOriginalInput = []

            OriginalInputIndex = fileDetails.index(OriginalInput)+1

            EndIndex = len(fileDetails)

            counter = OriginalInputIndex

            while counter < EndIndex:
                ExtractedOriginalInput.append(fileDetails[counter])

                counter += 1

            listToParse = ExtractedOriginalInput
        else:
            '''If the file has never been processed before, empty file so it can be overwritten with formatted data'''
            ExistingData = False
            fileContent.truncate(0)
            fileContent.seek(0)

            listToParse = fileDetails

        for lines in listToParse:

            formattedLines = lines.strip()
            prefixCode = formattedLines[0:2]

            PrefixType = prefixLookup(prefixCode)

            if(PrefixType and '[[' not in lines):
                fileChangeFlag = 1
                lineWithoutPrefix = formattedLines[2:]

                try:
                    returnedValues = generateInstance(PrefixType,lineWithoutPrefix,questionInstanceList,importantInstanceList,taskInstanceList)
                except Exception as e:
                    MessageToSend = 'Unable to generate instance due to error: {}'.format(e)
                    errorHandling('Critical',MessageToSend,filePath,unchangedFileDetails)

                ObjectId = returnedValues[0]
                questionInstanceList = returnedValues[1]
                importantInstanceList = returnedValues[2]
                taskInstanceList = returnedValues[3]
                linesWithId = '{} [[{}]]\n'.format(lines,ObjectId)

                linesWithId = linesWithId.replace("\n [[",' [[')

                modifiedFileList.append(linesWithId)
            else:
                modifiedFileList.append(lines)
        try:
            if len(questionInstanceList) > 0:
                printValue(questionInstanceList,'Q',ExistingData)
        except Exception as e:
            MessageToSend = 'Unable to parse question list due to error: {}'.format(e)
            errorHandling('Critical',MessageToSend,filePath,unchangedFileDetails)

        try:
            if len(importantInstanceList) > 0:
                printValue(importantInstanceList,'I',ExistingData)
        except Exception as e:
            MessageToSend = 'Unable to parse important list due to error: {}'.format(e)
            errorHandling('Critical',MessageToSend,filePath,unchangedFileDetails)

        try:
            if len(taskInstanceList) > 0:
                printValue(taskInstanceList,'T',ExistingData)
        except Exception as e:
            MessageToSend = 'Unable to parse task list due to error: {}'.format(e)
            errorHandling('Critical',MessageToSend,filePath,unchangedFileDetails)

        try:
            modifiedFileList.insert(0,OriginalInput)

            if fileChangeFlag == 1:
                with open(ExportFilePath,"a+") as newExportFile:
                        newExportFile.writelines(modifiedFileList)
        except Exception as e:
            MessageToSend = 'Unable to update file with formatted output due to error: {}'.format(e)
            errorHandling('Critical',MessageToSend,filePath,unchangedFileDetails)


def main():
    global ExportFilePath

    defineLogging()

    ExportFilePath = input('Enter file path: ')

    '''Standardize the slash direction'''
    ExportFilePath = ExportFilePath.replace("\\", "/")

    validFilePathEntered = 'N'

    while validFilePathEntered == 'N':
        if os.path.exists(ExportFilePath):
            validFilePathEntered = "Y"

            getContent(ExportFilePath)
        else:
            ExportFilePath = input('File {} does not exist. Please re-enter: '.format(ExportFilePath))
