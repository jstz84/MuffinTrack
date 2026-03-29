from datetime import date,datetime
import os
import logging

class Element:
    elementStatusDict = {
        'Question': 'Open',
        'Important': 'Active',
        'Task': 'To Do'
    }
       
    def __init__(self,elementType,text,answer=None,dueDate=None,comments=None,relatedId=None,assignedId=None):
        self.elementType = elementType
        self.createDateTime = datetime.now()
        self.text = text
        self.status = self.elementStatusDict[self.elementType]
        self.dueDate = dueDate
        self.answer = answer
        self.idAbbrev = self.elementType[0:1]
        self.comments = comments
        self.relatedId = relatedId
        self.assignedId = assignedId


def defineLogging():
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.DEBUG)

    return None

def errorHandling(severity,messageToLog,originalFilePath=None,originalFileContent=None):
    if severity == 'Critical':
        logging.critical(messageToLog)
        logging.info('Parsing unable to complete. Restoring file to original state and ending program')

        readWriteFile(originalFilePath,'W',originalFileContent)

        os._exit(1) # Exit immediately with an error status
    elif severity in ['Unhandled','Warning']:
        logging.warning(messageToLog)

def dictToOutput(elementType,fullDict):
    elementAttributeDict = {
        'Question': ['createDateTime','text','status','answer','comments','relatedId','assignedId'],
        'Important': ['createDateTime','text','status','comments','relatedId','assignedId'],
        'Task': ['createDateTime','text','status','dueDate','comments','relatedId','assignedId']
    }       

    formattedDict = {}

    for key,value in fullDict.items():
        if key in elementAttributeDict[elementType]:
            formattedDict[key] = value

    return formattedDict

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


def generateId(dynamicLineAbbrev,elementList,existingFileContent):
    currentDate = date.today()
    formattedDate = str(currentDate.strftime("%Y%m%d"))
    assignedIdList = []

    counter = 1

    generatedId = constructId(counter,formattedDate,dynamicLineAbbrev)

    if len(elementList) > 0:
        for listItems in elementList:
            for key,value in listItems.items():
                if key == 'assignedId' and value not in assignedIdList:
                    assignedIdList += value

    while generatedId in ''.join(existingFileContent) or generatedId in assignedIdList:

        counter = int(counter)

        counter += 1

        generatedId = constructId(counter,formattedDate,dynamicLineAbbrev)

    return generatedId

def appendObjectId (lines, objectId):
    linesWithId = '{} [[{}]]'.format(lines,objectId)

    linesWithId = linesWithId.replace("\n [[",' [[')

    return linesWithId

