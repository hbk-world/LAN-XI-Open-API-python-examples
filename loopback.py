# ## Open Api Demo
# This example shows a demo of the LAN-XI OpenApi interface
# In this demo we will set up a generator on output channel 0, the output should be connected to input channel 0.
# We then set up a stream from the input channel and collect data for 5 seconds. The data is then shown in an FFT.
# 
# ### Physical setup
# This example can be done on a LAN-XI 3050 generator module, with a connection between connector 1 and 5.
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

ip = "10.100.36.196"
host = "http://" + ip

# Open recorder application, enable TEDS detection at startup
response = requests.put(host + "/rest/rec/open")

# After this you can get information about the device, this is done with a GET request, the response will contain JSON that describes the module.

# Get module info, this contains information such as type, and what kinds of functions it supports
response = requests.get(host + "/rest/rec/module/info")
module_info = response.json()
print(module_info)

# To start a stream we first need to set a configuration. In this example we create a configuration by requesting a default channel setup. We use a tiny utility function to update all values with a given key.

import HelpFunctions.utility as utility
# Create a new recording
response = requests.put(host + "/rest/rec/create")
# Get Default setup for channels
response = requests.get(host + "/rest/rec/channels/input/default")
setup = response.json()
# Replace stream destination from default SD card to socket
utility.update_value("destinations", ["socket"], setup)
# Set enabled to false for all channels
utility.update_value("enabled", False, setup)
# Enable channel 0, which should be connected to generator 0
setup["channels"][0]["enabled"] = True
print(setup)

# The next step is to configurate the output channels. Again this is done by taking the default configuration and changing the parameters. You can also use a predefined generator setup, saved in a file, to 
# Prepare generator
response = requests.put(host + "/rest/rec/generator/prepare", 
    json = {"outputs": [{"number": 1}]} )
# Get the default generator setup
response = requests.get(host + "/rest/rec/generator/output/default")
generator_setup = response.json()
# Change the frequency to 1khz
generator_setup["outputs"][0]["gain"] = 1
generator_setup["outputs"][0]["inputs"][0]["frequency"] = 20000.0
generator_setup["outputs"][0]["inputs"][0]["gain"] = 0.75
generator_setup["outputs"][0]["inputs"][0]["signalType"] = "sine"
print(generator_setup)

response = requests.put(host + "/rest/rec/generator/output", json = generator_setup)
response = requests.put(host + "/rest/rec/generator/start", 
    json = {"outputs": [{"number": 1}]} )

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

N = sample_rate*5 # Collect 5 seconds of samples
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
        # Here we parse the data into a StreamPackage
        package = OpenapiStream.from_bytes(data)
        if(package.header.message_type == OpenapiStream.Header.EMessageType.e_signal_data): # If the data contains signal data
            for signal in package.content.signals: # For each signal in the package
                if signal != None:
                    # Sensitivity can not come from TEDS, set it to a default value
                    sensitivity = 1
                    # We append the data to an array and continue
                    array = np.append(array, np.array(list(map(lambda x: x.calc_value * sensitivity, signal.values))))
    response = requests.put(host + "/rest/rec/measurements/stop")
    response = requests.put(host + "/rest/rec/generator/stop")
    s.close()
print(str(array.size) + " samples collected")



# Create a plot of the data
import matplotlib.pyplot as plt
win = np.hamming(len(array))
scale_factor = interpretations[0][OpenapiStream.Interpretation.EDescriptorType.scale_factor]
unit = interpretations[0][OpenapiStream.Interpretation.EDescriptorType.unit]
data = (array * scale_factor) / 2 ** 23
freq, s_dbfs = utility.dbfft(data, sample_rate, win, ref = 1) #Reference = 1V
plt.plot(freq, s_dbfs)
plt.grid(True)
plt.xlabel('Frequency [Hz]')
plt.ylabel('Amplitude [dBV]')
plt.savefig('loopback-spectrum.png', dpi = 500)
print("Spectrum saved as loopback-spectrum.png")
