# Endesga 32, the single palette for every sprite in the talk.
HEX = {
    "rust": "be4a2f", "tan": "d77643", "sand": "ead4aa", "peach": "e4a672", "clay": "b86f50",
    "brown": "733e39", "plum": "3e2731", "wine": "a22633", "red": "e43b44", "orange": "f77622",
    "gold": "feae34", "yellow": "fee761", "green": "63c74d", "leaf": "3e8948", "pine": "265c42",
    "deep": "193c3e", "navy": "124e89", "sky": "0099db", "cyan": "2ce8f5", "white": "ffffff",
    "ice": "c0cbdc", "steel": "8b9bb4", "slate": "5a6988", "dusk": "3a4466", "night": "262b44",
    "ink": "181425", "hot": "ff0044", "grape": "68386c", "pink": "b55088", "rose": "f6757a",
    "skin": "e8b796", "skin2": "c28569",
}
C = {k: tuple(int(v[i:i + 2], 16) for i in (0, 2, 4)) for k, v in HEX.items()}

def rgba(name, a=255):
    return C[name] + (a,)
