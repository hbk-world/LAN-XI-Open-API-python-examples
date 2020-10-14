from HelpFunctions.lanxi import LanXI
from HelpFunctions.Stream import streamHandler
from HelpFunctions.Buffer import DataBuffer
import HelpFunctions.utility as utility
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import sys

# This example shows a multithreaded script to plot realtime time and fft data for a Lan-XI module. 
# Please run this script in en  release mode. The performance in debugging mode can't be guaranteed! 

# IP of Lan-XI
Lanxi = LanXI("169.254.213.171")
Lanxi.setup_stream()

class FigHandler:
    def __init__(self):
        self.ChunkToShow = 2**12
        self.fftSize = self.ChunkToShow

        # Used to store "old" spectrums for fft averaging 
        self.old  = 0
        self.oldold = 0

        ## Figures        
        self.fig, (self.ax1, self.ax2) = plt.subplots(2,1)
        axis = np.arange(self.ChunkToShow)
        axis = np.flip(axis * -1/Lanxi.sample_rate)

        # Subplot1 Time data
        self.line1, = self.ax1.plot(axis, np.arange(self.ChunkToShow))
        self.ax1.set_xlim(left=np.min(axis), right=np.max(axis))
        self.ax1.set_ylim(bottom=-1, top=1)
        self.ax1.grid()
        self.ax1.set_xlabel("Time [s]")
        self.ax1.set_ylabel("Amplitude")

        # Subplot 2 (FFT) 
        # Calculate the frequency vector 
        freq = np.arange((self.fftSize / 2) + 1) / (float(self.fftSize) / Lanxi.sample_rate)
        self.line2, = self.ax2.plot(freq, np.arange(len(freq)))
        self.ax2.set_xlim(left = 0, right=np.max(freq))
        self.ax2.set_ylim(bottom=-20, top=130)
        self.ax2.grid()
        self.ax2.set_xlabel("Frequency [Hz]")
        self.ax2.set_ylabel("Amplitude [dB SPL]")
        # Window for the fft
        self.win = np.hamming(self.fftSize)

        # Ensures we can see all labels etc.
        self.fig.tight_layout()
        # Call StopStream() method when figure is closed
        self.fig.canvas.mpl_connect('close_event', on_close)

    def _update(self, i):
        # Update the time domain subplot1
        self.line1.set_ydata(DataBuffer.getPart(self.ChunkToShow))
        # Update the frequency domain subplot2
        freq, s_dbfs = utility.dbfft(DataBuffer.getPart(self.fftSize), Lanxi.sample_rate, self.win, ref = 20 * 10**(-6)) #Reference = 20uPa
        # Avearege the fft for a smoother plot 
        self.line2.set_ydata(s_dbfs/3 + self.old/3 + self.oldold/3)
        self.oldold = self.old
        self.old = s_dbfs


    def startAnimation(self):
        self.ani = FuncAnimation(self.fig, self._update, interval=100)

# Create the stream and Rx data
streamer = streamHandler(Lanxi)

def on_close(event):
    print('Closed Figure!')
    streamer.stopStream()
    sys.exit(0)

import threading

if __name__ == "__main__":
    try:
        threading.Thread(target=streamer.startStream).start()
        fig = FigHandler()
        fig.startAnimation()
        plt.show()

    except:
        streamer.stopStream()