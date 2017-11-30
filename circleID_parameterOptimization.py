# import libraries 
import numpy as np 
import cv2
import time
import sys


arrayCoords = []
def mouseLocationClick(event,x,y,flags,param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print("click identified at: " +str([x,y]))
        arrayCoords.append([x,y])

startTime = time.time()

fileNameInput = "leptin_single_6.tif"
imageOfCirclesInArray = cv2.imread(fileNameInput,0) # import the raw image here, currently set as "0,488.tif"

# add in user interface for identifying minimum circle distance separation, and average circle radius.

lowerBoundMinDistance = 10
print("FINDING THE MINIMUM DISTANCE BETWEEN MICROARRAY SPOTS: click on the centers of two vertically adjacent microarray spots, then press (x) to continue")
cv2.namedWindow('Circle Parameter Optimization: min distance',cv2.WINDOW_NORMAL) # make a named window, and then attach a mouse click event to it as definted in the function def in the beginning of the code
cv2.setMouseCallback('Circle Parameter Optimization: min distance', mouseLocationClick)
cv2.imshow('Circle Parameter Optimization: min distance',imageOfCirclesInArray)
cv2.waitKey(0)

distTop = arrayCoords.pop()[1]
distBot = arrayCoords.pop()[1]
minimumDistBetweenCircles = abs(distBot - distTop) - lowerBoundMinDistance
print("Minimum Distance Between Circles: " + str(minimumDistBetweenCircles))
cv2.destroyAllWindows()

radiusBounds = 5
print("FINDING THE AVERAGE RADIUS OF MICROARRAY SPOTS: click on the OPPOSITE ENDS of one microarray spot (the vertical diameter), then press (x) to continue")
cv2.namedWindow('Circle Parameter Optimization: radius',cv2.WINDOW_NORMAL) # make a named window, and then attach a mouse click event to it as definted in the function def in the beginning of the code
cv2.setMouseCallback('Circle Parameter Optimization: radius', mouseLocationClick)
cv2.imshow('Circle Parameter Optimization: radius',imageOfCirclesInArray)
cv2.waitKey(0)

diameterTop = arrayCoords.pop()[1]
diameterBot = arrayCoords.pop()[1]

roughRadius = abs(diameterBot - diameterTop) / 2
radiusLowerBound = roughRadius - radiusBounds
radiusUpperBound = roughRadius + radiusBounds
print("radius bounds: " + str(radiusLowerBound) + " with " + str(radiusUpperBound))
cv2.destroyAllWindows()

## **** change this depending on how many microarray spots there SHOULD be in an image
targetNumberOfSpots = 149

## **** change these values depending on the array image you have
HoughCircMinDist = minimumDistBetweenCircles # the minimum distance between centers of circles (in pixels)
HoughCircMinRadius = radiusLowerBound # the lower limit of detected circle radius (in pixels). capture spots (generated from the genepix) usually are around 14-16 pixels in radius
HoughCircMaxRadius = radiusUpperBound # the upper limit of detected circle radius (in pixels) 

medianBlurArg = 3 # sliding window size, it's a moving averager to remove some random noise
circleAlgoImageSmoothed = cv2.medianBlur(imageOfCirclesInArray,medianBlurArg)
    
HoughCircDP = 1 # don't mess with this for now
HoughCircParam1 = 40 # don't mess with this for now, it's used for edge detection
HoughCircParam2 = 13 # the smaller this is, the more circles will be detected (including false ones) and the larger this is, the more circles will be potentially returned. Test this though.

houghParamList = [HoughCircDP, HoughCircMinDist, HoughCircParam1, HoughCircParam2, HoughCircMinRadius, HoughCircMaxRadius]

# this is the line of code that finds the circles in an image. more information about the parameters can be found at:
# https://www.pyimagesearch.com/2014/07/21/detecting-circles-images-using-opencv-hough-circles/
    
rangeOfComparison = 10
rangeOfParams1 = range(HoughCircParam1 - rangeOfComparison, HoughCircParam1 + rangeOfComparison + 1)
rangeOfParams2 = range(HoughCircParam2 - rangeOfComparison, HoughCircParam2 + rangeOfComparison + 1)

iterationNumber = 1 
# listOfPassedParameters = []
for eachParam1 in rangeOfParams1:
    for eachParam2 in rangeOfParams2:
        circlesRaw = cv2.HoughCircles(circleAlgoImageSmoothed,cv2.cv.CV_HOUGH_GRADIENT,houghParamList[0],houghParamList[1],param1=eachParam1,param2=eachParam2,minRadius=houghParamList[4],maxRadius=houghParamList[5])
        circles = np.uint16(np.around(circlesRaw))
        circleCount = len(circles[0])
        
        if (targetNumberOfSpots - circleCount) < 5:
                   print( "close to target < 5 || iter:" + str(iterationNumber) + " param1: " + str(eachParam1) + " param2: " + str(eachParam2) + "  ||| difference in ID  " + str(targetNumberOfSpots - circleCount) )
        iterationNumber = iterationNumber + 1
        
        if circleCount == targetNumberOfSpots:
            # listOfPassedParameters.append("------set of parameters found: param1: " + str(eachParam1) + " param2: " + str(eachParam2) + " with # circles found: " + str(circleCount))
            # print("------set of parameters found: param1: " + str(eachParam1) + " param2: " + str(eachParam2) + " with # circles found: " + str(circleCount))
            verificationImg = cv2.cvtColor(imageOfCirclesInArray,cv2.COLOR_GRAY2BGR)
            for i in circles[0]:
                cv2.circle(verificationImg,(i[0],i[1]),i[2],(0,255,0),1) # draw the outer circle
                cv2.circle(verificationImg,(i[0],i[1]),2,(0,0,255),2) # draw the center of the circle
            print("x to continue optimization. c to validate and end program, printing optimal parameters")
            cv2.imshow("verification image",verificationImg)    
            keyPressed = cv2.waitKey(0) # press any key on the image window to close and terminate the program
            cv2.destroyAllWindows()
            if keyPressed == ord("x"):
                print("circle parameters not optimized. continuing to search. Try: " + str(iterationNumber))
            if keyPressed == ord("c"):
                print("circle parameters optimized by user.")
                print("------set of parameters found: param1: " + str(eachParam1) + " param2: " + str(eachParam2) + " with # circles found: " + str(circleCount))
                print("finished in: " + str(time.time() - startTime))
                sys.exit()
print("if code reaches this point, then the target number of spots was never identified.")
            
            
















