#local application imports
from pathlib import Path
import sys
pathToThisPythonFile = Path(__file__).resolve()
sys.path.append(str(Path(pathToThisPythonFile.parents[3], 'herokuGorilla', 'backend', 'python')))
import myPythonLibrary.myPyFunc as myPyFunc

#standard library imports
import datetime
from pprint import pprint as p
import subprocess
import json

def noGitIgnoreFileFound(gitFolder):

    for obj in gitFolder.glob('*'):

        if obj.name == '.gitignore':

            fileObj = open(obj, 'r+')

            for line in fileObj:

                if '__pycache__' in line: return False

            fileObj.write('\n__pycache__')
            fileObj.close()

            return False

    return True

def mainFunction(arrayOfArguments):

    def returnGitFolder(fileObj):

        if fileObj.name == '.git': return fileObj.parents[0]

        return None

    includeWorkFiles = False
    # p(arrayOfArguments)

    if arrayOfArguments[1] == 'includeWorkFiles':

        includeWorkFiles = True
        del arrayOfArguments[1]

    pathToRepos = myPyFunc.getPathUpFolderTree(pathToThisPythonFile, 'repos')

    gitFoldersToExecuteCommandOn = myPyFunc.getArrayOfFileObjInTreeBreadthFirst(pathToRepos, returnGitFolder, pathsToExclude=[Path(pathToRepos, '.history'), Path(pathToRepos, '.vscode'),  Path(pathToRepos, 'reposFromOthers'), 'node_modules'])
    # p(gitFoldersToExecuteCommandOn)

    if includeWorkFiles and pathToRepos.parents[0].name == 'cnaylor':

        with open(Path(pathToRepos, 'privateData', 'python', 'git', 'git.json'), 'r') as filehandle:
            
            otherFoldersObj = json.load(filehandle)

        for otherFolder in otherFoldersObj:

            gitFoldersToExecuteCommandOn.append(Path(otherFolder))


    for gitFolder in gitFoldersToExecuteCommandOn:

        gitFolderStr = str(gitFolder)
        # p(gitFolderStr)

        if gitFolderStr[0:1] in ['C', '/']:
        
            gitCommandPrefix = 'git -C \"' + gitFolderStr + "\""

            if noGitIgnoreFileFound(gitFolder):

                fileObj = open(Path(gitFolder, '.gitignore'), 'w')
                fileObj.write('__pycache__')
                fileObj.close()

        elif gitFolderStr[0:1] == 'Y':

            gitCommandPrefix = 'git --git-dir=\"' + otherFoldersObj[gitFolderStr] + '\" --work-tree=\"' + gitFolderStr + "\""

        # p(gitCommandPrefix)
        

        if arrayOfArguments[1] == 'acp':

            subprocessesToRun = [gitCommandPrefix + ' add .']

            commitMessage = datetime.datetime.now().strftime("%Y-%m-%d %H:%M") + ', added, committed, & pushed using python script'
            if len(arrayOfArguments) > 3: commitMessage = arrayOfArguments[3]

            subprocessesToRun.append(gitCommandPrefix + ' commit -m \"' + commitMessage + '\"')
            subprocessesToRun.append(gitCommandPrefix + ' push')

            # if gitFolder.name[:6] == 'heroku' and 'includeheroku' in arrayOfArguments:
                # subprocess.run('git -C ' + gitFolderStr + ' push heroku master')

        else:

            subprocessesToRun = [gitCommandPrefix + ' ' + ' '.join(arrayOfArguments[1:])]

        for subprocessToRun in subprocessesToRun:
            p(subprocessToRun)
            # p(gitFolderStr)
            subprocess.run(subprocessToRun, shell=True)


if __name__ == '__main__':
    p(str(pathToThisPythonFile.name) + ' is not being imported. It is being run directly...')
    mainFunction(sys.argv)
else:
	p(str(pathToThisPythonFile.name) + ' is being imported. It is not being run directly...')

