# Chilkoti_D4imaging

To set up the development environment:

the IDE/package manager I use for Python 2.7: https://www.anaconda.com/download/

make sure you use 2.7, that's the current version
compatible with the image processing OpenCV library that we use for:
-circle (microspot) detection
-pattern matching (identifying array areas)
https://www.anaconda.com/download/


once downloaded, go to the anaconda command prompt and enter the following commands:

conda install -c menpo opencv 

conda install -c conda-forge matplotlib 



These commands should download the necessary openCV library for use in my code, and the matplotlib library is great for visualizations


Use the Spyder Python IDE for development. 

Use this GitHub repository to pull code from. Make a separate branch for your own work just to be safe. I have several scripts that are being worked on in parallel.

A description of each segment of code will be added to this readme soon.

for now, the optimized hough parameters for circle detection of the Leptin D4 as run by Dan is the following:

HoughCircDP = 1 # don't mess with this for now
HoughCircMinDist = 35 # the minimum distance between centers of circles (in pixels)
HoughCircParam1 = 40 # don't mess with this for now, it's used for edge detection
HoughCircParam2 = 13 # the smaller this is, the more circles will be detected (including false ones) and the larger this is, the more circles will be potentially returned. Test this though.
HoughCircMinRadius = 11 # the lower limit of detected circle radius (in pixels). capture spots (generated from the genepix) usually are around 14-16 pixels in radius
HoughCircMaxRadius = 20 # the upper limit of detected circle radius (in pixels)

we will probably need the future users to identify the max/min radii, and the minimum distance between each array roughly, depending on the image resolution, which changes from image to image, scanner to scanner.