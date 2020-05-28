"""
This is the Development Tools Command Line Interface. It will have controls for:
1) Generating a cropped region for pattern matching an array area
2) Clicking the window displays clicked region and brightnesses
3) Clicking two points will display the distance between the two
"""

import cv2
import numpy as np
from pypylon import pylon
import easygui
import json
from scipy import ndimage
import os
import csv
import sys
import matplotlib.pyplot as plt
import scipy.optimize as optimize

imgScaleDown = 1
videoConfig = {'gain': 24,
               'expo': 1e5,
               'digshift': 0,
               'pixelform':'Mono8',
               'binval': 2}

singleConfig = {'gain': 12,
                'expo': 1e6,
                'digshift': 4,
                'pixelform':'Mono12p',
                'binval': 2}

houghParams = {"minDist": 60,
               "param1" : 200,
               "param2" : 18,
               "minRadius": 28,
               "maxRadius": 35,
               "bgRadius": 3*30}
rowTolerance = 2 * 30
forcedRadius = int(32*1.2)


arrayCoords = []
def mouseLocationClick(event, x, y, flags, param):
    """
        displays the active clicked location, and the distance between two clicked locations, specifically in pixels.
        Does not correct for downsampled images.
    """
    if event == cv2.EVENT_LBUTTONDOWN:
        print("click identified at: " + str([x,y]))
        arrayCoords.append([x,y])
    if event == cv2.EVENT_RBUTTONDOWN:
        if len(arrayCoords) > 1:
            locOne = arrayCoords.pop()
            locTwo = arrayCoords.pop()
            distance = np.linalg.norm(np.array(locOne)-np.array(locTwo))
            print("distance: " + str(distance))
        else:
            print("click 2 places first")

