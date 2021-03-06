import sys, pathlib, time
sys.path.append(str(pathlib.Path.cwd().parents[1])) #for myPyLib
from myPyLib import _myPyFunc, myGoogleSheetsFunc

startTime = time.time()
print("Comment: Importing modules and setting up variables...")

from pprint import pprint as pp
from collections import OrderedDict


spreadsheetID = "1pjhFRIoB9mnbiMOj_hsFwsGth91l1oX_4kmeYrsT5mc"
sheetsToDownload = ["Transactions - Scrubbed", "Ticker Map"]
downloadedSheetIndex = 0
googleSheetsObj = myGoogleSheetsFunc.authFunc()
googleSheetsDataWithGrid = myGoogleSheetsFunc.getDataWithGrid(spreadsheetID, googleSheetsObj, sheetsToDownload)
tranScrubRowTotal = myGoogleSheetsFunc.countRows(googleSheetsDataWithGrid, sheetsToDownload.index("Transactions - Scrubbed"))
tranScrubColTotal = myGoogleSheetsFunc.countColumns(googleSheetsDataWithGrid, sheetsToDownload.index("Transactions - Scrubbed"))
tranScrubDataList = myGoogleSheetsFunc.extractValues(tranScrubRowTotal, tranScrubColTotal, googleSheetsDataWithGrid, sheetsToDownload.index("Transactions - Scrubbed"))

tickerMapListData = myGoogleSheetsFunc.extractValues(myGoogleSheetsFunc.countRows(googleSheetsDataWithGrid, sheetsToDownload.index("Ticker Map")), myGoogleSheetsFunc.countColumns(googleSheetsDataWithGrid, sheetsToDownload.index("Ticker Map")), googleSheetsDataWithGrid, sheetsToDownload.index("Ticker Map"))
tickerUniqueMapListData = []

for stock in tickerMapListData:

    if stock[2] not in [item[2] for item in tickerUniqueMapListData]:
        tickerUniqueMapListData.append(stock)



print("Comment: Importing modules and setting up variables...Done. " + str(round(time.time() - startTime, 3)) + " seconds")



firstFieldsDict = {0:
                       {"field": "stockName",
                        "alias": "Stock"},
                   1:
                       {"field": "broker",
                        "alias": "Broker"},
                   2:
                       {"field": "lot",
                        "alias": "Lot"}
                   }



colDict =   {
                0:  {"table": "tblResults",
                    "excludedFields": []},
                1:  {"table": "tblTickerMap",
                    "excludedFields": ["rowNumber", "stockName"]},
                2:  {"table": "tblPurchase",
                    "excludedFields": ["Stock", "Broker", "Lot"]},
                3:  {"table": "tblShares",
                    "excludedFields": ["Stock", "Broker", "Lot"]},
                4:  {"table": "tblSale",
                    "excludedFields": ["Stock", "Broker", "Lot"]}
            }
                # 5:  {"table": "tblDividends",
                #     "excludedFields": ["Stock", "Broker", "Lot"]},
                # 6:  {"table": "tblDividends",
                #     "excludedFields": ["Stock", "Broker", "Lot"],
                #      "additionalColumnText": "%"}
            # }




tblMainName = "tblTScrub"

columnsObj = OrderedDict()
columnsObj["tranDate"] = "date"
columnsObj["account"] = "varchar(255)"
columnsObj["accountType"] = "varchar(255)"
columnsObj["accountCategory"] = "varchar(255)"
columnsObj["amount"] = "float"
columnsObj["tranType"] = "varchar(255)"
columnsObj["stockName"] = "varchar(255)"
columnsObj["broker"] = "varchar(255)"
columnsObj["lot"] = "varchar(255)"
columnsObj["shares"] = "float"
columnsObj["dateYear"] = "int"


sqlObj = _myPyFunc.createDatabase("stockResults.db", str(pathlib.Path.cwd().parents[3]/"privateData"/"stockResults"), tblMainName, columnsObj)
_myPyFunc.populateTable(tranScrubRowTotal, tranScrubColTotal, tblMainName, tranScrubDataList, sqlObj["sqlCursor"], [0])


tickerColumnsObj = OrderedDict()
tickerColumnsObj["rowNumber"] = "int"
tickerColumnsObj["Ticker"] = "varchar(255)"
tickerColumnsObj["stockName"] = "varchar(255)"

_myPyFunc.createTable("tblTickerMap", tickerColumnsObj, sqlObj["sqlCursor"])
_myPyFunc.populateTable(len(tickerUniqueMapListData), len(tickerUniqueMapListData[0]), "tblTickerMap", tickerUniqueMapListData, sqlObj["sqlCursor"], [])



fieldAliasStr = _myPyFunc.fieldsDictToStr(firstFieldsDict, True, True)
fieldStr = _myPyFunc.fieldsDictToStr(firstFieldsDict, True, False)
aliasStr = _myPyFunc.fieldsDictToStr(firstFieldsDict, False, True)

