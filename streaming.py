
# ## Open Api Demo
# This notebook shows a demo of the LAN-XI OpenApi interface
# We will set up a stream from the input channel and collect data for 5 seconds. The data is then shown in an FFT.
# 
# ### Concepts
# The LAN-XI OpenApi has 2 parts:
#  - The REST protocol accessed using HTTP
#  - A binary streaming protocol
# Accessing the REST protocol is done using the requests library, which makes it easy to do HTTP requests. For the streaming protocol we have written a parser using [Kaitai struct](https://kaitai.io/) which is compiled to a python library, check their documentation for compiling to other languages.
# 
# ### Opening recorder application
# The first step is opening the recorder application on the device. This is done by sending an HTTP PUT request to the device

import requests

ip = "10.100.36.78"
host = "http://" + ip

# Open recorder application
response = requests.put(host + "/rest/rec/open")

# After this you can get information about the device, this is done with a GET request, the response will contain JSON that describes the module.

# Get module info, this contains information such as type, and what kinds of functions it supports
response = requests.get(host + "/rest/rec/module/info")
module_info = response.json()
print(module_info)

# Start TEDS detection, we then check when it is done and read it out as JSON

# Detect TEDS
response = requests.post(host + "/rest/rec/channels/input/channels/transducers/detect")
while requests.get(host + "/rest/rec/onchange").json()["transducerDetectionActive"]:
    pass
# Get TEDS information
response = requests.get(host + "/rest/rec/channels/input/all/transducers")
channels = response.json()
print(channels)

# To start a stream we first need to set a configuration. In this example we create a configuration by requesting a default channel setup. We use a tiny utility function to update all values with a given key.

import utility
# Create a new recording
response = requests.put(host + "/rest/rec/create")
# Get Default setup for channels
response = requests.get(host + "/rest/rec/channels/input/default")
setup = response.json()
# Replace stream destination from default SD card to socket
utility.update_value("destinations", ["socket"], setup)
# Set enabled to false for all channels
utility.update_value("enabled", False, setup)
# Enable channels with valid TEDS
for channel_nr in range(len(channels)):
    if channels[channel_nr] != None:
        setup["channels"][channel_nr]["transducer"] = channels[channel_nr]
        setup["channels"][channel_nr]["enabled"] = True
        setup["channels"][channel_nr]["ccld"] = channels[channel_nr]["requiresCcld"]
# Remove None channels
channels = list(filter(lambda x : x != None, channels))
print(setup)
if not any(channels):
    print("No channels enabled! Did you connect a microphone?")
    print("If you have no microphones, try out the loopback example instead")
    exit()

# Next we setup the input channels for streaming. We use the input setup we got previosly.

# Create input channels with the setup
response = requests.put(host + "/rest/rec/channels/input", json = setup)
print(response.text)
# Get streaming socket
response = requests.get(host + "/rest/rec/destination/socket")
inputport = response.json()["tcpPort"]
print(response.json())
response = requests.post(host + "/rest/rec/measurements")

# We need the sample rate to correctly calculate FFTs, we get that by finding the closest sample rate in module info

# Sample rate is found by doubling the channel bandwidth and finding the closest supported sample rate
# Channel bandwidth is found in the channel setup, it is in string format, so to get it as a number replace khz with *1000 and evaluate
bandwidth = setup["channels"][0]["bandwidth"]
bandwidth = bandwidth.replace('kHz', '*1000')
bandwidth = eval(bandwidth)
supported_sample_rates = module_info["supportedSampleRates"]
# Find the sample rate with the minimum difference to bandwidth * 2
sample_rate = min(supported_sample_rates, key = lambda x:abs(x - bandwidth * 2))
print(sample_rate)

# Now we can begin streaming, we use our defined parser to parse the binary protocol
from time import gmtime
import socket
import numpy as np

from openapi.openapi_header import *
from openapi.openapi_stream import *

N = sample_rate # Collect 5 seconds of samples
array = np.array([])
interpretations = [{},{},{},{},{},{}]
# Stream and parse data
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((ip, inputport))
    while array.size <= N:
        # First get the header of the data
        data = s.recv(28)
        wstream = OpenapiHeader.from_bytes(data)
        content_length = wstream.content_length + 28
        # We use the header's content_length to collect the rest of a package
        while len(data) < content_length:
            packet = s.recv(content_length - len(data))
            data += packet
        # Here we parse the data into a StreamPackage
        package = OpenapiStream.from_bytes(data)
        if(package.header.message_type == OpenapiStream.Header.EMessageType.e_interpretation):
            for interpretation in package.content.interpretations:
                interpretations[interpretation.signal_id - 1][interpretation.descriptor_type] = interpretation.value 
        if(package.header.message_type == OpenapiStream.Header.EMessageType.e_signal_data): # If the data contains signal data
            for signal in package.content.signals: # For each signal in the package
                if signal != None:
                    if channels[signal.signal_id - 1] != None:
                        scale_factor = interpretations[signal.signal_id - 1][OpenapiStream.Interpretation.EDescriptorType.scale_factor]
                        # We append the data to an array and continue
                        array = np.append(array, np.array(list(map(lambda x: x.calc_value, signal.values))))
    response = requests.put(host + "/rest/rec/measurements/stop")
    s.close()
print(str(array.size) + " samples collected")

import utility
# Create a plot of the data
import matplotlib.pyplot as plt
win = np.hamming(len(array))
scale_factor = interpretations[0][OpenapiStream.Interpretation.EDescriptorType.scale_factor]
unit = interpretations[0][OpenapiStream.Interpretation.EDescriptorType.unit]
data = (array * scale_factor) / 2 ** 23
freq, s_dbfs = utility.dbfft(data, sample_rate, win, ref = 20 * 10**(-6)) #Reference = 20uPa
plt.plot(freq, s_dbfs)
plt.grid(True)
plt.xlabel('Frequency [Hz]')
plt.ylabel('Amplitude [dBSPL]')
plt.savefig('streaming-spectrum.png', dpi = 500)
print("Spectrum saved as streaming-spectrum.png")
