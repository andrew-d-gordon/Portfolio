from math import log2, pow

# CONSTANTS
A4 = 440
C0 = A4 * pow(2, -4.75)
key_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
octaves = list(range(11))
notes_in_octave = len(key_names)


def freq_to_note(freq):
    if freq == 0:
        return 'C', -1
    h = round(12 * log2(freq / C0))  # can also use log(x)/log(2) to replace log2
    octave = h // 12
    n = h % 12
    return key_names[n], octave


def note_to_midi_pitch(note:str, octave:int):

    midi_pitch_val = key_names.index(note)
    midi_pitch_val += (notes_in_octave * octave)

    return midi_pitch_val