def printValue(printInstanceList,existingData,fileExtractList):

    HeaderPrefix = '***'
    HeaderSuffix = '\n'
    
    QuestionHeader= HeaderPrefix + 'Questions' + HeaderSuffix
    ImportantHeader = HeaderPrefix + 'Important' + HeaderSuffix
    TaskHeader = HeaderPrefix + 'Tasks' + HeaderSuffix
    OriginalInputHeader = HeaderPrefix + 'Original Input' + HeaderSuffix

    EmptyFileTemplate = [QuestionHeader,HeaderSuffix,ImportantHeader,HeaderSuffix,TaskHeader,HeaderSuffix,OriginalInputHeader]

    questionList = []
    importantList = []
    taskList = []

    '''Format the objects to print'''
    for itemsToParse in printInstanceList:
        elementType = itemsToParse['elementType']

        formattedDict = dictToOutput(elementType,itemsToParse)

        for key, value in formattedDict.items():
            DetailToAdd = '{}: {}{}'.format(key,value,HeaderSuffix)      

            if DetailToAdd.startswith('assignedId:'):
                valueToAppend = DetailToAdd + HeaderSuffix
            elif DetailToAdd != '' and not DetailToAdd.startswith('idAbbrev:'):
                valueToAppend = DetailToAdd

            match elementType:
                case 'Question':
                    questionList.append(valueToAppend)
                case 'Important':
                    importantList.append(valueToAppend)
                case 'Task':
                    taskList.append(valueToAppend)
                case _:
                    MessageToSend = 'Instance Type {} not found (01)'.format(elementType)
                    errorHandling('Warning',MessageToSend)

    if existingData == False:
        '''Will only be original input values'''
        for existingLines in fileExtractList:
            EmptyFileTemplate.append(existingLines)

        formattedFileAsList = EmptyFileTemplate.copy()
    else:
        formattedFileAsList = fileExtractList.copy()

    '''Indexing from bottom up so that elements are always in order of oldest to newest'''
    importantHeaderIndex = formattedFileAsList.index(ImportantHeader) - 1
    taskHeaderIndex = formattedFileAsList.index(TaskHeader) - 1
    originalInputHeaderIndex = formattedFileAsList.index(OriginalInputHeader) - 1
    
    if len(questionList) > 0:
        for questionDetail in questionList:
            formattedFileAsList.insert(importantHeaderIndex,questionDetail)

            importantHeaderIndex += 1
        
        importantHeaderIndex = formattedFileAsList.index(ImportantHeader) - 1
        taskHeaderIndex = formattedFileAsList.index(TaskHeader) - 1
        originalInputHeaderIndex = formattedFileAsList.index(OriginalInputHeader) - 1

    if len(importantList) > 0:
        for importantDetail in importantList:
            formattedFileAsList.insert(taskHeaderIndex, importantDetail)

            taskHeaderIndex += 1

        importantHeaderIndex = formattedFileAsList.index(ImportantHeader) - 1
        taskHeaderIndex = formattedFileAsList.index(TaskHeader) - 1
        originalInputHeaderIndex = formattedFileAsList.index(OriginalInputHeader) - 1

    if len(taskList) > 0:
        for taskDetail in taskList:
            formattedFileAsList.insert(originalInputHeaderIndex, taskDetail)

            originalInputHeaderIndex += 1

        importantHeaderIndex = formattedFileAsList.index(ImportantHeader) - 1
        taskHeaderIndex = formattedFileAsList.index(TaskHeader) - 1
        originalInputHeaderIndex = formattedFileAsList.index(OriginalInputHeader) - 1

    return formattedFileAsList


def generateInstance(dynamicLineType,instanceText,elementList,existingFileContent,foundRelatedId):
    dynamicLineTypeAbbev = dynamicLineType[0:1]

    IdToReturn = generateId(dynamicLineTypeAbbev,elementList,existingFileContent)

    NewElement = Element(dynamicLineType,instanceText,answer=None,comments=None,assignedId=IdToReturn,relatedId=foundRelatedId)
    
    elementList.append(NewElement.__dict__)

    returnList = [IdToReturn,elementList]

    return returnList

def findPrefix(lineToSearch):
    formattedLines = lineToSearch.strip()
    prefixCode = formattedLines[0:2]
    nestedElement = 0

    PrefixType = prefixLookup(prefixCode)

    if PrefixType == None:
        allowedNestedElementName = ['text:','comments:']

        for attribute in allowedNestedElementName:
            if lineToSearch.startswith(attribute):
                formattedLines = lineToSearch.replace(attribute,'').strip()
                
                prefixCode = formattedLines[0:2]

                PrefixType = prefixLookup(prefixCode)

                if PrefixType != None:
                    nestedElement = 1
    
    lineWithoutPrefix = formattedLines[2:]

    return [lineWithoutPrefix,PrefixType,nestedElement]

def parseLines(fileContents, originalInputPosition):
    elementInstanceList = []
    
    fileChangeFlag = 0

    for lines in fileContents:
        prefixHandled = findPrefix(lines)
        PrefixType = prefixHandled[1]
        nestedElementFlag = prefixHandled[2]

        if(PrefixType and '[[' not in lines):
            fileChangeFlag = 1

            lineWithoutPrefix = prefixHandled[0]

            lineIndexToUpdate = fileContents.index(lines)

            foundRelatedId = None
            
            if nestedElementFlag == 1:
                for i in range(4):
                    nextValue = fileContents[lineIndexToUpdate + i]
                    if nextValue.startswith('assignedId:'):
                        nextValue = nextValue.replace('assignedId: ','').replace('\n','')

                        foundRelatedId = appendObjectId('',nextValue)

            
            returnedValues = generateInstance(PrefixType,lineWithoutPrefix,elementInstanceList,fileContents,foundRelatedId)

            ObjectId = returnedValues[0]
            elementInstanceList = returnedValues[1]

            linesWithId = appendObjectId(lines,ObjectId) +'\n'

            '''Nested object id addition handled with instance generation'''
            if lineIndexToUpdate >= originalInputPosition or nestedElementFlag == 1:
                fileContents[lineIndexToUpdate] = linesWithId

    return [fileContents,fileChangeFlag,elementInstanceList]


