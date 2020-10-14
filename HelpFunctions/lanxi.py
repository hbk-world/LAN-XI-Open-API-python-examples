import requests
from.import utility as utility

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
        requests.put(self.host + "/rest/rec/open")
        # Get information about the device and configure 
        self.GetTeds()
        self.ConfigureStream()
        self.GetFs()


    def GetTeds(self):
        # Start TEDS detection, we then check when it is done and read it out as JSON
        # Detect TEDS
        self.response = requests.post(self.host + "/rest/rec/channels/input/all/transducers/detect")
        while requests.get(self.host + "/rest/rec/onchange").json()["transducerDetectionActive"]:
            pass
        # Get TEDS information
        self.response = requests.get(self.host + "/rest/rec/channels/input/all/transducers")
        self.channels = self.response.json()


    def ConfigureStream(self):
        # To start a stream we first need to set a configuration. In this example we create a configuration by requesting a default channel setup. We use a tiny utility function to update all values with a given key.
        # Create a new recording
        self.response = requests.put(self.host + "/rest/rec/create")
        # Get Default setup for channels
        self.response = requests.get(self.host + "/rest/rec/channels/input/default")
        self.setup = self.response.json()
        # Replace stream destination from default SD card to socket
        utility.update_value("destinations", ["socket"], self.setup)
        # Set enabled to false for all channels
        utility.update_value("enabled", False, self.setup)
        # Enable channels with valid TEDS
        for channel_nr in range(len(self.channels)):
            if self.channels[channel_nr] != None:
                self.setup["channels"][channel_nr]["transducer"] = self.channels[channel_nr]
                self.setup["channels"][channel_nr]["enabled"] = True
                self.setup["channels"][channel_nr]["ccld"] = self.channels[channel_nr]["requiresCcld"]
        # Remove None channels
        self.channels = list(filter(lambda x : x != None, self.channels))
        if not any(self.channels):
            print("No channels enabled! Did you connect a microphone?")
            exit()
        # Next we setup the input channels for streaming. We use the input setup we got previosly.
        # Create input channels with the setup

        self.response = requests.put(self.host + "/rest/rec/channels/input", json = self.setup)
        # Get streaming socket
        self.response = requests.get(self.host + "/rest/rec/destination/socket")
        self.inputport = self.response.json()["tcpPort"]
        self.response = requests.post(self.host + "/rest/rec/measurements")


    def GetFs(self):
        # Sample rate is found by doubling the channel bandwidth and finding the closest supported sample rate
        # Channel bandwidth is found in the channel setup, it is in string format, so to get it as a number replace khz with *1000 and evaluate
        bandwidth = self.setup["channels"][0]["bandwidth"]
        bandwidth = bandwidth.replace('kHz', '*1000')
        bandwidth = eval(bandwidth)
        self.response = requests.get(self.host + "/rest/rec/module/info")
        module_info = self.response.json()
        supported_sample_rates = module_info["supportedSampleRates"]
        # Find the sample rate with the minimum difference to bandwidth * 2
        self.sample_rate = min(supported_sample_rates, key = lambda x:abs(x - bandwidth * 2))