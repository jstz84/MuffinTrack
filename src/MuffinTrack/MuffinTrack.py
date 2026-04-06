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
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.INFO)

    return None

def messageHandling(severity,messageToLog,originalFilePath=None,originalFileContent=None):
    if severity in ['Critical','Unhandled']:
        logging.exception(messageToLog)
        logging.info('Parsing unable to complete. Restoring file to original state and ending program')

        readWriteFile(originalFilePath,'W',originalFileContent)

        os._exit(1) # Exit immediately with an error status
    elif severity in ['Warning']:
        logging.exception(messageToLog)
    elif severity in ['Info']:
        logging.info(messageToLog)

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

def tagLookup(tagName):
    tagDict = {'assignedId':'[[', 'multiLineStart':'<<','comment':'--'}

    if tagName in tagDict.keys():
        tagValue = tagDict[tagName]
    else:
        tagValue = None

    return tagValue

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
                    messageHandling('Warning',MessageToSend)

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


def generateInstance(dynamicLineType,instanceText,elementList,existingFileContent,foundRelatedId,commentAssociated):
    dynamicLineTypeAbbev = dynamicLineType[0:1]

    IdToReturn = generateId(dynamicLineTypeAbbev,elementList,existingFileContent)

    NewElement = Element(dynamicLineType,instanceText,answer=None,comments=commentAssociated,assignedId=IdToReturn,relatedId=foundRelatedId)
    
    elementList.append(NewElement.__dict__)

    returnList = [IdToReturn,elementList]

    return returnList

def findPrefix(lineToSearch):
    formattedLines = lineToSearch
    prefixCode = formattedLines[0:2]

    PrefixType = prefixLookup(prefixCode)

    if PrefixType == None:
        '''Expecation is that nested elements exist on a new line. If they are in text or comments, the prefix should be immediately after the attribute name'''
        allowedNestedElementName = ['text','comments']

        for attribute in allowedNestedElementName:
            if lineToSearch.startswith(attribute):
                formattedLines = lineToSearch.replace(('{}: '.format(attribute)),'')
                
                prefixCode = formattedLines[0:2]
                
                PrefixType = prefixLookup(prefixCode)
    
    lineWithoutPrefix = formattedLines[2:]

    return [lineWithoutPrefix,PrefixType]

def findNextInstanceOf(stringToFind,lineStartIndex,fileContents,indexLineReturnMode):
        nextInstanceFound = 0

        returnedValue = None

        while nextInstanceFound == 0 and lineStartIndex < len(fileContents):
            if stringToFind in fileContents[lineStartIndex]:

                match indexLineReturnMode:
                    case 'lineValue':
                        returnedValue = fileContents[lineStartIndex]
                    case 'lineIndex':
                        returnedValue = lineStartIndex

                nextInstanceFound = 1
            else:
                lineStartIndex += 1 

        if nextInstanceFound == 0 and stringToFind != '<<':
             messageToLog = ('Next instance of string "{}" Not Found!'.format(stringToFind))

             messageHandling('Warning',messageToLog)

        return returnedValue

def findRelatedId(contentsToSearch, lineIndexToUpdate):

    foundRelatedId = None

    NextAssignedIdInstance = findNextInstanceOf('assignedId:',lineIndexToUpdate,contentsToSearch,'lineValue')
    NextAssignedIdInstance = NextAssignedIdInstance.replace('assignedId: ','').replace('\n','')

    foundRelatedId = appendObjectId('',NextAssignedIdInstance)

    return foundRelatedId

