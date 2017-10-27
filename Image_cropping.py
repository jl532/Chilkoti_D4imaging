# import libraries 
import numpy as np 
import cv2

arrayCoords = []
def mouseLocationClick(event,x,y,flags,param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print("click identified at: " +str([x,y]))
        arrayCoords.append([x,y])

imgRaw = cv2.imread("62,5.tif",0) # import the raw image here, currently set as "0,488.tif"


cv2.namedWindow('Raw Image') # make a named window
cv2.setMouseCallback('Raw Image', mouseLocationClick)
cv2.imshow('Raw Image',imgRaw)
keyPress = cv2.waitKey(0)
print(KeyPress)
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
cv2.imshow('subcropped image',subImg)
cv2.waitKey(0)
cv2.destroyAllWindows()

















