"""
    This will be the final User interface for the Einstein D4Scope. Specifically suited for touchscreen use (480x 320)
    Will have the following functions:
    1) Upload Circle dictionary
    2) Live Feed to Align Sample, then click feed to take picture (3088 x 2064)
    3) picture will auto-save, and display circle matches to verify fit
    4) will display avg brightnesses and background brightness
    5) unique ID assigned to image and saved (based on date/time) as tiff
    6) Outlier Detection
"""
import os, sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (QApplication, 
                            QMainWindow, 
                            QVBoxLayout, 
                            QFileDialog)
from scipy import ndimage
import cv2
import numpy as np
import time
import pyqtgraph as pg
from pypylon import pylon
from einsteinEncodedUI import Ui_MainWindow
import easygui
import json
import csv
import os
from gpiozero import LED as pinMode
from time import sleep
from backend_einsteinUI import (cvWindow,
                         openImgFile,
                         cameraSetVals,
                         patternMatching,
                         generatePatternMasks,
                        patternMatchEbola)

# will store these configs in a json file later for modification
# Configs for video streaming, will be optimizable later
imgScaleDown = 2
videoConfig = {'gain': 32,
               'expo': 10e4,
               'digshift': 4,
               'pixelform':'Mono8',
               'binval': 2}

singleConfig = {'gain': 24,  # change this for gain if you need- 
                'expo': 1e6,
                'digshift': 4,
                'pixelform':'Mono12p',
                'binval': 1}

