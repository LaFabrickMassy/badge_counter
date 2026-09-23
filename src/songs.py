

    # 'C': 0, # Do
    # 'C#': 1, # Do diese
    # 'D': 2, # Ré
    # 'D#': 3, # Mi bémol
    # 'E': 4, # Mi
    # 'F': 5, # Fa
    # 'F#': 6, # Fa diese
    # 'G': 7, # Sol
    # 'G#': 8, # Sol difference
    # 'A': 9, # La
    # 'A#': 10, # Si bemol
    # 'B': 11, # Si



# noire = 1
WHOLE = 4 # Ronde
HALF = 2 # Blanche
QUARTER = 1 # Noire
EIGHTH = 0.5 # Croche
SIXTEENTH = 0.25 # Double croche

Blanche = 2
Noire = 1
Croche_pointee = 0.75
Croche = 0.5
Double_croche = 0.25

cancan = [
    ('D4', 1),  # re
    ('D4', 1), # re
    ('E4', 0.5), # mi
    ('G4', 0.5), # sol
    ('F4', 0.5), #fa
    ('E4', 0.5), #mi
    ('A4', 1), # la
    ('A4', 1), # la

    ('A4', 0.5), # la
    ('B4', 0.5), # si
    ('F4', 0.5), # fa
    ('G4', 0.5), # sol
    ('E4', 1), # mi
    ('E4', 1), # mi
]

le_bon_la_brute = [
    ('E4', 0.25),
    ('A4', 0.25),
    ('E4', 0.25),
    ('A4', 0.25),
    ('E4', 2),
    ('R', 0.5),
    ('C4', 1),
    ('D4', 1),
    ('A3', 2),
    ('R', 0.5),
    ('E4', 0.25),
    ('A4', 0.25),
    ('E4', 0.25),
    ('A4', 0.25),
    ('E4', 2),
    ('R', 0.5),
    ('C4', 1),
    ('D4', 1),
    ('G4', 2),
]

marseillaise = [
    ('C4', 0.25), # Al-
    ('C4', 0.37), # -lons
    ('C4', 0.25), # en-
    ('G4', 1), # -fants
    ('G4', 1), # de
    ('A5', 1), # la
    ('A5', 1), # pa-
    ('D5', 1.5), # -tri-
    ('B4', 0.5),#('A#4', 0.5), # -i-
    ('G4', 0.5) # -e
]

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
]

songs = [ # (song, tempo)
    (cancan, 180),
    (le_bon_la_brute, 104),
    (marseillaise, 104),
    (imperial_march, 104)
    ]