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

The full script that is only optimized for a really good image of Leptin is: 

