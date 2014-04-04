#!/usr/bin/env python

import os
import time
import platform

######################################################################################
#####	open file logic
#####
######################################################################################
def getParam(sentence):
	return sentence.split('#')[0].strip()

def addHyphen(key):
	return ('-' + key) if len(key) == 1 else ('--' + key)

def openInputFile(inputFile, isParamFile):
	'''
	Open the param.txt and option.txt file and grab the params.
	The first param is the name of the file and the second shows whether its param.txt(which should be operated differently)
	Param hyphen is added here(e.g. --preset)
	'''
	f = open(inputFile, 'r')
	strsList = f.readlines()
	paramList = [getParam(strs) for strs in strsList if getParam(strs)] #remove blank lines & comments
	f.close()

	keyList = []
	valueList = []
	for param in paramList:
		paramPair = param.split('=')
		key = paramPair[0].strip()
		if isParamFile:
			key = addHyphen(key)

		if len(paramPair) == 1:
			value = []
		else:
			valueStrList = paramPair[1].split(',')
			value = [value.strip() for value in valueStrList if value.strip()]
		# print valueList
		keyList.append(key) 
		valueList.append(value)
	return keyList, valueList #key: str; value: list([] if no arguments)


######################################################################################
#####	check validity logic
#####
######################################################################################
def checkInputValidity(optionKeyList):
	options = ['x265Directory', 'yuvFileDirectory', 'shutdown']
	for option in options:
		if option not in optionKeyList:
			raise Exception('Not enough options is provided, please check!')


######################################################################################
#####	get yuv files logic
#####
######################################################################################
def getYuvFileList(path):
	'''
	Return all the .yuv files found from the given path.
	Directory and single file both supported.
	'''
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

	fileWithNoDupes = []
	[fileWithNoDupes.append(i) for i in yuvFileList if not fileWithNoDupes.count(i)] # remove dupes
	return fileWithNoDupes


######################################################################################
#####	write cmd logic
#####
######################################################################################
def getInfoFromFilename(yuvFileWithPath):
	'''get information such as resolution, fps & bitdepth from a yuv filename along with its path'''
	filename = os.path.splitext(os.path.split(yuvFileWithPath)[1])[0]
	infoList = filename.split('_')
	res, fps = infoList[1:3]

	##The following logic should be updated if new format of naming a yuv file is applied
	if len(infoList) == 3:
		bitdepth = 8
	elif infoList[3].endswith('bit'): 
		bitdepth = int(infoList[3][:-len('bit')])  
	else:
		bitdepth = 8
	return res, fps, bitdepth

def cmdRecursion(f, cmd, curResultDir, outputFile, paramKeyList, paramValueList, optionKeyList, optionValueList, index):
	if index == len(paramKeyList):
		curCmd = cmd[:]

		sep = os.path.sep
		csvFileName = outputFile[0] + '.csv'
		outputFileName = ''.join(outputFile) + '.265'

		curCmd.append('-o %(curResultDir)s%(sep)s%(outputFileName)s' %locals())
		curCmd.append('--csv %(curResultDir)s%(sep)s%(csvFileName)s' %locals())

		if 'saveOutput' in optionKeyList:
			logFileName = ''.join(outputFile) + '.log'
			curCmd.append('>> %(curResultDir)s%(sep)s%(logFileName)s' %locals())

		f.write(' '.join(curCmd) + '\n')
	else:
		key = paramKeyList[index] #traverse list
		if paramValueList[index] == []: ###params with no arguments
			cmdRecursion(f, cmd + ['%(key)s' %locals()], curResultDir, outputFile, paramKeyList, paramValueList, optionKeyList, optionValueList, index+1)

		for value in paramValueList[index]:
			if len(paramValueList[index]) > 1: #the 265 file should be named differently due to different params
				cmdRecursion(f, cmd + ['%(key)s %(value)s' %locals()], curResultDir, outputFile + ['_%(value)s' %locals()], paramKeyList, paramValueList, optionKeyList, optionValueList, index+1)
			else:
				cmdRecursion(f, cmd + ['%(key)s %(value)s' %locals()], curResultDir, outputFile, paramKeyList, paramValueList, optionKeyList, optionValueList, index+1)


def writeSubCmd(f, resultDir, yuvFile, paramKeyList, paramValueList, optionKeyList, optionValueList):
	(res, fps, bitdepth) = getInfoFromFilename(yuvFile)
	filename = os.path.splitext(os.path.split(yuvFile)[1])[0]
	curResultDir = resultDir + os.path.sep + filename

	f.write('mkdir %s\n' %curResultDir)
	if platform.system() == 'Windows':
		cmd = ['x265.exe']
	else:
		cmd = ['./x265']
	cmd.append('--input %(yuvFile)s' %locals())
	cmd.append('--input-res %(res)s' %locals())
	cmd.append('--fps %(fps)s' %locals())
	if bitdepth != 8:
		cmd.append('--input-depth %(bitdepth)s' %locals())
	cmdRecursion(f, cmd, curResultDir, [filename.split('_')[0]], paramKeyList, paramValueList, optionKeyList, optionValueList, 0)


def writeCmd(outputFile, paramKeyList, paramValueList, optionKeyList, optionValueList):
	f = open(outputFile, 'w')
	sep = os.path.sep
	curTime = time.strftime('%Y%m%d%H%M',time.localtime(time.time()))
	dirName = curTime

	##adding test name, Chinese seems to be supported
	if 'suffix' in optionKeyList:
		suffix = optionValueList[optionKeyList.index('suffix')]
		if suffix:
			dirName = dirName + '_' + suffix[0]
		
	resultDir = os.getcwd() + sep + dirName #result directory name(full path)
	if platform.system() != 'Windows':
		f.write('#!/usr/bin/env bash\n')	

	f.write('mkdir %s\n' %resultDir)

	x265Directory = optionValueList[optionKeyList.index('x265Directory')][0]
	if platform.system() == 'Windows':
		f.write('cd /d %s\n\n' %x265Directory)
	else:
		f.write('cd %s\n\n' %x265Directory)
	
	yuvFileList = searchYuvFile(optionValueList[optionKeyList.index('yuvFileDirectory')])
	for yuvFile in yuvFileList:
		writeSubCmd(f, resultDir, yuvFile, paramKeyList, paramValueList, optionKeyList, optionValueList)
		f.write('\n')

	if optionValueList[optionKeyList.index('shutdown')][0].lower() == 'on':
		if platform.system() == 'Windows':
			f.write('shutdown /s\n')
		else:
			f.write('shutdown -h now\n')
	f.close()


######################################################################################
#####	main
#####
######################################################################################
def main():
	(paramKeyList, paramValueList) = openInputFile('param.txt', True)
	(optionKeyList, optionValueList) = openInputFile('option.txt', False)

	checkInputValidity(optionKeyList) #check option params
	
	if platform.system() == 'Windows':
		outputFile = 'autorun.bat'
	else:
		outputFile = 'autorun.bash'
		os.system('touch %(outputFile)s' %locals())
		os.system('chmod u+x %(outputFile)s' %locals())		
		
	writeCmd(outputFile, paramKeyList, paramValueList, optionKeyList, optionValueList)
	if optionValueList[optionKeyList.index('shutdown')][0].lower() == 'on':
		print 'Notice: You choose to shutdown after finishing the test.'
		if platform.system() == 'Windows':
			os.system('pause')

if __name__ == '__main__':
	main()
