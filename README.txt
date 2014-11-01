##################################################################################
Files included: 
createBat.py, option.txt, param.txt

##################################################################################
Functions: 
Generating running scripts(.bat for win & .bash for linux) for x265 encoder, which will generate a document named after the System time and all results will be stored in the document.

##################################################################################
Attention:
1. Please check the script before you run it in case it doesn't meet your demond.
2. Any bug report or function requirement is welcomed.

##################################################################################
Usage: 
"param.txt" includes the x265 options you need
    Options like "-o, --input, --input-res, --input-depth£¬--fps, --csv" will be automatically added.

"option.txt" includes some additonal options
    EncoderDirectory: the absolute path of the x265 encoder 
    yuvFileDirectory: the absolute path of the yuv videos / directories(The program will find all the yuv files in the directory recursively)

e.g.

Your encoder locates in A, all the yuv files are in B and C, and the x265 options you need are "--preset ultrafast/medium", "-q 22/27/32/37", "--psnr"

Then in "option.txt" you should write:
EncoderDirectory = A	
yuvFileDirectory = B, C

In "option.txt" you should write:
preset = ultrafast, medium
qp = 22, 27, 32, 37
psnr

