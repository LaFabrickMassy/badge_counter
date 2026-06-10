from machine import Pin, PWM
from time import sleep
import math

# =========================
# CONFIG
# =========================

TEMPO = 104
BUZZER_PIN = 15

# noire = 1
WHOLE = 4
HALF = 2
QUARTER = 1
EIGHTH = 0.5
SIXTEENTH = 0.25



# =========================
# CONVERSION NOTE -> FREQUENCE
# =========================

NOTE_INDEX = {
    'C': 0,
    'C#': 1,
    'D': 2,
    'D#': 3,
    'E': 4,
    'F': 5,
    'F#': 6,
    'G': 7,
    'G#': 8,
    'A': 9,
    'A#': 10,
    'B': 11
}

def note_to_freq(note):
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

    midi = NOTE_INDEX[name] + (octave + 1) * 12
    freq = 440 * (2 ** ((midi - 69) / 12))

    return int(freq)

# =========================
# MUSIQUE
# =========================

imperial_march = [

    # Intro
    ('A3', QUARTER),
    ('A3', QUARTER),
    ('A3', QUARTER),

    ('F3', EIGHTH + SIXTEENTH),
    ('C4', SIXTEENTH),

    ('A3', QUARTER),

    ('F3', EIGHTH + SIXTEENTH),
    ('C4', SIXTEENTH),

    ('A3', HALF),

    # Phrase 2
    ('E4', QUARTER),
    ('E4', QUARTER),
    ('E4', QUARTER),

    ('F4', EIGHTH + SIXTEENTH),
    ('C4', SIXTEENTH),

    ('G#3', QUARTER),

    ('F3', EIGHTH + SIXTEENTH),
    ('C4', SIXTEENTH),

    ('A3', HALF),

    # Développement
    ('A4', QUARTER),
    ('A3', EIGHTH),
    ('A3', SIXTEENTH),

    ('A4', QUARTER),
    ('G#4', EIGHTH),
    ('G4', SIXTEENTH),

    ('F#4', SIXTEENTH),
    ('F4', SIXTEENTH),
    ('F#4', EIGHTH),

    ('R', EIGHTH),

    ('A#3', EIGHTH),
    ('D#4', QUARTER),

    ('D4', EIGHTH),
    ('C#4', SIXTEENTH),
    ('C4', SIXTEENTH),

    ('B3', SIXTEENTH),
    ('C4', EIGHTH),

    ('R', EIGHTH),

    # Reprise
    ('F3', EIGHTH + SIXTEENTH),
    ('G#3', SIXTEENTH),

    ('F3', SIXTEENTH),
    ('A3', EIGHTH),

    ('C4', QUARTER),

    ('A3', EIGHTH),
    ('C4', QUARTER),

    ('E4', HALF),

]

soupe_aux_choux = [

    # Thème principal
    ('G4', 0.5),
    ('A4', 0.5),
    ('B4', 1),

    ('G4', 0.5),
    ('A4', 0.5),
    ('B4', 1),

    ('D5', 0.5),
    ('C5', 0.5),
    ('B4', 0.5),
    ('A4', 0.5),

    ('G4', 1),

    # Réponse
    ('B4', 0.5),
    ('C5', 0.5),
    ('D5', 1),

    ('B4', 0.5),
    ('C5', 0.5),
    ('D5', 1),

    ('E5', 0.5),
    ('D5', 0.5),
    ('C5', 0.5),
    ('B4', 0.5),

    ('A4', 1),

    # Variante
    ('G4', 0.5),
    ('B4', 0.5),
    ('D5', 1),

    ('C5', 0.5),
    ('B4', 0.5),
    ('A4', 1),

    ('G4', 0.5),
    ('A4', 0.5),
    ('B4', 0.5),
    ('D5', 0.5),

    ('G5', 1.5),

    # Fin
    ('D5', 0.5),
    ('B4', 0.5),
    ('G4', 2),
]

marseillaise = [

  # Allons enfants de la Patrie
    ('G4', 0.5),
    ('G4', 0.5),
    ('A4', 1),

    ('D4', 1),
    ('D4', 1),

    ('E4', 0.5),
    ('E4', 0.5),
    ('F#4', 1),

    ('G4', 2),

    # Le jour de gloire est arrivé
    ('G4', 0.5),
    ('A4', 0.5),
    ('B4', 1),

    ('B4', 1),
    ('A4', 0.5),
    ('G4', 0.5),

    ('F#4', 1),
    ('D4', 1),

    ('G4', 2),

    # Contre nous de la tyrannie
    ('B4', 0.5),
    ('B4', 0.5),
    ('C5', 1),

    ('D5', 1),
    ('B4', 1),

    ('A4', 0.5),
    ('G4', 0.5),

    ('F#4', 1),
    ('D4', 1),

    ('G4', 2),
]
# =========================
# LECTURE
# =========================

buzzer = PWM(Pin(BUZZER_PIN))

def play(song, tempo=TEMPO):
    beat_time = 60 / TEMPO

    for note, duration in song:

        note_time = beat_time * duration

        if note == 'R':
            buzzer.duty_u16(0)
            sleep(note_time)

        else:
            freq = note_to_freq(note)

            buzzer.freq(freq)

            # volume adapté buzzer passif
            buzzer.duty_u16(2000)

            sleep(note_time * 0.90)

            # mini séparation entre notes
            buzzer.duty_u16(0)

            sleep(note_time * 0.10)

    buzzer.duty_u16(0)

# =========================
# EXECUTION
# =========================

#play(imperial_march)
#play(soupe_aux_choux, tempo=132 )
play(marseillaise, tempo=120)