# $${\color{red}MOVED}$$
# https://github.com/hbkworld/LAN-XI-Open-API-python-examples

# LAN-XI OpenApi python example
This repository contains examples on using python for controlling and streaming from a LAN-XI module.
 - Streaming.py - Streams data acquired by a transducer, using TEDS to scale the result
 - Loopback.py - Connects an output channel to an input channel and generates a sine wave that is streamed

A more detailed explanation on how it works can be found inside each example. Each of the examples need to know the IP address of the device to communicate with, remember to set the variable "ip" to your device IP before running the examples.

Each example generates an image containing the spectrum of the measured data.

To be able to run this you need to have python installed, and optionally Visual Studio Code.

## Setup on windows
### Install Python and Visual Studio Code 
Follow this guide from microsoft on how to install python and visual studio code. We are not using Python for Web development, so avoid following that guide.

[Python install for beginners](https://docs.microsoft.com/en-us/windows/python/beginners)

This guide will show you how to install Visual Studio Code and Python. And  then show you how to use Python in VSCode and Powershell.
You do not need to follow the "Create game" chapter at the end of the guide.

After you have followed the guide you should install the libraries from our requirements.txt.
Download this repository either [as a zip](https://github.com/hbk-world/LAN-XI-Open-API-python-examples/archive/master.zip) or by using
```
git clone https://github.com/hbk-world/LAN-XI-Open-API-python-examples.git
```
Open Powershell in the current download directory by shift-clicking in the folder.

Then use the installed pip to install the required libraries.
```
pip install -r requirements.txt
```
We use the following libraries
 - requests, for http
 - Kaitai v0.9, for parsing the stream format
 - numpy, for calculating FFTs and other DSP related functions
 - matplotlib, for plotting the data as graphs
You can also install them with pip individually if you want.

You can now run the examples with F5 in the python code in VSCode, or in powershell with e.g ```python streaming.py```.
