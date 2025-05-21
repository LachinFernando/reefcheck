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

segment details:
segment one - has 40 number sets with values start from 0 and end from 19.5 incremented by 0.5. [0, 0.5, 1.0, ..., 18, 18.5, 19.0, 19.5]
segment two - has 40 number sets with values start from 25 and end from 44.5 incremented by 0.5. [25, 25.5, 26.0, ..., 43, 43.5, 44.0, 44.5]
segment three - has 40 number sets with values start from 50 and end from 69.5 incremented by 0.5. [50, 50.5, 51.0, ..., 68, 68.5, 69.0, 69.5]
segment four - has 40 number sets with values start from 75 and end from 94.5 incremented by 0.5. [75, 75.5, 76.0, ..., 93, 93.5, 94.0, 94.5]

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

Input image: Image of the recordings

Rotate the slate 90 degrees clockwise so headers read left-to-right.

Depth rows (exact text): 0–20 m (distance_one) · 25–45 m (distance_two) · 50–70 m (distance_three) · 75–95 m (distance_four)

For every species name below, inspect the cell at each depth and report:  
• count – integer you see (digits are normally circled)  
• *_clear – true if the numeral is crisp; false if faint, smudged or partly erased  
• If the cell is totally blank write count 0 and *_clear true.

Treat a circled “S” as the digit 5.

Return **one JSON object** that matches the Pydantic model shown after
the species list.  Do not add any other keys or text.

Species list (verbatim)  
Fish – Butterflyfish · Sweetlips · Snapper · Barramundi cod · Humphead wrasse · Bumphead parrotfish · Other parrotfish · Moray eel · Grouper 30-40 cm · Grouper 40-50 cm · Grouper 50-60 cm · Grouper > 60 cm  
Invertebrates – Banded coral shrimp · Diadema urchin · Pencil urchin · Collector urchin · Sea cucumber · Crown of Thorns · Triton · Lobster · Giant Clam < 10 cm · Giant Clam 10-20 cm · Giant Clam 20-30 cm · Giant Clam 30-40 cm · Giant Clam 40-50 cm · Giant Clam > 50 cm  
Impacts – Coral Damage – boat/anchor · Coral Damage – dynamite · Coral Damage – other · Trash – fish nets · Trash – general · Bleaching % population · Bleaching % colony  
Coral Disease – Black Band % colonies · White band % colonies  
Rare Animals – Shark · Turtle · Manta · Other
"""
