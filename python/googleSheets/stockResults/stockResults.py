#add multiply factor
#count rows in function arguments


import sys, pathlib
sys.path.append(str(pathlib.Path.cwd().parents[1]))
from myPyLib import myPyFunc, myGoogleSheetsFunc


startTime = myPyFunc.printElapsedTime(False, "Starting script")

import datetime
from collections import OrderedDict
from pprint import pprint as pp

resultsSpreadsheetID = "1pjhFRIoB9mnbiMOj_hsFwsGth91l1oX_4kmeYrsT5mc"
multiplyFactor = .25
sqlObj = myPyFunc.createDatabase("stockResults.db", str(pathlib.Path.cwd().parents[3]/"privateData"/"stockResults"))
sqlCursor = sqlObj["sqlCursor"]
googleSheetsAPIObj = myGoogleSheetsFunc.authFunc()

splitTime = myPyFunc.printElapsedTime(startTime, "Finished importing modules and intializing variables")


resultsToDownload = ["Inputs", "Ticker Map", "Raw Data - Robinhood", "Transactions To Add - Robinhood", "Transactions - Motif", "Chart of Accounts"]
resultsDownloadedWithGrid = myGoogleSheetsFunc.getDataWithGrid(resultsSpreadsheetID, googleSheetsAPIObj, resultsToDownload)

inputsExtractedValues = myGoogleSheetsFunc.extractValues(myGoogleSheetsFunc.countRows(resultsDownloadedWithGrid, resultsToDownload.index("Inputs")), myGoogleSheetsFunc.countColumns(resultsDownloadedWithGrid, resultsToDownload.index("Inputs")), resultsDownloadedWithGrid, resultsToDownload.index("Inputs"))
tickerMapIndexStockName = inputsExtractedValues[0][1]


tickerMapExtractedValues = myGoogleSheetsFunc.extractValues(myGoogleSheetsFunc.countRows(resultsDownloadedWithGrid, resultsToDownload.index("Ticker Map")), myGoogleSheetsFunc.countColumns(resultsDownloadedWithGrid, resultsToDownload.index("Ticker Map")), resultsDownloadedWithGrid, resultsToDownload.index("Ticker Map"))
tickerMapTickerColIndex = 1
tickerMapStockNameColIndex = 2
tickerMapUniqueExtractedValues = []

for tickerMapItem in tickerMapExtractedValues:

    if tickerMapItem[tickerMapIndexStockName] not in [tickerMapUniqueItem[tickerMapIndexStockName] for tickerMapUniqueItem in tickerMapUniqueExtractedValues]:
        tickerMapUniqueExtractedValues.append(tickerMapItem)

# tickerDict = myGoogleSheetsFunc.createDictMapFromSheet(resultsDownloadedWithGrid, resultsToDownload.index("Ticker Map"))

rawDataRobRows = myGoogleSheetsFunc.countRows(resultsDownloadedWithGrid, resultsToDownload.index("Raw Data - Robinhood"))
rawDataRobExtractedValues = myGoogleSheetsFunc.extractValues(rawDataRobRows, myGoogleSheetsFunc.countColumns(resultsDownloadedWithGrid, resultsToDownload.index("Raw Data - Robinhood")), resultsDownloadedWithGrid, resultsToDownload.index("Raw Data - Robinhood"))
transactionsToAddRobExtractedValues = myGoogleSheetsFunc.extractValues(myGoogleSheetsFunc.countRows(resultsDownloadedWithGrid, resultsToDownload.index("Transactions To Add - Robinhood")), myGoogleSheetsFunc.countColumns(resultsDownloadedWithGrid, resultsToDownload.index("Transactions To Add - Robinhood")), resultsDownloadedWithGrid, resultsToDownload.index("Transactions To Add - Robinhood"))

resultsTranScrubList = myGoogleSheetsFunc.extractValues(myGoogleSheetsFunc.countRows(resultsDownloadedWithGrid, resultsToDownload.index("Transactions - Motif")), myGoogleSheetsFunc.countColumns(resultsDownloadedWithGrid, resultsToDownload.index("Transactions - Motif")), resultsDownloadedWithGrid, resultsToDownload.index("Transactions - Motif"))
chartOfAccountsDict = myGoogleSheetsFunc.createDictMapFromSheet(resultsDownloadedWithGrid, resultsToDownload.index("Chart of Accounts"))


splitTime = myPyFunc.printElapsedTime(splitTime, "Finished downloading and extracting data")


#create data

newTransRobListCurrColIndex = 0
newTransRobRow = []
newTransRobList = []
newTransRobListDescColIndex = 0
newTransRobListDateColIndex = 1
newTransRobListAmountColIndex = 2
newTransRobListNumSharesColIndex = 4
rawDataRobColumnIndexWithData = 0
rawDataRobLastRowIndex = rawDataRobRows - 1
newTransLengthWithoutShares = newTransRobListAmountColIndex + 1


