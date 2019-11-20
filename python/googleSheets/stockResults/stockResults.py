import sys, pathlib
sys.path.append(str(pathlib.Path.cwd().parents[0]))
sys.path.append(str(pathlib.Path.cwd().parents[1]))
from myPythonLibrary import myPythonFunctions
startTime = myPythonFunctions.startCode()

# import robinhoodTransactions

multiplyFactor = 1
accountColumn = 1
# listOfSheetData = []
destRange = "Transactions - Scrubbed"
rangesToDownload = ["Transactions", "Transactions - Scrubbed", "Chart of Accounts", "Transactions - Robinhood"]
saveJSONFile = False
# spreadsheetID = "1yZfwzel6R3HTUtH5HIv7LEjAaoJDPESG6jCEz-b7jBw" #simple spreadsheet
spreadsheetID = "1pjhFRIoB9mnbiMOj_hsFwsGth91l1oX_4kmeYrsT5mc" #full spreadsheet


import importlib, sqlite3, os
googleSheetsFunctions = importlib.import_module("myGoogleSheetsPythonLibrary.googleSheetsFunctions")
googleSheetsAuthenticate = importlib.import_module("myGoogleSheetsPythonLibrary.googleSheetsAuthenticate")
from pprint import pprint as pp


googleSheetsObj = googleSheetsAuthenticate.authFunc()
googleSheetsDataWithGrid = googleSheetsFunctions.getDataWithGrid(spreadsheetID, googleSheetsObj, rangesToDownload)


finishSetupTime = myPythonFunctions.time.time()
print("Comment: Importing modules and setting up variables...Done. " + str(round(finishSetupTime - startTime, 3)) + " seconds")

if saveJSONFile:
    myPythonFunctions.saveFile(googleSheetsDataWithGrid, pathlib.Path(pathlib.Path.cwd().parents[3]/"privateData"/"stockResults"/"googleSheetsDataWithGrid.json"))
    print("Comment: Writing data to file...Done. " + str(round(myPythonFunctions.time.time() - finishSetupTime, 3)) + " seconds")




listOfSheetData = googleSheetsFunctions.extractValues(googleSheetsFunctions.countRows(googleSheetsDataWithGrid, 0), googleSheetsFunctions.countColumns(googleSheetsDataWithGrid, 0), googleSheetsDataWithGrid, 0)
listOfSheetDataRobinhood = googleSheetsFunctions.extractValues(googleSheetsFunctions.countRows(googleSheetsDataWithGrid, 3), googleSheetsFunctions.countColumns(googleSheetsDataWithGrid, 3), googleSheetsDataWithGrid, 3)
listOfSheetData.extend(listOfSheetDataRobinhood[1:len(listOfSheetDataRobinhood)])

numberOfRows = len(listOfSheetData)
numberOfColumns = len(listOfSheetData[0])

brokerageMap = {"Mt": "Motif",
                "Rh": "Robinhood"}



for indexOfRow in range(1, numberOfRows):
    listOfSheetData[indexOfRow][accountColumn] = listOfSheetData[indexOfRow][accountColumn].replace(" - " + listOfSheetData[indexOfRow][5], " ")
    listOfSheetData[indexOfRow][accountColumn] = listOfSheetData[indexOfRow][accountColumn].replace(
        " - " + str(listOfSheetData[indexOfRow][6]), " ")
    listOfSheetData[indexOfRow][accountColumn] = listOfSheetData[indexOfRow][accountColumn].replace(
        listOfSheetData[indexOfRow][4] + " - ", "")
    listOfSheetData[indexOfRow][accountColumn] = listOfSheetData[indexOfRow][accountColumn].rstrip()

    if listOfSheetData[indexOfRow][5] in brokerageMap:
        listOfSheetData[indexOfRow][5] = brokerageMap[listOfSheetData[indexOfRow][5]]

    listOfSheetData[indexOfRow][2] = listOfSheetData[indexOfRow][2] * multiplyFactor

    if listOfSheetData[indexOfRow][7] == "":
        listOfSheetData[indexOfRow][7] = 0



