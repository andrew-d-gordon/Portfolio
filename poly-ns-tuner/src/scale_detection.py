# Scale detection, weight algos

# !pip install py-midi
# import midi
import math


class NoteSet:
    def __init__(self):
        self.closest_scale = ""
        self.note_amounts = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        self.keys = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]
        self.modes = ["Major", "Minor"]

        # chromatic scales ascending, ordered by modes: major, minor, more to be added...
        # weight info: *2 for dominant, *1 for other in-scale tones, *0 for non-scale tones
        self.scale_weights = [[2, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1],
                              [1, 2, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0],
                              [0, 1, 2, 0, 1, 0, 1, 1, 0, 1, 0, 1],
                              [1, 0, 1, 2, 0, 1, 0, 1, 1, 0, 1, 0],
                              [0, 1, 0, 1, 2, 0, 1, 0, 1, 1, 0, 1],
                              [1, 0, 1, 0, 1, 2, 0, 1, 0, 1, 1, 0],
                              [0, 1, 0, 1, 0, 1, 2, 0, 1, 0, 1, 1],
                              [1, 0, 1, 0, 1, 0, 1, 2, 0, 1, 0, 1],
                              [1, 1, 0, 1, 0, 1, 0, 1, 2, 0, 1, 0],
                              [0, 1, 1, 0, 1, 0, 1, 0, 1, 2, 0, 1],
                              [1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 2, 0],
                              [0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 2],
                              [2, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0],
                              [0, 2, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1],
                              [1, 0, 2, 0, 1, 1, 0, 1, 0, 1, 1, 0],
                              [0, 1, 0, 2, 0, 1, 1, 0, 1, 0, 1, 1],
                              [1, 0, 1, 0, 2, 0, 1, 1, 0, 1, 0, 1],
                              [1, 1, 0, 1, 0, 2, 0, 1, 1, 0, 1, 0],
                              [0, 1, 1, 0, 1, 0, 2, 0, 1, 1, 0, 1],
                              [1, 0, 1, 1, 0, 1, 0, 2, 0, 1, 1, 0],
                              [0, 1, 0, 1, 1, 0, 1, 0, 2, 0, 1, 1],
                              [1, 0, 1, 0, 1, 1, 0, 1, 0, 2, 0, 1],
                              [1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 2, 0],
                              [0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 2]]

    def set_note_amounts(self, notes):
        for note in notes:
            note_mod = note % 12
            self.note_amounts[note_mod] += 1

    def set_scale_by_idx(self, scale_idx):

        # Find scale key
        scale_key_idx = scale_idx % 12
        scale_key = self.keys[scale_key_idx]

        # Find scale mode
        scale_mode_idx = math.floor(scale_idx / 12)
        scale_mode = self.modes[scale_mode_idx]

        self.closest_scale = scale_key + " " + scale_mode

    def find_closest_scale(self):
        max_weight = -1
        closest_scale_idx = -1
        candidate_weight_matrix = [[note * noteWeight for note, noteWeight in zip(self.note_amounts, self.scale_weights[i])]
                                 for i in range(len(self.scale_weights))]

        for idx in range(len(candidate_weight_matrix)):
            candidate_weight = sum(candidate_weight_matrix[idx])
            if max_weight < candidate_weight:
                max_weight = candidate_weight
                closest_scale_idx = idx

        self.set_scale_by_idx(closest_scale_idx)

        # return max_weight, closest_scale_idx

    def show_note_values(self):
        print("C: ", self.note_amounts[0])
        print("Df:", self.note_amounts[1])
        print("D: ", self.note_amounts[2])
        print("Ef:", self.note_amounts[3])
        print("E: ", self.note_amounts[4])
        print("F: ", self.note_amounts[5])
        print("Gf:", self.note_amounts[6])
        print("G: ", self.note_amounts[7])
        print("Af:", self.note_amounts[8])
        print("A: ", self.note_amounts[9])
        print("Bf:", self.note_amounts[10])
        print("B: ", self.note_amounts[11])


# example use case
# notes set could be maintained as queue of a desired size (updating in a 'sliding window' fashion)
'''
notes = [60, 60, 62, 63, 65, 67]
n = NoteSet()
n.set_note_amounts(notes)

n.find_closest_scale()
print(n.closest_scale)
'''