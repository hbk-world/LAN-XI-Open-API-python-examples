from openapi.openapi_header import *
from openapi.openapi_stream import *
import socket
import requests
import asyncio
import numpy as np
from.Buffer import DataBuffer

class streamHandler:
    def __init__(self, LanXI):
        self.lanxi = LanXI
        self.ip = LanXI.ip
        self.inputport = LanXI.inputport
        self.host = "http://" + self.ip

    def startStream(self):
        self.StreamRun = True
        asyncio.run(self.runStream())
        self.loop = asyncio.get_event_loop()
        self.loop.close()

    def stopStream(self):
        requests.put(self.host + "/rest/rec/measurements/stop")
        requests.put(self.host + "/rest/rec/finish")
        requests.put(self.host + "/rest/rec/close")
        self.StreamRun = False
        self.s.close()
 
    async def runStream(self):
        self.loop = asyncio.get_running_loop()
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
                # Here we parse the data
                package = OpenapiStream.from_bytes(data)
                self.PackageHandler(package)

    
    def PackageHandler(self, package):
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
