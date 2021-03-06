# general libraries for opencv, numpy, csv manipulation, etc.
import numpy as np 
import cv2
import sys
import csv
from operator import itemgetter

# libraries for file I/O
from tkinter import filedialog
from tkinter import messagebox
import tkinter as tk
root = tk.Tk()
root.overrideredirect(1)
root.withdraw()

# for plotting
import matplotlib.pyplot as plt
import pylab # for sigmoid fit
from scipy.optimize import curve_fit # for sigmoid fit

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
#        print("this circle is being analyzed in circle pixel ID")
#        print(eachCircle)
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

def blankOrLowArrayCheck(listOfD4arrays,capCircles, numberOfCaptSpots): # oinly necessary if you use this with multiple arrays in one image.
    capLocations = []
    #print(capCircles)
    if len(listOfD4arrays) > 0:
        for whatever in range(numberOfCaptSpots):
            capLocations.append([0,0,0])
        #print(capLocations)
            
        for eachPreviousD4Array in listOfD4arrays:
            previousCaptCircles = eachPreviousD4Array.returnCaptureCircleInfo()
            circleIterator = 0
            for eachCapCircle in previousCaptCircles:
                #print(eachCapCircle[0])
                #print(circleIterator)
                capLocations[circleIterator][0] = capLocations[circleIterator][0] + eachCapCircle[0]
                capLocations[circleIterator][1] = capLocations[circleIterator][1] + eachCapCircle[1]
                capLocations[circleIterator][2] = capLocations[circleIterator][2] + eachCapCircle[2]
                circleIterator = circleIterator + 1
                
        for eachIterator in range(len(capLocations)):
            capLocations[eachIterator][0] = capLocations[eachIterator][0] / len(listOfD4arrays)
            capLocations[eachIterator][1] = capLocations[eachIterator][1] / len(listOfD4arrays)
            capLocations[eachIterator][2] = capLocations[eachIterator][2] / len(listOfD4arrays)
            
#        print('average of past capture spots here:')
#        print(capLocations)
        circleIterator = 0
        maxRadius = 20
        for eachLocation in capLocations:            
            if (abs(eachLocation[0] - capCircles[circleIterator][0]) > maxRadius) or (abs(eachLocation[1] - capCircles[circleIterator][1]) > maxRadius):
                capCircles[circleIterator] = eachLocation
#                print("blank detected, replacing ")
#                print(capCircles[circleIterator])
#                print("with")
#                print(eachLocation)
            circleIterator = circleIterator + 1
        return capCircles
    else:
        return capCircles
    
class D4Array:
    "a class that carries all of the information needed for each Array"
    def __init__(self,analyte,concentration,intensities,background,d4fileName,d4coordinates,centerOfArrayCoordinates, captCircles):
        self.analyte = analyte
        self.concentration = concentration
        self.intensities = intensities
        self.stdev = np.std(intensities)
        self.background = background
        self.d4fileName = d4fileName
        self.d4coordinates = d4coordinates
        self.centerOfArrayCoordinates = centerOfArrayCoordinates
        self.captCircles = captCircles
        
    def displayAllInfo(self):
        print(self.analyte + " " + str(self.concentration)+ " " +str(self.intensities)+ " " +str(self.stdev)+ " "+str(self.background))
        print(self.d4fileName+" "+str(self.d4coordinates)+" "+str(self.centerOfArrayCoordinates)+" "+str(self.captCircles))
    def returnCaptureCircleInfo(self):
        return self.captCircles

def fileNameFinder(directory):
    locationOfLastSlash = 0
    for iterChars in range(len(directory)):
        if directory[iterChars] == "/":
            locationOfLastSlash = iterChars
    return directory[(locationOfLastSlash+1):]
                
# ask for file to select, use Tkinter. ## need to figure out how to make windows go in front.
startBool = messagebox.askyesno("D4 Automated Analysis Algorithm start page (Jason Liu Dec 2017)",
                                "Would you like to analyze your D4 Images?")
while(startBool):
    print("select image file you would like to analyze")
    file_path = str(filedialog.askopenfilename())
    file_name = fileNameFinder(file_path)
    imgRaw = cv2.imread(str(file_name),0)
    # verify file identity
    cv2.namedWindow('Image: ' + file_name + 
                    ' uploaded to program', cv2.WINDOW_NORMAL) # make a named window'
    cv2.imshow('Image: ' + file_name +  
               ' uploaded to program',imgRaw)
    imageCheckBool = messagebox.askyesno("D4 A3 Verify Image",
                                    "Is this the correct image?")
    cv2.destroyAllWindows()
    if imageCheckBool:
        print("File selected. Proceeding to Analysis")
        startBool = False
    else:
        endBool = messagebox.askyesno("D4 A3 Continue?",
                                      "Do you wish to continue running program?")
        if not endBool:
            sys.exit("Program quit by user.")    

