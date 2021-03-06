#local application imports
from pathlib import Path
import sys
pathToThisPythonFile = Path(__file__).resolve()
sys.path.append(str(Path(pathToThisPythonFile.parents[3], 'herokuGorilla', 'backend', 'python')))
import myPythonLibrary._myPyFunc as _myPyFunc
import googleSheets.processIsNotRunning.processIsNotRunning as processIsNotRunning

#standard library imports
import os
from pprint import pprint as p
import shutil


def isNotFile(fileObj):

    if fileObj.is_file():
        return False
    else:
        return True


def mainFunction(arrayOfArguments):

    pathToThisPythonFile = Path(__file__).resolve()

    pathToPublicProjectsPython = _myPyFunc.getPathUpFolderTree(pathToThisPythonFile, 'python')
    pathToBatchScriptsFolder = Path(pathToPublicProjectsPython, 'customCommandLineApps', 'batchScripts', 'scripts')

    def arrayOfSubFolders(pathToFolder):
        
        arrayOfSubFolders = []
    
        for fileObj in pathToFolder.iterdir():

            if isNotFile(fileObj):
            
                arrayOfSubFolders.append(fileObj)

        return arrayOfSubFolders


    for batchFileToTrash in os.listdir(pathToBatchScriptsFolder):
        shutil.move(Path(pathToBatchScriptsFolder, batchFileToTrash), Path(pathToBatchScriptsFolder.parents[0], 'scriptsTrashed', batchFileToTrash))


    folderArray = [pathToPublicProjectsPython]


    while folderArray:

        currentFolder = folderArray.pop(0)
        folderArray.extend(arrayOfSubFolders(currentFolder))
        
        if currentFolder != 'scriptsForCustom':

            for fileObj in currentFolder.iterdir():

                if fileObj.is_file() and fileObj.suffix == '.py' and fileObj.stem[:1] != '_':
                
                    pathOfPythonFileToRun = ''

                    # p(fileObj.parts)

                    for partOfPathToFileObj in fileObj.parts[len(pathToPublicProjectsPython.parts):]:
                        pathOfPythonFileToRun = pathOfPythonFileToRun + '/' + partOfPathToFileObj

                    # p(pathOfPythonFileToRun)

                    pathOfBatchFileToWriteTo = Path(pathToBatchScriptsFolder, fileObj.stem + '.bat')
                    objOfBatchFileToWriteTo = open(pathOfBatchFileToWriteTo, 'w+')

                    objOfBatchFileToWriteTo.write('@echo off \npython %~dp0/../../..' + pathOfPythonFileToRun + ' %*')
                    objOfBatchFileToWriteTo.close()


if __name__ == '__main__':
    mainFunction(sys.argv)