for rawDataRobIndexOfRow in range(0, rawDataRobRows):

    rawDataRobNextCellValueHasNoShares = True
    robRawDataCurrentCellValue = rawDataRobExtractedValues[rawDataRobIndexOfRow][rawDataRobColumnIndexWithData]

    if rawDataRobIndexOfRow + 1 <= rawDataRobLastRowIndex:
        if len(str(rawDataRobExtractedValues[rawDataRobIndexOfRow + 1][rawDataRobColumnIndexWithData]).split(" share")) > 1:
            rawDataRobNextCellValueHasNoShares = False

    if newTransRobListCurrColIndex == newTransRobListAmountColIndex and robRawDataCurrentCellValue != "Failed":
        newTransRobRow.append(abs(robRawDataCurrentCellValue))
    else:
        newTransRobRow.append(robRawDataCurrentCellValue)



    if (newTransRobListCurrColIndex == newTransRobListAmountColIndex and rawDataRobNextCellValueHasNoShares) or newTransRobListCurrColIndex == 3:
        newTransRobListCurrColIndex = -1

        if len(newTransRobRow) == newTransLengthWithoutShares:
            newTransRobRow.extend(["", ""])
        elif len(newTransRobRow) == newTransRobListNumSharesColIndex:
            newTransRobRow.append(int(str(robRawDataCurrentCellValue).split(" share")[newTransRobListDescColIndex]))


        newTransRobList.append(newTransRobRow)
        newTransRobRow = []

    newTransRobListCurrColIndex = newTransRobListCurrColIndex + 1


newTransRobList.sort(key=lambda item: int(item[newTransRobListDateColIndex]))
splitTime = myGoogleSheetsFunc.populateSheet(1, 1000, "Transactions - Robinhood", googleSheetsAPIObj, resultsSpreadsheetID, newTransRobList, True, writeToSheet=False, splitTimeArg=splitTime)



#create transactions

tranRobDoubleEntryList = [["Date", "Account", "Amount+-", "Transaction Type", "Stock Name", "Broker", "Lot", "Shares", "Ticker", "Capital Invested"]]
tranRobDoubleEntryList.extend(transactionsToAddRobExtractedValues[1:])


leftStrMap = {
                "Dividend from ": {"tranType": "Dividend", "debitAccount": "Cash", "creditAccount": "Dividend Revenue"},
                "Withdrawal to ": {"tranType": "Owners - Pay", "debitAccount": "Capital Contributions", "creditAccount": "Cash", "stockName": "All Stocks", "lotInfo": "All Lots"},
                "Deposit from ": {"tranType": "Owners - Receive Cash", "debitAccount": "Cash", "creditAccount": "Capital Contributions", "stockName": "All Stocks", "lotInfo": "All Lots"},
                "Interest Payment": {"tranType": "Interest", "debitAccount": "Cash", "creditAccount": "Interest Revenue", "stockName": "Cash", "lotInfo": "Cash"},
                "AKS from Robinhood": {"tranType": "Purchase - Stock Gift", "debitAccount": "Investment Asset", "creditAccount": "Gain On Gift", "stockName": "AKS", "shares": 1}
}

rightStrMap = {" Market Buy": {"tranType": "Purchase", "debitAccount": "Investment Asset", "creditAccount": "Cash"}}


lastDate = int(myPyFunc.convertDateToSerialDate(datetime.datetime(2013, 10, 31)))    # lastDate = int(myPyFunc.convertDateToSerialDate(datetime.datetime(2018, 10, 31)))