def getExistingData(fileDetails):
    OriginalInput = '***Original Input\n'

    if OriginalInput in fileDetails:
        '''If file has been processed before, find and save the existing original input header index'''
        ExistingData = True

        OriginalInputIndex = fileDetails.index(OriginalInput) + 1
    else:
        ExistingData = False

        OriginalInputIndex = 0

    return [OriginalInputIndex,ExistingData]

def getFilePath(passedFilePath):
    if passedFilePath != None:
        FilePathInput = passedFilePath
    else:
        FilePathInput = input('Enter file path: ')

        '''Standardize the slash direction. Replace double quotes'''
        FilePathInput = FilePathInput.replace("\\", "/").replace('"','')

        validFilePathEntered = 'N'

        while validFilePathEntered == 'N':
            if os.path.exists(FilePathInput):
                validFilePathEntered = "Y"
            else:
                FilePathInput = input('File {} does not exist. Please re-enter: '.format(FilePathInput))        

    return FilePathInput

def readWriteFile(filePath,actionNeeded,fileWithChanges=None):
    if actionNeeded == 'R':
        with open(filePath, "r+") as fileContent:
            '''Unmodified to restore the file back to its original state in the event of failure'''
            fileDetails = fileContent.readlines()
        
        return fileDetails
    elif actionNeeded == 'W':
        with open(filePath,"w") as newFileVersion:
            newFileVersion.writelines(fileWithChanges)

        return None


def main(optionalFilePath=None):
    defineLogging()

    '''Get file path from input'''
    try:
        filePath = getFilePath(optionalFilePath)
    except Exception as e:
        MessageToSend = 'Unable to get file path. Exiting: {}'.format(e)
        errorHandling('Warning',MessageToSend)
        os._exit(1) # Exit immediately with an error status

    '''Read file'''
    try:
        fileContents = readWriteFile(filePath,'R')
    except Exception as e:
        MessageToSend = 'Unable to read file at path. Exiting: {}'.format(e)
        errorHandling('Warning',MessageToSend)
        os._exit(1) # Exit immediately with an error status

    '''Find if file has been processed before'''
    try:
        flagData = getExistingData(fileContents)
    except Exception as e:
        MessageToSend = 'Unable to identify existing data: {}'.format(e)
        errorHandling('Critical',MessageToSend,filePath,fileContents)

    originalInputIndex = flagData[0]
    existingData = flagData[1]

    '''Parse lines in file for changes'''
    try:
        parsedValues = parseLines(fileContents, originalInputIndex)
    except Exception as e:
        MessageToSend = 'Unable to parse text lines: {}'.format(e)
        errorHandling('Critical',MessageToSend,filePath,fileContents)
    
    fileDetails = parsedValues[0]
    fileChangeFlag = parsedValues[1]
    elementInstanceList = parsedValues[2]
    
    if fileChangeFlag == 1:

        '''Format new elements to print'''
        try:
            fullFileListToPrint = printValue(elementInstanceList,existingData,fileDetails)
        except Exception as e:
            MessageToSend = 'Unable to organize formatted objects: {}'.format(filePath,e)
            errorHandling('Critical',MessageToSend,filePath,fileContents)   

        '''Write back to file'''
        try:
            readWriteFile(filePath,'W',fullFileListToPrint)
        except Exception as e:
            MessageToSend = 'Unable to update file at {}: {}'.format(filePath,e)
            errorHandling('Critical',MessageToSend,filePath,fileContents)


if __name__=="__main__":
    try:
        main()
    except Exception as e:
        MessageToSend = 'Unhandled error: {}'.format(e)
        errorHandling('Unhandled',MessageToSend)