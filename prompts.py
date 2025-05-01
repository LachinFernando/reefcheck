SLATE_IMAGE_INSTRUCTIONS = """
You will see a photo of a Reef-Check slate that lists substrate observations by distance (rows) and segment (columns). 

For every distance value that appears in the left-most column of each segment extract:

1. distance the numeric value (e.g., 0.5, 17.5).

2. label one of HC, NIA, RB, OT, SC, SP, SD, RKC, RC, SI, or no_label if the cell is crossed out / empty.

3. label_status True if the label is clearly readable or the cell is clearly crossed out; False if the text is smudged or only partially visible and you are guessing.

Key rule for “no_label”:

1. A cell that contains only one of the following counts as no_label, label_status=true

2. A single diagonal slash (/ or \)

3. A straight vertical or horizontal line

4. An “X” or check mark

5. is completely blank

Never invent a label for these cells.

Guessing rule:

Guess only if you see shapes that resemble letters/numbers of a substrate code but they are smudged or incomplete; then set label_status=false

Example:
{"distance": 0.0,  "label": "HC",       "label_status": true}
{"distance": 0.5,  "label": "no_label", "label_status": true}
{"distance": 1.0,  "label": "RB",       "label_status": false}

"""

FISH_INVERT_INSTRUCTIONS =IMAGE_INSTRUCTIONS = """
You will be shown a photo of a diver’s tally sheet. 

The sheet lists various marine species in columns and four depth‐ranges in rows:
0–20 m, 25–45 m, 50–70 m, 75–95 m.

For each depth‐range where a count is written, extract:

depth_range – one of "0–20 m", "25–45 m", "50–70 m", "75–95 m"

species – the printed column header (e.g. "Butterflyfish", "Grouper", "Crown of Thorns", "Trail urchin", etc.)

count – the number handwritten in that cell

clear – True if the numeral is crisp and unambiguous, false if it is smudged, faint, or partially erased

Rules

If a cell is blank → do not omit, but set the count as zero.

If the digit is partially visible → include it but set "clear": False.

Only use the exact species names as they appear in the header.

If the header is sub divided again, use the main header and the sub divided header as the name.
Ex:
Trash --> Fish nets
Trash --> general
Names can be: 
Trash-fishnets
Trash-general

Do not omit when the count is zero for species.
"""
