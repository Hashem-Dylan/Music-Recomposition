import pandas as pd
import wave
from pydub import AudioSegment
import numpy as np
import matplotlib.pyplot as plt


"""
This file contains lots of useful and well-documented utility functions to perform preprocessing on audio data.
"""

def get_wav_duration(filepath):
    """Returns the duration of a WAV audio file located at `filepath`.
    
    Args:
        filepath (str): The file path to the WAV audio file.
        
    Returns:
        float: The duration of the WAV audio file in seconds.
    """
    
    # Open the WAV audio file in read-only mode.
    with wave.open(filepath, 'r') as wav:
        
        # Get the total number of frames in the audio file.
        frames = wav.getnframes()
        
        # Get the sampling rate of the audio file.
        rate = wav.getframerate()
        
        # Calculate the duration of the audio file in seconds.
        duration = frames / float(rate)
        
        # Return the duration of the audio file.
        return duration

      
def merge_mix(mix_wav_file_path, inst_wav_file_path, inst_destination_path, mix_destination_path):
  """
  Merges a single instrument audio file with a mix audio file, exporting the resulting audio to two new WAV files.

  Args:
      mix_wav_file_path (str): The file path to the mix audio file.
      inst_wav_file_path (str): The file path to the single instrument audio file.
      inst_destination_path (str): The file path for the new single instrument audio file.
      mix_destination_path (str): The file path for the new mix audio file.
  """
  
  # Open the mix file and read its audio data
  mix = AudioSegment.from_file(mix_wav_file_path, format="wav")

  # Open the single instrument file and read its audio data
  single_inst = AudioSegment.from_file(inst_wav_file_path, format="wav")

  # Check if single_inst is shorter than mix
  if single_inst.duration_seconds < mix.duration_seconds:
      # Calculate the number of times single_inst needs to be repeated
      num_repeats = int(mix.duration_seconds / single_inst.duration_seconds) + 1

      # Concatenate single_inst with itself the necessary number of times
      repeated_single_inst = single_inst * num_repeats

      # Truncate repeated_single_inst to the duration of mix
      repeated_single_inst = repeated_single_inst[:mix.duration_seconds * 1000]

      # Export the modified single instrument audio data to a new WAV file
      repeated_single_inst.export(inst_destination_path, format="wav")

      # Overlay the repeated_single_inst audio data on top of the mix audio data
      overlayed_audio = mix.overlay(repeated_single_inst)
  else:
    # Overlay the single instrument audio data on top of the mix audio data
    overlayed_audio = mix.overlay(single_inst)

    # Make single_inst the same duration as mix
    single_inst = single_inst[:mix.duration_seconds * 1000]

    # Export the modified single instrument audio data to a new WAV file
    single_inst.export(inst_destination_path, format="wav")

  # Export the overlayed audio data to a new WAV file
  overlayed_audio.export(mix_destination_path, format="wav")
  

def visualize_audio(wav):
    """
    Visualizes an audio file by plotting its left channel signal values and a spectrogram.

    Args:
        wav (str): The path to the audio file to visualize.

    Returns:
        None
    """
    with wave.open(wav, 'rb') as wav_obj:
        # Get audio file parameters
        sample_freq, n_samples, n_channels, _, _, _ = wav_obj.getparams()

        # Calculate audio duration
        t_audio = n_samples/sample_freq

        # Read audio data as bytes and convert to numpy array
        signal_wave = wav_obj.readframes(n_samples)
        signal_array = np.frombuffer(signal_wave, dtype=np.int16)

        # Separate left and right channels from signal array
        l_channel, r_channel = signal_array[::n_channels], signal_array[1::n_channels]

        # Generate time values for plot
        times = np.linspace(0, t_audio, num=n_samples)

        # Create plot with left channel signal values
        fig, axs = plt.subplots(nrows=2, figsize=(15,10))
        axs[0].plot(times, l_channel)
        axs[0].set(title='Left Channel', ylabel='Signal Value', xlabel='Time (s)', xlim=[0, t_audio])

        # Create plot with spectrogram of left channel
        axs[1].specgram(l_channel, Fs=sample_freq, vmin=-20, vmax=50)
        axs[1].set(title='Left Channel', ylabel='Frequency (Hz)', xlabel='Time (s)', xlim=[0, t_audio])

        # Add colorbar to spectrogram plot
        fig.colorbar(axs[1].images[0])

        # Show the plot
        plt.show()

  