for line in newTransRobList:

    if line[newTransRobListAmountColIndex] != "Failed" and line[newTransRobListDateColIndex] > lastDate:

        mappedTransactionData = {}

        for leftStringToCheckFor in leftStrMap:
            if line[newTransRobListDescColIndex][:len(leftStringToCheckFor)] == leftStringToCheckFor:
                mappedTransactionData = leftStrMap[leftStringToCheckFor]
                mappedTransactionData["strToCheckFor"] = leftStringToCheckFor
                mappedTransactionData["stockNamePosition"] = 1

        if not mappedTransactionData:
            for rightStrToCheckFor in rightStrMap:
                if line[newTransRobListDescColIndex][-len(rightStrToCheckFor):] == rightStrToCheckFor:
                    mappedTransactionData = rightStrMap[rightStrToCheckFor]
                    mappedTransactionData["strToCheckFor"] = rightStrToCheckFor
                    mappedTransactionData["stockNamePosition"] = 0

        # pp(transaction)

        if "stockName" in mappedTransactionData:
            stockName = mappedTransactionData["stockName"]
        elif line[newTransRobListDescColIndex].split(mappedTransactionData["strToCheckFor"])[mappedTransactionData["stockNamePosition"]] in ["Xperi", "Tessera Technologies, Inc. - Common Stock"]:
            stockName = "Xperi, formerly Tessera"
        else:
            stockName = line[newTransRobListDescColIndex].split(mappedTransactionData["strToCheckFor"])[mappedTransactionData["stockNamePosition"]]


        if "lotInfo" in mappedTransactionData:
            lot = mappedTransactionData["lotInfo"]
        elif mappedTransactionData["tranType"] in ["Purchase", "Purchase - Stock Gift", "Purchase - Stock From Merger"]:
            lot = myPyFunc.convertSerialDateToDateWithoutDashes(line[newTransRobListDateColIndex])
        else:

            filterForLots = [{1: "Investment Asset", 3: "Purchase", 4: stockName},
                             {1: "Investment Asset", 3: "Purchase - Stock From Merger", 4: stockName}]
            filteredList = myPyFunc.filterListOfLists(tranRobDoubleEntryList, filterForLots)

            if len(filteredList) == 1:
                lot = myPyFunc.convertSerialDateToDateWithoutDashes(filteredList[0][0])


        if "shares" in mappedTransactionData:
            shares = mappedTransactionData["shares"]
        else:
            shares = line[newTransRobListNumSharesColIndex]

        tranRobDoubleEntryList.append([line[newTransRobListDateColIndex], mappedTransactionData["debitAccount"], line[newTransRobListAmountColIndex], mappedTransactionData["tranType"], stockName, "Robinhood", lot, shares, "", ""])
        tranRobDoubleEntryList.append([line[newTransRobListDateColIndex], mappedTransactionData["creditAccount"], -line[newTransRobListAmountColIndex], mappedTransactionData["tranType"], stockName, "Robinhood", lot, "", "", ""])



splitTime = myPyFunc.printElapsedTime(splitTime, "Finished creating Robinhood double entry transactions")




tblRobinhoodColumns = myPyFunc.createColumnsDict([
    {"\"Date\"": "date"},
    {"\"Account\"": "varchar(255)"},
    {"\"Amount+-\"": "float"},
    {"\"Transaction Type\"": "varchar(255)"},
    {"\"Stock Name\"": "varchar(255)"},
    {"\"Broker\"": "varchar(255)"},
    {"\"Lot\"": "varchar(255)"},
    {"\"Shares\"": "float"},
    {"\"Ticker\"": "varchar(255)"},
    {"\"Capital Invested\"": "varchar(255)"}
])




#
# tickerColumnsObj = OrderedDict()
# tickerColumxnsObj["rowNumber"] = "int"
# tickerColumnsObj["Ticker"] = "varchar(255)"
# tickerColumnsObj["stockName"] = "varchar(255)"
#
# myPyFunc.createTable("tblTickerMap", tickerColumnsObj, sqlCursor)
# myPyFunc.populateTable(len(tickerMapUniqueExtractedValues), len(tickerMapUniqueExtractedValues[0]), "tblTickerMap", tickerMapUniqueExtractedValues, sqlCursor, [])
# pp(myPyFunc.getQueryResult("select * from tblTickerMap", "tblTickerMap", sqlCursor, False))


myPyFunc.createAndPopulateTable("tblRobinhood", tblRobinhoodColumns, sqlCursor, len(tranRobDoubleEntryList), len(tranRobDoubleEntryList[0]), tranRobDoubleEntryList, [0])
# splitTime = m|}yGoogleSheetsFunc.populateSheet(2, 1000, "tblRobinhood", googleSheetsAPIObj, resultsSpreadsheetID, myPyFunc.getQueryResult("select * from tblRobinhood;", sqlCursor, True), True, writeToSheet=True, splitTimeArg=splitTime)



# myPyFunc.createTableAs("tblLots", sqlCursor, f"select stockName, lot, sum(amount), sum(shares) from tblRobinhood where account = 'Investment Asset' and broker = 'Robinhood' group by stockName, lot having sum(shares) > 0;")
unsoldStockValuesList = myPyFunc.getQueryResult("select \"Stock Name\", \"Lot\", sum(\"Amount+-\"), sum(\"Shares\") from tblRobinhood where \"Account\" = 'Investment Asset' and \"Broker\" = 'Robinhood' group by \"Stock Name\", \"Lot\" having sum(\"Shares\") > 0;", sqlCursor, False)
# splitTime = myGoogleSheetsFunc.populateSheet(2, 1000, "Transactions - Unsold Stock", googleSheetsAPIObj, resultsSpreadsheetID, unsoldStockValuesList, True, writeToSheet=True, splitTimeArg=splitTime)



# sqlCommand = f"select tblLots.*, tblTickerMap.ticker, '=googlefinance(indirect(\"E\"&row()))*indirect(\"D\"&row())' as googleFin, '=indirect(\"F\"&row())-indirect(\"C\"&row())' as gainLoss from tblLots left outer join tblTickerMap on tblLots.stockName = tblTickerMap.stockName;"
# myGoogleSheetsFunc.populateSheet(3, 1000, "Unsold Stock Values - Robinhood", googleSheetsAPIObj, resultsSpreadsheetID, myPyFunc.getQueryResult(sqlCommand, sqlCursor, False), True)



