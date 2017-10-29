# import libraries 
import numpy as np 
import cv2
import time

fileNameInput = "62,5.tif"
medianBlurArg = 3 # i think this is the sliding window size, it's a moving averager to remove some random noise
HoughCircDP = 1 # don't mess with this for now
HoughCircMinDist = 30 # the minimum distance between centers of circles (in pixels)
HoughCircParam1 = 30 # don't mess with this for now, it's used for edge detection
HoughCircParam2 = 16 # the smaller this is, the more circles will be detected (including false ones) and the larger this is, the more circles will be potentially returned. Test this though.
HoughCircMinRadius = 13 # the lower limit of detected circle radius (in pixels). capture spots (generated from the genepix) usually are around 14-16 pixels in radius
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

# the following variables are used to determine the center of the array.
# The x and y coordinates are added together first in the next for loop, and then 
# the total x and y coordinate sums are divided by the number of counted circles

circlesCenterPosX = 0
circlesCenterPosY = 0
circleCount = 0

for i in circles[0,:]:
    cv2.circle(cimg,(i[0],i[1]),i[2],(0,255,0),1) # draw the outer circle
    cv2.circle(cimg,(i[0],i[1]),2,(0,0,255),2) # draw the center of the circle
    circleCount = circleCount + 1 # this counts the number of identified circles
    circlesCenterPosX = circlesCenterPosX + i[0] # sum of x positions added together
    circlesCenterPosY = circlesCenterPosY + i[1]
circlesCenterPosX = circlesCenterPosX/circleCount #this is where the averages are calculated
circlesCenterPosY = circlesCenterPosY/circleCount

# draws a blue marker at the calculated center of the array
cv2.circle(cimg,(circlesCenterPosX,circlesCenterPosY),5,(255,0,0),3)

# compare the distance from the center and categorize which ones are closest (5 for now)
dist = []
for i in circles[0,:]: # calculates the distance from each circle to the center of the array
    distanceFromCenter = np.sqrt( pow((i[0] - circlesCenterPosX),2) + pow((i[1] - circlesCenterPosY),2) )
    dist.append(distanceFromCenter) # stores those values into an array
pointers = range(len(circles[0,:])) # makes a pointer array that matches the pointers in the "circle" list
closestCircles = sorted(zip(dist,pointers),reverse=False)[:numberOfCaptureSpots] # sorts and returns the closest numberOfCaptureSpots ([:numberOfCaptureSpots]) circles


overallIntensities = []
captureSpotLocations = []
for capturePointers in closestCircles: # works with one capture spot at a time, each (capturePointer) in the list of the closest circles (closestCircles)
    
    circleInformation = circles[0,capturePointers[1]] # pulls the position and radius information from the 5 closest circles
    xCoordCirc = circleInformation[0] # separates the x and y coordinates of the center of the circles and the circle radius 
    yCoordCirc = circleInformation[1]
    radiusCirc = circleInformation[2]
    cv2.circle(cimg,(xCoordCirc,yCoordCirc),radiusCirc,(0,0,255),1) # plots detection circles / centers in red
    cv2.circle(cimg,(xCoordCirc,yCoordCirc),1,(0,255,0),1)
    # new code begin
    circIntensities = [] # start a new list of the circle intensities 
    for exesInCircle in range(( xCoordCirc - radiusCirc ),( xCoordCirc + radiusCirc )):
        # for each x value in each circle
        whyRange = np.sqrt(pow(radiusCirc,2) - pow((exesInCircle - xCoordCirc),2)) #calculates the y-coordinates that define the top and bottom bounds of a slice (at x position) of the circle 
        discreteWhyRange = int(whyRange) 
        #print("at x-pos of " + str(exesInCircle) +" with calculated y-range of " + str(discreteWhyRange))
        for whysInCircle in range(( yCoordCirc - discreteWhyRange),( yCoordCirc + discreteWhyRange)):
            #print("raw image intensities: " + str(imgRaw[whysInCircle,exesInCircle])+" x: "+str(exesInCircle)+" y: "+str(whysInCircle))
            circIntensities.append(imgRaw[whysInCircle,exesInCircle]) # appends all pixel intensities within the circle in this list
            verificationImg[whysInCircle,exesInCircle]=[0,0,255] # colors red in all pixels within the circle, just for verification
    captureSpotLocations.append([whysInCircle,exesInCircle]) # appends the locations of all of the pixels within the circle 
    overallIntensities.append(np.mean(circIntensities)) #takes the average of all the pixel intensities within the circle in question
    
    # new code end
finishedTime = time.time() - startTime

cv2.imshow('Raw Image',imgRaw) # show the original raw image
cv2.imshow('Raw Image with Superimposed, identified Spots',cimg) # show the raw image with superimposed identified circles
cv2.imshow('Redded out areas of capture spots',verificationImg)
cv2.waitKey(0) # press any key on the image window to close and terminate the program
cv2.destroyAllWindows()

print("done, with " + str(circleCount) + " circles identified in " + str(finishedTime) + " seconds") # prints out the number of identified circles for debugging purposes.
print(str(overallIntensities))
















