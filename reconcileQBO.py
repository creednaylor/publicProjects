print("Comment: Importing modules and setting up variables...")
import time
startTime = time.time()


import sys
sys.path.append("..")
from creed_modules import creedFunctions


import pickle, os.path, googleapiclient.discovery, google_auth_oauthlib.flow, google.auth.transport.requests
# from pprint import pprint
# import lumpy



copyToV2 = False
accountList = ["BAF 2 - 5006 (transfers to Bluebird)"]

def getLastCell(currentData, currentSheet):

    for sheet in currentData["sheets"]:

        if sheet["properties"]["title"] == currentSheet:

            totalRows = len(sheet["data"][0]["rowData"])
            totalColumnsByRow = []

            for row in sheet["data"][0]["rowData"]:
                totalColumnsByRow.append(len(row.get("values", [])))


    return creedFunctions.columnToLetter(max(totalColumnsByRow)) + str(totalRows)



def filterFunc(element):

    if element == 2:
        return True
    else:
        return False


def convertNumber(num):
    # try:
        num = creedFunctions.convertEmptyStrToZero(num)
        num = creedFunctions.removeCommaFromStr(num)
        num = float(num)
        return num
    # except BaseException as e:
    #     print("Error on " + num + " " + str(e))



credentialsPath = os.path.abspath(os.path.join(os.curdir, "..\\private_data\\googleCredentials\\googleCredentials.json"))
tokenPath = os.path.abspath(os.path.join(os.curdir, "..\\private_data\\googleCredentials\\googleToken.pickle"))
googleScopes = ["https://www.googleapis.com/auth/spreadsheets"]
credentialsObj = None


if os.path.exists(tokenPath):
    with open(tokenPath, "rb") as tokenObj:
        credentialsObj = pickle.load(tokenObj)


# If there are no (valid) credentials available, let the user log in.
if not credentialsObj or not credentialsObj.valid:
    if credentialsObj and credentialsObj.expired and credentialsObj.refresh_token:
        credentialsObj.refresh(google.auth.transport.requests.Request())
    else:
        flowObj = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(credentialsPath, googleScopes)
        credentialsObj = flowObj.run_local_server(port=0)
    # Save the credentials for the next run
    with open(tokenPath, "wb") as tokenObj:
        pickle.dump(credentialsObj, tokenObj)



googleSheetsObj = googleapiclient.discovery.build("sheets", "v4", credentials=credentialsObj).spreadsheets()
currentSpreadsheetID = "1T-DVnBRKYAsA1N_jqdKDMErav-PrrPBdLGS4wiLGCd4"

# currentSpreadsheetSheets = {}
# for sheet in googleSheetsObj.get(spreadsheetId=currentSpreadsheetID).execute()["sheets"]:
#     currentSpreadsheetSheets[sheet["properties"]["title"]] = sheet

print("Comment: Importing modules and setting up variables...Done. " + str(round(time.time() - startTime, 3)) + " seconds")


if copyToV2:

    startTime = time.time()
    print("Comment: Creating v2 sheet...")



    currentSpreadsheetData = googleSheetsObj.get(spreadsheetId=currentSpreadsheetID, includeGridData=True).execute()
    currentSheetName = "Original"
    currentBegRange = "A1"
    currentEndRange = getLastCell(currentSpreadsheetData, currentSheetName)


    currentSheetValues = googleSheetsObj.values().get(spreadsheetId=currentSpreadsheetID, range=currentSheetName + "!" + currentBegRange + ":" + currentEndRange).execute()["values"]
    sheetToWrite = "v2"
    firstRowToAppend = []

    for cell in currentSheetValues[0]:
        firstRowToAppend.append(cell)

    firstRowToAppend.insert(0, "Transaction Number")

    valuesToWrite = []
    valuesToWrite.append(firstRowToAppend)


    transactionNum = 1

    for row in currentSheetValues[1:]:

        if row:
            rowToAppend = []
            rowToAppend.append(transactionNum)

            if row[0] != "":
                currentDate = row[0]

            rowToAppend.append(currentDate)


            if row[1] != "":
                currentClr = row[1]

            rowToAppend.append(currentClr)


            for index, col in enumerate(row[2:]):
                rowToAppend.append(col)

            valuesToWrite.append(rowToAppend)

        else:

            transactionNum = transactionNum + 1



    bodyToWrite = {
        "values": valuesToWrite
    }

    googleSheetsObj.values().update(spreadsheetId=currentSpreadsheetID, range=sheetToWrite + "!A1", valueInputOption="USER_ENTERED", body=bodyToWrite).execute()


    print("Comment: Creating v2 sheet...Done. " + str(round(time.time() - startTime, 3)) + " seconds")


startTime = time.time()
print("Comment: Creating v3 sheet...")

currentSpreadsheetData = googleSheetsObj.get(spreadsheetId=currentSpreadsheetID, includeGridData=True).execute()
currentSheetName = "v2"
currentBegRange = "A1"
currentEndRange = getLastCell(currentSpreadsheetData, currentSheetName)


currentSheetValues = googleSheetsObj.values().get(spreadsheetId=currentSpreadsheetID, range=currentSheetName + "!" + currentBegRange + ":" + currentEndRange).execute()["values"]
currentAccountIndex = 3
currentTransIndex = 0
currentAmountIndex = 5
currentDebitIndex = 6
currentCreditIndex = 7
sheetToWrite = "v3"
firstRowToAppend = ["Account", "Amount+-"]


for cell in currentSheetValues[0]:
    firstRowToAppend.append(cell)

valuesToWrite = []
valuesToWrite.append(firstRowToAppend)


if not accountList:
    accountList = []

    for row in currentSheetValues[1:]:
        accountList.append(row[currentAccountIndex])

    accountList = list(dict.fromkeys(accountList))



for currentAccount in accountList:

    transactionList = []

    for row in currentSheetValues[1:]:
        print(row)
        if row[currentAccountIndex] == currentAccount:
            transactionList.append(row[currentTransIndex])

    transactionList = list(dict.fromkeys(transactionList))
    print(transactionList)


    for currentTrans in transactionList:

        for row in currentSheetValues[1:]:
            if row[currentTransIndex] == currentTrans and row[currentAccountIndex] != currentAccount:

                convertedNumbers = {
                    currentAmountIndex: convertNumber(row[currentAmountIndex]),
                    currentDebitIndex: convertNumber(row[currentDebitIndex]),
                    currentCreditIndex: convertNumber(creedFunctions.convertOutOfRangeToZero(row, currentCreditIndex))
                }


                rowToAppend = [currentAccount, -convertedNumbers[currentDebitIndex] + convertedNumbers[currentCreditIndex]]

                for index, col in enumerate(row):
                    if index in convertedNumbers.keys():
                        rowToAppend.append(convertedNumbers[index])
                    else:
                        rowToAppend.append(col)

                # print(rowToAppend)
                valuesToWrite.append(rowToAppend)

                fileForPrintObj = open(os.path.abspath(os.path.join(os.curdir, "..\\private_data\\reconcileQBO\\fileForPrint")), 'w+')
                fileForPrintObj.write(str(rowToAppend))
                fileForPrintObj.close()


bodyToWrite = {
    "values": valuesToWrite
}

googleSheetsObj.values().update(spreadsheetId=currentSpreadsheetID, range=sheetToWrite + "!A1", valueInputOption="USER_ENTERED", body=bodyToWrite).execute()


print("Comment: Creating v3 sheet...Done. " + str(round(time.time() - startTime, 3)) + " seconds")


