# Poly NS Tuner
**Polyphonic Pitch, Scale Detection and Pitch Tracking Tools for Python**

The Poly NS Tuner library provides the ability to parse audio (.wav) files for polyphonic pitch information, scale detection, and pitch tracked MIDI file generation within Python. 

The project utilizes Librosa, NumPy, and Fourier transforms for the DSP and pitch weighting algorithms as well as prettymidi for MIDI file generation.

Polyphonic pitch detection tools represented here follow a loose integration of the fiddle~ algorithm by Miller Puckette (UCSD), Theodore Apel (UCSD), and David Zicarelli (Cycling74).

Details of this algorithm is available in the PDF within the misc folder.
