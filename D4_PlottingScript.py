# Script to plot a standard curve

# import libraries
import numpy as np
import matplotlib.pyplot as plt
import pylab # for sigmoid fit
from scipy.optimize import curve_fit # for sigmoid fit

# sample data (JG - AF532 test)
intensityData = [20709.20, 22413.00, 29321.20, 11907.00, 8153.00, 7987.60, 3005.00, 1370.20, 2112.40, 548.20, 563.00, 517.20, 366.00, 335.00, 271.20, 266.80, 215.60, 341.40, 266.60, 200.60, 213.40, 256.00, 288.00, 189.20]
stdevData = [100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100]
controlData = [1678.33, 3659.67, 3506.67, 1702.33, 2714.33, 2494.67, 1658.00, 4353.00, 4232.33, 1853.67, 2673.33, 2713.00, 1803.67, 2284.67, 2313.33, 1882.00, 3050.67, 2843.33, 2084.00, 1949.33, 1987.00, 1834.67, 2988.67, 2067.00]
controlStdevData = [100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100]
backgroundData = [172.00, 173.33, 198.33, 144.00, 165.33, 192.33, 196.67, 146.33, 186.67, 169.33, 159.00, 198.67, 166.00, 167.67, 175.33, 162.00, 142.33, 151.67, 173.00, 136.33, 146.33, 184.67, 145.67, 136.00]
initData = 500
wellsData = 24
blanksData = 3

# function: getDataPoints
# datapoint value = (intensity - background) / (control - background)
# datapoint stdev = sqrt(stdev^2 + controlStdev^2)
# reference for averaging stdevs: https://stats.stackexchange.com/questions/25848/how-to-sum-a-standard-deviation
def getDataPoints(intensities, intensityStdevs, controls, controlStdevs, backgrounds):
    numDataPoints = len(intensities)
    outputValues = []
    outputStdevs = []
    for i in range (0, numDataPoints):
        currValue = ( intensities[i] - backgrounds[i] ) / (controls[i] - backgrounds[i])
        currStdev = np.sqrt(np.power(intensityStdevs[i], 2) + np.power(controlStdevs[i], 2))
        outputValues.append(currValue)
        outputStdevs.append(currStdev)
    output = [outputValues, outputStdevs]
    return output

# function: getStandardConcs
# returns list of standard curve concentrations
def getStandardConcs(init, wells, blanks):
    # return variable
    stdConcs = [0]*wells
    # serial dilution
    stdConcs[0] = float(init);
    for i in range (1, wells - blanks):
        stdConcs[i] = stdConcs[i-1] / 2
    # add blanks
    for j in range (wells - blanks, wells):
        stdConcs[j] = float(0)
    return stdConcs

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

# SCRIPT:
data = getDataPoints(intensityData, stdevData, controlData, controlStdevData, backgroundData)
values = data[0] # intensities only
stdevs = data[1] # standard deviations only
concs = getStandardConcs(initData, wellsData, blanksData)
#plotStdCurve(concs, values)
fitData(concs, values, blanksData) 
lob_intensity = limitOfBlank_intensity(concs, values, stdevs, blanksData)
lod_intensity = limitOfDetection_intensity(concs, values, stdevs, blanksData, lob_intensity)