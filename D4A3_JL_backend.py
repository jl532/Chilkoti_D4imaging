# import libraries 
import numpy as np 
import cv2
import sys
from operator import itemgetter

arrayCoords = []
def mouseLocationClick(event,x,y,flags,param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print("click identified at: " +str([x,y]))
        arrayCoords.append([x,y])
      

class D4Array:
    "a class that carries all of the information needed for each Array"
    def __init__(self,analyte,concentration,intensities,background,d4fileName,d4coordinates,centerOfArrayCoordinates, capturePositions , captureRadii):
        self.analyte = analyte
        self.concentration = concentration
        self.intensities = intensities
        self.stdev = np.std(intensities)
        self.background = background
        self.d4fileName = d4fileName
        self.d4coordinates = d4coordinates
        self.centerOfArrayCoordinates = centerOfArrayCoordinates
        self.capturePositions = capturePositions
        self.captureRadii = captureRadii
        
    def displayAllInfo(self):
        print(self.analyte + " " + str(self.concentration)+ " " +str(self.intensities)+ " " +str(self.stdev)+ " "+str(self.background))
        print(self.d4fileName+" "+str(self.d4coordinates)+" "+str(self.centerOfArrayCoordinates)+" "+str(self.capturePositions)+" "+str(self.captureRadii))
                
fileIObool = True
while fileIObool:
    # prompt user for file name in same directory as the python script LeptinGood.tif
    fileName = raw_input("Enter the file name with the .tif extension:  ")
    # import .tif file 
    imgRaw = cv2.imread(str(fileName),0)
    # verify file identity
    cv2.namedWindow('Image: ' + fileName +  ' uploaded to program',cv2.WINDOW_NORMAL) # make a named window'
    cv2.imshow('Image: ' + fileName +  ' uploaded to program',imgRaw)
    print("Press X if this is the right file: " + str(fileName) + ". press b to choose a different file. to exit, press q.  ")
    keyPress = cv2.waitKey(0)
    cv2.destroyAllWindows()
    if keyPress == ord("x"):
        print("fileIObool loop complete")
        fileIObool = False
    if keyPress == ord("b"):
        print("fileIObool loop re-run.")
    if keyPress == ord("q"):
        sys.exit()

# user parameters to be used later:
userPromptBool = True
while(userPromptBool):
    IOanalyte = raw_input("What is the analyte being used in this assay? Just add more in with / separating each:  ")
    numberOfArrays = raw_input("How many total Arrays are there in this image?  ")
    startingConcentration = raw_input("What is the starting concentration in ng/mL?   ")
    numberOfCaptureSpots = raw_input("How many capture spots are there in each Array?  ")
    
    print(IOanalyte + " is/are the selected analyte for this slide")
    print(str(numberOfArrays) + " is the number of arrays on this image")
    print(startingConcentration + " is the starting concentration.")
    print(numberOfCaptureSpots + " is the number of capture spots in each Array")
    promptVerify = raw_input("verify the information you have entered. enter x to continue, b to redo, q to exit program:   ")
    if promptVerify == 'x':
        userPromptBool = False
    if promptVerify == 'b':
        userPromptBool = True
    if promptVerify == 'q':
        sys.exit()
    
listD4Arrays = []
d4Concentration = float(startingConcentration)
for eachArray in range(int(numberOfArrays)):
    cropIOBool = True
    blankBool = False
    while cropIOBool:
        print("Select Array " + str(eachArray+1) + " region, clicking Top left, and then bottom right. Press x to confirm the area")
        
        # display the fill .tif image 
        imgRaw = cv2.imread(str(fileName),0)
        cv2.namedWindow('Raw Image',cv2.WINDOW_NORMAL) # make a named window, and then attach a mouse click event to it as definted in the function def in the beginning of the code
        cv2.setMouseCallback('Raw Image', mouseLocationClick)
        cv2.imshow('Raw Image',imgRaw)
        keyPress = cv2.waitKey(0)
        if keyPress == ord("x"):
            arrayBotRigCoords = arrayCoords.pop()
            arrayTopLefCoords = arrayCoords.pop()
            print("subplot coordinates: " + str(arrayBotRigCoords)+ " " + str(arrayTopLefCoords))
        if keyPress == ord("q"):
            print("cropping system exit")
            sys.exit()
        cv2.destroyAllWindows()
        cropXCoords = sorted([arrayBotRigCoords[0],arrayTopLefCoords[0]])
        cropYCoords = sorted([arrayBotRigCoords[1],arrayTopLefCoords[1]])
        print(str(cropXCoords))
        print(str(cropYCoords))
        
        subImg = imgRaw[cropYCoords[0]:cropYCoords[1],cropXCoords[0]:cropXCoords[1]]
        cv2.namedWindow('subcropped image',cv2.WINDOW_NORMAL) 
        cv2.imshow('subcropped image',subImg)
        print("x to continue, c to blank, b to reselect, q to exit program")
        keyPress = cv2.waitKey(0)
        cv2.destroyAllWindows()
        if keyPress == ord("b"):
            print("redoing cropIOBool Loop")
        if keyPress == ord("x"):
            print("cropIOBool Loop complete")
            cropIOBool = False
        if keyPress == ord("c"):
            print("cropIOBool Loop complete--BLANK")
            cropIOBool = False
            blankBool = True
        if keyPress == ord("q"):
            print("CropIOBool Loop exit")
            sys.exit()
    singleArrayIDBool = True
    while singleArrayIDBool:
        verifyImg = cv2.cvtColor(subImg,cv2.COLOR_GRAY2BGR)
        smoothedCroppedIMG = cv2.medianBlur(subImg,3)
        
        circles = cv2.HoughCircles(smoothedCroppedIMG,cv2.cv.CV_HOUGH_GRADIENT,1,40,param1=30,param2=16,minRadius=10,maxRadius=20)
        circles = np.uint16(np.around(circles))
            
        arrayCenterPosX = int(np.mean(circles[0,:][:,0]))
        arrayCenterPosY = int(np.mean(circles[0,:][:,1]))
        circleCount = len(circles[0,:][:,1])
        
        for i in circles[0,:]:
            cv2.circle(verifyImg,(i[0],i[1]),i[2],(0,255,0),1) # draw the outer circle
            cv2.circle(verifyImg,(i[0],i[1]),2,(0,0,255),2) # draw the center of the circle
        cv2.circle(verifyImg,(arrayCenterPosX,arrayCenterPosY),5,(255,0,0),3) # draws a blue marker at the calculated center of the array
        
        if blankBool:
            if len(listD4Arrays) == 0:
                print("error: do not start with a blank. begin with non-blank arrays so average position of capture spots is identified.")
                singleArrayIDBool = False
            else:
                print("using previously analyzed arrays within image to estimate blank capture spot locations")
                sumCaptureCoordinates = []
                avgCaptureCoordinates = []
                    sumCaptureCoordinates.append([0,0,0])
                    avgCaptureCoordinates.append([0,0,0])
                
                for eachPreviousArray in listD4Arrays:
                    centerCoordinates = eachPreviousArray.centerOfArrayCoordinates
                    captureCoordinates = eachPreviousArray.capturePositions
                    captureRadii = eachPreviousArray.captureRadii
                    # add in average radii
                    normalizedCapCoordinates = []
                    count = 0
                    for eachCapCoord in captureCoordinates:
                        normalizedCapCoordinates.append([eachCapCoord[0]  - centerCoordinates[0] + arrayCenterPosX, eachCapCoord[1]- centerCoordinates[1] + arrayCenterPosY, captureRadii[count]])
                        count = count + 1
                    captureRangeOfExes = max(blankExes[0] for blankExes in normalizedCapCoordinates) - min(blankExes[0] for blankExes in normalizedCapCoordinates)
                    captureRangeOfWhys = max(blankWhys[1] for blankWhys in normalizedCapCoordinates) - min(blankWhys[1] for blankWhys in normalizedCapCoordinates)
                    # if the range of exes is larger than the average capture circle size, the cap spots vary in the y direction, so sort along y
                    if (captureRangeOfExes > np.mean(eachPreviousArray.captureRadii)):
                        blankSortedCoords = sorted(normalizedCapCoordinates, key=itemgetter(1))
                    # if the range of whys is larger than the average capture circle size, the cap spots vary in the x direction, so sort along x
                    elif (captureRangeOfWhys > np.mean(eachPreviousArray.captureRadii)):
                        blankSortedCoords = sorted(normalizedCapCoordinates, key=itemgetter(0))
                    else: 
                        print("Error in sorting previous capture spots for blank...")
                    for index in range(int(numberOfCaptureSpots)):
                        for xy in range(3):
                            sumCaptureCoordinates[index][xy] = sumCaptureCoordinates[index][xy] + blankSortedCoords[index][xy]
                            
                for index in range(int(numberOfCaptureSpots)):
                    for xy in range(3):
                        avgCaptureCoordinates[index][xy] = int(round(sumCaptureCoordinates[index][xy] / len(listD4Arrays)))
                        
                singleArrayIntensities = []
                captureSpotLocations = []
                captureSpotRadii = []
                for eachAvgCircCoord in avgCaptureCoordinates:
                    xCoordCirc = eachAvgCircCoord[0]
                    yCoordCirc = eachAvgCircCoord[1]
                    radiusCirc = eachAvgCircCoord[2]
                    cv2.circle(verifyImg,(xCoordCirc,yCoordCirc),radiusCirc,(0,0,255),1) # plots all of the circles / centers
                    cv2.circle(verifyImg,(xCoordCirc,yCoordCirc),1,(0,255,0),1)
                    circIntensities = []
                    for exesInCircle in range(( xCoordCirc - radiusCirc),( xCoordCirc + radiusCirc)):
                        # for each x value in each circle
                        whyRange = np.sqrt(pow(radiusCirc,2) - pow((exesInCircle - xCoordCirc),2))
                        discreteWhyRange = int(whyRange)
                        #print("at x-pos of " + str(exesInCircle) +" with calculated y-range of " + str(discreteWhyRange))
                        for whysInCircle in range(( yCoordCirc - discreteWhyRange),( yCoordCirc + discreteWhyRange)):
                            #print("raw image intensities: " + str(imgRaw[whysInCircle,exesInCircle])+" x: "+str(exesInCircle)+" y: "+str(whysInCircle))
                            circIntensities.append(subImg[whysInCircle,exesInCircle])
                            verifyImg[whysInCircle,exesInCircle]=(255,0,0)
                    captureSpotLocations.append([xCoordCirc,yCoordCirc])
                    captureSpotRadii.append(radiusCirc)                   
                    singleArrayIntensities.append(np.mean(circIntensities))  
                    
                maxCircRadius = max(captureSpotRadii)
                
                bgMaxXCircCoordinate = max([bgXCoords[0] for bgXCoords in captureSpotLocations])
                bgMinXCircCoordinate = min([bgXCoords[0] for bgXCoords in captureSpotLocations])
                bgMaxYCircCoordinate = max([bgYCoords[1] for bgYCoords in captureSpotLocations])
                bgMinYCircCoordinate = min([bgYCoords[1] for bgYCoords in captureSpotLocations])
                bgInnerBoundary = int(round(1.2 * maxCircRadius))
                bgOuterBoundary = 3 * maxCircRadius
                
                # making the two concentric rectangles for background noise
                bgBigRectTop = bgMinYCircCoordinate - bgOuterBoundary
                bgBigRectBot = bgMaxYCircCoordinate + bgOuterBoundary
                
                bgBigRectRight = bgMaxXCircCoordinate + bgOuterBoundary
                bgBigRectLeft = bgMinXCircCoordinate - bgOuterBoundary
                
                bgSmolRectTop = bgMinYCircCoordinate - bgInnerBoundary
                bgSmolRectBot = bgMaxYCircCoordinate + bgInnerBoundary
                
                bgSmolRectRight = bgMaxXCircCoordinate + bgInnerBoundary
                bgSmolRectLeft = bgMinXCircCoordinate - bgInnerBoundary
                
                bgIntensities =[]
                for exesInBG in range(bgBigRectLeft , bgBigRectRight):
                        for whysInBG in range(bgBigRectTop , bgBigRectBot):
                            if ((whysInBG > bgSmolRectBot) or (whysInBG < bgSmolRectTop)):
                                bgIntensities.append(subImg[whysInBG,exesInBG])
                                verifyImg[whysInBG,exesInBG]=(0,0,255)
                            elif ((exesInBG > bgSmolRectRight) or (exesInBG < bgSmolRectLeft)):
                                bgIntensities.append(subImg[whysInBG,exesInBG])
                                verifyImg[whysInBG,exesInBG]=(0,0,255)
                background = np.mean(bgIntensities)
                
                cv2.imshow("verification of spot IDs in BLANK",verifyImg)
                cv2.imshow("original cropped image",subImg)
                D4ArrayEach = D4Array(IOanalyte,0,singleArrayIntensities,background,fileName,[cropXCoords,cropYCoords],[arrayCenterPosX,arrayCenterPosY],captureSpotLocations, captureSpotRadii)
                D4ArrayEach.displayAllInfo()
                print("press x if the array BLANK was properly analyzed. press b to redo")
                pressedKey = cv2.waitKey(0) 
                cv2.destroyAllWindows()
                if keyPress == ord("b"):
                    print("redoing singleArrayIDBool Loop")
                if keyPress == ord("x"):
                    print("singleArrayIDBool Loop complete")
                    singleArrayIDBool = False
                    listD4Arrays.append(D4ArrayEach)
                if keyPress == ord("q"):
                    print("debug loop exit")
                    sys.exit()
                singleArrayIDBool = False
        else:
            dist = []
            for i in circles[0,:]: # calculates the distance from each circle to the center of the array
                distanceFromCenter = np.sqrt( pow((i[0] - arrayCenterPosX),2) + pow((i[1] - arrayCenterPosY),2) )
                dist.append(distanceFromCenter) # stores those values into an array
            pointers = range(len(circles[0,:])) # makes a pointer array that matches the pointers in the "circle" list
            closestCircles = sorted(zip(dist,pointers),reverse=False)[:int(numberOfCaptureSpots)] # sorts and returns the closest 5 ([:5]) circles
            
            # looking at the capture spots
            singleArrayIntensities = []
            captureSpotLocations = []
            captureSpotRadii = []
            print("found " + str(len(closestCircles)) + " circles")
            for capturePointers in closestCircles:
                circleInformation = circles[0,capturePointers[1]] # pulls the position and radius information from the 5 closest circles
                xCoordCirc = circleInformation[0]
                yCoordCirc = circleInformation[1]
                radiusCirc = circleInformation[2] + 2
                cv2.circle(verifyImg,(xCoordCirc,yCoordCirc),radiusCirc,(0,0,255),1) # plots all of the circles / centers
                cv2.circle(verifyImg,(xCoordCirc,yCoordCirc),1,(0,255,0),1)
                # new code begin
                circIntensities = []
                for exesInCircle in range(( xCoordCirc - radiusCirc),( xCoordCirc + radiusCirc)):
                    # for each x value in each circle
                    whyRange = np.sqrt(pow(radiusCirc,2) - pow((exesInCircle - xCoordCirc),2))
                    discreteWhyRange = int(whyRange)
                    #print("at x-pos of " + str(exesInCircle) +" with calculated y-range of " + str(discreteWhyRange))
                    for whysInCircle in range(( yCoordCirc - discreteWhyRange),( yCoordCirc + discreteWhyRange)):
                        #print("raw image intensities: " + str(imgRaw[whysInCircle,exesInCircle])+" x: "+str(exesInCircle)+" y: "+str(whysInCircle))
                        circIntensities.append(subImg[whysInCircle,exesInCircle])
                        verifyImg[whysInCircle,exesInCircle]=(255,0,0)
                captureSpotLocations.append([xCoordCirc,yCoordCirc])
                captureSpotRadii.append(radiusCirc)
                singleArrayIntensities.append(np.mean(circIntensities))  
            
            # looking at the background, from two radii away from each circle
            # identify a background area by excluding the region outside of the capture spots
            # background = 69
            maxCircRadius = max(captureSpotRadii)
            bgMaxXCircCoordinate = max([bgXCoords[0] for bgXCoords in captureSpotLocations])
            bgMinXCircCoordinate = min([bgXCoords[0] for bgXCoords in captureSpotLocations])
            bgMaxYCircCoordinate = max([bgYCoords[1] for bgYCoords in captureSpotLocations])
            bgMinYCircCoordinate = min([bgYCoords[1] for bgYCoords in captureSpotLocations])
            bgInnerBoundary = int(round(1.2 * maxCircRadius))
            bgOuterBoundary = 3 * maxCircRadius
            
            # making the two concentric rectangles for background noise
            bgBigRectTop = bgMinYCircCoordinate - bgOuterBoundary
            bgBigRectBot = bgMaxYCircCoordinate + bgOuterBoundary
            
            bgBigRectRight = bgMaxXCircCoordinate + bgOuterBoundary
            bgBigRectLeft = bgMinXCircCoordinate - bgOuterBoundary
            
            bgSmolRectTop = bgMinYCircCoordinate - bgInnerBoundary
            bgSmolRectBot = bgMaxYCircCoordinate + bgInnerBoundary
            
            bgSmolRectRight = bgMaxXCircCoordinate + bgInnerBoundary
            bgSmolRectLeft = bgMinXCircCoordinate - bgInnerBoundary
            
            bgIntensities =[]
            for exesInBG in range(bgBigRectLeft , bgBigRectRight):
                    for whysInBG in range(bgBigRectTop , bgBigRectBot):
                        if ((whysInBG > bgSmolRectBot) or (whysInBG < bgSmolRectTop)):
                            bgIntensities.append(subImg[whysInBG,exesInBG])
                            verifyImg[whysInBG,exesInBG]=(0,0,255)
                        elif ((exesInBG > bgSmolRectRight) or (exesInBG < bgSmolRectLeft)):
                            bgIntensities.append(subImg[whysInBG,exesInBG])
                            verifyImg[whysInBG,exesInBG]=(0,0,255)
            background = np.mean(bgIntensities)
            
            cv2.imshow("verification of spot IDs",verifyImg)
            cv2.imshow("original cropped image",subImg)
            D4ArrayEach = D4Array(IOanalyte,d4Concentration,singleArrayIntensities,background,fileName,[cropXCoords,cropYCoords],[arrayCenterPosX,arrayCenterPosY],captureSpotLocations, captureSpotRadii)
            D4ArrayEach.displayAllInfo()
            print("press x if the array was properly analyzed. press b to redo")
            pressedKey = cv2.waitKey(0) 
            cv2.destroyAllWindows()
            if keyPress == ord("b"):
                print("redoing singleArrayIDBool Loop")
            if keyPress == ord("x"):
                print("singleArrayIDBool Loop complete")
                singleArrayIDBool = False
                d4Concentration = d4Concentration / 2.0
                listD4Arrays.append(D4ArrayEach)
            if keyPress == ord("q"):
                print("debug loop exit")
                sys.exit()
print("program terminated")
        
        
        # add in modification of number of capture spots or something, and interfacing for concentrations. 
