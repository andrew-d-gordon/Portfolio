# IMPORTS
from librosa import load
from poly_note_detection import *
from freq_note_conversions import *
from scale_detection import *
from pitch_tracking import *
from generating_midi_file import *
from audio_stream_test import decibelScale


# FOR GENERATION OF MIDI FILE CORRESPONDING TO RECORDED NOTE PREDICTIONS
def midi_generation(recorded_notes, recorded_notes_mp, sr, sample_name, sample_bpm):
    # Get num seconds per hop to help calculate duration
    sec_per_hop = seconds_per_hop(sr)

    # Start time calculation equal to start_time * seconds_per_hop
    recorded_notes_start_times = [note[2] * sec_per_hop for note in recorded_notes]

    # Duration calculated via samples_per_hop * num frames lasted + 1, e.g. start frame 0, end frame 2, duration of 6144
    recorded_notes_duration = [(note[3] - note[2] + 1) * sec_per_hop for note in recorded_notes]

    '''
    print("\nMidi File Generation...\n")
    print("This is sr:", sr, ", This is sec_per_hop:", sec_per_hop)
    print("This is recorded_notes:", recorded_notes)
    print("This is recorded_notes_midi_predictions:", recorded_notes_mp)
    print("This is recorded_notes_durations:", recorded_notes_duration)
    print("This is recorded_notes_start_times:", recorded_notes_start_times)
    '''

    score = make_midi_score(recorded_notes_mp, recorded_notes_duration, recorded_notes_start_times, sample_bpm)
    write_score(score, sample_name)


# RETRIEVE samples_per_buffer/REMAINING SAMPLES OF FILE FOR POLY_NOTE_TUNER
def split_wav_into_chunk(data, location_in_audio, samples_per_buffer, need_full_buffer=True):
    if len(data) - location_in_audio > samples_per_buffer:
        return data[location_in_audio:location_in_audio+samples_per_buffer]  # PROCESS ONE SECOND OF AUDIO
    else:
        if need_full_buffer:
            return np.array([])  # RETURN EMPTY LIST, DO NOT PROCESS REMAINING SAMPLES
        else:
            return data[location_in_audio:]  # PROCESS REMAINING SAMPLES/LESS THAN N SECONDS OF AUDIO


# PRINTS FOR PEAK RETRIEVAL LISTS
def peak_list_prints(current_peaks, current_peaks_midi_pitch, current_peaks_freqs, current_peaks_amps):
    print("\nHere are feature lists for unique candidate peaks...\n")
    print("Current peaks notes:", current_peaks)
    print("Current peaks midi pitches:", current_peaks_midi_pitch)
    print("Current peaks freqs:", current_peaks_freqs)
    print("Current peaks amplitudes:", current_peaks_amps)


# PREDICTS NUM_PITCHES PITCH PREDICTIONS AS MIDI_PITCH LIST
def poly_note_tuner(data, sr, num_candidates, num_pitches):
    # COMPUTE FOURIER TRANSFORM (VIA DFT)
    ft, xf, audio_len = compute_ft(data, sr)

    # CONVERT FT COMPLEX VALS TO AMP
    ft_amp = convert_magnitude(ft)

    # CANDIDATE PEAK SELECTION
    current_peaks, current_peaks_freqs, current_peaks_amps = collect_peaks(ft_amp, xf, audio_len, num_candidates)
    current_peaks_midi_pitch = [note_to_midi_pitch(elem[0], elem[1]) for elem in current_peaks]

    # OPTIONAL PRINT CURRENT CANDIDATE PEAKS (NOTES, MIDI PITCHES, FREQS, AMPS)
    # peak_list_prints(current_peaks, current_peaks_midi_pitch, current_peaks_freqs, current_peaks_amps)

    # CANDIDATE PEAK LIKELIHOOD CALCULATION AND FUNDAMENTAL SELECTION
    current_peak_weights = compute_peak_likelihood(current_peaks_midi_pitch, current_peaks_amps, num_candidates)
    fundamental_predictions = retrieve_n_best_fundamentals(current_peak_weights, current_peaks, num_pitches)
    fundamental_predictions_mp = [(note_to_midi_pitch(elem[0], elem[1]), elem[2]) for elem in fundamental_predictions]
    print("Current fundamental predictions MP:", fundamental_predictions_mp)

    return fundamental_predictions_mp

    # DURATION/END AND START NOTE MONITORING, pass most recent guessed notes list...


