from pathlib import Path
pathToThisPythonFile = Path(__file__).resolve()
import sys
sys.path.append(str(Path(pathToThisPythonFile.parents[2], 'myPythonLibrary')))
import _myPyFunc
sys.path.append(str(Path(_myPyFunc.getPathUpFolderTree(pathToThisPythonFile, 'googleSheets'), 'myGoogleSheetsLibrary')))
import _myGoogleSheetsFunc, _myGspreadFunc

from pprint import pprint as p
import gspread

pathToRepos = _myPyFunc.getPathUpFolderTree(pathToThisPythonFile, 'repos')
arrayOfPartsToAddToPath = ['privateData', 'python', 'googleCredentials']

pathToCredentialsFileServiceAccount = _myPyFunc.addToPath(pathToRepos, arrayOfPartsToAddToPath + ['usingServiceAccount', 'jsonWithAPIKey.json'])

gspObj = gspread.service_account(filename=pathToCredentialsFileServiceAccount)
gspSpreadsheet = gspObj.open("Reconcile Arrays")
gspFirstArraySheet = gspSpreadsheet.worksheet('firstArray')
gspSecondArraySheet = gspSpreadsheet.worksheet('secondArray')

_myGspreadFunc.clearSheet(0, -1, 0, -1, gspFirstArraySheet)
_myGspreadFunc.clearSheet(0, -1, 0, -1, gspSecondArraySheet)

_myGspreadFunc.clearSheets(0, -1, 0, -1, []])

# gspFirstArraySheet.update('D4', 'bingo')

# _myGspreadFunc.clearSheet(0, -1, 0, -1, gspFirstArraySheet)