# User sees image and uses UI to select if it is a single array, or multiple arrays.
cv2.namedWindow(file_name, cv2.WINDOW_NORMAL)
cv2.imshow(file_name,imgRaw)

# use command line interface to ask user what kind of image this is:
analysisTypeBool = True
while(analysisTypeBool):
    analysisType = input("What kind of image is this? for one array, enter 'one array'. for multiple arrays, enter 'multiple arrays'.")
    if analysisType == "one array":
        print("one array analysis mode selected")
        analysisTypeBool = False
    elif analysisType == "multiple arrays":
        print("multiple arrays selected")
        analysisTypeBool = False
    else:
        print("input not recognized. please try again.")
        
cv2.destroyAllWindows()
print("beginning analysis selected...")


#


# user parameters to be used later:
userPromptBool = True
while(userPromptBool):
    IOanalyte = input("What is the analyte being used in this assay? Just add more in with / separating each:  ")
    numberOfArrays = input("How many total Arrays are there in this image?  ")
    startingConcentration = input("What is the starting concentration in ng/mL?   ")
    numberOfCaptureSpots = input("How many capture spots are there in each Array?  ")
    numberOfBlanks = input("How many blanks are there in this image?  ")
    
    print(IOanalyte + " is/are the selected analyte for this slide")
    print(str(numberOfArrays) + " is the number of arrays on this image")
    print(str(startingConcentration) + " is the starting concentration.")
    print(str(numberOfCaptureSpots) + " is the number of capture spots in each Array")
        
    promptVerify = input("verify the information you have entered. enter x to continue, b to redo, q to exit program:   ")
    if promptVerify == 'x':
        userPromptBool = False
    if promptVerify == 'b':
        userPromptBool = True
    if promptVerify == 'q':
        sys.exit()
    
imgRaw_downSampled_gray = cv2.pyrDown(imgRaw) # image is already grey!

template = cv2.imread('blank_ideal_3rings.tif',0)
template_downSampled = cv2.pyrDown(template)
width_template, height_template = template_downSampled.shape[::-1]
res = cv2.matchTemplate(imgRaw_downSampled_gray,template_downSampled,cv2.TM_CCORR_NORMED)

threshold = 0.6
locations = np.where( res >= threshold)
neighborRadius = max(width_template, height_template)
rawPotentialArrays = zip(*locations[::-1])

stagedManyArrays = []
arrayIterator = 0
bestCitizens = []
for each in range(numberOfArrays):
    bestCitizens.append([0,[0,0],0])
for eachRawPotArray in rawPotentialArrays:
    if len(stagedManyArrays) == 0:
        stagedManyArrays.append([ res[eachRawPotArray[1],eachRawPotArray[0]], [eachRawPotArray[0],eachRawPotArray[1]] , arrayIterator])
        bestCitizens[arrayIterator] = ([ res[eachRawPotArray[1],eachRawPotArray[0]], [eachRawPotArray[0],eachRawPotArray[1]] , arrayIterator])
    else:
        storageSpace = []
        for eachStagedArray in stagedManyArrays:
            if ((eachRawPotArray[0] < eachStagedArray[1][0] + neighborRadius) and (eachRawPotArray[0] > eachStagedArray[1][0] - neighborRadius)):
                if ((eachRawPotArray[1] < eachStagedArray[1][1] + neighborRadius) and (eachRawPotArray[1] > eachStagedArray[1][1] - neighborRadius)):
                    #print(str([eachRawPotArray[0],eachRawPotArray[1]]) + " close to " + str([eachStagedArray[1][0], eachStagedArray[1][1]]))
                    storageSpace = [res[eachRawPotArray[1],eachRawPotArray[0]], [eachRawPotArray[0],eachRawPotArray[1]], eachStagedArray[2]]
                    if (res[eachRawPotArray[1],eachRawPotArray[0]] > bestCitizens[eachStagedArray[2]][0]):
                        bestCitizens[eachStagedArray[2]] = [ res[eachRawPotArray[1],eachRawPotArray[0]], [eachRawPotArray[0],eachRawPotArray[1]] , eachStagedArray[2]]
        if (len(storageSpace) ==  0 ):
            #print(str([eachRawPotArray[0],eachRawPotArray[1]]) + " NOT close to " + str([eachStagedArray[1][0], eachStagedArray[1][1]]))
            arrayIterator = arrayIterator + 1
            storageSpace= [res[eachRawPotArray[1],eachRawPotArray[0]], [eachRawPotArray[0],eachRawPotArray[1]], arrayIterator]
            if (res[eachRawPotArray[1],eachRawPotArray[0]] > bestCitizens[arrayIterator][0]):
                bestCitizens[arrayIterator] = [ res[eachRawPotArray[1],eachRawPotArray[0]], [eachRawPotArray[0],eachRawPotArray[1]] , arrayIterator]
        stagedManyArrays.append(storageSpace)
        