# unsoldStockValuesDataWithGrid = myGoogleSheetsFunc.getDataWithGrid(resultsSpreadsheetID, googleSheetsAPIObj, ["Unsold Stock Values - Robinhood"])
# unsoldStockValuesList = myGoogleSheetsFunc.extractValues(myGoogleSheetsFunc.countRows(unsoldStockValuesDataWithGrid, 0), myGoogleSheetsFunc.countColumns(unsoldStockValuesDataWithGrid, 0), unsoldStockValuesDataWithGrid, 0)


# doubleEntryUnsoldStockList = []

#
# for lot in unsoldStockValuesList:
#
#     doubleEntryUnsoldStockList.append([priceDate, "Cash", lot[5], tranType, lot[0], "Robinhood", lot[1], "", "", ""])
#     doubleEntryUnsoldStockList.append([priceDate, "Investment Asset", -lot[2], tranType, lot[0], "Robinhood", lot[1], lot[3], "", ""])
#
#     if lot[6] < 0:
#         gainLossAccount = "Loss On Sale - Hypothetical"
#     else:
#         gainLossAccount = "Gain On Sale - Hypothetical"
#
#     doubleEntryUnsoldStockList.append([priceDate, gainLossAccount, -lot[6], tranType, lot[0], "Robinhood", lot[1], "", "", ""])
#




doubleEntryUnsoldStockList = []
tranType = "Sale - Hypothetical"
priceDate = int(myPyFunc.convertDateToSerialDate(datetime.datetime.now()))
gainLossAccount = "=if(" + myGoogleSheetsFunc.cellOff(0, 1) + "<0,\"Gain On Sale - Hypothetical\",\"Loss On Sale - Hypothetical\")"


for line in unsoldStockValuesList:

    lotStockName = line[0]
    lotFromLotList = line[1]
    lotInvestmentAmount = line[2]
    lotShares = line[3]
    tickerSymbol = ""

    for ticker in tickerMapUniqueExtractedValues:
        if lotStockName == ticker[tickerMapStockNameColIndex]:
            tickerSymbol = ticker[tickerMapTickerColIndex]


    lotCurrentAmount = "googlefinance(" + myGoogleSheetsFunc.cellOff(0, 6) + ")*" + myGoogleSheetsFunc.cellOff(0, 5)

    doubleEntryUnsoldStockList.append([priceDate, "Cash", "=" + lotCurrentAmount, tranType, lotStockName, "Robinhood", lotFromLotList, lotShares, tickerSymbol, ""])
    doubleEntryUnsoldStockList.append([priceDate, "Investment Asset", -lotInvestmentAmount, tranType, lotStockName, "Robinhood", lotFromLotList, lotShares, tickerSymbol, ""])
    doubleEntryUnsoldStockList.append([priceDate, gainLossAccount, "=-" + lotCurrentAmount + "+" + myGoogleSheetsFunc.cellOff(0, 7), tranType, lotStockName, "Robinhood", lotFromLotList, lotShares, tickerSymbol, lotInvestmentAmount])



tranRobDoubleEntryList.extend(doubleEntryUnsoldStockList)
splitTime = myGoogleSheetsFunc.populateSheet(2, 1000, "Transactions - Robinhood - Double Entry", googleSheetsAPIObj, resultsSpreadsheetID, tranRobDoubleEntryList, True, writeToSheet=False, splitTimeArg=splitTime)



tranDateColIndex = 0
tranAccountColIndex = 1
# tranAmountColIndex = 2
# tranStockColIndex = 4
# tranBrokerColIndex = 5
# tranLotColIndex = 6
# tranSharesColIndex = 7



# resultsTranScrubList = transMotifExtractedValues
# resultsTranScrubList = [item for item in resultsTranScrubList if item[tranAmountColIndex] != 0]




#Scrub Transactions sheet

# brokerageMap = {"Mt": "Motif",
#                 "Rh": "Robinhood"}
#
# multiplyFactor = 1



