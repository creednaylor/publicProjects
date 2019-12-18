from myPyLib import myPyFunc
from pprint import pprint as pp


def hasFormattedValue(cell):

    for item in cell:
        if "formattedValue" in item:
            return True

    return False



def isWhite(cell):

    try:
        if cell["userEnteredFormat"]["backgroundColor"]["red"] + cell["userEnteredFormat"]["backgroundColor"]["green"] + cell["userEnteredFormat"]["backgroundColor"]["blue"] == 3:
            return True
    except KeyError:
        return True

    return False





def getDataWithGrid(spreadsheetIDStr, googleSheetsObj, rangesArgument):
    return googleSheetsObj.get(spreadsheetId=spreadsheetIDStr, includeGridData=True, ranges=rangesArgument).execute()





def getCellValue(dataObj, sheetPos, rowPos, colPos):
    sheetsData = myPyFunc.getFromDict(dataObj, "sheets")
    currentSheetData = myPyFunc.getFromList(sheetsData, sheetPos)
    dataOnSheet = myPyFunc.getFromList(myPyFunc.getFromDict(currentSheetData, "data"), 0)
    currentRowsData = myPyFunc.getFromDict(dataOnSheet, "rowData")
    currentRowData = myPyFunc.getFromDict(myPyFunc.getFromList(currentRowsData, rowPos), "values")
    try:
        return myPyFunc.getFromList(currentRowData, colPos)["formattedValue"]
    except:
        return ""




def getCellValueEffective(dataObj, sheetPos, rowPos, colPos):
    sheetsData = myPyFunc.getFromDict(dataObj, "sheets")
    currentSheetData = myPyFunc.getFromList(sheetsData, sheetPos)
    dataOnSheet = myPyFunc.getFromList(myPyFunc.getFromDict(currentSheetData, "data"), 0)
    currentRowsData = myPyFunc.getFromDict(dataOnSheet, "rowData")
    currentRowData = myPyFunc.getFromDict(myPyFunc.getFromList(currentRowsData, rowPos), "values")
    try:
        return myPyFunc.getFromList(currentRowData, colPos)["effectiveValue"]
    except:
        return getCellValue(dataObj, sheetPos, rowPos, colPos)



def countRows(dataObj, sheetPos):

    sheetsData = myPyFunc.getFromDict(dataObj, "sheets")

    # saveFile(sheetsData, pathlib.Path(pathlib.Path.cwd().parents[3]/"privateData"/"stockResults"/"sheetsData.json"))
    # for i in sheetsData:
    #     pp(str(i)[:50])

    currentSheetData = myPyFunc.getFromList(sheetsData, sheetPos)
    dataOnSheet = myPyFunc.getFromList(myPyFunc.getFromDict(currentSheetData, "data"), 0)

    if "rowData" in dataOnSheet:
        return len(myPyFunc.getFromDict(dataOnSheet, "rowData"))
    else:
        return 1000000





def countColumns(dataObj, sheetPos):
    sheetsData = myPyFunc.getFromDict(dataObj, "sheets")
    currentSheetData = myPyFunc.getFromList(sheetsData, sheetPos)
    dataOnSheet = myPyFunc.getFromList(myPyFunc.getFromDict(currentSheetData, "data"), 0)

    if "rowData" in dataOnSheet:
        currentRowsData = myPyFunc.getFromDict(dataOnSheet, "rowData")
        currentRowData = myPyFunc.getFromDict(myPyFunc.getFromList(currentRowsData, 0), "values")
        return len(currentRowData)
    else:
        return 1000000






def extractValues(numRows, numCols, dataObj, sheetPos):

    listToReturn = []

    for indexOfRow in range(0, numRows):
        currentRowData = []

        for indexOfColumn in range(0, numCols):
            dictionary = getCellValueEffective(dataObj, sheetPos, indexOfRow, indexOfColumn)

            if not isinstance(dictionary, str):
                dictKey = list(dictionary.keys())[0]
                currentRowData.append(dictionary[dictKey])  # {"value": dictionary[dictKey], "type": dictKey})
            else:
                currentRowData.append("")  # {"value": "", "type": ""})

        listToReturn.append(currentRowData)


    return listToReturn




def extractValuesAndTypes(numRows, numCols, dataObj, sheetPos):

    listToReturn = []

    for indexOfRow in range(0, numRows):
        currentRowData = []

        for indexOfColumn in range(0, numCols):
            dictionary = getCellValueEffective(dataObj, sheetPos, indexOfRow, indexOfColumn)

            if not isinstance(dictionary, str):
                dictKey = list(dictionary.keys())[0]
                currentRowData.append({"value": dictionary[dictKey], "type": dictKey})
            else:
                currentRowData.append({"value": "", "type": ""})

        listToReturn.append(currentRowData)


    return listToReturn




