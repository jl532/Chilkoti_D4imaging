# import libraries 
import numpy as np 
import cv2

imgRaw = cv2.imread("0,488.tif",0) # import the raw image here, currently set as "0,488.tif"
imgsmooth = cv2.medianBlur(imgRaw,3) # low pass filter the image, blurring a pixel with a 3 pixel sliding window
cimg = cv2.cvtColor(imgRaw,cv2.COLOR_GRAY2BGR) #converts raw image to grayscale

# this is the line of code that finds the circles in an image. more information about the parameters can be found at:
# https://www.pyimagesearch.com/2014/07/21/detecting-circles-images-using-opencv-hough-circles/
circles = cv2.HoughCircles(imgsmooth,cv2.HOUGH_GRADIENT,1,40,param1=30,param2=15,minRadius=10,maxRadius=60)

# rounds and typecasts the circle information into unsigned 16 bit integers 
circles = np.uint16(np.around(circles))

# the following variables are used to determine the center of the array.
# The x and y coordinates are added together first in the next for loop, and then 
# the total x and y coordinate sums are divided by the number of counted circles

circlesCenterPosX = 0
circlesCenterPosY = 0
circleCount = 0

for i in circles[0,:]:
    cv2.circle(cimg,(i[0],i[1]),i[2],(0,255,0),2) # draw the outer circle
    cv2.circle(cimg,(i[0],i[1]),2,(0,0,255),3) # draw the center of the circle
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
closestCircles = sorted(zip(dist,pointers),reverse=False)[:5] # sorts and returns the closest 5 ([:5]) circles
for capturePointers in closestCircles:
    circleInformation = circles[0,capturePointers[1]] # pulls the position and radius information from the 5 closest circles
    cv2.circle(cimg,(circleInformation[0],circleInformation[1]),circleInformation[2],(0,0,255),2) # plots all of the circles / centers
    cv2.circle(cimg,(circleInformation[0],circleInformation[1]),1,(0,255,0),3)
    
cv2.imshow('Raw Image',imgRaw) # show the original raw image
cv2.imshow('Raw Image with Superimposed, identified Spots',cimg) # show the raw image with superimposed identified circles
cv2.waitKey(0) # press any key on the image window to close and terminate the program
cv2.destroyAllWindows()

print("done, with " + str(circleCount) + " circles identified") # prints out the number of identified circles for debugging purposes.