# for resultsTranScrubIndexOfRow in range(1, resultsTranScrubRowTotal):

    # resultsTranScrubList[resultsTranScrubIndexOfRow][tranAccountColIndex] = resultsTranScrubList[resultsTranScrubIndexOfRow][tranAccountColIndex].replace(" - " + resultsTranScrubList[resultsTranScrubIndexOfRow][tranBrokerColIndex], " ")
    # resultsTranScrubList[resultsTranScrubIndexOfRow][tranAccountColIndex] = resultsTranScrubList[resultsTranScrubIndexOfRow][tranAccountColIndex].replace(
    #     " - " + str(resultsTranScrubList[resultsTranScrubIndexOfRow][tranLotColIndex]), " ")
    # resultsTranScrubList[resultsTranScrubIndexOfRow][tranAccountColIndex] = resultsTranScrubList[resultsTranScrubIndexOfRow][tranAccountColIndex].replace(
    #     resultsTranScrubList[resultsTranScrubIndexOfRow][tranStockColIndex] + " - ", "")
    # resultsTranScrubList[resultsTranScrubIndexOfRow][tranAccountColIndex] = resultsTranScrubList[resultsTranScrubIndexOfRow][tranAccountColIndex].rstrip()
    #
    # if resultsTranScrubList[resultsTranScrubIndexOfRow][tranBrokerColIndex] in brokerageMap:
    #     resultsTranScrubList[resultsTranScrubIndexOfRow][tranBrokerColIndex] = brokerageMap[resultsTranScrubList[resultsTranScrubIndexOfRow][tranBrokerColIndex]]

    # ticker = resultsTranScrubList[resultsTranScrubIndexOfRow][tranStockColIndex]

    # if ticker in tickerDict:
    #
    #     for key in tickerDict[ticker]:
    #         resultsTranScrubList[resultsTranScrubIndexOfRow][tranStockColIndex] = tickerDict[ticker][key]

    # resultsTranScrubList[resultsTranScrubIndexOfRow][tranAmountColIndex] = resultsTranScrubList[resultsTranScrubIndexOfRow][tranAmountColIndex] * multiplyFactor
    #
    # if resultsTranScrubList[resultsTranScrubIndexOfRow][tranSharesColIndex] == "":
    #     resultsTranScrubList[resultsTranScrubIndexOfRow][tranSharesColIndex] = 0


# splitTime = myGoogleSheetsFunc.populateSheet(1, 1000, "1", googleSheetsAPIObj, resultsSpreadsheetID, resultsTranScrubList, True)

resultsTranScrubList.extend(tranRobDoubleEntryList[1:len(tranRobDoubleEntryList)])
resultsTranScrubRowTotal = len(resultsTranScrubList)
accountDataPointsToMap = 2




#use map


for resultsTranScrubIndexOfRow in range(0, resultsTranScrubRowTotal):

    accountName = resultsTranScrubList[resultsTranScrubIndexOfRow][tranAccountColIndex]

    for indexOfAccountMap in range(0, accountDataPointsToMap):
        # pp(chartOfAccountsDict[accountName].values())

        if accountName == gainLossAccount:
            mappedAccountData = "=vlookup(" + myGoogleSheetsFunc.cellOff(0, -(indexOfAccountMap + 9)) + "," + "indirect(\"Chart of Accounts!r1c1:r" + str(len(chartOfAccountsDict)) + "c" + str(accountDataPointsToMap + 1) + "\",false)" + "," + str(indexOfAccountMap + 2) + ",)"                   #"=vlookup(indirect(\"r[0]c[-9]\",false),'Chart of Accounts'!$A$1:$C$26," + "2" + ",)"
        else:
            mappedAccountData = list(chartOfAccountsDict[accountName].values())[indexOfAccountMap]
        resultsTranScrubList[resultsTranScrubIndexOfRow].append(mappedAccountData)

    if resultsTranScrubIndexOfRow == 0:
        resultsTranScrubList[resultsTranScrubIndexOfRow].append("Year")
    else:
        resultsTranScrubList[resultsTranScrubIndexOfRow].append(myPyFunc.convertSerialDateToYear(resultsTranScrubList[resultsTranScrubIndexOfRow][tranDateColIndex]))



splitTime = myGoogleSheetsFunc.populateSheet(2, 1000, "Transactions - Scrubbed", googleSheetsAPIObj, resultsSpreadsheetID, resultsTranScrubList, False, writeToSheet=False, splitTimeArg=splitTime)


resultsTranScrubRowTotal = len(resultsTranScrubList)
resultsTranScrubColTotal = len(resultsTranScrubList[0])
# pp(resultsTranScrubRowTotal)
# pp(resultsTranScrubColTotal)



scrubTranToDownload = ["Transactions - Scrubbed"]
scrubTranDownloadedWithGrid = myGoogleSheetsFunc.getDataWithGrid(resultsSpreadsheetID, googleSheetsAPIObj, scrubTranToDownload)
resultsTranScrubList = myGoogleSheetsFunc.extractValues(myGoogleSheetsFunc.countRows(scrubTranDownloadedWithGrid, scrubTranToDownload.index("Transactions - Scrubbed")), myGoogleSheetsFunc.countColumns(scrubTranDownloadedWithGrid, scrubTranToDownload.index("Transactions - Scrubbed")), scrubTranDownloadedWithGrid, scrubTranToDownload.index("Transactions - Scrubbed"))