def reduceSheet(rowsToKeep, columnsToKeep, sheetName, googleSheetsObj, spreadsheetID, clearSheet):

    googleSheetsDataWithGrid = getDataWithGrid(spreadsheetID, googleSheetsObj, sheetName)
    totalRows =  countRows(googleSheetsDataWithGrid, 0)
    totalColumns = countColumns(googleSheetsDataWithGrid, 0)
    requestObj = {}
    requestObj["requests"] = []

    if totalRows > rowsToKeep:
        requestObj["requests"].append({
                    "deleteDimension": {
                        "range": {
                            "sheetId": googleSheetsDataWithGrid["sheets"][0]["properties"]["sheetId"],
                            "dimension": "ROWS",
                            "startIndex": rowsToKeep,
                            "endIndex": totalRows
                        }
                    }
                })




    if totalColumns > columnsToKeep:

        requestObj["requests"].append({
                    "deleteDimension": {
                        "range": {
                            "sheetId": googleSheetsDataWithGrid["sheets"][0]["properties"]["sheetId"],
                            "dimension": "COLUMNS",
                            "startIndex": columnsToKeep,
                            "endIndex": totalColumns
                        }
                    }
                })


    if requestObj["requests"]:
        googleSheetsObj.batchUpdate(spreadsheetId=spreadsheetID, body=requestObj).execute()

    if clearSheet:
        googleSheetsObj.values().clear(spreadsheetId=spreadsheetID, range=sheetName, body={}).execute()




def createDictMapFromSheet(googleSheetsDataWithGrid, sheetIndex):

    from collections import OrderedDict

    rowTotal = countRows(googleSheetsDataWithGrid, sheetIndex)
    colTotal = countColumns(googleSheetsDataWithGrid, sheetIndex)

    mappingDict = {}

    for indexOfRow in range(0, rowTotal):

        colDict = OrderedDict()

        for indexOfColumn in range(1, colTotal):

            colTitle = getCellValue(googleSheetsDataWithGrid, sheetIndex, 0, indexOfColumn)

            colDict[colTitle] = getCellValue(googleSheetsDataWithGrid, sheetIndex, indexOfRow, indexOfColumn)

        mappingDict[getCellValue(googleSheetsDataWithGrid, sheetIndex, indexOfRow, 0)] = colDict

    return mappingDict




def populateSheet(rowsToKeep, colsToKeep, sheetName, googleSheetsObj, spreadsheetID, valuesList, clearSheet, **kwargs):

    dontPopulateSheet = kwargs.get("dontPopulateSheet", False)

    if not dontPopulateSheet:

        reduceSheet(rowsToKeep, colsToKeep, sheetName, googleSheetsObj, spreadsheetID, clearSheet)
        googleSheetsObj.values().update(spreadsheetId=spreadsheetID, range=sheetName, valueInputOption="USER_ENTERED", body={"values": valuesList}).execute()
        googleSheetsDataWithGrid = getDataWithGrid(spreadsheetID, googleSheetsObj, sheetName)


        requestObj = {
            "requests": [
                {
                    "autoResizeDimensions": {
                        "dimensions": {
                            "sheetId": googleSheetsDataWithGrid["sheets"][0]["properties"]["sheetId"],
                            "dimension": "COLUMNS",
                            "startIndex": 0,
                            "endIndex": len(valuesList[0]) + 1
                        }
                    }
                }
            ]
        }

        googleSheetsObj.batchUpdate(spreadsheetId=spreadsheetID, body=requestObj).execute()

    splitTime = kwargs.get("splitTimeArg", None)

    if splitTime:
        return myPyFunc.printElapsedTime(splitTime, "Finished writing to " + sheetName)



def authFunc():

    import pickle, pathlib, googleapiclient.discovery, google_auth_oauthlib.flow, google.auth.transport.requests
    # print(pathlib.Path.cwd().parents[3])

    credentialsPath = str(pathlib.Path.cwd().parents[3]) + "\\privatedata\\googleCredentials\\googleCredentials.json"
    tokenPath = str(pathlib.Path.cwd().parents[3]) + "\\privatedata\\googleCredentials\\googleToken.pickle"
    googleScopes = ["https://www.googleapis.com/auth/spreadsheets"]
    credentialsObj = None


    if pathlib.Path.exists(pathlib.Path(tokenPath)):
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


    return googleapiclient.discovery.build("sheets", "v4", credentials=credentialsObj).spreadsheets()