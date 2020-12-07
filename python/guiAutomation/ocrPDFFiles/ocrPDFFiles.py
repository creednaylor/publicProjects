from pathlib import Path

import pyautogui
pathToThisPythonFile = Path(__file__).resolve()
import sys
sys.path.append(str(pathToThisPythonFile.parents[3]))
from herokuGorilla.backend.python.myPythonLibrary import myPyFunc
from herokuGorilla.backend.python.myPythonLibrary import myPyAutoGui
from herokuGorilla.backend.python.googleSheets.myGoogleSheetsLibrary import myGspreadFunc

from pprint import pprint as p
import datetime

def addFileToOCRList(fileObj):

    myPyAutoGui.clickWhenLocalPNGAppears('addFilesButton', pathToThisPythonFile.parents[0])

    pyautogui.press('f')
    myPyAutoGui.getCoordinatesWhenLocalPNGAppears('filenameBoxReady', pathToThisPythonFile.parents[0])

    # pyautogui.keyDown('shift')

    # while not myPyAutoGui.getCoordinatesIfLocalPNGIsShowing('pathArrow', pathToThisPythonFile.parents[0]):
    #     pyautogui.press('tab')


    # # pyautogui.keyUp('shift')

    # pyautogui.press('enter')
    # pyautogui.write(str(fileObj.parents[0]))
    # pyautogui.press('enter')

    # myPyAutoGui.getCoordinatesWhenLocalPNGAppears('folderBoxReady', pathToThisPythonFile.parents[0])

    # pyautogui.keyDown('shift')

    # while not myPyAutoGui.getCoordinatesIfLocalPNGIsShowing('filenameBoxReady', pathToThisPythonFile.parents[0], confidence=.95):
    #     pyautogui.press('tab')

    # pyautogui.keyUp('shift')

    pyautogui.write(str(fileObj))
    pyautogui.press('enter')
    myPyAutoGui.waitUntilLocalPNGDisappears('addFilesDialogBox', pathToThisPythonFile.parents[0])


def ocrPDFFiles(arrayOfArguments):

    # arrayOfPDFFiles = getArrayOfPDFFiles(arrayOfArguments[1])

    filesSheetName = arrayOfArguments[4]
    pathBelowRepos = pathToThisPythonFile
    spreadsheetLevelObj = myGspreadFunc.getSpreadsheetLevelObj(True, pathBelowRepos, googleAccountUsername=arrayOfArguments[3]).open(arrayOfArguments[2])
    
    googleSheetsFileArray = spreadsheetLevelObj.worksheet(filesSheetName).get_all_values()

    groupMax = 60
    currentGroupCount = 0

    filePathColIdx = 0
    completedColIdx = 1

    for rowIndex, row in enumerate(googleSheetsFileArray):

        if rowIndex:

            fileObjPath = Path(row[filePathColIdx])

            if row[completedColIdx] == '':

                addFileToOCRList(fileObjPath)
                currentGroupCount = currentGroupCount + 1
                row[completedColIdx] = 'Yes - ' + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))

            if currentGroupCount == groupMax or rowIndex == len(googleSheetsFileArray) - 1:

                # p(fileObjPath)
                
                myPyAutoGui.clickWhenLocalPNGAppears('nextButtonBeginOCR', pathToThisPythonFile.parents[0])
                myPyAutoGui.clickWhenLocalPNGAppears('closeActionCompleted', pathToThisPythonFile.parents[0])
                myPyAutoGui.waitUntilLocalPNGDisappears('closeActionCompleted', pathToThisPythonFile.parents[0])
                currentGroupCount = 0
                

                pyautogui.press(['alt', 'f', 'w', 'down', 'down', 'enter'])


                clearAndResizeParameters = [
                    {
                        'sheetObj': spreadsheetLevelObj.worksheet(filesSheetName),
                        'resizeRows': 2,
                        'startingRowIndexToClear': 0,
                        'resizeColumns': 1
                    },
                ]

                myGspreadFunc.clearAndResizeSheets(clearAndResizeParameters)
                myGspreadFunc.displayArray(spreadsheetLevelObj.worksheet(filesSheetName), googleSheetsFileArray)
                # myGspreadFunc.autoAlignColumnsInSpreadsheet(spreadsheetLevelObj)


def mainFunction(arrayOfArguments):

    ocrPDFFiles(arrayOfArguments)


if __name__ == '__main__':
    p(str(pathToThisPythonFile.name) + ' is not being imported. It is being run directly...')
    mainFunction(sys.argv)
else:
    p(str(pathToThisPythonFile.name) + ' is being imported. It is not being run directly...')