# main()
# Set # of candidates pitches and # of pitches to predict,
# Load sample, process samples_per_buffer samples of audio through poly_note_tuner,
# Take predictions from poly_note_tuner, pitch track them, send pitch tracked notes through to scale detection.
def main():
    # CONSTANTS
    num_pitches = 3
    num_candidates = 70
    num_pitches_for_scale_detection = 3
    min_pitch_track_frames = 4  # minimum num of frames for pitch to track

    # LOAD SAMPLE/PREP BUFFER
    sample_name = 'piano_chords_Cm_vanilla'
    sample_bpm = 135  # Ideally set to BPM of project audio is from or BPM of input audio
    data, sr = load('samples/piano_chords_Cm_vanilla.wav', sr=None)
    audio_len = len(data)
    samples_per_buffer = 4096  # optionally seconds_per_buffer * sr
    hop_size = samples_per_buffer // 2

    # LOAD FIRST BUFFER OF AUDIO TO PROCESS, INIT FRAME_COUNT
    location_in_audio = 0
    audio_to_process = split_wav_into_chunk(data, location_in_audio, samples_per_buffer)
    frame_count = 0

    # INIT PITCH TRACK BUFFERS, SCALE DETECTION OBJECT
    pitch_track_notes_all = []  # HAS PREV NOTES AS: [MP, MAG, START_FRAME]
    pitch_track_notes_set = []  # HAS PREV NOTES AS: MP
    recorded_notes = []  # HAS NOTES AS: [MP, MAG, START_FRAME, END_FRAME]
    recorded_notes_mp = []  # HAS NOTES AS: MP
    # all_note_predictions = []
    n = NoteSet()

    while audio_to_process.size > 0:

        print("\n=== FRAME ", frame_count, "===")
        # PROCESS AUDIO, MOVE AUDIO FILE LOCATION PTR AHEAD
        new_note_predictions = poly_note_tuner(audio_to_process, sr, num_candidates, num_pitches)
        location_in_audio += hop_size

        ''' #optional note_predictions list to maintain, can replace note buffer for noteSet object
        for note in new_note_predictions:
            all_note_predictions.append(note[0])
        '''

        # FORWARD PREDICTED NOTES TO PITCH TRACK MAINTENANCE
        new_pt_ended_notes, pitch_track_notes_all, pitch_track_notes_set = \
            update_pitch_track(new_note_predictions, pitch_track_notes_all, pitch_track_notes_set, frame_count)

        print("New ended notes:", new_pt_ended_notes)

        # Append new_ended_notes to recorded lists (one with mp, mag, start, and end data and one with just mp)
        for note in new_pt_ended_notes:
            # FILTER OUT NOTES WITH LESS THAN min_pitch_track_frames DURATION, ADD NOTES WITH GOOD LEN TO RECORDED_NOTES
            if note[3] - note[2] > min_pitch_track_frames:
                recorded_notes.append(note)
                recorded_notes_mp.append(note[0])

        print("\nNumber of tracked note predictions:", len(recorded_notes_mp))
        print("Current tracked note prediction history:", recorded_notes_mp)

        # RUN SCALE PREDICTION IF ENOUGH NOTES IN PITCH TRACK BUFFER
        if len(recorded_notes_mp) > num_pitches_for_scale_detection:
            n.set_note_amounts(recorded_notes_mp)
            n.find_closest_scale()
            print(n.closest_scale)

        # CHECK IF MORE AUDIO TO PROCESS, IF NOT, EXIT
        if audio_len - location_in_audio > 0:
            audio_to_process = split_wav_into_chunk(data, location_in_audio, samples_per_buffer)
            frame_count += 1
        else:
            break

    # GENERATE MIDI FILE
    midi_generation(recorded_notes, recorded_notes_mp, sr, sample_name, sample_bpm)

    print("Fin")


if __name__ == "__main__":
    main()