tblScrubbedColumns = myPyFunc.createColumnsDict([
    {"\"Date\"": "date"},
    {"\"Account\"": "varchar(255)"},
    {"\"Amount+-\"": "float"},
    {"\"Transaction Type\"": "varchar(255)"},
    {"\"Stock Name\"": "varchar(255)"},
    {"\"Broker\"": "varchar(255)"},
    {"\"Lot\"": "varchar(255)"},
    {"\"Shares\"": "float"},
    {"\"Ticker\"": "varchar(255)"},
    {"\"Capital Invested\"": "varchar(255)"},
    {"\"Account Type\"": "varchar(255)"},
    {"\"Account Category\"": "varchar(255)"},
    {"\"Year\"": "int"}
])



myPyFunc.createTable("tblScrubbed", tblScrubbedColumns, sqlCursor)
myPyFunc.populateTable(resultsTranScrubRowTotal, resultsTranScrubColTotal, "tblScrubbed", resultsTranScrubList, sqlCursor, [0])



# tickerColumnsObj = OrderedDict()
# tickerColumnsObj["rowNumber"] = "int"
# tickerColumnsObj["Ticker"] = "varchar(255)"
# tickerColumnsObj["stockName"] = "varchar(255)"
#
# myPyFunc.createTable("tblTickerMap", tickerColumnsObj, sqlCursor)
# myPyFunc.populateTable(len(tickerMapUniqueExtractedValues), len(tickerMapUniqueExtractedValues[0]), "tblTickerMap", tickerMapUniqueExtractedValues, sqlCursor, [])






# fieldAliasStr = myPyFunc.fieldsDictToStr(firstFieldsDict, True, True)
# fieldStr = myPyFunc.fieldsDictToStr(firstFieldsDict, True, False)




fieldStr = "\"Stock Name\", \"Broker\", \"Lot\", \"Ticker\""
sqlConvertedDate = "ltrim(strftime('%m', \"Date\"), '0') || '/' || ltrim(strftime('%d', \"Date\"), '0') || '/' || substr(strftime('%Y', \"Date\"), 3, 2)"


sqlCommand = f"select {fieldStr}, {sqlConvertedDate} as 'Purchase Date', -sum(\"Amount+-\") as 'Capital Invested' from tblScrubbed where \"Account\" = 'Cash' and \"Transaction Type\" like '%Purchase%' and \"Transaction Type\" not like '%Group Shares%' group by {fieldStr}, \"Date\" order by \"Broker\", \"Stock Name\", \"Lot\";"
# pp(sqlCommand)
myPyFunc.createTableAs("tblPurchase", sqlCursor, sqlCommand)
splitTime = myGoogleSheetsFunc.populateSheet(2, 1000, "tblPurchase", googleSheetsAPIObj, resultsSpreadsheetID, myPyFunc.getQueryResult("select * from tblPurchase", sqlCursor, True), True, writeToSheet=False, splitTimeArg=splitTime)



sqlCommand = f"select {fieldStr}, sum(\"Shares\") as 'Shares' from tblScrubbed where \"Account\" = 'Investment Asset' and \"Transaction Type\" like '%Purchase%' and \"Transaction Type\" not like '%Group Shares%' group by {fieldStr}  order by \"Broker\", \"Stock Name\", \"Lot\";"
# pp(sqlCommand)
myPyFunc.createTableAs("tblShares", sqlCursor, sqlCommand)
splitTime = myGoogleSheetsFunc.populateSheet(2, 1000, "tblShares", googleSheetsAPIObj, resultsSpreadsheetID, myPyFunc.getQueryResult("select * from tblShares", sqlCursor, True), True, writeToSheet=False, splitTimeArg=splitTime)


sqlCommand = f"select {fieldStr}, \"Transaction Type\", case when \"Transaction Type\" != 'Sale - Hypothetical' then {sqlConvertedDate} end as 'Sale Date', sum(\"Amount+-\") as 'Last Value' from tblScrubbed where \"Account\" = 'Cash' and \"Transaction Type\" like '%Sale%' and \"Transaction Type\" not like '%Group Shares%' group by {fieldStr}, \"Transaction Type\" order by \"Broker\", \"Stock Name\", \"Lot\";"
# pp(sqlCommand)
myPyFunc.createTableAs("tblSale", sqlCursor, sqlCommand)
splitTime = myGoogleSheetsFunc.populateSheet(2, 1000, "tblSale", googleSheetsAPIObj, resultsSpreadsheetID, myPyFunc.getQueryResult("select * from tblSale", sqlCursor, True), True, writeToSheet=False, splitTimeArg=splitTime)




#get list of values to put as the pivot columns


pivotColDict = myPyFunc.createPivotColDict("Year", 12, "Amount+-", 1, resultsTranScrubList)
pivotColStr = pivotColDict["pivotColStr"]
# pp(pivotColStr)

