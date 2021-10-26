import sys


def note_with_start_frame(note, start_frame):
    note.append(start_frame)
    return note


def note_with_end_frame(note, end_frame):
    note.append(end_frame)
    return note


# OPTIONAL PRINTS TO BE RUN AT END OF UPDATE_PITCH_TRACK
def pitch_track_prints(ended_notes, pitch_track_notes_all, pitch_track_notes_set):
    print("\nPitch Track...")
    print("This is ended_notes:", ended_notes)
    print("This is pitch_track_notes_set END:", pitch_track_notes_set)
    print("This is pitch_track_notes_all END:", pitch_track_notes_all)


# FIND ALL OLD NOTES IN PITCH TRACK LIST, RECORD AS ENDED NOTES
def find_finished_notes(new_note_preds_mps, pitch_track_notes_all, pitch_track_notes_set, frame_count):

    # INIT NOTES_TO_END RETURN LIST
    notes_to_end = []
    notes_to_remove = []

    # IF NOTE IN PREVIOUS PITCH TRACK SET NOT IN NEW_NOTE_PREDS, RECORD END OF NOTE, POP FROM PITCH TRACK
    for note in pitch_track_notes_set:
        if note not in new_note_preds_mps:
            # FIND IDX OF NOTE FOR BOTH PITCH TRACK LISTS
            note_to_end_idx = pitch_track_notes_set.index(note)
            note_to_end = pitch_track_notes_all[note_to_end_idx]

            # ADD ENDED NOTE WITH END_FRAME INFO TO NOTES_TO_END
            notes_to_remove.append(note_to_end)
            notes_to_end.append(note_with_end_frame(note_to_end, frame_count))

        else:
            continue

    # POP REMOVED NOTE(S) FROM PITCH TRACK LISTS
    for note_r in notes_to_remove:
        pitch_track_notes_all.remove(note_r)
        pitch_track_notes_set.remove(note_r[0])

    return notes_to_end


# update_pitch_track serves to verify occurrences of new notes and the ends of existing predicted notes.
# It returns notes which have ended (and end_frame) and an updated set of notes for the pitch_track list.
# frame_count arg serves to represent the current frame which has been processed.
# Notes in pitch_tracked_notes are of the form: [midi_pitch, amplitude, start_frame]
# Notes in ended_notes are of the form: [midi_pitch, amplitude, start_frame, end_frame]
def update_pitch_track(new_note_predictions, pitch_track_notes_all, pitch_track_notes_set, frame_count):

    if len(pitch_track_notes_all) > 7:
        print("EXCEEDED LENGTH")
        sys.exit(1)

    # FIND FINISHED NOTES, INIT ENDED_NOTES LIST
    new_note_preds_mps = [elem[0] for elem in new_note_predictions]
    print("\nNew note pred mps:", new_note_preds_mps)

    expired_notes = find_finished_notes(new_note_preds_mps, pitch_track_notes_all, pitch_track_notes_set, frame_count)
    ended_notes = expired_notes

    print("Current PT notes:", pitch_track_notes_set)

    for note in new_note_predictions:
        # APPEND START_FRAME TO NOTE (as list), SEARCH FOR MATCH IN PITCH_TRACKS
        _note = note_with_start_frame(list(note), frame_count)

        # IF NOTE NOT YET TRACKED: APPEND START FRAME TO NOTE, ADD TO TRACKED SET
        # ELSE: NOTE IN PITCH_TRACKED_NOTES...
        if _note[0] not in pitch_track_notes_set:
            pitch_track_notes_all.append(_note)
            pitch_track_notes_set.append(_note[0])

        else:
            index_of_note_in_pitch_track = pitch_track_notes_set.index(_note[0])
            amp_pitch_track_note = pitch_track_notes_all[index_of_note_in_pitch_track][1]

            # IF CANDIDATE NOTE LOUDER THAN SAME TRACKED NOTE: END CURRENT PT NOTE, OVERWRITE MAG, SF W/CANDIDATE INFO
            # ELSE: UPDATE NOTE IN PITCH_TRACK AMP TO HAVE NEW (SMALLER) NOTE AMP
            if amp_pitch_track_note < _note[1]:
                end_note = pitch_track_notes_all[index_of_note_in_pitch_track]
                ended_notes.append(note_with_end_frame(end_note, frame_count))

                # UPDATE NOTE (inherits mag and frame)
                pitch_track_notes_all[index_of_note_in_pitch_track] = _note

            else:
                pitch_track_notes_all[index_of_note_in_pitch_track][1] = _note[1]

    return ended_notes, pitch_track_notes_all, pitch_track_notes_set
