# import libraries 
import numpy as np 
import cv2
import time

arrayCoords = []
def mouseLocationClick(event,x,y,flags,param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print("click identified at: " +str([x,y]))
        arrayCoords.append([x,y])


fileIObool = True
while fileIObool:
    # prompt user for file name in same directory as the python script LeptinGood.tif
    fileName = raw_input("Enter the file name with the .tif extension:  ")
    # import .tif file 
    imgRaw = cv2.imread(str(fileName),0)
    # verify file identity
    cv2.namedWindow('Image: ' + fileName +  ' uploaded to program',cv2.WINDOW_NORMAL) # make a named window'
    cv2.imshow('Image: ' + fileName +  ' uploaded to program',imgRaw)
    print("Press X if this is the right file: " + str(fileName) + " otherwise, press any other key  ")
    keyPress = cv2.waitKey(0)
    cv2.destroyAllWindows()
    if keyPress == 120:
        print("fileIObool loop complete")
        fileIObool = False
    else:
        print("fileIObool loop re-run.")


# user parameters to be used later:
analyte = raw_input("What is the analyte being used in this assay? Just add more in with / separating each  ")
print(analyte + " is/are the selected analyte for this slide")
numberOfArrays = raw_input("How many total Arrays are there in this image?  ")
print(numberOfArrays + " is the number of arrays on this image")
numberOfCaptureSpots = raw_input("How many capture spots are there in each Array?  ")
print(numberOfCaptureSpots + " is the number of capture spots in each Array")


for eachArray in range(int(numberOfArrays)):
    cropIOBool = True
    while cropIOBool:
        print("Select Array " + str(eachArray) + " region, clicking Top left, and then bottom right. Press x to confirm the area")
        
        # display the fill .tif image 
        imgRaw = cv2.imread(str(fileName),0)
        cv2.namedWindow('Raw Image',cv2.WINDOW_NORMAL) # make a named window, and then attach a mouse click event to it as definted in the function def in the beginning of the code
        cv2.setMouseCallback('Raw Image', mouseLocationClick)
        cv2.imshow('Raw Image',imgRaw)
        keyPress = cv2.waitKey(0)
        if keyPress == 120:
            arrayBotRigCoords = arrayCoords.pop()
            arrayTopLefCoords = arrayCoords.pop()
            print("subplot coordinates: " + str(arrayBotRigCoords)+ " " + str(arrayTopLefCoords))
        cv2.destroyAllWindows()
        cropXCoords = sorted([arrayBotRigCoords[0],arrayTopLefCoords[0]])
        cropYCoords = sorted([arrayBotRigCoords[1],arrayTopLefCoords[1]])
        print(str(cropXCoords))
        print(str(cropYCoords))
        
        subImg = imgRaw[cropYCoords[0]:cropYCoords[1],cropXCoords[0]:cropXCoords[1]]
        cv2.namedWindow('subcropped image',cv2.WINDOW_NORMAL) 
        cv2.imshow('subcropped image',subImg)
        print("x to continue. b to reselect the region")
        keyPress = cv2.waitKey(0)
        cv2.destroyAllWindows()
        if keyPress == 98:
            print("redoing cropIOBool Loop")
        if keyPress == 120:
            print("cropIOBool Loop complete")
            cropIOBool = False
    singleArrayIDBool = True
    while singleArrayIDBool:
        verifyImg = subImg
        smoothedCroppedIMG = cv2.medianBlur(subImg,3)
        circles = cv2.HoughCircles(smoothedCroppedIMG,cv2.cv.CV_HOUGH_GRADIENT,1,40,param1=30,param2=15,minRadius=10,maxRadius=60)
        circles = np.uint16(np.around(circles))
        circlesCenterPosX = 0
        circlesCenterPosY = 0
        circleCount = 0
        for i in circles[0,:]:
            cv2.circle(verifyImg,(i[0],i[1]),i[2],(0,255,0),1) # draw the outer circle
            cv2.circle(verifyImg,(i[0],i[1]),2,(0,0,255),2) # draw the center of the circle
            circleCount = circleCount + 1 # this counts the number of identified circles
            circlesCenterPosX = circlesCenterPosX + i[0] # sum of x positions added together
            circlesCenterPosY = circlesCenterPosY + i[1]
        circlesCenterPosX = circlesCenterPosX/circleCount #this is where the averages are calculated
        circlesCenterPosY = circlesCenterPosY/circleCount
        cv2.circle(verifyImg,(circlesCenterPosX,circlesCenterPosY),5,(255,0,0),3) # draws a blue marker at the calculated center of the array
        
        dist = []
        for i in circles[0,:]: # calculates the distance from each circle to the center of the array
            distanceFromCenter = np.sqrt( pow((i[0] - circlesCenterPosX),2) + pow((i[1] - circlesCenterPosY),2) )
            dist.append(distanceFromCenter) # stores those values into an array
        pointers = range(len(circles[0,:])) # makes a pointer array that matches the pointers in the "circle" list
        closestCircles = sorted(zip(dist,pointers),reverse=False)[:int(numberOfCaptureSpots)] # sorts and returns the closest 5 ([:5]) circles
        overallIntensities = []
        captureSpotLocations = []
        for capturePointers in closestCircles:
            circleInformation = circles[0,capturePointers[1]] # pulls the position and radius information from the 5 closest circles
            xCoordCirc = circleInformation[0]
            yCoordCirc = circleInformation[1]
            radiusCirc = circleInformation[2]
            cv2.circle(verifyImg,(xCoordCirc,yCoordCirc),radiusCirc,(0,0,255),1) # plots all of the circles / centers
            cv2.circle(verifyImg,(xCoordCirc,yCoordCirc),1,(0,255,0),1)
            # new code begin
            circIntensities = []
            for exesInCircle in range(( xCoordCirc - radiusCirc ),( xCoordCirc + radiusCirc )):
                # for each x value in each circle
                whyRange = np.sqrt(pow(radiusCirc,2) - pow((exesInCircle - xCoordCirc),2))
                discreteWhyRange = int(whyRange)
                #print("at x-pos of " + str(exesInCircle) +" with calculated y-range of " + str(discreteWhyRange))
                for whysInCircle in range(( yCoordCirc - discreteWhyRange),( yCoordCirc + discreteWhyRange)):
                    #print("raw image intensities: " + str(imgRaw[whysInCircle,exesInCircle])+" x: "+str(exesInCircle)+" y: "+str(whysInCircle))
                    circIntensities.append(subImg[whysInCircle,exesInCircle])
            captureSpotLocations.append([whysInCircle,exesInCircle])
            overallIntensities.append(np.mean(circIntensities))  
        cv2.imshow("verification of spot IDs",verifyImg)
        cv2.imshow("original cropped image",subImg)
        print("press x to end. press b to redo")
        pressedKey = cv2.waitKey(0) # press any key on the image window to close and terminate the program
        cv2.destroyAllWindows()
        if keyPress == 98:
            print("redoing singleArrayIDBool Loop")
        if keyPress == 120:
            print("singleArrayIDBool Loop complete")
            singleArrayIDBool = False
        
        # add in modification of number of capture spots or something, and interfacing for concentrations. 
