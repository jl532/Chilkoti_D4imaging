import cv2
import numpy as np
import time
from operator import itemgetter


def pullElementsFromList(datList,argument): # use this when you have a 2d list and want a specific element from each entry
    return [thatSpecificArgument[argument] for thatSpecificArgument in datList]

def mouseLocationClick(event,x,y,flags,param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print("click identified at: " +str([x,y]))
        
        
startTime = time.time()

numberOfArrays = 24
        
            
img_rgb = cv2.imread('LeptinGood.tif')
ds_img_rgb = cv2.pyrDown(img_rgb) # downsampling with gaussian subsampling 
ds_img_gray = cv2.cvtColor(ds_img_rgb , cv2.COLOR_BGR2GRAY)

template = cv2.imread('blank_ideal_3rings.tif',0)
ds_template = cv2.pyrDown(template)

w, h = ds_template.shape[::-1]
res = cv2.matchTemplate(ds_img_gray,ds_template,cv2.TM_CCORR_NORMED)  ## [y, x, correlation value]


threshold = 0.6  #previously .7
loc = np.where( res >= threshold) # [Y Y Y Y Y Y] in first row [X X X X X] in second row 

neighborRadius = max(w,h)
rawPotentialArrays = zip(*loc[::-1]) # [X, Y] many many entries


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

# verification rectangles
for eachBestCitizen in bestCitizens:
    cv2.rectangle( ds_img_rgb , (eachBestCitizen[1][0], eachBestCitizen[1][1]), (eachBestCitizen[1][0] + w, eachBestCitizen[1][1] + h), (0,0,255),2)

finishedTime = time.time() - startTime

print("time to process the full image: " + str(finishedTime))
cv2.imwrite('identified shit in red.tif', ds_img_rgb)
cv2.namedWindow('identified shit in red',cv2.WINDOW_NORMAL) 
cv2.setMouseCallback('identified shit in red', mouseLocationClick)
cv2.imshow('identified shit in red',ds_img_rgb) # show the raw image with superimposed identified circles
cv2.waitKey(0) # press any key on the image window to close and terminate the program
cv2.destroyAllWindows()