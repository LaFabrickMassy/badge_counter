from machine import Pin, PWM
from time import sleep
from songs import SIXTEENTH , songs
import random


DEFAULT_TEMPO = 104
# =========================
# System sounds
# =========================

hello_world = [
    ('A5', SIXTEENTH),
    ('A5', SIXTEENTH),
    ('A5', SIXTEENTH)
]

game_over = [
    ('B3', SIXTEENTH),
    ('A3', SIXTEENTH),
    ('G3', SIXTEENTH),
    ('F3', SIXTEENTH),
    ('E3', SIXTEENTH),
    ('D3', SIXTEENTH),
    ('E3', SIXTEENTH),
]
bipbip = [
    ('A5', SIXTEENTH),
    ('A5', SIXTEENTH)
]



class Buzzer:

    def __init__(self, pin):
        self.buzzer_pin = pin
        self.buzz = PWM(Pin(self.buzzer_pin))

    # =========================
    # CONVERSION NOTE -> FREQUENCE
    # =========================

    NOTE_INDEX = {
        'C': 0, # Do
        'C#': 1, # Do diese
        'D': 2, # Ré
        'D#': 3, # Mi bémol
        'E': 4, # Mi
        'F': 5, # Fa
        'F#': 6, # Fa diese
        'G': 7, # Sol
        'G#': 8, # Sol difference
        'A': 9, # La
        'A#': 10, # Si bemol
        'B': 11, # Si
    }


    def note_to_freq(self, note):
        """
        Convertit une note type 'A4' en fréquence.
        """
        if note == 'R':
            return 0

        if len(note) == 2:
            name = note[0]
            octave = int(note[1])
        else:
            name = note[:2]
            octave = int(note[2])

        midi = self.NOTE_INDEX[name] + (octave + 1) * 12
        freq = 440 * (2 ** ((midi - 69) / 12))

        return int(freq)


    def play(self, song, tempo=DEFAULT_TEMPO):
        beat_time = 60.0 / tempo

        for note, duration in song:

            note_time = beat_time * duration

            if note == 'R':
                self.buzz.duty_u16(0)
                sleep(note_time)

            else:
                freq = self.note_to_freq(note)

                self.buzz.freq(freq)

                # volume adapté buzzer passif
                self.buzz.duty_u16(2000)

                sleep(note_time * 0.95)

                # mini séparation entre notes
                self.buzz.duty_u16(0)

                sleep(note_time * 0.05)

        self.buzz.duty_u16(0)

    def play_random_song(self):
        index = random.randrange(len(songs))
        song, tempo = songs[index]
        self.play(song, tempo)




if __name__ == "__main__":
    buzzer = Buzzer(15)
    for i in range(len(songs)):
        buzzer.play_random_song()

    # for song, tempo in songs:
    #     play(song, tempo)