def combineMultiLines(startIndex,lineWithoutPrefix,fileContents):
    multiLineEndIndex = findNextInstanceOf(">>",startIndex,fileContents,'lineIndex')

    '''Starting on the line after the current one, see if another start tag is listed before the end tag found'''
    multiLineNextStartIndex = findNextInstanceOf('<<',startIndex + 1,fileContents,'lineIndex')

    if multiLineNextStartIndex and multiLineNextStartIndex < multiLineEndIndex and multiLineNextStartIndex > startIndex:
        messageToLog = 'Multiline parsing opened, but never closed. Line Text: {}'.format(lineWithoutPrefix)

        messageHandling('Info',messageToLog)

        multiLineWithoutPrefix = lineWithoutPrefix
        multiLineEndIndex = startIndex
    elif multiLineNextStartIndex == None or multiLineNextStartIndex > multiLineEndIndex:
        '''Get all the applicable lines in their current format'''
        '''List slicing: start is always inclusive, end is always exclusive. Overlap doesn't matter'''
        multiLineAsList = fileContents[startIndex:multiLineEndIndex + 1]
        multiLineAsListLength = len(multiLineAsList) - 1

        multiLineAsList[0] = lineWithoutPrefix
        multiLineAsList[multiLineAsListLength] = multiLineAsList[multiLineAsListLength].replace('>>','')

        '''Don't insist on formatting. Multiline should maintain what's in place'''
        multiLineWithoutPrefix = ''.join(multiLineAsList)

    multiLineWithoutPrefix = multiLineWithoutPrefix.replace('<<','')

    return [multiLineWithoutPrefix,multiLineEndIndex]

def findComments(line):

    commentIdentifier = tagLookup('comment')
    newLineIdentifier = '\n'

    identifierIndex = line.index(commentIdentifier)

    preIdentifier = line[0:identifierIndex]

    if newLineIdentifier in line:
        nextNewLineIndex = line.index(newLineIdentifier,identifierIndex)
        postIdentifier = line[identifierIndex:nextNewLineIndex].replace(commentIdentifier,'')

        preIdentifier = preIdentifier + line[nextNewLineIndex:len(line)]
    else:
        postIdentifier = line[identifierIndex:len(line)].replace(commentIdentifier,'')

    return [preIdentifier,postIdentifier]

def getLineInfo(line, fileContent,fileInfo):
        assignedIdReferenceWrapper = tagLookup('assignedId')
        multiLineWrapper = tagLookup('multiLineStart')
        commentIdentifier = tagLookup('comment')

        strippedLine = line.strip(' ')

        prefixHandled = findPrefix(strippedLine)

        lineInfoDict = {'prefixType':prefixHandled[1],
                        'lineIndex': fileContent.index(line),
                        'processElement':0,
                        'multiLine':0,
                        'nestedElement':0,
                        'foundComments':0,
                        'multiLineEndingIndex':None,
                        'lineWithoutPrefix':None,
                        'originalLine':line}
        
        if(lineInfoDict['prefixType'] and assignedIdReferenceWrapper not in line):
            '''Format lines'''

            fileInfo['fileChangeFlag'] = 1
            lineInfoDict['lineWithoutPrefix'] = prefixHandled[0]
            lineInfoDict['processElement'] = 1

            if multiLineWrapper in line:
                lineInfoDict['multiLine'] = 1

                multiLineResults = combineMultiLines(lineInfoDict['lineIndex'],lineInfoDict['lineWithoutPrefix'],fileContent)
                multiLineReturnedLine = multiLineResults[0]

                lineInfoDict['multiLineEndingIndex'] = multiLineResults[1]

                if assignedIdReferenceWrapper not in multiLineReturnedLine:
                    lineInfoDict['lineWithoutPrefix'] = multiLineReturnedLine
                else:
                    lineInfoDict['processElement'] = 0

            if lineInfoDict['lineIndex'] < fileInfo['originalInputIndex']:
                lineInfoDict['nestedElement'] = 1

            if commentIdentifier in lineInfoDict['lineWithoutPrefix']:
                lineInfoDict['foundComments'] = 1

            lineInfoDict['lineWithoutPrefix'] = lineInfoDict['lineWithoutPrefix'].strip()
    

        return [fileInfo,lineInfoDict]

