let path = require('path');
let fs = require('fs');
let l = require('../node/creedLibrary/creedLibrary')
thisFilePathArray = path.resolve(__dirname, __filename).split(path.sep);
thisFileParentPathArray = thisFilePathArray.slice(0, thisFilePathArray.length - 1)
configJSON = JSON.parse(fs.readFileSync([...thisFileParentPathArray, 'nConfig.json'].join(path.sep)));
nameOfAuthor = configJSON['nameOfAuthor'];


const isDirectory = (fileObjPathArray) => {

    return fs.statSync(pathArrayToStr(fileObjPathArray)).isDirectory();

};


const isFile = (fileObjPathArray) => {

    return fs.statSync(pathArrayToStr(fileObjPathArray)).isFile();

};


const pathArrayToStr = (pathArray) => {

    return pathArray.join(path.sep);

};


const getSuffix = (fileObjPathArray) => {

    arrayOfFileNameParts = fileObjPathArray.slice(-1)[0].split('.');

    if (arrayOfFileNameParts.length > 1) return '.'.concat(arrayOfFileNameParts.slice(-1)[0]);

    return '';

};


const getStem = (fileObjPathArray) => {

    arrayOfFileNameParts = fileObjPathArray.slice(-1)[0].split('.');

    if (arrayOfFileNameParts.length > 1) return arrayOfFileNameParts.slice(0, arrayOfFileNameParts.length - 1).join('.');

    return arrayOfFileNameParts[0];
};


const getArrayOfFileObjectsFromDir = (fileObjPathArray, pathsToExclude) => {

    const fileObjHasPathToExclude = (fileObj, pathsToExclude) => {

        for (let pathToExclude of pathsToExclude) {

            if (pathArrayToStr(fileObj).includes(pathArrayToStr(pathToExclude))) return true;

        }

        return false;

    }

    arrayOfFileObjFromDir = [];

    fs.readdirSync(pathArrayToStr(fileObjPathArray)).forEach(filename => {

        fileObjInDirToAdd = [...fileObjPathArray, filename];

        if (!fileObjHasPathToExclude(fileObjInDirToAdd, pathsToExclude)) arrayOfFileObjFromDir.push(fileObjInDirToAdd);

    });

    return arrayOfFileObjFromDir;
};


const findFilePathBreadthFirst = (rootPathArray, isJSFileToImport, pathsToExclude=[]) => {

    arrayOfFileObjects = [rootPathArray];

    while (arrayOfFileObjects.length) {

        fileObjPathArray = arrayOfFileObjects.shift();

        if (isJSFileToImport(fileObjPathArray)) return fileObjPathArray;

        if (isDirectory(fileObjPathArray)) arrayOfFileObjects.push(...getArrayOfFileObjectsFromDir(fileObjPathArray, pathsToExclude));

        // if (getSuffix(fileObjPathArray) == '.js') l.c(fileObjPathArray);
        // // l.c(getSuffix(fileObjPathArray));

    }

};

const importJSFile = (arrayOfArguments) => {

    // l.c(arrayOfArguments)
    l.c(`Searching for command '${arrayOfArguments[0]}.js' (created by ${nameOfAuthor})...`);

    rootPathArray = l.getPathUpFolderTree(thisFilePathArray, configJSON['nameOfDirectoryToSetAsRoot']);

    pathToJSFileForImport = findFilePathBreadthFirst(rootPathArray, (fileObjPathArray) => {

        if (getSuffix(fileObjPathArray) == '.js' && getStem(fileObjPathArray) == arrayOfArguments[0] && isFile(fileObjPathArray)) return true;

        return false;

    }, pathsToExclude=[[...rootPathArray, '.history'], [...rootPathArray, '.vscode'], [...rootPathArray, 'reposFromOthers'], [...rootPathArray, 'privateData', 'python', 'dataFromStocks'], ['node_modules'], ['.git']]);

    relativePathToJSFileForImport = './'.concat(path.relative(pathArrayToStr(thisFileParentPathArray), pathArrayToStr(pathToJSFileForImport)))
    // l.c(relativePath);

    require(relativePathToJSFileForImport)(arrayOfArguments.slice(1));
    // mainFunctionImportedJSFile(arrayOfArguments.slice(1));

};


if (require.main === module) {

    l.c(`${thisFilePathArray.slice(-1)[0]} (created by ${nameOfAuthor}) is not being imported. It is being run directly...`);
    // l.c(process.argv)
    importJSFile(process.argv.slice(2));

} else {

    l.c(`${thisFilePathArray.slice(-1)[0]} (created by ${nameOfAuthor}) is being imported. It is not being run directly...`);

}



