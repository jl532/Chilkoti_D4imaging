# import libraries 
import numpy as np 
import cv2
import time
from operator import itemgetter

arrayCoords = []
def mouseLocationClick(event,x,y,flags,param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print("click identified at: " +str([x,y]))
        arrayCoords.append([x,y])
        
def pullElementsFromList(datList,argument): # use this when you have a 2d list and want a specific element from each entry
    return [thatSpecificArgument[argument] for thatSpecificArgument in datList]
        
def circleDistanceSorter(circleArray,position,numberofCaptSpots):
    dist = []
    for i in circleArray[0,:]: # calculates the distance from each circle to the center of the array
        distanceFromCenter = np.sqrt( pow((i[0] - position[0]),2) + pow((i[1] - position[1]),2) )
        dist.append(distanceFromCenter) # stores those values into an array
    pointers = range(len(circleArray[0,:])) # makes a pointer array that matches the pointers in the "circle" list
    closestCirclesPointers = sorted(zip(dist,pointers),reverse=False) # sorts and returns the sorted list [distance,pointers]
    sortedCirclesFromCenter = circleArray[0,pullElementsFromList(closestCirclesPointers,1)] # returns the circle List entries sorted by distance using the pointers to the circle List
    captureSpots = sortedCirclesFromCenter[:numberofCaptSpots]
    sortedCaptureSpotsByWhy = sorted(captureSpots, key = itemgetter(1))
    maxCircleRadius = max(pullElementsFromList(sortedCaptureSpotsByWhy,2))
    yCoordinateRowOfCircles= sortedCaptureSpotsByWhy[0][1]
    fullySortedList = []
    rowCircleList = []
    for eachCircle in sortedCaptureSpotsByWhy:
        #print(eachCircle)
        if (abs(eachCircle[1]-yCoordinateRowOfCircles) < maxCircleRadius):
            rowCircleList.append(eachCircle)
            #print(str(eachCircle) + " added")
        else:
            rowCirclesSortedByX = sorted(rowCircleList, key = itemgetter(0))
            fullySortedList = fullySortedList + rowCirclesSortedByX
            #print(str(rowCircleList) + " flushed")
            rowCircleList = []
            yCoordinateRowOfCircles = eachCircle[1]
            rowCircleList.append(eachCircle)
    rowCirclesSortedByX = sorted(rowCircleList, key = itemgetter(0))
    fullySortedList = fullySortedList + rowCirclesSortedByX
    #print(str(rowCircleList) + " flushed")
#    print(fullySortedList)        
    return fullySortedList

def circlePixelID(circleList): # output pixel locations of all circles within the list,
    circleIDpointer = 0
    pixelLocations = []
    for eachCircle in circleList:
        xCoordCirc = eachCircle[0] # separates the x and y coordinates of the center of the circles and the circle radius 
        yCoordCirc = eachCircle[1]
        radiusCirc = eachCircle[2] + 2
        for exesInCircle in range(( xCoordCirc - radiusCirc ),( xCoordCirc + radiusCirc )):
            whyRange = np.sqrt(pow(radiusCirc,2) - pow((exesInCircle - xCoordCirc),2)) #calculates the y-coordinates that define the top and bottom bounds of a slice (at x position) of the circle 
            discreteWhyRange = int(whyRange) 
            for whysInCircle in range(( yCoordCirc - discreteWhyRange),( yCoordCirc + discreteWhyRange)):
                pixelLocations.append([exesInCircle,whysInCircle, radiusCirc, circleIDpointer])
        circleIDpointer = circleIDpointer + 1 
    return pixelLocations

def rectangleBackgroundAreaDefiner(capturePixelInformation):
    maxRadius = max(pullElementsFromList(capturePixelInformation,2))
    smolRectRight = max(pullElementsFromList(capturePixelInformation,0)) + int(maxRadius * 1.2)
    smolRectLeft = min(pullElementsFromList(capturePixelInformation,0)) - int(maxRadius * 1.2)
    smolRectBot = max(pullElementsFromList(capturePixelInformation,1)) + int(maxRadius * 1.2)
    smolRectTop = min(pullElementsFromList(capturePixelInformation,1)) - int(maxRadius * 1.2)
    
    bigRectRight = smolRectRight + int(maxRadius * 3)
    bigRectLeft = smolRectLeft - int(maxRadius * 3)
    bigRectBot = smolRectBot + int(maxRadius * 3)
    bigRectTop = smolRectTop - int(maxRadius * 3)
    
    backgroundPixels = []
    for bgExes in range(bigRectLeft,bigRectRight):
        for bgWhys in range(bigRectTop,bigRectBot):
            if ((bgWhys > smolRectBot) or (bgWhys < smolRectTop)):
                backgroundPixels.append([bgExes,bgWhys])
            elif ((bgExes > smolRectRight) or (bgExes < smolRectLeft)):
                backgroundPixels.append([bgExes,bgWhys])
    return backgroundPixels
                

fileNameInput = "62,5.tif"
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
cimg = cv2.cvtColor(imgRaw,cv2.COLOR_GRAY2BGR) #converts raw image from grayscale to Blue/Green/Red
verificationImg = cimg.copy();

# this is the line of code that finds the circles in an image. more information about the parameters can be found at:
# https://www.pyimagesearch.com/2014/07/21/detecting-circles-images-using-opencv-hough-circles/

circles = cv2.HoughCircles(imgsmooth,cv2.HOUGH_GRADIENT,HoughCircDP,HoughCircMinDist,param1=HoughCircParam1,param2=HoughCircParam2,minRadius=HoughCircMinRadius,maxRadius=HoughCircMaxRadius)

# rounds and typecasts the circle information into unsigned 16 bit integers 
circles = np.uint16(np.around(circles))

# the following variables are used to determine the center of the array.
# The x and y coordinates are added together first in the next for loop, and then 
# the total x and y coordinate sums are divided by the number of counted circles

arrayCenterPosX = int(np.mean(circles[0,:][:,0]))
arrayCenterPosY = int(np.mean(circles[0,:][:,1]))
circleCount = len(circles[0,:][:,1])

for i in circles[0,:]:
    cv2.circle(cimg,(i[0],i[1]),i[2],(0,255,0),1) # draw the outer circle
    cv2.circle(cimg,(i[0],i[1]),2,(0,0,255),2) # draw the center of the circle

# draws a blue marker at the calculated center of the array
cv2.circle(cimg,(arrayCenterPosX,arrayCenterPosY),5,(255,0,0),3)

# compare the distance from the center and categorize which ones are closest (5 for now)
captureCircles = circleDistanceSorter(circles,[arrayCenterPosX,arrayCenterPosY],numberOfCaptureSpots)
capturePixels = circlePixelID(captureCircles)
verificationImg[pullElementsFromList(capturePixels,1),pullElementsFromList(capturePixels,0)] = [0,0,250]
backgroundPixels = rectangleBackgroundAreaDefiner(capturePixels)
verificationImg[pullElementsFromList(backgroundPixels,1),pullElementsFromList(backgroundPixels,0)] = [255,0,0]

captureIntensities= [ imgRaw[pullElementsFromList(capturePixels,1),pullElementsFromList(capturePixels,0)], pullElementsFromList(capturePixels,3) ]



#detectionCircles = circleDistanceSorter(circles,[arrayCenterPosX,arrayCenterPosY])
#detectionPixels = circlePixelID(detectionCircles)
#verificationImg[pullElementsFromList(detectionPixels,1),pullElementsFromList(detectionPixels,0)] = [0,255,0]


finishedTime = time.time() - startTime

# cv2.imshow('Raw Image',imgRaw) # show the original raw image

cv2.namedWindow('Raw Image',cv2.WINDOW_NORMAL) # make a named window, and then attach a mouse click event to it as definted in the function def in the beginning of the code
cv2.setMouseCallback('Raw Image', mouseLocationClick)
cv2.imshow('Raw Image',imgRaw)

cv2.imshow('Raw Image with Superimposed, identified circles',cimg) # show the raw image with superimposed identified circles
cv2.imshow('Verification image',verificationImg)
cv2.waitKey(0) # press any key on the image window to close and terminate the program
cv2.destroyAllWindows()

print("done, with " + str(circleCount) + " circles identified in " + str(finishedTime) + " seconds") # prints out the number of identified circles for debugging purposes.
