def updateObjectId(fileContent,objectId,lineInfo,fileInfo):
    if lineInfo['multiLine'] == 1:
        linesWithId = appendObjectId(fileContent[lineInfo['multiLineEndingIndex']],objectId) +'\n'

        fileContent[lineInfo['multiLineEndingIndex']] = linesWithId
    elif lineInfo['lineIndex'] >= fileInfo['originalInputIndex'] or lineInfo['nestedElement'] == 1:
        '''Object id addition handled if changes to line or prefix found in specific attribute lines'''
        
        linesWithId = appendObjectId(lineInfo['originalLine'],objectId) +'\n'

        fileContent[lineInfo['lineIndex']] = linesWithId

    return fileContent



def parseLines(fileContents, fileInfoDict):
    elementInstanceList = []

    for lines in fileContents:

        #TODO: Don't have to pass contents to all the functions
        lineInfo = getLineInfo(lines,fileContents,fileInfoDict)

        fileInfoDict = lineInfo[0]
        lineInfoDict = lineInfo[1]

        if lineInfoDict['processElement'] == 1:
            '''Process Lines'''
            if lineInfoDict['nestedElement'] == 1:
                foundRelatedId = findRelatedId(fileContents,lineInfoDict['lineIndex'])
            else:
                foundRelatedId = None

            if lineInfoDict['foundComments'] == 1:
                foundComments = findComments(lineInfoDict['lineWithoutPrefix'])

                lineWithoutComments = foundComments[0]
                commentLine = foundComments[1]

                lineInfoDict['lineWithoutPrefix'] = lineWithoutComments
            else:
                commentLine = None
            
            returnedValues = generateInstance(lineInfoDict['prefixType'],lineInfoDict['lineWithoutPrefix'],elementInstanceList,fileContents,foundRelatedId,commentLine)

            '''Object Id Assignment -- Break out into own function'''
            ObjectId = returnedValues[0]
            elementInstanceList = returnedValues[1]

            fileContents = updateObjectId(fileContents,ObjectId,lineInfoDict,fileInfoDict)

    return [fileContents,fileInfoDict,elementInstanceList]


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
        messageHandling('Warning',MessageToSend)
        os._exit(1) # Exit immediately with an error status

    '''Read file'''
    try:
        fileContents = readWriteFile(filePath,'R')
        unchangedFileContents = fileContents.copy()
    except Exception as e:
        MessageToSend = 'Unable to read file at path. Exiting: {}'.format(e)
        messageHandling('Warning',MessageToSend)
        os._exit(1) # Exit immediately with an error status

    '''Find if file has been processed before'''
    try:
        flagData = getExistingData(fileContents)
    except Exception as e:
        MessageToSend = 'Unable to identify existing data: {}'.format(e)
        messageHandling('Critical',MessageToSend,filePath,unchangedFileContents)

    fileInfoDict = {'originalInputIndex':flagData[0],'existingData':flagData[1],'fileChangeFlag':0}

    '''Parse lines in file for changes'''
    try:
        parsedValues = parseLines(fileContents, fileInfoDict)
    except Exception as e:
        MessageToSend = 'Unable to parse text lines: {}'.format(e)
        messageHandling('Critical',MessageToSend,filePath,unchangedFileContents)
    
    fileDetails = parsedValues[0]
    fileInfoDict = parsedValues[1]
    elementInstanceList = parsedValues[2]
    
    if fileInfoDict['fileChangeFlag'] == 1:

        '''Format new elements to print'''
        try:
            fullFileListToPrint = printValue(elementInstanceList,fileInfoDict['existingData'],fileDetails)
        except Exception as e:
            MessageToSend = 'Unable to organize formatted objects: {}'.format(filePath,e)
            messageHandling('Critical',MessageToSend,filePath,unchangedFileContents)   

        '''Write back to file'''
        try:
            readWriteFile(filePath,'W',fullFileListToPrint)
        except Exception as e:
            MessageToSend = 'Unable to update file at {}: {}'.format(filePath,e)
            messageHandling('Critical',MessageToSend,filePath,unchangedFileContents)


if __name__=="__main__":
    try:
        main()
    except Exception as e:
        MessageToSend = 'Unhandled error: {}'.format(e)
        messageHandling('Unhandled',MessageToSend)