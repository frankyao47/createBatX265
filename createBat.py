#!/usr/bin/env python

import os
import time

def writeCmd(f, curTime, yuvFile, res, fps):
	filename = os.path.splitext(os.path.split(yuvFile)[1])[0]
	dirname = curTime + os.path.sep + filename
	f.write('mkdir %s\n' %dirname)

	# presetList = ['ultrafast', 'medium', 'placebo']
	presetList = ['medium']
	qpList = ['22', '27', '32', '37']
	versionList = ['v1']
	iFrameFlag = 1 # 1 implies intra only
	frameNumbers = 0 # 0 implies all frames

	sep = os.path.sep
	for preset in presetList:
		for qp in qpList:
			for version in versionList:
				outputFile = preset + '_' + qp + '_' + version + '.265' ##output filename
				csvFile = 'result_' + filename + '.csv'
			
				#### cmd
				f.write('x265.exe -o %(dirname)s%(sep)s%(outputFile)s --input %(yuvFile)s --input-res %(res)s --fps %(fps)s \
--csv %(dirname)s%(sep)s%(csvFile)s -q %(qp)s --preset %(preset)s -i %(iFrameFlag)s -f %(frameNumbers)s --myversion %(version)s\n' %locals())
	f.write('\n')


def searchYuvFile(path):
    files = os.listdir(path)
    yuvFiles = []

    for file in files:
        if os.path.isdir(os.path.join(path, file)):
            yuvFiles.extend(searchYuvFile(os.path.join(path, file)))
        elif os.path.splitext(file)[1] == '.yuv':
        	yuvFiles.append(os.path.join(path, file))
        else:
        	pass

    return yuvFiles

def getYuvFileList(dirFilename):
	f = open(dirFilename, 'r')
	searchList = f.readlines() #dir and file list
	f.close()

	searchList = [dir for dir in searchList if dir[0] != '#' and not dir.isspace()] #ignore comment
	searchList = [dir.replace('\n','') for dir in searchList] #remove \n
	yuvFiles = []
	#print '\n'.join(searchList)
	for i in searchList:
		yuvFiles.extend(searchYuvFile(i))

	noDupes = []
	[noDupes.append(i) for i in yuvFiles if not noDupes.count(i)] # remove dupes

	return noDupes

def getResFps(yuvFile):
	filename = os.path.splitext(os.path.split(yuvFile)[1])[0]
	(image, res, fps) = filename.split('_')
	#print res, fps
	return [res, fps]

def main():
	yuvFileList = getYuvFileList('searchList.txt')
	f = open('autorun.bat', 'w')

	curTime = time.strftime('%Y%m%d%H%M',time.localtime(time.time()))
	f.write('mkdir %s\n' %curTime)

	#print '\n'.join(yuvFileList)
	for yuvFile in yuvFileList:
		(res, fps) = getResFps(yuvFile)	
		writeCmd(f, curTime,  yuvFile, res, fps)

	f.write("shutdown /s\n")
	f.close()

if __name__ == '__main__':
	main() 

