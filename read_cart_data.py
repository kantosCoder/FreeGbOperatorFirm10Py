import serial
import time
import json
import os

DB_JSON = 'gb_gbc_roms_info.json'

# PKMN GAME SPECIFICATION

PKM_RED = ["0x384A", "0x1810"]
PKM_BLUE = ["0xF49D", "0x14D7"]
PKM_YELLOW = ["0x5637"]
PKM_SILVER = ["0x064B"]
PKM_GOLD = ["0x9353"]
PKM_CRYSTAL = ["0x42F4"]

def identificar_por_global_checksum(puerto='COM8'):
    if not os.path.exists(DB_JSON):
        print(f"[r]Error: No se encuentra {DB_JSON}[/red]")
        return

    try:
        print("\033[1m"+ "\033[32m" + r"""
 __                   __               _________            .___             _______________   ________  ________
|  | _______    _____/  |_  ____  _____\_   ___ \  ____   __| _/___________  \_____  \   _  \  \_____  \/  _____/
|  |/ /\__  \  /    \   __\/  _ \/  ___/    \  \/ /  _ \ / __ |/ __ \_  __ \  /  ____/  /_\  \  /  ____/   __  \ 
|    <  / __ \|   |  \  | (  <_> )___ \\     \___(  <_> ) /_/ \  ___/|  | \/ /       \  \_/   \/       \  |__\  \
|__|_ \(____  /___|  /__|  \____/____  >\______  /\____/\____ |\___  >__|    \_______ \_____  /\_______ \_____  /
     \/     \/     \/                \/        \/            \/    \/                \/     \/         \/     \/ 
        """ + "\033[0m")
        print("\033[1m"+ "\033[32m" + "EPILOGUE GB OPERATOR - POKEMON MULTIGEN CART INFO READER (FW10)\n" + "\033[0m")
        
        
        #GB Operator data comm USB serialpy library
        
        ser = serial.Serial(puerto, 115200, timeout=1)
        ser.write(bytes.fromhex("04" + "00"*59 + "b3556b81")) # Power order (USB)
        time.sleep(0.5)
        ser.write(bytes.fromhex("15" + "00"*59 + "2FB93C26")) # Info order (USB)
        time.sleep(0.8)
        
        raw = bytearray()
        while ser.in_waiting > 0:
            raw.extend(ser.read(ser.in_waiting))
        ser.close()

        if len(raw) < 1024:
            print("Error de comunicación.")
            return

        """ Global Checksum en Bloque 1 de datos (offset 512), 
         (específicamente en los bytes 18 y 19)."""
        bloque = raw[512:1024]
        g_chk = bloque[18:20].hex().upper() # Captura "14D7"
        target = f"0x{g_chk}"

        print(f"\nBuscando Checksum Global: {target}")

        #STEP 2. JSON DB SEARCH
        with open(DB_JSON, 'r', encoding='utf-8') as f:
            db = json.load(f)
        nombre_cart = "UNKNOWN"
        target_chk = target
        if target_chk in PKM_RED: nombre_cart = "ROJO"
        elif target_chk in PKM_BLUE: nombre_cart = "AZUL"
        elif target_chk in PKM_YELLOW: nombre_cart = "AMARILLO"
        elif target_chk in PKM_GOLD: nombre_cart = "ORO"
        elif target_chk in PKM_SILVER: nombre_cart = "PLATA"
        elif target_chk in PKM_CRYSTAL: nombre_cart = "CRISTAL"
        resultado = {
            "status": "success",
            "cartucho": nombre_cart,
            "checksum": target
        }
        # Imprimimos una marca clara para PHP
        print("---JSON_START---")
        print(json.dumps(resultado))
        print("---JSON_END---")
        for game_id, data in db.items():
            if data.get("global_checksum") == target:
                print("\n" + "═"*50)
                print(f"JUEGO: {data.get('full_title')}")
                print(f"TIPO DE CARTUCHO:  {data.get('cartridge_type')}")
                print("═"*50)
                return

        print(f"No se pudo encontrar el checksum {target} en la db.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    identificar_por_global_checksum()