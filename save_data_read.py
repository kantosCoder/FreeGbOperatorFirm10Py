import json
import os

CHAR_MAP = {
    0x80: "A", 0x81: "B", 0x82: "C", 0x83: "D", 0x84: "E", 0x85: "F", 0x86: "G",
    0x87: "H", 0x88: "I", 0x89: "J", 0x8A: "K", 0x8B: "L", 0x8C: "M", 0x8D: "N",
    0x8E: "O", 0x8F: "P", 0x90: "Q", 0x91: "R", 0x92: "S", 0x93: "T", 0x94: "U",
    0x95: "V", 0x96: "W", 0x97: "X", 0x98: "Y", 0x99: "Z",
    0xA0: "a", 0xA1: "b", 0xA2: "c", 0xA3: "d", 0xA4: "e", 0xA5: "f", 0xA6: "g",
    0xA7: "h", 0xA8: "i", 0xA9: "j", 0xAA: "k", 0xAB: "l", 0xAC: "m", 0xAD: "n",
    0xAE: "o", 0xAF: "p", 0xB0: "q", 0xB1: "r", 0xB2: "s", 0xB3: "t", 0xB4: "u",
    0xB5: "v", 0xB6: "w", 0xB7: "x", 0xB8: "y", 0xB9: "z",
    0x50: "", 0x7F: " "
}

def decode_text(data):
    return "".join([CHAR_MAP.get(b, "") for b in data if b != 0x50]).strip('/')

def bcd_to_int(data):
    try:
        res = "".join([hex(b)[2:].zfill(2) for b in data])
        return int(res)
    except: return 0

def parse_save(file_path):
    with open(file_path, "rb") as f:
        sav = f.read()

    # DETECCIÓN TÉCNICA
    # En Gen 2, el bloque de nombre/ID empieza en 0x2009. 
    # En Gen 1, esa zona suele ser 0x00 o datos de la Pokédex.
    id_g2 = int.from_bytes(sav[0x2009:0x200B], "big")
    first_char_g2 = sav[0x200B]
    
    # Si el ID de Gen 2 parece válido y el primer carácter del nombre está en el mapa
    if id_g2 != 0 and first_char_g2 in CHAR_MAP:
        mode = "GEN2"
    else:
        mode = "GEN1"

    if mode == "GEN1":
        return {
            "metadata": {"gen": 1, "region": "EUR/ESP"},
            "party_count": sav[0x2F2C],
            "entrenador": {
                "nombre": decode_text(sav[0x2598:0x259F]),
                "id": int.from_bytes(sav[0x2605:0x2607], "big"),
                "dinero": bcd_to_int(sav[0x25F3:0x25F6]),
                "tiempo": f"{sav[0x2CED]}h {sav[0x2CEF]}m"
            },
            "pokedex": {
                "vistos": sum(bin(b).count('1') for b in sav[0x25B6:0x25C9]),
                "atrapados": sum(bin(b).count('1') for b in sav[0x25A3:0x25B6])
            },
            "medallas": {
                "Roca": bool(sav[0x2602] & 1), "Cascada": bool(sav[0x2602] & 2),
                "Trueno": bool(sav[0x2602] & 4), "Arcoiris": bool(sav[0x2602] & 8),
                "Alma": bool(sav[0x2602] & 16), "Pantano": bool(sav[0x2602] & 32),
                "Volcan": bool(sav[0x2602] & 64), "Tierra": bool(sav[0x2602] & 128)
            }
        }
    else:
        return {
            "metadata": {"gen": 2, "region": "EUR/ESP"},
            "party_count": sav[0x281A],
            "entrenador": {
                "nombre": decode_text(sav[0x200B:0x2012]),
                "id": id_g2,
                "dinero": int.from_bytes(sav[0x23DB:0x23DE], "big"),
                "tiempo": f"{sav[0x2054]}h {sav[0x2055]}m"
            },
            "pokedex": {
                "vistos": sum(bin(b).count('1') for b in sav[0x2A6C:0x2A8C]),
                "atrapados": sum(bin(b).count('1') for b in sav[0x2A4C:0x2A6C])
            },
            "medallas": {
                "Céfiro": bool(sav[0x23E4] & 1), "Colmena": bool(sav[0x23E4] & 2),
                "Planicie": bool(sav[0x23E4] & 4), "Niebla": bool(sav[0x23E4] & 8),
                "Tormenta": bool(sav[0x23E4] & 16), "Mineral": bool(sav[0x23E4] & 32),
                "Glaciar": bool(sav[0x23E4] & 64), "Dragón": bool(sav[0x23E4] & 128)
            }
        }

if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    archivo = sys.argv[1] if len(sys.argv) > 1 else "plata.sav"
    try:
        data = parse_save(archivo)
        print(json.dumps(data, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"error": str(e)}))