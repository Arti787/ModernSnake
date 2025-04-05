import numpy as np
from scipy.io.wavfile import write
import random

# Define the sampling rate
sampling_rate = 44100  # 44.1 kHz

# Define the duration of each chord in seconds
original_duration = 2
duration = original_duration / 10
pause_duration = 0.1  # Define the duration of each pause in seconds

# Define the frequencies of the notes for each chord
chords = {
    "Cm": [261.63, 311.13, 392.00],  # C minor: C, Eb, G
    "F5": [698.46, 880.00, 1046.50], # F5: F, A, C one octave higher
    "A5": [440.00, 554.37, 659.25],  # A5: A, C#, E one octave higher
    "Dm": [293.66, 349.23, 440.00],  # D minor: D, F, A
    "Em": [329.63, 392.00, 493.88],  # E minor: E, G, B
    "Gm": [392.00, 466.16, 587.33],  # G minor: G, Bb, D
    "C5": [523.25, 659.25, 783.99],  # C5: C, E, G one octave higher
}

# Define the chord progression with pauses
chord_progression = ["Cm", "F5", "A5", "Dm", None, "Em", "Gm", None, "C5"]

# Function to generate a sine wave for a given frequency and duration
def generate_sine_wave(frequency, duration, sampling_rate):
    t = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)
    wave = 0.5 * np.sin(2 * np.pi * frequency * t)
    return wave

# Function to add randomness to frequency
def add_randomness(frequency):
    random_factor = random.uniform(0.95, 1.05)
    return frequency * random_factor

# Generate the melody
melody = np.array([])

for chord in chord_progression:
    if chord is None:
        # Add a pause
        chord_wave = np.zeros(int(sampling_rate * pause_duration))
    else:
        # Generate the chord wave with randomness
        chord_wave = np.zeros(int(sampling_rate * duration))
        for frequency in chords[chord]:
            random_freq = add_randomness(frequency)
            chord_wave += generate_sine_wave(random_freq, duration, sampling_rate)
        chord_wave = chord_wave / len(chords[chord])
    melody = np.concatenate((melody, chord_wave))

# Normalize the melody to the range [-1, 1]
melody = melody / np.max(np.abs(melody))

# Save the melody as a WAV file
output_file = "melody.wav"
write(output_file, sampling_rate, melody.astype(np.float32))

print("Melody saved as melody_with_pauses_randomized.wav")