myPyFunc.createTableAs("tblDividends", sqlCursor, f"select {fieldStr}, {pivotColStr} from tblScrubbed where \"Account\" = 'Cash' and \"Transaction Type\" like '%Dividend%' group by {fieldStr};")
splitTime = myGoogleSheetsFunc.populateSheet(2, 1000, "tblDividends", googleSheetsAPIObj, resultsSpreadsheetID, myPyFunc.getQueryResult("select * from tblDividends", sqlCursor, True), True, writeToSheet=False, splitTimeArg=splitTime)





myPyFunc.createTableAs("tblAllLots", sqlCursor, f"select {fieldStr} from tblPurchase union select {fieldStr} from tblSale union select {fieldStr} from tblDividends;")
splitTime = myGoogleSheetsFunc.populateSheet(2, 1000, "tblResults", googleSheetsAPIObj, resultsSpreadsheetID, myPyFunc.getQueryResult("select * from tblAllLots", sqlCursor, True), True, writeToSheet=False, splitTimeArg=splitTime)




colDict =   {
                0:  {"table": "tblAllLots",
                    "excludedFields": []},
                1:  {"table": "tblPurchase",
                    "excludedFields": ["Stock Name", "Broker", "Lot", "Ticker"]},
                2:  {"table": "tblShares",
                    "excludedFields": ["Stock Name", "Broker", "Lot", "Ticker"]},
                3:  {"table": "tblSale",
                    "excludedFields": ["Stock Name", "Broker", "Lot", "Ticker"]}
            }


colListStr = myPyFunc.getAllColumns(colDict, sqlCursor)
# pp(colListStr)




divColStr = ""
percentColStr = ""


for colCount in range(0, len(pivotColDict["colList"])):

    currentColName = "tblDividends.\"" + str(pivotColDict["colList"][colCount]) + "\""
    currentYear = "int(left(indirect(\"r1c[0]\", false), 4))"

    purchaseDateCell = "indirect(\"e\"&row())"
    purchaseYear = "year(" + purchaseDateCell + ")"
    purchaseBeforeCondition = currentYear + "<" + purchaseYear

    saleDateCell = "indirect(\"i\"&row())"
    saleYear = "year(" + saleDateCell + ")"
    saleDate = "if(" + saleDateCell + "=\"\", year(today()), " + saleYear + ")"
    saleAfterCondition = currentYear + ">" + saleDate

    dividendTotalCondition = "if(or(" + purchaseBeforeCondition + ", " + saleAfterCondition + "), \"NO\", \"\")"
    divColStr = divColStr + "case when " + currentColName + " is null then '=" + dividendTotalCondition + "' else " + currentColName + " end as '" + str(pivotColDict["colList"][colCount]) + "'"

    capitalInvestedCell = "indirect(\"f\"&row())"
    currentYearTotalDividendCell = myGoogleSheetsFunc.cellOff(0, -7)
    currentYearTotalDividend = "if(" + currentYearTotalDividendCell + "=\"\", 0, " + currentYearTotalDividendCell + ")"
    currentYearTotalDividendCondition = "if(" + currentYearTotalDividendCell + "<>\"NO\", " + currentYearTotalDividendCell + "/" + capitalInvestedCell + ", \"\")"


    # if (or ( and (" + myGoogleSheetsFunc.cellOff(0, -6) + " <> \"\"," + myGoogleSheetsFunc.cellOff(0, -6) + "<>\"NO\"),and(int(left(indirect(\"R1C[0]\",false),4))>=year(indirect(\"E\"&row())),int(left(indirect(\"R1C[0]\",false),4))<=if(indirect(\"H\"&row())=\"\",year(today()),year(indirect(\"H\"&row()))))),iferror(indirect(\"R[0]C[-6]\",false)/indirect(\"F\"&row()),0),\"\")'
    percentColStr = percentColStr + "'=" + currentYearTotalDividendCondition + "' as '" + str(pivotColDict["colList"][colCount]) + " %'"   #int(left(indirect(\"R1C[0]\",false),4))<year(indirect(\"E\"&row())),int(left(indirect(\"R1C[0]\",false),4))>if(indirect(\"H\"&row())=\"\",year(today()),year(indirect(\"H\"&row())))),\"NO\",\"\")'

    if colCount != len(pivotColDict["colList"]) - 1:
        divColStr = divColStr + ", "
        percentColStr = percentColStr + ", "

# pp(divColStr)
# pp(percentColStr)




# sqlCommand = f"select " + colListStr + ", " + divColStr + ", '', " + percentColStr + ", ' ', '=sum(indirect(\"L\"&row()):indirect(\"Q\"&row()))' as 'Total Dividends', '' as 'Dividend Yield on Cost', '' as 'Forward Dividend', '' as 'Forward Dividend Yield', '' as '% of Portfolio' from tblResults " \
#             "left outer join tblTickerMap on tblResults.Stock = tblTickerMap.stockName " \

