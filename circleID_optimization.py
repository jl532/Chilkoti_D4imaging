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

startTime = time.time()

fileNameInput = "62,5.tif"
targetNumberOfSpots = 149
imageOfCirclesInArray = cv2.imread(fileNameInput,0) # import the raw image here, currently set as "0,488.tif"
cimg = cv2.cvtColor(imageOfCirclesInArray,cv2.COLOR_GRAY2BGR)


medianBlurArg = 3 # sliding window size, it's a moving averager to remove some random noise
circleAlgoImageSmoothed = cv2.medianBlur(imageOfCirclesInArray,medianBlurArg)
    
HoughCircDP = 1 # don't mess with this for now
HoughCircMinDist = 35 # the minimum distance between centers of circles (in pixels)
HoughCircParam1 = 40 # don't mess with this for now, it's used for edge detection
HoughCircParam2 = 13 # the smaller this is, the more circles will be detected (including false ones) and the larger this is, the more circles will be potentially returned. Test this though.
HoughCircMinRadius = 11 # the lower limit of detected circle radius (in pixels). capture spots (generated from the genepix) usually are around 14-16 pixels in radius
HoughCircMaxRadius = 20 # the upper limit of detected circle radius (in pixels)

houghParamList = [HoughCircDP, HoughCircMinDist, HoughCircParam1, HoughCircParam2, HoughCircMinRadius, HoughCircMaxRadius]

# this is the line of code that finds the circles in an image. more information about the parameters can be found at:
# https://www.pyimagesearch.com/2014/07/21/detecting-circles-images-using-opencv-hough-circles/
    
rangeOfComparison = 10

rangeOfParams1 = range(HoughCircParam1 - rangeOfComparison, HoughCircParam1 + rangeOfComparison + 1)
rangeOfParams2 = range(HoughCircParam2 - rangeOfComparison, HoughCircParam2 + rangeOfComparison + 1)

iterationNumber = 1 
for eachParam1 in rangeOfParams1:
    for eachParam2 in rangeOfParams2:
        circlesRaw = cv2.HoughCircles(circleAlgoImageSmoothed,cv2.cv.CV_HOUGH_GRADIENT,houghParamList[0],houghParamList[1],param1=eachParam1,param2=eachParam2,minRadius=houghParamList[4],maxRadius=houghParamList[5])
        circles = np.uint16(np.around(circlesRaw))
        circleCount = len(circles[0])
        
        # print( "iteration Number: " + str(iterationNumber) + " param1: " + str(eachParam1) + " param2: " + str(eachParam2) + "  ||| difference in ID  " + str(targetNumberOfSpots - circleCount) )
        iterationNumber = iterationNumber + 1
        
        if circleCount == targetNumberOfSpots:
            print("------set of parameters found: param1: " + str(eachParam1) + " param2: " + str(eachParam2) + " with # circles found: " + str(circleCount))
#            verificationImg = cv2.cvtColor(imageOfCirclesInArray,cv2.COLOR_GRAY2BGR)
#            for i in circles[0]:
#                cv2.circle(verificationImg,(i[0],i[1]),i[2],(0,255,0),1) # draw the outer circle
#                cv2.circle(verificationImg,(i[0],i[1]),2,(0,0,255),2) # draw the center of the circle
#            cv2.imshow("verification image",verificationImg)    
#            cv2.waitKey(0) # press any key on the image window to close and terminate the program
#            cv2.destroyAllWindows()
         
finishedTime = time.time() - startTime

print("done, with " + str(circleCount) + " circles identified in " + str(finishedTime) + " seconds") # prints out the number of identified circles for debugging purposes.
















