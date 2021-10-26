from pretty_midi import *
import os
import sys
import math

buffer_size = 4096


def seconds_per_hop(sr):
    return (buffer_size // 2) / sr


def make_midi_score(pitches, durs, start_times, bpm, pgm=1, drums=False):
    """
    Turn a list of pitches and durations into MIDI.

    make_music takes a list of pitches and a list of durations
    and returns a MIDI file. The instrument program number
    as well as percussion channel can be set through the function
    arguments.

    Arguments:
      pitches (list): list of pitches.
      durs (list): list of durations (sec).
      start_times (list): List of start times (sec).
      bpm (int): BPM for output midi file (should match input audio/proj. bpm).
      pgm (int): MIDI program number.
      drums (bool): set to True for drum sounds.

    Returns:
      score (pretty_midi.Score): MIDI score.
    """

    # create a PrettyMIDI score
    score = pretty_midi.PrettyMIDI(None, 220, bpm)

    # create an instrument
    ins = pretty_midi.Instrument(program=pgm, is_drum=drums)

    # loop through list of pitches and durs
    now_time = 0
    for pitch, dur, start in zip(pitches, durs, start_times):

        # split into 12tet and microtones
        micros, twlvtet = math.modf(pitch)

        # create a new note
        note = pretty_midi.Note(velocity=100, pitch=int(twlvtet), start=start, end=start + dur)

        # and note to the instrument
        ins.notes.append(note)

        # if microtonal
        if micros != 0:
            # create a new pitch bend (4096 is a semitone in standard MIDI +/-2 pitchbend range)
            micropitch = pretty_midi.PitchBend(pitch=int(round(micros * 4096)), time=start)

            # and add it to the instrument
            ins.pitch_bends.append(micropitch)

        # advance time
        now_time += dur

    # add instrument to the score
    score.instruments.extend([ins])

    # return it
    return score


def write_score(score, name):
    file_path = 'midi_output/{0}_midi_guess.mid'.format(name)
    score.write(file_path)
    # y = score.fluidsynth(fs=44100)


'''
# David's pretty_midi example: 
# https://colab.research.google.com/drive/1SeyhtKD7TB5MecBcJc35tCJoYQnpHKMk#scrollTo=0sQvT8L5k5nw

# PrettyMidi(): __init__(midi_file=None, resolution=220, initial_tempo=120.0)
# pitches
my_pitches = [x for x in range(48)]

# durations
my_durs = [1.0/(x+1) for x in range(48)]

def make_music(pitches, durs, pgm=1, drums=False):
  """
  Turn a list of pitches and durations into MIDI.

  make_music takes a list of pitches and a list of durations
  and returns a MIDI file. The instrument program number 
  as well as percussion channel can be set through the function
  arguments.
  
  Arguments:
    pitches (list): list of pitches.
    durs (list): list of durations.
    pgm (int): MIDI program number.
    drums (bool): set to True for drum sounds.
    
  Returns:
    score (pretty_midi.Score): MIDI score.
  """

  # create a PrettyMIDI score
  score = pretty_midi.PrettyMIDI()

  # create an instrument
  ins = pretty_midi.Instrument(program=pgm, is_drum=drums)

  # loop through list of pitches and durs
  now_time = 0
  for pitch, dur in zip(pitches, durs):

    # split into 12tet and microtones
    micros, twlvtet = math.modf(pitch)

    # create a new note
    note = pretty_midi.Note(velocity=100, pitch=int(twlvtet), start=now_time, end=now_time+dur)

    # and note to the instrument
    ins.notes.append(note)

    # if microtonal
    if micros != 0:
                                            
      # create a new pitch bend (4096 is a semitone in standard MIDI +/-2 pitchbend range)
      micropitch = pretty_midi.PitchBend(pitch=int(round(micros*4096)), time=now_time)

      # and add it to the instrument
      ins.pitch_bends.append(micropitch)

    # advance time
    now_time += dur

  # add instrument to the score
  score.instruments.extend([ins])

  # return it
  return score

score.write('music2.mid')

y = score.fluidsynth(fs=44100)

# notebook function
IPython.display.Audio(y, rate=44100)


'''