detectedNumberOfArrays = len(bestCitizens)

if (numberOfArrays == detectedNumberOfArrays):
    print("----------- we are in business. all arrays found.----------------------")
    
#upsample locations 2x for each best citizen
    
arrayIterator = 0
for eachCitizen in bestCitizens:
    bestCitizens[arrayIterator][1][0] = eachCitizen[1][0] * 2
    bestCitizens[arrayIterator][1][1] = eachCitizen[1][1] * 2
    arrayIterator = arrayIterator + 1

listD4Arrays = []
d4Concentration = float(startingConcentration)

for eachArray in bestCitizens:
    subImg = imgRaw[eachArray[1][1]:(eachArray[1][1] + (height_template*2)) , eachArray[1][0]:(eachArray[1][0] + (width_template*2))]
    singleArrayIDBool = True
    while singleArrayIDBool:
        verifyImg_circles = cv2.cvtColor(subImg,cv2.COLOR_GRAY2BGR)
        verifyImg_pixels = verifyImg_circles.copy()
        smoothedCroppedIMG = cv2.medianBlur(subImg,3)
        circles = cv2.HoughCircles(smoothedCroppedIMG,cv2.cv.CV_HOUGH_GRADIENT,1,40,param1=30,param2=16,minRadius=11,maxRadius=20)
        circles = np.uint16(np.around(circles))
        arrayCenterPosX = int(np.mean(circles[0,:][:,0]))
        arrayCenterPosY = int(np.mean(circles[0,:][:,1]))
        circleCount = len(circles[0,:][:,1])
        for i in circles[0,:]:
            cv2.circle(verifyImg_circles,(i[0],i[1]),i[2],(0,255,0),1) # draw the outer circle
            cv2.circle(verifyImg_circles,(i[0],i[1]),2,(0,0,255),2) # draw the center of the circle\
        cv2.circle(verifyImg_circles,(arrayCenterPosX,arrayCenterPosY),5,(255,0,0),3) # draws a marker at the center of the array
        
        captureCircles = circleDistanceSorter(circles,[arrayCenterPosX,arrayCenterPosY],numberOfCaptureSpots)            
        
        captureCircles = blankOrLowArrayCheck(listD4Arrays, captureCircles, numberOfCaptureSpots)
            
        capturePixels = circlePixelID(captureCircles)
        verifyImg_pixels[pullElementsFromList(capturePixels,1),pullElementsFromList(capturePixels,0)] = [0,0,255]
        
        backgroundPixels = rectangleBackgroundAreaDefiner(capturePixels)
        verifyImg_pixels[pullElementsFromList(backgroundPixels,1),pullElementsFromList(backgroundPixels,0)] = [255,0,0]
        
        avgBackground = np.mean(subImg[pullElementsFromList(backgroundPixels,1),pullElementsFromList(backgroundPixels,0)])
        
        
        captureIntensities = []
        for each in capturePixels:
            captureIntensities.append([each[3], subImg[each[1],each[0]]])
        
        separatedCaptureIntensities = [[] * 1 for i in range(numberOfCaptureSpots)]
        for eachIntensity in captureIntensities:
            separatedCaptureIntensities[int(eachIntensity[0])].append(eachIntensity[1])
        
        avgCircleIntensities = []
        for eachCircle in separatedCaptureIntensities:
            avgCircleIntensities.append(np.mean(eachCircle))
            
        d4ArrayEach = D4Array(IOanalyte, d4Concentration, avgCircleIntensities, avgBackground, inputFileName, eachArray[1], [arrayCenterPosX, arrayCenterPosY], captureCircles)
            
#        detectionCircles = circleDistanceSorter(circles,[arrayCenterPosX,arrayCenterPosY])[numberOfCaptureSpots:]
#        verifyImg_pixels[pullElementsFromList(detectionPixels,1),pullElementsFromList(detectionPixels,0)] = [0,255,0]
        