_myPyFunc.createTableAs("tblPurchase", sqlObj["sqlCursor"], f"select {fieldAliasStr}, ltrim(strftime('%m', tranDate), '0') || '/' || ltrim(strftime('%d', tranDate), '0') || '/' || substr(strftime('%Y', tranDate), 3, 2) as 'Purchase Date', -sum(amount) as 'Capital Invested' from {tblMainName} where account = 'Cash' and tranType like '%Purchase%' and tranType not like '%Group Shares%' group by {fieldStr}, tranDate;")
_myPyFunc.createTableAs("tblShares", sqlObj["sqlCursor"], f"select {fieldAliasStr}, sum(shares) as Shares from {tblMainName} where account = 'Investment Asset' and tranType like '%Purchase%' and tranType not like '%Group Shares%' group by {fieldStr};")
_myPyFunc.createTableAs("tblSale", sqlObj["sqlCursor"], f"select {fieldAliasStr}, case when tranType != 'Sale - Hypothetical' then ltrim(strftime('%m', tranDate), '0') || '/' || ltrim(strftime('%d', tranDate), '0') || '/' || substr(strftime('%Y', tranDate), 3, 2) end as 'Sale Date', sum(amount) as 'Last Value', '' as 'To Sell', '=indirect(\"I\"&row())-indirect(\"F\"&row())' as 'Gain (Loss)', '=iferror(indirect(\"J\"&row())/indirect(\"F\"&row()),\"\")' as '% Gain (Loss)' from {tblMainName} where account = 'Cash' and tranType like '%Sale%' and tranType not like '%Group Shares%' group by {fieldStr}, tranDate;")

# strftime('%m/%d', tranDate) + '/' +
#get list of values to put as the pivot columns


pivotColDict = _myPyFunc.createPivotColDict("dateYear", 10, "amount", 1, tranScrubDataList)
pivotColStr = pivotColDict["pivotColStr"]
# pp(pivotColStr)

_myPyFunc.createTableAs("tblDividends", sqlObj["sqlCursor"], f"select {fieldAliasStr}, {pivotColStr} from {tblMainName} where account = 'Cash' and tranType like '%Dividend%' group by {fieldStr};")
_myPyFunc.createTableAs("tblResults", sqlObj["sqlCursor"], f"select {aliasStr} from tblPurchase union select {aliasStr} from tblSale union select {aliasStr} from tblDividends;")


colListStr = _myPyFunc.getAllColumns(colDict, sqlObj["sqlCursor"])
# pp(colListStr)




divColStr = ""
percentColStr = ""

for colCount in range(0, len(pivotColDict["colList"])):

    currentColName = "tblDividends.'" + str(pivotColDict["colList"][colCount]) + "'"
    divColStr = divColStr + "case when " + currentColName + " is null then '=if(or(int(left(indirect(\"R1C[0]\",false),4))<year(indirect(\"E\"&row())),int(left(indirect(\"R1C[0]\",false),4))>if(indirect(\"H\"&row())=\"\",year(today()),year(indirect(\"H\"&row())))),\"NO\",\"\")' else " + currentColName + " end as '" + str(pivotColDict["colList"][colCount]) + "'"
    # =if (
    # or (M90 <> "", and (AA$2 >= year($G90), AA$2 <= if ($H90="", year(today()), year($H90)))), iferror(M90 / $I90, 0), "")

    percentColStr = percentColStr + "'=if(or(and(indirect(\"R[0]C[-6]\",false)<>\"\",indirect(\"R[0]C[-6]\",false)<>\"NO\"),and(int(left(indirect(\"R1C[0]\",false),4))>=year(indirect(\"E\"&row())),int(left(indirect(\"R1C[0]\",false),4))<=if(indirect(\"H\"&row())=\"\",year(today()),year(indirect(\"H\"&row()))))),iferror(indirect(\"R[0]C[-6]\",false)/indirect(\"F\"&row()),0),\"\")' as '" + str(pivotColDict["colList"][colCount]) + " %'"   #int(left(indirect(\"R1C[0]\",false),4))<year(indirect(\"E\"&row())),int(left(indirect(\"R1C[0]\",false),4))>if(indirect(\"H\"&row())=\"\",year(today()),year(indirect(\"H\"&row())))),\"NO\",\"\")'

    if colCount != len(pivotColDict["colList"]) - 1:
        divColStr = divColStr + ", "
        percentColStr = percentColStr + ", "

# pp(divColStr)






sqlCommand = f"select " + colListStr + ", " + divColStr + ", '', " + percentColStr + ", ' ', '=sum(indirect(\"L\"&row()):indirect(\"Q\"&row()))' as 'Total Dividends', '' as 'Dividend Yield on Cost', '' as 'Forward Dividend', '' as 'Forward Dividend Yield', '' as '% of Portfolio' from tblResults " \
            "left outer join tblTickerMap on tblResults.Stock = tblTickerMap.stockName " \
            "left outer join tblPurchase on tblResults.Broker = tblPurchase.Broker and tblResults.Stock = tblPurchase.Stock and tblResults.Lot = tblPurchase.Lot " \
            "left outer join tblShares on tblResults.Broker = tblShares.Broker and tblResults.Stock = tblShares.Stock and tblResults.Lot = tblShares.Lot " \
            "left outer join tblSale on tblResults.Broker = tblSale.Broker and tblResults.Stock = tblSale.Stock and tblResults.Lot = tblSale.Lot " \
            "left outer join tblDividends on tblResults.Broker = tblDividends.Broker and tblResults.Stock = tblDividends.Stock and tblResults.Lot = tblDividends.Lot"

# pp("Blank line")
# pp(sqlCommand)

_myPyFunc.createTableAs("tblResultsJoined", sqlObj["sqlCursor"], sqlCommand)

sqlList = ["update tblResultsJoined set 'Last Value' = '=googlefinance(indirect(\"D\"&row()))*indirect(\"G\"&row())' where tblResultsJoined.'Sale Date' is null;"]
_myPyFunc.executeSQLStatements(sqlList, sqlObj["sqlCursor"])


myGoogleSheetsFunc.populateSheet(2, 1000, "SQL Query Result - Table", googleSheetsObj, spreadsheetID, _myPyFunc.getQueryResult("select * from tblResultsJoined order by Broker, Stock, Lot", "tblResultsJoined", sqlObj["sqlCursor"], True), True)
_myPyFunc.closeDatabase(sqlObj["sqlConnection"])



# if os.path.exists(dbPath):
#   os.remove(dbPath)
# else:
#   print("The file does not exist")



