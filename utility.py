import numpy as np

def update_value(key, value, tree):
    if key in tree:
        tree[key] = value
    else:
        for subtree in tree.values():
            if isinstance(subtree, dict):
                update_value(key, value, subtree)
            if isinstance(subtree, list):
                for element in subtree:
                    update_value(key, value, element)

def time_format_to_utc(time_count, time_family):
    return 2**-(time_family.k)*3**-(time_family.l)* 5**-(time_family.m)* 7**-(time_family.n) * time_count


def dbfft(x, fs, win=None, ref=32768):
    """
    Calculate spectrum in dB scale
    Args:
        x: input signal
        fs: sampling frequency
        win: vector containing window samples (same length as x).
             If not provided, then rectangular window is used by default.
        ref: reference value used for dBFS scale. 32768 for int16 and 1 for float

    Returns:
        freq: frequency vector
        s_db: spectrum in dB scale
    """

    N = len(x)  # Length of input sequence

    if win is None:
        win = np.ones(1, N)
    if len(x) != len(win):
            raise ValueError('Signal and window must be of the same length')
    x = x * win

    # Calculate real FFT and frequency vector
    sp = np.fft.rfft(x)
    freq = np.arange((N / 2) + 1) / (float(N) / fs)

    # Scale the magnitude of FFT by window and factor of 2,
    # because we are using half of FFT spectrum.
    s_mag = np.abs(sp) * 2 / np.sum(win)

    # Convert to dBFS
    s_dbfs = 20 * np.log10(s_mag/ref)

    return freq, s_dbfs