class ColorImageView(pg.ImageView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lut = None
    def updateImage(self, autoHistogramRange = True):
        super().updateImage(autoHistogramRange)
        self.getImageItem().setLookupTable(self.lut)

def cvWindow(name, image, keypressBool, delay):
    print("---Displaying: "
          +  str(name)
          + "  ---")
    cv2.namedWindow(name, cv2.WINDOW_NORMAL)
    cv2.imshow(name, image)
    pressedKey = cv2.waitKey(delay)
    cv2.destroyAllWindows()
    if keypressBool:
        return pressedKey
        sys.exit()

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        
        self.videoOn = False 
        self.videoToggleButton.clicked.connect(self.videoToggleUI)
        self.shotButton.clicked.connect(self.singleCaptureUI)

        self.actionOpen_Image.triggered.connect(self.openImage)
        self.actionOpen_Circle_Dictionary.triggered.connect(self.circleDictUpload)
        self.actionOpenData.triggered.connect(self.dataFileOpen)
        self.actionExit.triggered.connect(self.exitProgram)
        
        self.actionGainUp.triggered.connect(self.vidGainUp)
        self.actionGainDown.triggered.connect(self.vidGainDown)
        
        self.actionon.triggered.connect(self.autoOn)
        self.actionoff.triggered.connect(self.autoOff)
        self.actionNewSlide.triggered.connect(self.startNewSlide)
        self.arrayCount = 1
        self.slideNumber = 1
    
        self.plotting_widget.setLayout(QVBoxLayout())
        self.im_widget = pg.ImageView(self)
        self.im_widget.ui.histogram.hide()
        self.im_widget.ui.roiBtn.hide()
        self.im_widget.ui.menuBtn.hide()
        self.plotting_widget.layout().addWidget(self.im_widget)
        self.im_widget.show()

        # automatically adds in encoded standard image
        patternFile = "/home/pi/Desktop/code/standard_image-batch7-Ebov.json"
        #patternFile = "/home/pi/Desktop/code/standard_image-batch9-farcorners.json"
        self.patternDict = {}
        with open(patternFile) as json_file:
            self.patternDict = json.load(json_file)
        print("Pattern Dictionary Active")
        self.circleDictUploaded = True  
        self.autoCircles = False

        # set up video buffer to image converter for 8 bit
        self.vidConverter = pylon.ImageFormatConverter()
        self.vidConverter.OutputPixelFormat = pylon.PixelType_Mono8
        self.vidConverter.OutputBitalignment = pylon.OutputBitAlignment_MsbAligned

        # set up single capture buffer to image converter for 12 bit

        self.singleConverter = pylon.ImageFormatConverter()
        self.singleConverter.OutputPixelFormat = pylon.PixelType_Mono16
        self.singleConverter.OutputBitalignment = pylon.OutputBitAlignment_MsbAligned

        # set up laser pin control
        self.laser = pinMode(26)
        
    def vidGainUp(self):
        gain = self.camera.Gain.GetValue()
        if gain > 35:
            self.editTextBox("Gain cannot go higher!")
        else:
            self.camera.Gain = gain + 4
            self.editTextBox("Gain set to: " + str(gain + 4))
    
    def vidGainDown(self):
        gain = self.camera.Gain.GetValue()
        if gain < 4:
            self.editTextBox("Gain cannot go lower!")
        else:
            self.camera.Gain = gain - 4
            self.editTextBox("Gain set to: " + str(gain - 4))


    def editTextBox(self, text):
        self.label.setText(QtWidgets.QApplication.translate("", text, None, -1))

    def startNewSlide(self):
        self.slideNumber = self.slideNumber + 1
        self.arrayCount = 1
        self.editTextBox("New Slide: " + str(self.slideNumber))

    def videoToggleUI(self):
        if self.videoOn:
            # print("live stream off, toggle live stream button to turn on")
            self.editTextBox("live stream off, toggle Live stream button to turn on")
            self.videoOn = False
            self.camera.Close()
            self.laser.off()
        else:
            self.editTextBox("live stream on, toggle Live stream button to turn off")
            self.videoOn = True
            self.camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
            self.camera.Open()
            self.laser.on()
            #sleep(0.5) #no sleep needed
            self.camera = cameraSetVals(self.camera, videoConfig)
            self.camera.Width = 900
            self.camera.Height = 600
            
            self.camera.OffsetX = 340 # needs to be a multiple of 4 i think...
            self.camera.OffsetY = 350 
            self.camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
            while self.camera.IsGrabbing():
                self.buffer = self.camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
                if self.buffer.GrabSucceeded():
                    frame = self.vidConverter.Convert(self.buffer).GetArray()
#                     frameDown = cv2.pyrDown(frame)
                    if self.autoCircles:
                        self.autoAnalyze(frame, "video")
                    #crosshairs
                    frame = cv2.line(frame, (450, 220), (450, 380), 254, thickness = 1) # addressed as row, column
                    frame = cv2.line(frame, (380, 300), (520, 300), 254, thickness = 1) # vertical
                    frame = cv2.line(frame, (450, 270), (450, 330), 254, thickness = 3) # thicker center
                    frame = cv2.line(frame, (420, 300), (480, 300), 254, thickness = 3) # thicker center
                    
                    # aligning assist for pos control spots, two horizontal lines.
                    frame = frame = cv2.line(frame, (20, 160), (880, 160), 254, thickness = 2) # addressed as row, column
                    frame = frame = cv2.line(frame, (20, 425), (800, 425), 254, thickness = 2)
                    self.im_widget.setImage(np.transpose(frame))
                self.buffer.Release()
                QApplication.processEvents()
            self.camera.Close()

    def singleCaptureUI(self): # add laser control when testing on rpi
        self.editTextBox("single capture starting/processing.")
        if hasattr(self, "camera"): # deactivate if video is interrupted with single capture
            self.camera.Close()
            self.videoOn = False
            pass
        self.camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
        self.camera.Open()
        self.camera = cameraSetVals(self.camera, singleConfig)
        self.laser.on()
        sleep(0.5)
        buffer = self.camera.GrabOne(int(singleConfig['expo']*1.1))
        if not buffer:
            raise RuntimeError("Camera failed to capture single image")
        image = self.singleConverter.Convert(buffer).GetArray()
        image = (image * 16)
        image = cv2.medianBlur(image, 3)
        self.laser.off()
        self.im_widget.setImage(np.transpose(image))
        buffer.Release()
        self.camera.Close()
        # save image with what is in the lineEdit box, unique number increasing
        if self.autoCircles:
            self.autoAnalyze(image, "single")
        else:
            self.editTextBox("saved slide" + str(self.slideNumber) + " ar" + str(self.arrayCount))
        self.saveImage(image)
    
    def autoAnalyze(self, image, typeOfAnalysis):
        if typeOfAnalysis == "single":
            fileName = self.lineEdit.text() + "Slide_" +  str(self.slideNumber) + "_array" + str(self.arrayCount)
            payload = patternMatchEbola(image, self.patternDict, fileName)
            #verImg = cv2.cvtColor(payload["ver_Img"].copy(), cv2.COLOR_BGR2GRAY)
            self.im_widget.setImage(np.transpose(cv2.cvtColor(payload["ver_Img"], cv2.COLOR_BGR2GRAY)))
            fileName = fileName + "_Verification_file.tiff"
            cwd = os.getcwd()
            cv2.imwrite("/home/pi/Desktop/Data Output/" + fileName, payload["ver_Img"])
            #self.editTextBox(fileName + " has been saved")
            #textOut = ("intens: " + str(payload["avgBout"]))
            self.editTextBox("saved slide" + str(self.slideNumber) + " ar" + str(self.arrayCount)+ "|| intens: " + str(payload["avgBout"]))
            #self.editTextBox(textOut)
            #print(textOut)
            pass
        if typeOfAnalysis == "video":
            pass
    
    def saveImage(self, image): # saves image!
        cwd = os.getcwd()
        fileName = self.lineEdit.text()
        fileName = fileName + "Slide_" +  str(self.slideNumber) + "_array" + str(self.arrayCount) + ".tiff"
        cv2.imwrite("/home/pi/Desktop/nCoV_Scans/" + fileName, image)
        self.arrayCount = self.arrayCount + 1
        #self.editTextBox(fileName + " has been saved")
        return fileName

    
    def openImage(self):
        filePath = openImgFile()
        self.editTextBox("opening " + str(filePath))
        image = cv2.imread(filePath, -1)        
        self.im_widget.setImage(np.transpose(image))
        self.editTextBox("image opened")


    def circleDictUpload(self):
        """ 
            currently takes in the template image that needs to be matched.
            implementing json later...
        """
        filePath = openImgFile()
        self.editTextBox("opening " + str(filePath))
        #self.template = cv2.imread(filePath, 0)        
        #self.displayImageFullscreen(self.template)
        self.patternDict = {}
        with open(filePath) as json_file:
            self.patternDict = json.load(json_file)
        self.editTextBox("circle dictionary uploaded")
        self.circleDictUploaded = True

    def autoOn(self):
        self.autoCircles = True
        self.editTextBox("automatic circle finding activated")
#         self.payload = patternMatching(self.image, self.patternDict)
#         #cvWindow("test", payload["ver_Img"], False)
#         verImg = cv2.cvtColor(payload["ver_Img"].copy(), cv2.COLOR_BGR2GRAY)
#         self.displayImageInWindow(verImg)
#         textOut = ("avg intens: " + str(round(payload["avgIntens"], 2)) +
#                    " . BG: " + str(round(payload["background"], 2)))
#         self.editTextBox(textOut)
    
    def autoOff(self):
        self.autoCircles = False
        self.editTextBox("automatic circle finding DEactivated")

    def analyzeImage(self):
        self.editTextBox("Function not yet implemented")

    def dataFileOpen(self):
        self.editTextBox("Select Data File for output")
        filePath = openImgFile()
        
    def exitProgram(self):
        sys.exit()    
        
def main():
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()
    frame = MainWindow()
    frame.show()
    app.exec_()
    app.quit()

if __name__ == '__main__':
    main()

