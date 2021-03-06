#on comparison sheet, could write only the necessary columns

#local application imports
from pathlib import Path
import sys
pathToThisPythonFile = Path(__file__).resolve()
sys.path.append(str(pathToThisPythonFile.parents[3]))
import herokuGorilla.backend.python.myPythonLibrary._myPyFunc as _myPyFunc

startTime = _myPyFunc.printElapsedTime(False, "Starting code")

from pprint import pprint as pp
import win32com.client

excelApp = win32com.client.gencache.EnsureDispatch('Excel.Application')
excelApp.Visible = True
excelApp.DisplayAlerts = False

# pp("Manual printout: " + str(Path.cwd().parents[3]) + "\\privateData\\python\\excel\\bankRecSecondary")
filePath = _myPyFunc.replacePartOfPath(pathToThisPythonFile.parents[0], 'publicProjects', 'privateData')
fileName = "Bank Rec"
fileExtension = ".xlsx"


excelApp.Workbooks.Open(Path(filePath, fileName + fileExtension))
excelApp.Calculation = win32com.client.constants.xlCalculationManual
excelBackupWb = excelApp.Workbooks(fileName + fileExtension)
excelBackupWb.SaveAs(Filename=str(Path(filePath, fileName + " Before Running 2" + fileExtension)), FileFormat=51)
excelApp.Calculation = win32com.client.constants.xlCalculationAutomatic
excelBackupWb.Close()


excelApp.Workbooks.Open(Path(filePath, fileName + fileExtension))
excelApp.Calculation = win32com.client.constants.xlCalculationManual
excelWb = excelApp.Workbooks(fileName  + fileExtension)

excelGPTableSheet = excelWb.Worksheets("GP Table")
excelBankTableSearchSheet = excelWb.Worksheets("Bank Table Search")
excelCompSheet = excelWb.Worksheets("Comparison")
excelCompSheet.UsedRange.Clear()


rowAfterHeader = 2
bankColumns = 8
bankTableSearchCol = 8
gpColumns = 17
gpSearchValueCol = 6



splitTime = _myPyFunc.printElapsedTime(startTime, "Finished importing modules and intializing variables")


excelBankTableSearchSheet.Range(excelBankTableSearchSheet.Cells(1, 1), excelBankTableSearchSheet.Cells(1, bankColumns)).Copy(excelCompSheet.Cells(1, 1))
excelGPTableSheet.Range(excelGPTableSheet.Cells(1, 1), excelGPTableSheet.Cells(1, gpColumns)).Copy(excelCompSheet.Cells(1, bankColumns + 1))

gpRow = rowAfterHeader


while excelGPTableSheet.Cells(gpRow, 1).Value:

    #put in GP data

    excelGPTableSheet.Range(excelGPTableSheet.Cells(gpRow, 1), excelGPTableSheet.Cells(gpRow, gpColumns)).Copy(excelCompSheet.Cells(gpRow, bankColumns + 1))

    #check bank data

    rowsToCheck = []

    startingSearchRow = 2
    endingSearchRow = excelBankTableSearchSheet.Cells(2, bankTableSearchCol).End(win32com.client.constants.xlDown).Row
    searchText = excelGPTableSheet.Cells(gpRow, gpSearchValueCol).Value
    endingSearchRow = excelBankTableSearchSheet.Cells(rowAfterHeader, bankTableSearchCol).End(win32com.client.constants.xlDown).Row


    while startingSearchRow <= endingSearchRow:

        startingSearchCell = excelBankTableSearchSheet.Cells(startingSearchRow, bankTableSearchCol)
        endingSearchCell = excelBankTableSearchSheet.Cells(startingSearchRow, bankTableSearchCol).End(
            win32com.client.constants.xlDown)

        # pp(startingSearchCell.Address)
        # pp(endingSearchCell.Address)

        foundRange = excelBankTableSearchSheet.Range(startingSearchCell, endingSearchCell).Find(What=searchText, LookAt=win32com.client.constants.xlWhole)

        pp("foundRange is " + str(foundRange))

        if foundRange:
            rowsToCheck.append(foundRange.Row)
            startingSearchRow = foundRange.Row + 1
            pp(foundRange)
        else:
            break


    if len(rowsToCheck) == 1:
            excelBankTableSearchSheet.Range(excelBankTableSearchSheet.Cells(rowsToCheck[0], 1), excelBankTableSearchSheet.Cells(rowsToCheck[0], bankColumns)).Copy(excelCompSheet.Cells(gpRow, 1))
            excelBankTableSearchSheet.Cells(rowsToCheck[0], 1).EntireRow.Delete()

    gpRow = gpRow + 1



excelCompSheet.Cells.EntireColumn.AutoFit()
excelApp.DisplayAlerts = True
excelApp.Calculation = win32com.client.constants.xlCalculationAutomatic
excelWb.Save()
excelApp.Visible = True

_myPyFunc.printElapsedTime(startTime, "Total time to run code")