def cvWindow(name, image, keypressBool, delay):
    print("---Displaying: "
          +  str(name)
          + "  ---")
    cv2.namedWindow(name, cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(name, mouseLocationClick)
    cv2.setWindowProperty(name, cv2.WND_PROP_FULLSCREEN, 
                              cv2.WINDOW_FULLSCREEN)
    cv2.imshow(name, image)
    pressedKey = cv2.waitKey(delay)
    cv2.destroyAllWindows()
    if keypressBool:
        return pressedKey
        sys.exit()

def tolerantSortXYR(listInput, tolerance):
    """ 
    Will sort entries in a list into a proper order with some tolerance 
    between values. Important when 2D image locations need to be sorted
    into grid format when pixel locations are imprecise (vary by some tolerance)
    in the case of the D4 array, this tolerance is around a diameter of the capture
    spot.

    listInput = list of [x, y, radius] circle location data
    tolerance = radius of the circles (or diameter if more tolerant)

    output = sorted list by Y (with tolerance) and X (With tolerance)
    """

    sortedByWhy = sorted(listInput, key = lambda x: x[1])
    firstYCoord = sortedByWhy[0][1]
    sortedOutput = []
    yRowList = []
    for each in sortedByWhy:
        if (abs(each[1]-firstYCoord) < tolerance):
            yRowList.append(each)
        else:
            xSortedRow = sorted(yRowList, key = lambda x: x[0])
            sortedOutput = sortedOutput + xSortedRow
            yRowList = []
            firstYCoord = each[1]
            yRowList.append(each)
    xSortedRow = sorted(yRowList, key = lambda x: x[0])
    sortedOutput = sortedOutput + xSortedRow
    return sortedOutput

def outlierDetection(inputNumbers):
    """
        Outputs the list with asterisks in front of outliers. 
    """
    sortedNums = sorted(inputNumbers)
    q1, q3 = np.percentile(sortedNums, [25,75])
    iqr = q3 - q1
    lowerBound = q1 - (1.5 * iqr)
    upperBound = q3 + (1.5 * iqr)
    outputList = []
    outlierPosList = []
    removedList = []
    for iterator, eachNum in enumerate(inputNumbers):
        if (eachNum > upperBound or eachNum < lowerBound):
            outputList.append("*" + str(eachNum))
            outlierPosList.append(True)
        else:
            if eachNum < 0: # if negative, mark as outlier
                outputList.append("*" + str(eachNum))
                outlierPosList.append(True)
            else:
                outputList.append(eachNum)
                outlierPosList.append(False)
                removedList.append(eachNum)

    return outputList, outlierPosList, removedList

def optionSelect():
    clearPrompt()
    print("Welcome to the D4Scope Development Tools Command line interface")
    print("by Jason Liu, August 7, 2019")
    optionLoop = True
    while optionLoop:
        print("    ")
        print("Image Analysis: 'A'")
        print("Camera Control: 'B'")
        print("Circle Pattern Generation: 'C'")
        print("Test Pattern Matching: 'D'")
        print("Generate Figures of Merit/Dose Response: E")
        print("Exit: 'X' or 'x'")
        cmdInput = input("Type in your desired selection and press enter to start: ")
        if cmdInput == 'X'or cmdInput == 'x':
            print("exiting program")
            break
        if cmdInput == 'A':
            imageAnalysis()
        if cmdInput == 'B':
            cameraControl()
        if cmdInput == 'C':
            patternGen()
        if cmdInput == 'D':
            testPatternMatch()
        if cmdInput == 'E':
            testFiguresOfMerit()

def imageAnalysis():
    """ Image analysis downsamples the image by a factor set in the code
        this is important because sometimes the display may not be
        able to handle the full image displayed-- keep this in mind.

    """
    print("Image Analysis selected. Select and open an image")
    filePath = openImgFile()
    if filePath:
        print("Opening " + str(filePath))
        image = cv2.imread(filePath, -1)
        for each in range(imgScaleDown-1):
            image = cv2.pyrDown(image)
        print("Bitdepth: " + str(np.amax(image)))
        print("Size: " + str(np.shape(image)))
        print("Lclick to display location")
        print("Rclick to calculate distance between two previous clicks")
        print("press any key to leave image analysis")
        cvWindow(filePath.split('.')[0].split("/")[-1], image, False, 0)            
    else:
        print("Invalid File Path")

def openImgFile():
    filePath = easygui.fileopenbox()
    if filePath == None:
        return []
    #elif filePath.split('.')[-1] != ".tiff":
    #     print("only .tiff files can be opened")
    return filePath
    
def clearPrompt():
    for each in range(3):
        print("")

def buffer2image(buffer):
    converter = pylon.ImageFormatConverter()
    converter.OutputPixelFormat = pylon.PixelType_Mono8
    converter.OutputBitalignment = pylon.OutputBitAlignment_MsbAligned
    img = converter.Convert(buffer)
    image = img.GetArray()
    return image
    
def cameraControl():
    clearPrompt()
    print("Camera Control selected. Camera will connect")
    camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
    print("connected Device model: " +
          str(camera.GetDeviceInfo().GetModelName()))
    camera.Open()

    print("Live stream: 'L'; Single Capture: 'S'")
    optionSelect = input("Select Option: ")
    if optionSelect == 'L':
        liveStream(camera)
    if optionSelect == 'S':
        singleCapture(camera)

def cameraSetVals(camera, config):
    camera.PixelFormat = config['pixelform']
    camera.Gain = config['gain']
    camera.ExposureTime = config['expo']
    camera.DigitalShift = config['digshift']
    camera.BinningVertical.SetValue(config['binval'])
    camera.BinningHorizontal.SetValue(config['binval'])
    return camera
    
def liveStream(camera):
    clearPrompt()
    camera = cameraSetVals(camera, videoConfig)
    print("livestream activating. 'x' exit, 's' save last image")
    camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
    windowName = "live stream"
    cv2.namedWindow(windowName, cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(windowName, mouseLocationClick)
    while camera.IsGrabbing():
        buffer = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
        if buffer.GrabSucceeded():
            frame = buffer2image(buffer)
            cv2.imshow(windowName, frame)
            keypress = cv2.waitKey(1)
            if keypress == ord('x'):
                cv2.destroyAllWindows()
                camera.StopGrabbing()
                break
            elif keypress == ord('s'):
                cv2.destroyAllWindows()
                camera.StopGrabbing()
                saveFName = input("Filename to save as (.tiff will be added)? ")
                cv2.imwrite(str(saveFName) + ".tiff", frame)
                print(saveFName + " saved.")
                break
        buffer.Release()
    camera.Close()

def singleCapture(camera):
    clearPrompt()
    camera = cameraSetVals(camera, singleConfig)
    buffer = camera.GrabOne(int(expo * 1.1))
    if not buffer:
        raise RuntimeError("Camera failed to capture single image")
    image = buffer2image(buffer)
    cvWindow("single capture result", image, False, 0)
    saveFName = input("Filename to save as (.tiff will be added)? ")
    cv2.imwrite(str(saveFName) + ".tiff", image)
    print(saveFName + " saved.")
    camera.Close()

def patternGen():
    filePath = openImgFile()
    print("Opening " + str(filePath))
    image = cv2.imread(filePath, 0)
    # crops input image to array area, output = subImg
    print("leftclick positions (2) top left and bottom right corner bounds for the std. press d when done")
    keyPress = cvWindow('Raw Image',image, True, 0)
    if keyPress == ord('d'):
        arrayBotRigCoords = arrayCoords.pop()
        arrayTopLefCoords = arrayCoords.pop()
        print("subplot coordinates: " + str(arrayBotRigCoords)+ " " + str(arrayTopLefCoords))
    cropXCoords = sorted([arrayBotRigCoords[0],arrayTopLefCoords[0]])
    cropYCoords = sorted([arrayBotRigCoords[1],arrayTopLefCoords[1]])
    print(str(cropXCoords))
    print(str(cropYCoords))
    subImg = image[cropYCoords[0]:cropYCoords[1],cropXCoords[0]:cropXCoords[1]].copy()
    cvWindow("crop result", subImg, False, 0)

    smoothImg = cv2.medianBlur(subImg, 3)
    circlesD = cv2.HoughCircles(smoothImg,
                                cv2.HOUGH_GRADIENT,1,
                                minDist = houghParams["minDist"],
                                param1 = houghParams["param1"],
                                param2 = houghParams["param2"],
                                minRadius = houghParams["minRadius"],
                                maxRadius = houghParams["maxRadius"])
    circlesX = np.uint(np.around(circlesD))
    circleLocs = circlesX[0]

    verImg = cv2.cvtColor(subImg.copy(), cv2.COLOR_GRAY2RGB)
    idealStdImg = np.zeros(subImg.shape, dtype = np.uint8)


    for eachCircle in circleLocs:
        # force all radii to same value- 31 px - Cassio recommended
        eachCircle[2] = forcedRadius
        
        cv2.circle(verImg,
                   (eachCircle[0], eachCircle[1]),
                   eachCircle[2]+4,
                   (30,30,255),
                   3)
        cv2.circle(verImg,
                   (eachCircle[0], eachCircle[1]),
                   2,
                   (30,30,255),
                   2)
        cv2.circle(idealStdImg,
                   (eachCircle[0], eachCircle[1]),
                   eachCircle[2],
                   255,
                   3)
        cv2.circle(idealStdImg,
                   (eachCircle[0], eachCircle[1]),
                   eachCircle[2],
                   100,
                   -1)
    cvWindow("verification image", verImg, False, 0)
    cvWindow("pattern generated", idealStdImg, False, 0)

    print("pattern generated and saving now...")
    imageOutName = "standard_image.tiff"
    cv2.imwrite(imageOutName, idealStdImg)
    circleLocs = tolerantSortXYR(circleLocs.tolist(), rowTolerance)
    stdSpotDict = {"batch" : "cassio-EBOV-batch9",
                   "spot_info": circleLocs,
                   "shape": [idealStdImg.shape[0],idealStdImg.shape[1]]}
    jsonFileOutName = "standard_image-batch9-farcorners.json"
    out_file = open(jsonFileOutName, "w")
    json.dump(stdSpotDict, out_file)
    out_file.close()

def generatePatternMasks(spot_info, shape):
    """Creates masks from the pattern for later analysis of image

    Generates pattern from JSON encoded circle locations and generates masks
    for spots and bgMask. This is important for efficient quantification of
    brightness in the spots and background within the image.

    Args:
        spot_info (list): encoded circle coordinates within the pattern

        shape (list): encoded shape of the pattern, circles are relative to
            this.
    Returns:
        pattern (np array): the pattern to be found within the image

        spotsMask (np array): the masks for the spots within the image

        bgMask (np array): the masks for the background wihin the image

    """
    pattern = np.zeros(shape, dtype=np.uint8)
    spotsMask = pattern.copy()
    bgMask = 255 * np.ones(shape, dtype=np.uint8)
    bgMasksList = []

    sortedCircles = tolerantSortXYR(spot_info, rowTolerance)
    for eachCircle in sortedCircles:
        bgMaskEach = np.zeros(shape, dtype=np.uint8)
        #circlePixels = circlePixelIDSingle(eachCircle)
        # for eachPixel in circlePixels:
        #     pattern[eachPixel[1], eachPixel[0]] = 50
        #     spotsMask[eachPixel[1], eachPixel[0]] = 255
        #     bgMask[eachPixel[1], eachPixel[0]] = 0
        cv2.circle(pattern,
                   (eachCircle[0], eachCircle[1]),
                   eachCircle[2],
                   100,
                   -1)
        cv2.circle(spotsMask,
                   (eachCircle[0], eachCircle[1]),
                   eachCircle[2],
                   255,
                   -1)
        cv2.circle(bgMask,
                   (eachCircle[0], eachCircle[1]),
                   eachCircle[2]+2,
                   0,
                   -1)
        cv2.circle(bgMaskEach,
                   (eachCircle[0], eachCircle[1]),
                   round(eachCircle[2] * 1.5),
                   1,
                   -1)
        for eachCircle in spot_info:
            cv2.circle(bgMaskEach,
                       (eachCircle[0], eachCircle[1]),
                       eachCircle[2]+2,
                       0,
                       -1)
        bgMasksList.append(bgMaskEach)
    # for each in bgMasksList:
    #     cvWindow("bg mask test", each, False, 0)
    return pattern, spotsMask, bgMask, bgMasksList

def templateMatch8b(image, pattern):
    """ Core template matching algorithm to compare image to pattern

    Calculates the correlation between the pattern and the image at all points
    in 2d sliding window format weighs the correlations higher in the center of
    the image where the spots should be.

    Args:
        image (np array): the image to be processed

        pattern (np array): the pattern to be found in the image (circles)

    Returns:
        topLeftMatch (list): location of the best fit defined as the top left
            coordinate within the image

        verImg (np array): copy of the image in color with a rectangle drawn
            where the pattern was best fit

    """
    imageCols, imageRows = image.shape[::-1]
    stdCols, stdRows = pattern.shape[::-1]
    # print("pattern std shape: " + str(pattern.shape[::-1]))
    # grab dimensions of input image and convert to 8bit for manipulation
    image8b = cv2.normalize(image.copy(),
                            np.zeros(shape=(imageRows, imageCols)),
                            0, 255,
                            norm_type=cv2.NORM_MINMAX,
                            dtype=cv2.CV_8U)
    verImg = cv2.cvtColor(image8b.copy(), cv2.COLOR_GRAY2RGB)

    res = cv2.matchTemplate(image8b, pattern, cv2.TM_CCORR_NORMED)
    _, _, _, max_loc = cv2.minMaxLoc(res)
    gausCols, gausRows = res.shape[::-1]
    # print("max location REAL: " + str(max_loc))
    # print("gaus img shape: " + str(res.shape[::-1]))

    x, y = np.meshgrid(range(gausCols), range(gausRows))
    centerRow = int((imageRows - stdRows)/2) - 30
    centerCol = int((imageCols - stdCols)/2) - 50
    # print("center row and col" + " " + str(centerRow) + " " + str(centerCol))
    # draws circle where the gaussian is centered.
    cv2.circle(verImg, (centerCol, centerRow), 3, (0, 0, 255), 3)
    sigma = 800  # inverse slope-- smaller = sharper peak, larger = dull peak
    gausCenterWeight = np.exp(-((x-centerCol)**2 + (y-centerRow)**2) /
                              (2.0 * sigma**2))
    _, _, _, testCenter = cv2.minMaxLoc(gausCenterWeight)
    # print("gaussian center: " + str(testCenter))
    weightedRes = res * gausCenterWeight
    _, _, _, max_loc = cv2.minMaxLoc(weightedRes)
    # print(max_loc)  # max loc is reported as written as column,row...
    bottomRightPt = (max_loc[0] + stdCols,
                     max_loc[1] + stdRows)
    # cv2.rectangle takes in positions as (column, row)....
    cv2.rectangle(verImg,
                  max_loc,
                  bottomRightPt,
                  (0, 105, 255),
                  15)
    # cvWindow("rectangle drawn", verImg, False)
    topLeftMatch = max_loc  # col, row
    return topLeftMatch, verImg

def patternMatchEbola(image, patternDict, fileClass):
    payload = patternMatching(image, patternDict)
    # ebola tests have 4 rows, top and bottom rows of 5 are excluded from analysis-
    payload["intensities"] = payload["intensities"][4:12]
    payload["eachBackground"] = payload["eachBackground"][4:12]
    bgSubIntensities = [intens - bg for intens, bg in zip(payload["intensities"], payload["eachBackground"])]
    payload["intensities-capt"], outlierPosList, payload["removedOutliers"] = outlierDetection(bgSubIntensities)
    payload["outlier count"] = sum(outlierPosList)
    payload["avgBout"] = np.mean(payload["removedOutliers"])
    for iterator, eachBool in enumerate(outlierPosList):
        if eachBool:
            print("outlier: " + str(payload["intensities-capt"][iterator]))
    print("fileclass: " + str(fileClass))
#     eachLine = []
#     eachLine.append("file: ")
#     eachLine.append(fileClass)
#     eachLine.append("intensities: ")
#     for eachSpot in payload['intensities']:
#         eachLine.append(eachSpot)
#     eachLine.append("number of outliers")
#     eachLine.append(payload["outlier count"])
# 
#     eachLine.append("capture intensities-outliers marked")
#     for eachSpot in payload['intensities-capt']:
#         eachLine.append(eachSpot)
#     eachLine.append("average background: ")
#     eachLine.append(payload['avgbackground'])
#     eachLine.append("each background")
#     for eachBG in payload['eachBackground']:
#         eachLine.append(eachBG)
#     with open("/home/pi/Desktop/Data Output/outputData-Ebov-ein9.csv", 'a', newline='') as writeFile:
#         writer = csv.writer(writeFile)
#         writer.writerow(eachLine)
    
    return payload


def patternMatchUGH3(image, patternDict, fileClass, orientation):
    # need to flip (well, really rotate the image 180 degrees
    # probably just need to flip the first 8. ask user to set it via button.
    # b/c the spots locations are rotated for the upside down case.
    if orientation == "flipped":
        image = cv2.flip(image,-1)
    payload = patternMatching(image, patternDict)
    # ebola tests have 4 rows, top and bottom rows of 5 are excluded from analysis-
    # in the case of UGH3, after tolerant row sorting, the numbering is row wise, left to right,
    # top to bottom. Therefore, the numbering for each grouping is:
    # analyte one: 0,4,8; two: 1,5,9; three:2,6,10; four:3,7,11; five:12,13,14; six:15,16,17
    # oriented with "prongs" facing up. This actually means that
    orderingUGH3 = [0,4,8,1,5,9,2,6,10,3,7,11,12,13,14,15,16,17]

    payload["intensities"] = [payload["intensities"][i] for i in orderingUGH3]
    payload["eachBackground"] = [payload["eachBackground"][i] for i in orderingUGH3]
    
    # background subtract each feature with the paired background value
    bgSubIntensities = [intens - bg for intens, bg in zip(payload["intensities"], payload["eachBackground"])]
    # Run outlier detection, marking each of the positions depending on their outlierness. Should maybe output
    # percentage chance of outlier, or some kind of scale that we could input to make more or less tolerant
    
    payload["intensities-capt"], outlierPosList, payload["removedOutliers"] = outlierDetection(bgSubIntensities)
    # intense-capt is outlier-removed list. this won't work with multiplex... i don't think
#     payload["outlier count"] = sum(outlierPosList)
#     payload["avgBout"] = np.mean(payload["removedOutliers"])
#     for iterator, eachBool in enumerate(outlierPosList):
#         if eachBool:
#             print("outlier: " + str(payload["intensities-capt"][iterator]))
# calculate average intensity for each group.
    #payload["
    #for eachGroup in range(7):
       # iterates from 0-6
    #print("fileclass: " + str(fileClass))
    
    return payload


def patternMatching(rawImg16b, patternDict):
    """ Performs pattern matching algorithm on uploaded image

    Takes the input image to be processed and the pattern, and finds the
    circles, draws circles on a copy of the original image- on a verification
    image. Then, this program quantifies the brightness of the spot features
    and the background intensity within the pattern (not-spot areas). Spits out
    a downsized verification image (because it doesn't need to be 16 bit or as
    large as the original image to show that circles were found).

    Args:
        rawImg16b: 16 bit raw image to be pattern matched

        patternDict (dictionary): dictionary with encoded pattern

    Returns:
        payload (dictionary): contains verification image and the brightnesses
            of the spots and of the background

    """
    pattern, spotMask, bgMask, bgMasksList = generatePatternMasks(patternDict['spot_info'],
                                                                     patternDict['shape'])
    #print(patternDict['spot_info'])
    max_loc, verImg = templateMatch8b(rawImg16b, pattern)
    stdCols, stdRows = pattern.shape[::-1]

    circleLocs = patternDict['spot_info']

    subImage = rawImg16b[max_loc[1]:max_loc[1] + stdRows,
                         max_loc[0]:max_loc[0] + stdCols].copy()
    for eachCircle in circleLocs:
        drawCircle  = [0,0]
        drawCircle[0] = eachCircle[0] + max_loc[0]
        drawCircle[1] = eachCircle[1] + max_loc[1]
        cv2.circle(verImg,
                   (drawCircle[0], drawCircle[1]),
                   eachCircle[2],
                   (30, 30, 255),
                   3)
        cv2.circle(verImg,
                   (drawCircle[0], drawCircle[1]),
                   2,
                   (30, 30, 255),
                   2)
    #print(patternDict['spot_info'])
    label_im, nb_labels = ndimage.label(spotMask)
    spot_vals = ndimage.measurements.mean(subImage, label_im,
                                          range(1, nb_labels+1))
    mean_vals = ndimage.measurements.mean(subImage, label_im)
    # print(spot_vals)
    print("avg spot intensity: " + str(mean_vals))
    label_bg, bg_labels = ndimage.label(bgMask)
    mean_bg = ndimage.measurements.mean(subImage, label_bg)
    print("avg background: " + str(mean_bg))

    verImg = cv2.pyrDown(verImg)  # downsizes
    # cv2.imwrite("verification-img.tiff", verImg)

    # Find background of each Circle
    bgCalculated = []
    for eachBgMask in bgMasksList:
        # maskedSubImg = np.multiply(eachBgMask,subImage)
        # cvWindow("mult result", maskedSubImg, False, 0)
        label_bgEa, _ = ndimage.label(eachBgMask)
        mean_bgEa = ndimage.measurements.mean(subImage, label_bgEa)
        bgCalculated.append(mean_bgEa)

    payload = {"ver_Img": verImg,
               "intensities": spot_vals.tolist(),
               "avgIntens": mean_vals,
               "avgbackground": mean_bg,
               "eachBackground": bgCalculated}
    #print(patternDict['spot_info'])
    return payload

def testPatternMatch():
    patternFile = "standard_imageManual.json"
    patternDict = {}
    with open(patternFile) as json_file:
        patternDict = json.load(json_file)
    print("Pattern Dictionary Uploaded")
    cwd = os.getcwd()

    # builds list with all file names
    # fileNames = []
    # for each1Num in [5,6,7]: # number of slides
    #     for eachCNum in [1,2,3]: # column 
    #         for eachRNum in [1,2,3,4,5,6,7,8]: # row
    #             fileNameG = cwd + "/8-23/batch_5_slide_" + str(each1Num) + "_L" +  str(eachRNum) + "_C" + str(eachCNum) + ".tiff"  
    #             fileNames.append(fileNameG)
    fileNames = ["better-ebola-old_file_2.tiff"]
#     for eachType in ["liquid","closed","open"]: # column 
#         for eachNum in range(1,25): # number of slides
#             fileNameG = cwd + "/acrylic top test/Slide 8 - " + str(eachNum) + " - " + eachType + ".tiff"  
#             fileNames.append(fileNameG)

    fullData = []
    for eachImage in fileNames:
        print("processing image: " + str(eachImage))
        rawImg = cv2.imread(eachImage, -1)
        payload = patternMatching(rawImg, patternDict)
        cvWindow(eachImage, payload["ver_Img"], False, 0)
        # textOut = ("avg intens: " + str(round(payload["avgIntens"], 2)) +
        #             " . BG: " + str(round(payload["background"], 2)))
        # print(textOut)
        # print(payload["eachBackground"])
        excatenatedFileName = eachImage.split("/")[-1]
        cv2.imwrite(cwd + "/verif-FBS/" + "VER-" + excatenatedFileName, payload["ver_Img"])
        bgSubIntensities = [intens - bg for intens, bg in zip(payload["intensities"], 
                                                              payload["eachBackground"])]
        payload["intensities-capt"], outlierPosList, payload["removedOutliers"] = outlierDetection(bgSubIntensities[5:15])
        payload["outlier count"] = sum(outlierPosList)
        for iterator, eachBool in enumerate(outlierPosList):
            if eachBool:
                print("outlier: " + str(payload["intensities-capt"][iterator]))
        writeCSVData(eachImage, payload)
        fullData.append(payload["removedOutliers"])
    writeJSONData(fullData, "dataWithOutliersRemoved")
    # plot full Data here! 
    #plotData(fullData)

    print("pattern matching test complete")


def writeCSVData(fileName, dataPayload):    
    eachLine = []
    eachLine.append("file: ")
    cutFileName = fileName.split("/")[-1]
    eachLine.append(cutFileName)
    eachLine.append("intensities: ")
    for eachSpot in dataPayload['intensities']:
        eachLine.append(eachSpot)
    eachLine.append("number of outliers")
    eachLine.append(dataPayload["outlier count"])

    eachLine.append("capture intensities-outliers marked")
    for eachSpot in dataPayload['intensities-capt']:
        eachLine.append(eachSpot)
    eachLine.append("average background: ")
    eachLine.append(dataPayload['avgbackground'])
    eachLine.append("each background")
    for eachBG in dataPayload['eachBackground']:
        eachLine.append(eachBG)
    with open('outputData-Ebov-ein9.csv', 'a', newline='') as writeFile:
        writer = csv.writer(writeFile)
        writer.writerow(eachLine)


def writeJSONData(dataPayload, fileName):
    with open(fileName, 'w') as fileOutput:
        json.dump(dataPayload, fileOutput)
    print("data written to json: " + str(fileName))


def readJSONData(fileName):
    dataPayload = []
    with open(fileName) as json_file:
        dataPayload = json.load(json_file)
    return dataPayload

def testFiguresOfMerit():
    payload = readJSONData("dataWithOutliersRemoved")
    print(payload[0])
    plotData(payload)

def slideSerializer(startNumber, replicates, style):
    """ 
        there are two methods for sequential dilutions of assays developed in the lab
        one is triplicate, with each row being replicates, going down in concentration
        in each row going down. the other style is a full slide dose response, going down
        each column starting on the left and going to the right. 

        This assumes the order of the arrays is going down in rows starting in column 1, then 2, then 3.
        if this order is changed, the math for this function will need to be reworked
        
        startNumber - 0 indexed, based on numbers given from the slide
        triplicateCassio - triples going down the slide, bottom row blanks
                for multiple slides, input 0, 24, 48.... etc for each
        singlicateCassio - full dose response running down left going right, bottom R blanks
                replicates is imporatnt here when using multiple slides
        others will be added later as they appear

        will report grouped replicates and the blanks in the appropriate order.... hopefully
    """
    groups = []
    blanks = []
    if style == "triplicateCassio21pt":
        for each in range(7):
            groups.append([startNumber + each, 
                            startNumber + each + 8, 
                            startNumber + each + 16])
        blanks = [startNumber + 7, 
                  startNumber + 15,
                  startNumber + 23]

    if style == "triplicateCassio18pt":
        for each in range(6):
            groups.append([startNumber + each, 
                            startNumber + each + 8, 
                            startNumber + each + 16])
        blanks = [startNumber + 6, startNumber + 7,
                  startNumber + 14, startNumber + 15,
                  startNumber + 22, startNumber + 23]


    if style == "singlicateCassio":
        realArrays = [0,1,2,3,4,5,6,
                      8,9,10,11,12,13,14,
                      16,17,18,19,20,21,22]
        blankArrays = [7,15,23]
        for eachConc in realArrays:
            replicateList = []
            for eachReplicate in range(replicates):
                replicateList.append((eachReplicate*24)+eachConc+startNumber)
            groups.append(replicateList)
        for eachBlank in blankArrays:
            replicateList = []
            for eachReplicate in range(replicates):
                blanks = blanks + [eachBlank+startNumber + (eachReplicate*24)]
    return groups, blanks


def fiveParamSigFunction(x, lowAsymp, slope, inflection, highAsymp, symmetry):
    botExpo = (1.0 + ((x/inflection)**slope))**symmetry
    return (highAsymp + ((lowAsymp-highAsymp)/botExpo))


def backCalculateConc(brightness, lowAsymp, slope, inflection, highAsymp, symmetry):
    insideExpo = ((lowAsymp-highAsymp)/(brightness-highAsymp))**(1.0/symmetry)
    outsideExpo = inflection * ((insideExpo - 1.0)**(1.0/slope))
    return outsideExpo


def fiveParameterFit(concs, brightnesses):
    x = np.array(concs)
    y = np.array(brightnesses)
    guess = [3e2, 12, 3e2, 5e4, 2e2] #based on visual inspection
    params, params_covariance = optimize.curve_fit(fiveParamSigFunction,
                                                   x,
                                                   y,
                                                   guess)
    print("params found: " + str(params))
    print("covariance: " + str(params_covariance))
    params[0] = 3e2
    params[2] = 8e3
    return params

def plotData(dataList):
    """
     imports the serialized array positions from slideSerializer and then groups 
     replicates together, averages all spots, and standard deviations from each spot 
    """

    # for triplicate style:
    numSlides = 3
    replicateList = []
    blanksList = []
    for eachSlide in range(numSlides):
        realArrays, blankArrays = slideSerializer(eachSlide*24, 0, "triplicateCassio18pt") 
        replicateList = replicateList + realArrays
        blanksList = blanksList + blankArrays

    # for singlicate
    # replicateListSS, blanksListSS = slideSerializer(72, 3, "singlicateCassio") 

    # replicate list should have all of the array numbers in lists as organized in dataList 
    averageList = []
    stdevList = []
    for eachRepSet in replicateList: # eg [0,8,16] for tripcate, [0,24,48] for singlicate
        tempSpotAvgs = []
        for eachRep in eachRepSet: # eg 0, then 8, then 16
            tempSpotAvgs.append(np.mean(dataList[eachRep]))
        averageList.append(np.mean(tempSpotAvgs))
        stdevList.append(np.std(tempSpotAvgs))

    startConc = 500
    concs = []
    for each in range(len(averageList)):
        concs.append(startConc/(2**each))
    print("concs: ")
    print(concs)
    print("avgs: ")
    print(averageList)
    print("stds: ")
    print(stdevList)

    logisParams = fiveParameterFit(concs, averageList)
    x_min, x_max = np.amin(concs), np.amax(concs)
    xs = np.linspace(x_min, 
                     x_max,
                     10000)

    fig = plt.figure()
    ax = plt.axes()
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("concentration (log)")
    ax.set_ylabel("brightness (AU)")
    plt.errorbar(concs, averageList, yerr=stdevList)
    plt.plot(xs, fiveParamSigFunction(xs, *logisParams))
    plt.title("automated dose response generation for first 3 slides")
    plt.show()


    plt.errorbar
    blanks = []
    for each in blanksList:
        blanks.append(np.mean(dataList[each]))
    blanksAvg = np.mean(blanks)
    blanksStd = np.std(blanks)
    print("blanks Avg: " + str(blanksAvg))
    print("blanks Std: " + str(blanksStd))
    limitOfBlank = blanksAvg + (1.645 * blanksStd)
    limitOfDet = limitOfBlank + (1.645 * stdevList[-1])
    print("Limit Of Blank bright: " + str(limitOfBlank))
    print("Limit Of Detection bright: " + str(limitOfDet))

    limitOfBlankCon = backCalculateConc(limitOfBlank, *logisParams)
    limitOfDetCon = backCalculateConc(limitOfDet, *logisParams)
    print("Limit Of Blank concentration (ng/mL): " + str(limitOfBlankCon))
    print("Limit Of Detection concentration (ng/mL): " + str(limitOfDetCon))




def main():
    optionSelect()

if __name__ == '__main__':
    main()