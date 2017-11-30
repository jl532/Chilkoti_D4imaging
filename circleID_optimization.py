# import libraries 
import numpy as np 
import cv2
import time

arrayCoords = []
def mouseLocationClick(event,x,y,flags,param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print("click identified at: " +str([x,y]))
        arrayCoords.append([x,y])
        
def pullElementsFromList(datList,argument): # use this when you have a 2d list and want a specific element from each entry
    return [thatSpecificArgument[argument] for thatSpecificArgument in datList]

def circleIDMultivariableOptimization(imageOfCirclesInArray,targetNumberOfCircles):
    medianBlurArg = 3 # sliding window size, it's a moving averager to remove some random noise
    circleAlgoImageSmoothed = cv2.medianBlur(imageOfCirclesInArray,medianBlurArg)
        
    HoughCircDP = 1 # don't mess with this for now
    HoughCircMinDist = 25 # the minimum distance between centers of circles (in pixels)
    HoughCircParam1 = 40 # don't mess with this for now, it's used for edge detection
    HoughCircParam2 = 15 # the smaller this is, the more circles will be detected (including false ones) and the larger this is, the more circles will be potentially returned. Test this though.
    HoughCircMinRadius = 14 # the lower limit of detected circle radius (in pixels). capture spots (generated from the genepix) usually are around 14-16 pixels in radius
    HoughCircMaxRadius = 30 # the upper limit of detected circle radius (in pixels)
    
    houghParamList = [HoughCircDP, HoughCircMinDist, HoughCircParam1, HoughCircParam2, HoughCircMinRadius, HoughCircMaxRadius]
        
    circlesRaw = cv2.HoughCircles(circleAlgoImageSmoothed,cv2.cv.CV_HOUGH_GRADIENT,houghParamList[0],houghParamList[1],param1=houghParamList[2],param2=houghParamList[3],minRadius=houghParamList[4],maxRadius=houghParamList[5])
    circles = np.uint16(np.around(circlesRaw))
    circleCount = len(circles[0])
    if circleCount is not targetNumberOfCircles:
        circleIDLoopBool = True
    else:
        return circles
    while circleIDLoopBool:
        #begin to perturb the model variables to identify parameters required to find the right number of circles
        # figure out algorithmically how best to perturb
    
fileNameInput = "62,5.tif"
targetNumberOfSpots = 149

medianBlurArg = 3 # sliding window size, it's a moving averager to remove some random noise
HoughCircDP = 1 # don't mess with this for now
HoughCircMinDist = 25 # the minimum distance between centers of circles (in pixels)
HoughCircParam1 = 40 # don't mess with this for now, it's used for edge detection
HoughCircParam2 = 15 # the smaller this is, the more circles will be detected (including false ones) and the larger this is, the more circles will be potentially returned. Test this though.
HoughCircMinRadius = 14 # the lower limit of detected circle radius (in pixels). capture spots (generated from the genepix) usually are around 14-16 pixels in radius
HoughCircMaxRadius = 30 # the upper limit of detected circle radius (in pixels)
numberOfCaptureSpots = 5
 
startTime = time.time()

imgRaw = cv2.imread(fileNameInput,0) # import the raw image here, currently set as "0,488.tif"
imgsmooth = cv2.medianBlur(imgRaw,medianBlurArg) # low pass filter the image, blurring a pixel with a 3 pixel sliding window
cimg = cv2.cvtColor(imgRaw,cv2.COLOR_GRAY2BGR) #converts raw image to grayscale
verificationImg = cimg.copy();

# this is the line of code that finds the circles in an image. more information about the parameters can be found at:
# https://www.pyimagesearch.com/2014/07/21/detecting-circles-images-using-opencv-hough-circles/

circles = cv2.HoughCircles(imgsmooth,cv2.cv.CV_HOUGH_GRADIENT,HoughCircDP,HoughCircMinDist,param1=HoughCircParam1,param2=HoughCircParam2,minRadius=HoughCircMinRadius,maxRadius=HoughCircMaxRadius)

# rounds and typecasts the circle information into unsigned 16 bit integers 
circles = np.uint16(np.around(circles))

circleCount = len(circles[0])

finishedTime = time.time() - startTime

print("done, with " + str(circleCount) + " circles identified in " + str(finishedTime) + " seconds") # prints out the number of identified circles for debugging purposes.
















