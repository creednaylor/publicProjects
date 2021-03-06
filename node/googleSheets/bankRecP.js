let path = require('path');
pathArrayThisFile = path.resolve(__dirname, __filename).split(path.sep);

let googleSheetsLibrary = require('../creedLibrary/googleSheetsLibrary/googleSheetsLibrary');
let c = console.log.bind(console);

const getSheetAndUpdateSheet = async ([googleSheetsUsername, googleSpreadsheetTitle, receivingBankFromPayPalData, accountantName, defaultTransferFromCheckbook, defaultTransferToCheckbook]) => {

    bankSheetTitle = 'bank';
    expandedBankSheetTitle = 'expandedBank';
    transfersToPostSheetTitle = 'transfersToPost';
    transactionsToPostSheetTitle = 'transactionsToPost';
    glForFees = '01-000-5321';

    bankSheetLevelObj = await googleSheetsLibrary.getSheetLevelObj(pathArrayThisFile, googleSheetsUsername, googleSpreadsheetTitle, bankSheetTitle);
    bankNewSheetLevelObj = await googleSheetsLibrary.getSheetLevelObj(pathArrayThisFile, googleSheetsUsername, googleSpreadsheetTitle, expandedBankSheetTitle);
    transfersToPostSheetLevelObj = await googleSheetsLibrary.getSheetLevelObj(pathArrayThisFile, googleSheetsUsername, googleSpreadsheetTitle, transfersToPostSheetTitle);
    transactionsToPostSheetLevelObj = await googleSheetsLibrary.getSheetLevelObj(pathArrayThisFile, googleSheetsUsername, googleSpreadsheetTitle, transactionsToPostSheetTitle);

    bankArray = await bankSheetLevelObj.getArrayOfValues();

    const expandedBankArray = bankArray.reduce(function(accumulator, currentElement, currentIndex) {

        arrayBeforeAmount = currentElement.slice(0, 5);
        arrayAfterAmount = currentElement.slice(9, currentElement.length)
        transactionTypes = ['Gross', 'Fee'];

        if (currentIndex > 0) {

            transactionTypes.forEach((transactionType, transactionTypeIndex) => {

                currentAmountStr = currentElement[transactionTypeIndex + 5].replace(',', '')

                if (currentAmountStr.includes('(')) {

                    currentAmount = -parseFloat(currentAmountStr.replaceAll(/\(|\)/g, ''))

                } else {

                    currentAmount = parseFloat(currentAmountStr);

                }

                if (currentAmount) {

                    accumulator.push(arrayBeforeAmount.concat(transactionType, currentAmount, arrayAfterAmount));

                }
            });

        } else {

            accumulator.push(arrayBeforeAmount.concat('Type', 'Amount', ...arrayAfterAmount));

        }

        return accumulator;

    }, []);

    transfersToPostArray = [['Transfer Date', 'Description', 'Transfer From Checkbook ID', 'Amount', 'Transfer To Checkbook ID', 'Status', 'Person']];
    feesToPostArray = [['Option', 'Type', 'Transaction Date', 'Checkbook ID', 'Paid To or Rcvd From', 'Description', 'Amount', 'Account', 'Amount2', 'Status', 'Person']];


    expandedBankArray.forEach((row) => {

        if (row[10] === receivingBankFromPayPalData) {

            [transferFromCheckbook, transferToCheckbook] = [defaultTransferFromCheckbook, defaultTransferToCheckbook];

            if (row[6] > 0) {

                [transferFromCheckbook, transferToCheckbook] = [defaultTransferToCheckbook, defaultTransferFromCheckbook];

            }

            description = transferFromCheckbook + ' to ' + transferToCheckbook;

            transfersToPostArray.push([row[0], description, transferFromCheckbook, Math.abs(row[6]), transferToCheckbook, '', accountantName])

        }

        if (row[5] === 'Fee') {

            adjustmentType = 'Decrease Adjustment';

            if (row[6] > 0) adjustmentType = 'Increase Adjustment';

            feesToPostArray.push(['Enter Transaction', adjustmentType, row[0], defaultTransferFromCheckbook, defaultTransferFromCheckbook, 'Fee', Math.abs(row[6]), glForFees, Math.abs(row[6]), '', accountantName]);

        }

    });

    bankNewSheetLevelObj.updateSheet(expandedBankArray);
    transfersToPostSheetLevelObj.updateSheet(transfersToPostArray);
    transactionsToPostSheetLevelObj.updateSheet(feesToPostArray);

    // c(expandedBankArray);

}

module.exports = getSheetAndUpdateSheet;