#        cv2.imshow('Raw Image',subImg) # show the original raw image
#        cv2.imshow('Raw Image with Superimposed, identified circles', verifyImg_circles) # show the raw image with superimposed identified circles
#        cv2.imshow('Verification image',verifyImg_pixels)
#        pressedKey = cv2.waitKey(0) 
#        cv2.destroyAllWindows()
#        if pressedKey == ord("b"):
#            print("redoing singleArrayIDBool Loop")
#        if pressedKey == ord("x"):
#            print("singleArrayIDBool Loop complete " + str(len(listD4Arrays)))
        singleArrayIDBool = False
        d4Concentration = d4Concentration / 2.0
        listD4Arrays.append(d4ArrayEach)
#        if pressedKey == ord("q"):
#            print("debug loop exit")
#            sys.exit()

# now do CSV output and plotting....
with open(outputCSVFileName, 'wb' ) as outputCSV:
    csvWriter = csv.writer(outputCSV, delimiter= ",", quotechar = "|" , quoting = csv.QUOTE_MINIMAL)
    for eachArray in listD4Arrays:
        csvWriter.writerow( eachArray.intensities + [eachArray.analyte] + [eachArray.concentration] +  [np.mean(eachArray.intensities)] + [eachArray.stdev] ) 
        
# plot this stuff
# pull avg intensity data out of listD4Arrays
intensityData = []
stdevData = []
backgroundData = []
arrayConcentrations = []
for eachArray in listD4Arrays:
    intensityData.append(np.mean(eachArray.intensities))
    stdevData.append(eachArray.stdev)
    backgroundData.append(eachArray.background)
    arrayConcentrations.append(eachArray.concentration)

def plotStdCurve(x, y):
    plt.loglog(x, y, 'ko')
    return

# used by fitData function
def sigmoid(x, x0, k):
     y = 1 / (1 + np.exp(-k*(x-x0)))
     return y

# used by fitData function
# normalizes an array to range from 0 to 1
def normalize(array):
    mindata = min(array)
    maxdata = max(array)
    for el in np.nditer(array, op_flags=['readwrite']):
        el[...] = (el - mindata) / (maxdata - mindata)
    return array

# sample script @ https://gist.github.com/andrewgiessel/5684769
def fitData(x, y, blanks):
    xdata = np.log10(x[0:(len(x)-blanks)])
    ydata = np.log10(y[0:(len(y)-blanks)])
    
    # normalize ydata range (0 to 1)
    ydata = normalize(ydata)
    
    popt, pcov = curve_fit(sigmoid, xdata, ydata)
    #print popt
    
    x = np.linspace(min(xdata), max(xdata), 50)
    y = sigmoid(x, *popt)
    
    pylab.plot(xdata, ydata, 'o', label='data')
    pylab.plot(x,y, label='fit')
    pylab.ylim(-0.05, 1.05)
    pylab.legend(loc='best')
    pylab.title(IOanalyte + " data plot with 3-factor sigmoid fit")
    pylab.xlabel("log10'd concentrations in ng/mL")
    pylab.ylabel("normalized intensities")
    pylab.savefig("testOutputPlotted.png")
    pylab.show()
    
    return

def limitOfBlank_intensity(concs, intensities, stdevs, numBlanks):
    # Armbruster & Pry formula: LoB = meanBlank + 1.645(sdBlank)
    blankIntensities = intensities[len(intensities)-numBlanks : len(intensities)]
    meanBlank = np.mean(blankIntensities)
    sdBlank = np.std(blankIntensities)
    lob_intensity = meanBlank + 1.645*sdBlank
    return lob_intensity

def limitOfDetection_intensity(concs, intensities, stdevs, numBlanks, lob_intensity):
    # Arumbruster & Pry formula: LoD = LoB + 1.645(SD low concentration sample)
    lowconcIntensities = intensities[len(intensities)-numBlanks-3 : len(intensities)] # -3 term indicates that lowest concentration samples considered are the three samples nearest to the blanks
    lod_intensity = lob_intensity + 1.645*(np.std(lowconcIntensities))
    return lod_intensity

#plotStdCurve(concs, values)
fitData(arrayConcentrations, intensityData, numberOfBlanks) 
#lob_intensity = limitOfBlank_intensity(arrayConcentrations, intensityData, stdevData, stdevData)
#lod_intensity = limitOfDetection_intensity(arrayConcentrations, intensityData, stdevData, numberOfBlanks, lob_intensity)
        
print("program terminated")

        
        
    
    
    
    
