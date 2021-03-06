import sys, pathlib
sys.path.append(str(pathlib.Path.cwd().parents[1]))
from myPyLib import _myPyFunc, myGoogleSheetsFunc


startTime = _myPyFunc.printElapsedTime(False, "Starting script")
from pprint import pprint as pp

spreadsheetID = "1jbV5jjW-iWlCoBgwB0mmywbfTRcMK7XaOF-u79mLVv8"
sqlObj = _myPyFunc.createDatabase("accountingCycle.db", str(pathlib.Path.cwd().parents[3]/"privateData"/"accountingCycle"))
sqlCursor = sqlObj["sqlCursor"]
googleSheetsAPIObj = myGoogleSheetsFunc.authFunc()

splitTime = _myPyFunc.printElapsedTime(startTime, "Finished importing modules and intializing variables")

toDownload = ["Journal"]
journalDownloadedWithGrid = myGoogleSheetsFunc.getDataWithGrid(spreadsheetID, googleSheetsAPIObj, toDownload)
journalList = myGoogleSheetsFunc.extractValues(journalDownloadedWithGrid, toDownload, "Journal")


colTblJournal = _myPyFunc.createColumnsDict([
    {"`Date`": "date"},
    {"`Account`": "varchar(255)"},
    {"Debit": "varchar(255)"},
    {"Credit": "varchar(255)"}
])


_myPyFunc.createAndPopulateTable("tblJournal", colTblJournal, sqlCursor, journalList, [0])
uniqueAccountList = _myPyFunc.getQueryResult("select distinct `Account` from tblJournal", sqlCursor, False)
splitTime = myGoogleSheetsFunc.populateSheet(2, 1, "tblJournalAccounts", googleSheetsAPIObj, spreadsheetID, uniqueAccountList, True, writeToSheet=False, splitTimeArg=splitTime, columnRow=False)


ledgerData = {}

for account in uniqueAccountList:
    accountName = account[0]
    ledgerData[accountName] = [[accountName, ""]]
    sqlCommand = "select * from tblJournal where `Account` = '" + accountName + "'"
    accountTransactionList = _myPyFunc.getQueryResult(sqlCommand, sqlCursor, False)
    for transaction in accountTransactionList:
        ledgerData[accountName].append(transaction[-2:])



ledgerList = ledgerData["Cash"]


cellFormattingRequest = [{
                    "repeatCell": {
                        "range": {
                            "sheetId": myGoogleSheetsFunc.getSheetID("Ledger", googleSheetsAPIObj, spreadsheetID),
                            "startRowIndex": 0,
                            "endRowIndex": 1
                        },
                        "cell": {
                            "userEnteredFormat": {
                                "textFormat": {
                                    "bold": True
                                }
                            }
                        },
                        "fields": "userEnteredFormat(textFormat)"
                    }
                }]

splitTime = myGoogleSheetsFunc.populateSheet(2, 1, "Ledger", googleSheetsAPIObj, spreadsheetID, ledgerList, True, writeToSheet=True, splitTimeArg=splitTime, columnRow=False, cellFormattingRequest=cellFormattingRequest)





# {
#   "requests": [
#     {
#       "mergeCells": {
#         "range": {
#           "sheetId": sheetId,
#           "startRowIndex": 0,
#           "endRowIndex": 2,
#           "startColumnIndex": 0,
#           "endColumnIndex": 2
#         },
#         "mergeType": "MERGE_ALL"
#       }
#     },
#     {
#       "mergeCells": {
#         "range": {
#           "sheetId": sheetId,
#           "startRowIndex": 2,
#           "endRowIndex": 6,
#           "startColumnIndex": 0,
#           "endColumnIndex": 2
#         },
#         "mergeType": "MERGE_COLUMNS"
#       }
#     },
#   ]
# }