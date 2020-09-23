import requests
import socket
from openapi.openapi_header import *
from openapi.openapi_stream import *
import asyncio
import numpy as np

class Buffer:
    def __init__(self, size):
        self.size = size
        self.data = np.zeros(self.size)

    def append(self, x):
        """
        Adds data in the front of the buffer. Discard the oldest data if buffer is full
        """
        self.data =  np.append(self.data[-(self.size - len(x)) :: ] , x)

    def get(self):
        """
        Returns the whole buffer
        """
        return self.data

    def getPart(self, start = 2**16):
        """
        Returns X points of the newest data.
        """
        return self.data[-start :: ]


# Create databuffer to store the converted package data
DataBuffer = Buffer(2**16)

class LanXI:
    def __init__(self, ip):
        self.ip = ip
        self.host = "http://" + self.ip

    def setup_stream(self):
        """
        Setup of channel 1 with a microphone
        """
        # This setup is indentical to the one found in "Streaming.py", refer to this for more info.

        # Open recorder application
        response = requests.put(self.host + "/rest/rec/open")

        # After this you can get information about the device, this is done with a GET request, the response will contain JSON that describes the module.

        # Get module info, this contains information such as type, and what kinds of functions it supports
        response = requests.get(self.host + "/rest/rec/module/info")
        module_info = response.json()
        #print(module_info)

        # Start TEDS detection, we then check when it is done and read it out as JSON

        # Detect TEDS
        response = requests.post(self.host + "/rest/rec/channels/input/all/transducers/detect")
        while requests.get(self.host + "/rest/rec/onchange").json()["transducerDetectionActive"]:
            pass
        # Get TEDS information
        response = requests.get(self.host + "/rest/rec/channels/input/all/transducers")
        channels = response.json()

        # To start a stream we first need to set a configuration. In this example we create a configuration by requesting a default channel setup. We use a tiny utility function to update all values with a given key.
        import utility
        # Create a new recording
        response = requests.put(self.host + "/rest/rec/create")
        # Get Default setup for channels
        response = requests.get(self.host + "/rest/rec/channels/input/default")
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
        self.channels = list(filter(lambda x : x != None, channels))
        #print(setup)
        if not any(self.channels):
            print("No channels enabled! Did you connect a microphone?")
            exit()

        # Next we setup the input channels for streaming. We use the input setup we got previosly.
        # Create input channels with the setup
        response = requests.put(self.host + "/rest/rec/channels/input", json = setup)
        # Get streaming socket
        response = requests.get(self.host + "/rest/rec/destination/socket")
        self.inputport = response.json()["tcpPort"]
        response = requests.post(self.host + "/rest/rec/measurements")

        # Sample rate is found by doubling the channel bandwidth and finding the closest supported sample rate
        # Channel bandwidth is found in the channel setup, it is in string format, so to get it as a number replace khz with *1000 and evaluate
        bandwidth = setup["channels"][0]["bandwidth"]
        bandwidth = bandwidth.replace('kHz', '*1000')
        bandwidth = eval(bandwidth)
        supported_sample_rates = module_info["supportedSampleRates"]
        # Find the sample rate with the minimum difference to bandwidth * 2
        sample_rate = min(supported_sample_rates, key = lambda x:abs(x - bandwidth * 2))
        #print("sample_rate: " + sample_rate)
        self.sample_rate = sample_rate


class streamHandler:
    def __init__(self, LanXI):
        self.lanxi = LanXI
        self.ip = LanXI.ip
        self.inputport = LanXI.inputport
        self.host = "http://" + self.ip

    def startStream(self):
        self.StreamRun = True
        asyncio.run(self.runStream())
        loop = asyncio.get_event_loop()
        loop.close()

    async def runStream(self):
        loop = asyncio.get_running_loop()
        self.interpretations = [{},{},{},{},{},{}]
        # Stream and parse data
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.s:
            self.s.connect((self.ip, self.inputport))
            while True and self.runStream:
            # First get the header of the data
                data = self.s.recv(28)
                wstream = OpenapiHeader.from_bytes(data)
                content_length = wstream.content_length + 28
                    # We use the header's content_length to collect the rest of a package
                while len(data) < content_length:
                    packet = self.s.recv(content_length - len(data))
                    data += packet
                    # Here we parse the data into a StreamPackage
                package = OpenapiStream.from_bytes(data)
                if(package.header.message_type == OpenapiStream.Header.EMessageType.e_interpretation):
                    for interpretation in package.content.interpretations:
                        self.interpretations[interpretation.signal_id - 1][interpretation.descriptor_type] = interpretation.value
                if(package.header.message_type == OpenapiStream.Header.EMessageType.e_signal_data): # If the data contains signal data
                    for signal in package.content.signals: # For each signal in the package
                        if signal != None:
                            if self.lanxi.channels[signal.signal_id - 1] != None:
                                scale_factor = self.interpretations[signal.signal_id - 1][OpenapiStream.Interpretation.EDescriptorType.scale_factor]
                                scale_factor = self.interpretations[0][OpenapiStream.Interpretation.EDescriptorType.scale_factor]
                                DataBuffer.append(((np.array(list(map(lambda x: x.calc_value, signal.values)))) * scale_factor) / 2 ** 23)
    
    def stopStream(self):
        requests.put(self.host + "/rest/rec/measurements/stop")
        requests.put(self.host + "/rest/rec/finish")
        requests.put(self.host + "/rest/rec/close")
        self.StreamRun = False
        self.s.close()
        
