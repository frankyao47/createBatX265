#!/usr/bin/env python

import os
import time

######################################################################################
#####	open file logic
#####
######################################################################################
def getParam(sentence):
	return sentence.split('#')[0].strip()

def addHyphen(key):
	return len(key) == 1 and ('-' + key) or ('--' + key)

def openInputFile(inputFile, isParamFile):
	f = open(inputFile, 'r')
	strsList = f.readlines()
	paramList = [getParam(strs) for strs in strsList if getParam(strs)]
	f.close()

	keyList = []
	valueList = []
	for param in paramList:
		key = param.split('=')[0].strip()
		if isParamFile:
			key = addHyphen(key)
		valueStrList = param.split('=')[1].split(',')
		value = [value.strip() for value in valueStrList if value.strip()]
		# print valueList
		keyList.append(key) 
		valueList.append(value)
	return (keyList, valueList)

######################################################################################
#####	check validity logic
#####
######################################################################################
def checkInputValidity(optionKeyList):
	if not ('x265Directory' in optionKeyList and 'yuvFileDirectory' in optionKeyList and 'shutdown' in optionKeyList):
		raise Exception('Not enough options is provided, please check!')


######################################################################################
#####	get yuv files logic
#####
######################################################################################
def getYuvFileList(path):
	yuvFileList = []
	if os.path.isfile(path) and os.path.splitext(path)[1] == '.yuv':
		yuvFileList.append(path)
	elif os.path.isdir(path):
		files = os.listdir(path)
		for f in files:
			if os.path.isdir(os.path.join(path, f)):
				yuvFileList.extend(getYuvFileList(os.path.join(path, f)))
			elif os.path.isfile(os.path.join(path, f)) and os.path.splitext(f)[1] == '.yuv':
				yuvFileList.append(os.path.join(path, f))
			else:
				pass
	# print yuvFilesList
	return yuvFileList

def searchYuvFile(dirList):
	yuvFileList = []
	#print '\n'.join(searchList)
	for i in dirList:
		yuvFileList.extend(getYuvFileList(i))

	noDupes = []
	[noDupes.append(i) for i in yuvFileList if not noDupes.count(i)] # remove dupes
	return noDupes


######################################################################################
#####	write cmd logic
#####
######################################################################################
def getResFps(yuvFile):
	filename = os.path.splitext(os.path.split(yuvFile)[1])[0]
	(image, res, fps) = filename.split('_')
	#print res, fps
	return (res, fps)

def cmdRecursion(f, cmd, curResultDir, outputFile, paramKeyList, paramValueList, index):
	if index == len(paramKeyList):
		curCmd = cmd[:]
		curOutputFile = outputFile[:]

		sep = os.path.sep
		curOutputFile.append('.265')
		csvFile = curOutputFile[0] + '.csv'
		outputFileStr = ''.join(curOutputFile)
		
		curCmd.append('-o %(curResultDir)s%(sep)s%(outputFileStr)s' %locals())
		curCmd.append('--csv %(curResultDir)s%(sep)s%(csvFile)s' %locals())
		f.write(' '.join(curCmd) + '\n')
	else:
		key = paramKeyList[index] #traverse list
		for value in paramValueList[index]:
			curOutputFile = outputFile[:]

			if len(paramValueList[index]) > 1:
				curOutputFile.append('_%(value)s' %locals())
			curCmd = cmd[:]
			curCmd.append('%(key)s %(value)s' %locals())
			cmdRecursion(f, curCmd, curResultDir, curOutputFile, paramKeyList, paramValueList, index+1)


def writeSubCmd(f, resultDir, yuvFile, paramKeyList, paramValueList):
	(res, fps) = getResFps(yuvFile)
	filename = os.path.splitext(os.path.split(yuvFile)[1])[0]
	curResultDir = resultDir + os.path.sep + filename

	f.write('mkdir %s\n' %curResultDir)
	cmd = ['x265.exe']
	cmd.append('--input %(yuvFile)s' %locals())
	cmd.append('--input-res %(res)s' %locals())
	cmd.append('--fps %(fps)s' %locals())
	cmdRecursion(f, cmd, curResultDir, [filename.split('_')[0]], paramKeyList, paramValueList, 0)


def writeCmd(outputFile, paramKeyList, paramValueList, optionKeyList, optionValueList):
	f = open(outputFile, 'w')
	sep = os.path.sep
	curTime = time.strftime('%Y%m%d%H%M',time.localtime(time.time()))
	resultDir = os.getcwd() + sep + curTime
	
	f.write('mkdir %s\n' %resultDir)

	x265Directory = optionValueList[optionKeyList.index('x265Directory')][0]
	f.write('cd /d %s\n\n' %x265Directory)
	
	yuvFileList = searchYuvFile(optionValueList[optionKeyList.index('yuvFileDirectory')])
	for yuvFile in yuvFileList:
		writeSubCmd(f, resultDir, yuvFile, paramKeyList, paramValueList)
		f.write('\n')

	if(optionValueList[optionKeyList.index('shutdown')][0].lower() == 'on'):
		f.write('shutdown /s\n')
	f.close()

######################################################################################
#####	main
#####
######################################################################################
def main():
	(paramKeyList, paramValueList) = openInputFile('param.txt', True)
	(optionKeyList, optionValueList) = openInputFile('option.txt', False)
	# print paramDict, optionDict
	checkInputValidity(optionKeyList)
	# print yuvFileList
	outputFile = 'autorun.bat'
	writeCmd(outputFile, paramKeyList, paramValueList, optionKeyList, optionValueList)

if __name__ == '__main__':
	main()