#"=" + myGoogleSheetsFunc.cellOff(0, -1) + "-" + myGoogleSheetsFunc.cellOff(0, -5) +


# pp(myGoogleSheetsFunc.cellOff(0, -1))

sqlCommand = "select " + colListStr + ", " + \
            "'=" + myGoogleSheetsFunc.cellOff(0, -1) + "-" + myGoogleSheetsFunc.cellOff(0, -5) + "' as \"Gain (Loss)\", " + \
            "'=iferror(" + myGoogleSheetsFunc.cellOff(0, -1) + "/" + myGoogleSheetsFunc.cellOff(0, -6) + ",\"\")' as \"% Gain (Loss)\", " + \
            divColStr + ", " + \
            "\"\", " + \
            percentColStr + ", ' '" + \
            "\" \", " + \
            "'=sum(" + myGoogleSheetsFunc.cellOff(0, -14) + ":" + myGoogleSheetsFunc.cellOff(0, -9) + ")' as \"Total Dividends\", " + \
            "'' as \"Dividend Yield On Cost\", " + \
            "'' as \"Forward Dividend\", " + \
            "'' as \"% of Portfolio\"" + \
            " from tblAllLots " + \
            "left outer join tblPurchase on tblAllLots.Broker = tblPurchase.Broker and tblAllLots.\"Stock Name\" = tblPurchase.\"Stock Name\" and tblAllLots.Lot = tblPurchase.Lot " \
            "left outer join tblShares on tblAllLots.Broker = tblShares.Broker and tblAllLots.\"Stock Name\" = tblShares.\"Stock Name\" and tblAllLots.Lot = tblShares.Lot " \
            "left outer join tblSale on tblAllLots.Broker = tblSale.Broker and tblAllLots.\"Stock Name\" = tblSale.\"Stock Name\" and tblAllLots.Lot = tblSale.Lot " \
            "left outer join tblDividends on tblAllLots.Broker = tblDividends.Broker and tblAllLots.\"Stock Name\" = tblDividends.\"Stock Name\" and tblAllLots.Lot = tblDividends.Lot " + \
            f"order by tblAllLots.Broker, tblAllLots.\"Stock Name\", tblAllLots.Lot"





myPyFunc.createTableAs("tblResults", sqlCursor, sqlCommand)



# sqlCommand = f"select {fieldStr}, case when \"Transaction Type\" != 'Sale - Hypothetical' then ltrim(strftime('%m', \"Transaction Type\"), '0') || '/' || ltrim(strftime('%d', \"Transaction Type\"), '0') || '/' || substr(strftime('%Y', \"Transaction Type\"), 3, 2) end as 'Sale Date', sum(\"Amount+-\") as 'Last Value', '' as 'To Sell', '=indirect(\"I\"&row())-indirect(\"F\"&row())' as 'Gain (Loss)', '=iferror(indirect(\"J\"&row())/indirect(\"F\"&row()),\"\")' as '% Gain (Loss)' from tblScrubbed where \"Account\" = 'Cash' and \"Transaction Type\" like '%Sale%' and \"Transaction Type\" not like '%Group Shares%' group by {fieldStr}, \"Transaction Type\" order by \"Broker\", \"Stock Name\", \"Lot\";"



sqlList = ["update tblResults set 'Last Value' = '=googlefinance(" + myGoogleSheetsFunc.cellOff(0, -6) + ")" + "*" + myGoogleSheetsFunc.cellOff(0, -3) + "' where tblResults.\"Sale Date\" is null;"]
myPyFunc.executeSQLStatements(sqlList, sqlCursor)

splitTime = myGoogleSheetsFunc.populateSheet(2, 1000, "tblResults", googleSheetsAPIObj, resultsSpreadsheetID, myPyFunc.getQueryResult("select * from tblResults", sqlCursor, True), True, writeToSheet=True, splitTimeArg=splitTime)


# splitTime = myGoogleSheetsFunc.populateSheet(2, 1000, "SQL Query Result - Table", googleSheetsAPIObj, resultsSpreadsheetID, myPyFunc.getQueryResult("select * from tblResultsJoined order by Broker, Stock, Lot", sqlCursor, True), True, writeToSheet=True, splitTimeArg=splitTime)
# splitTime = myGoogleSheetsFunc.populateSheet(2, 1000, "SQL Query Result - Balance Sheet", googleSheetsAPIObj, resultsSpreadsheetID, myPyFunc.getQueryResult("select * from tblResultsJoined order by Broker, Stock, Lot", sqlCursor, True), True, writeToSheet=True, splitTimeArg=splitTime)



myPyFunc.closeDatabase(sqlObj["sqlConnection"])
splitTime = myPyFunc.printElapsedTime(splitTime, "Finished with database")
myPyFunc.printElapsedTime(startTime, "Total time to run code")