numberOfRowsChartOfAccounts = googleSheetsFunctions.countRows(googleSheetsDataWithGrid, 2)
numberOfColumnsChartOfAccounts = googleSheetsFunctions.countColumns(googleSheetsDataWithGrid, 2)
chartOfAccountsDict = {}


for indexOfRow in range(1, numberOfRowsChartOfAccounts):

    mapDict = {}

    for indexOfColumn in range(1, numberOfColumnsChartOfAccounts):
        mapDict[googleSheetsFunctions.getCellValue(googleSheetsDataWithGrid, 2, 0, indexOfColumn)] = googleSheetsFunctions.getCellValue(googleSheetsDataWithGrid, 2, indexOfRow, indexOfColumn)

    chartOfAccountsDict[googleSheetsFunctions.getCellValue(googleSheetsDataWithGrid, 2, indexOfRow, 0)] = mapDict



for columnToMap in range(numberOfColumnsChartOfAccounts - 1, 0, -1):

    columnHeading = googleSheetsFunctions.getCellValue(googleSheetsDataWithGrid, 2, 0, columnToMap)

    for indexOfRow in range(0, numberOfRows):

        accountName = listOfSheetData[indexOfRow][accountColumn]
        # pp(accountName)

        if indexOfRow == 0:
            listOfSheetData[indexOfRow].insert(accountColumn + 1, columnHeading)
        else:
            # pp(chartOfAccountsDict[accountName][columnHeading])
            listOfSheetData[indexOfRow].insert(accountColumn + 1, chartOfAccountsDict[accountName][columnHeading])



valuesToWrite = {"values": listOfSheetData}
googleSheetsObj.values().update(spreadsheetId=spreadsheetID, range=destRange, valueInputOption="USER_ENTERED", body=valuesToWrite).execute()



databaseName = "stockResults.db"
dbPath = pathlib.Path(pathlib.Path.cwd().parents[3]/"privateData"/"stockResults"/databaseName)

sqlConnection = sqlite3.connect(dbPath)
sqlCrsr = sqlConnection.cursor()
tblName = "tblTransactionsScrubbed"
sqlList = []

sqlList.append("drop table if exists " + tblName + ";")
sqlList.append("create table " + tblName + " (tranDate date, account varchar(255), accountType varchar(255), accountCategory varchar(255), amount float, tranType varchar(255), stockName varchar(255), broker varchar(255), lot varchar(255), shares float);")

sqlCommand = "insert into " + tblName + " values "

rangeOfRowsUpperLimit = numberOfRows

for indexOfRow in range(1, rangeOfRowsUpperLimit):

    sqlCommand = sqlCommand + "(" \

    rangeOfColumnsUpperLimit = len(listOfSheetData[0])
    
    for indexOfColumn in range(0, rangeOfColumnsUpperLimit):

        sqlCommand = sqlCommand + "\""

        if indexOfColumn == 0:
            sqlCommand = sqlCommand + myPythonFunctions.convertSerialDateToMySQLDate(listOfSheetData[indexOfRow][indexOfColumn])
        else:
            sqlCommand = sqlCommand + str(listOfSheetData[indexOfRow][indexOfColumn])

        sqlCommand = sqlCommand + "\""

        if indexOfColumn != rangeOfColumnsUpperLimit - 1:
            sqlCommand = sqlCommand + ", "

    sqlCommand = sqlCommand + ")"

    if indexOfRow != rangeOfRowsUpperLimit - 1:
        sqlCommand = sqlCommand + ", "


sqlCommand = sqlCommand + ";"

# pp(sqlCommand)

sqlList.append(sqlCommand)

sqlList.append("select * from " + tblName + " where stockName = 'Viacom';")

myPythonFunctions.executeSQLStatements(sqlList, sqlCrsr)

ans = sqlCrsr.fetchall()
pp(ans)

sqlConnection.commit()
sqlConnection.close()



# pp(listOfSheetData[0:3])


# if os.path.exists(dbPath):
#   os.remove(dbPath)
# else:
#   print("The file does not exist")


