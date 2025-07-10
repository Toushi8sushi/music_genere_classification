from scipy.io import wavfile
import numpy as np

# Read audio file
sample_rate, data = wavfile.read('handel.wav')

# If stereo, take one channel
if len(data.shape) > 1:
    data = data[:, 0]


# Normalize
data = data.astype(np.float64)
data = data / np.max(np.abs(data))

# Make time array
t = np.arange(len(data)) / sample_rate

import pywt
import matplotlib.pyplot as plt

# Choose wavelet and scales
wavelet = 'cmor1.5-1.0'  # Complex Morlet wavelet is good for audio
widths = np.geomspace(1, 512, num=100)  # Logarithmic spacing for scales

# Compute CWT
cwtmatr, freqs = pywt.cwt(data, widths, wavelet, sampling_period=1/sample_rate)

# Take absolute value for visualization
cwtmatr = np.abs(cwtmatr)

# Plot scaleogram
plt.figure(figsize=(12, 6))
plt.pcolormesh(t, freqs, cwtmatr, shading='gouraud')
plt.yscale('log')
plt.xlabel('Time (s)')
plt.ylabel('Frequency (Hz)')
plt.title('Continuous Wavelet Transform (Scaleogram)')
plt.colorbar(label='Magnitude')
plt.show()
