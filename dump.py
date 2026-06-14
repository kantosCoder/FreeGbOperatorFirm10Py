import serial
import time
import json
import os
import datetime
import sys

# GB OPERATOR COMMS AUTODUMP FOR POKEMON 1ST AND 2ND GEN USING SERIALPY kantosCoder 2026
#=====================================================================================
# ============================VARIABLE DECLARATION====================================
#=====================================================================================

# OS PATHS INSTANCE

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_JSON = os.path.join(BASE_DIR, 'gb_gbc_roms_info.json')
USR_PROFILE = sys.argv[1] if len(sys.argv) > 1 else "null"
SAVE_BOX = sys.argv[2] if len(sys.argv) > 2 else "CAJA 1"



# COM PORT SETTINGS
PUERTO = 'COM8'

# CHECKSUM DATA LIST
GEN1_CHECKSUMS = [
    "0xAB23", "0x4AB2", "0x9E42", "0x49E4", "0xD83A", "0x4D83", "0x047C", "0x14D7"
]
GEN2_CHECKSUMS = [
    "0x70E5", "0x1D83", "0xD83A", "0x6A34", "0x937B", "0x7B28", "0x2863", "0x7295", 
    "0x951C", "0x1C88", "0x34A6", "0xA61B", "0x1B86", "0x8670", "0x4D83", "0x0C53", 
    "0x1FE6", "0x2A8E", "0x031C", "0x064B", "0x9353"
]

# PKMN GAME SPECIFICATION

PKM_RED = ["0x384A", "0x1810"]
PKM_BLUE = ["0xF49D", "0x14D7"]
PKM_YELLOW = ["0x5637"]
PKM_SILVER = ["0x064B"]
PKM_GOLD = ["0x9353"]
PKM_CRYSTAL = ["0x42F4"]


#=====================================================================================
#================================MAIN PROGRAM LOGIC===================================
#=====================================================================================

#=================================CARTRIDGE CHECKER===================================
def id_check(ser):
    """CHECKSUM OBTENTION"""
    ser.write(bytes.fromhex("04" + "00"*59 + "b3556b81")) # Power On order (USB)
    time.sleep(0.5)
    ser.write(bytes.fromhex("15" + "00"*59 + "2FB93C26")) # Get Info order (USB)
    time.sleep(0.8)
    
    raw = ser.read(ser.in_waiting)
    if len(raw) < 1024: return None
    
    bloque_id = raw[512:1024]
    g_chk = bloque_id[18:20].hex().upper()
    return f"0x{g_chk}"

def name_find(target_chk):
    """GBOpyrator DB NAME FIND"""
    if not os.path.exists(DB_JSON): return "\033[31m Archivo DB no encontrado \033[0m"
    try:
        with open(DB_JSON, 'r', encoding='utf-8') as f:
            db = json.load(f)
            for _, data in db.items():
                if data.get("global_checksum") == target_chk:
                    return data.get("full_title", "Título desconocido")
    except: pass
    print(json.dumps(resultado))
    return "\033[31m  Juego no registrado en DB \033[0m"


#=====================================SRAM DUMPER=====================================
def multigen_dumper():
    try:
        print("\033[1m"+ "\033[32m" + r"""
 __                   __               _________            .___             _______________   ________  ________
|  | _______    _____/  |_  ____  _____\_   ___ \  ____   __| _/___________  \_____  \   _  \  \_____  \/  _____/
|  |/ /\__  \  /    \   __\/  _ \/  ___/    \  \/ /  _ \ / __ |/ __ \_  __ \  /  ____/  /_\  \  /  ____/   __  \ 
|    <  / __ \|   |  \  | (  <_> )___ \\     \___(  <_> ) /_/ \  ___/|  | \/ /       \  \_/   \/       \  |__\  \
|__|_ \(____  /___|  /__|  \____/____  >\______  /\____/\____ |\___  >__|    \_______ \_____  /\_______ \_____  /
     \/     \/     \/                \/        \/            \/    \/                \/     \/         \/     \/ 
        """ + "\033[0m")
        print("\033[1m"+ "\033[32m" + "EPILOGUE GB OPERATOR - POKEMON MULTIGEN DUMP (FW10)\n" + "\033[0m")

        ser = serial.Serial(PUERTO, 115200, timeout=2)
        
        # STEP 1. IDENT ---
        target_chk = id_check(ser)
        if not target_chk:
            print("\033[31m" + "No se ha podido identificar el cartucho"+ "\033[0m")
            ser.close()
            print(f"Error: {e}")
            resultado = {
                "status": "failure",
                "reason": "unknown_cart"
            }
            print(json.dumps(resultado))
            return

        nombre = name_find(target_chk)
        gen = 0
        if target_chk in GEN1_CHECKSUMS: gen = 1
        elif target_chk in GEN2_CHECKSUMS: gen = 2
        print("\033[36m-" * 65)
        print("\033[1m"+ "INFORMACIÓN DE CARTUCHO INTRODUCIDO"+"\033[0m" + "\033[36m")
        print("-" * 65)
        print(f"NOMBRE: {nombre}")
        print(f"ID (CHECKSUM): {target_chk}")
        print("-" * 65 + "\033[0m")

        # STEP 2. VOLCADO SRAM ---
        print("\033[1m"+ "\033[35m"+ "\n\n<<<PROCESO DE VOLCADO DE MEMORIA SRAM>>>\n"+ "\033[0m")
        print("\n\nOBTENIENDO SRAM EN CRUDO...\n"+ "\033[0m")
        cmd_read = bytes.fromhex("020000001000008000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000a0481847")
        ser.reset_input_buffer()
        ser.write(cmd_read)
        
        raw_sram = bytearray()
        start = time.time()
        while (time.time() - start) < 5:
            if ser.in_waiting > 0:
                raw_sram.extend(ser.read(ser.in_waiting))
        ser.close()

        # STEP 3. PROCESAMIENTO ---
        idx_datos = -1
        for i in range(64, len(raw_sram)):
            if raw_sram[i] != 0x00:
                idx_datos = i
                break

        if idx_datos == -1:
            print("\033[31m" + "Error: No se detectaron datos reales."+ "\033[0m")
            print(f"Error: {e}")
            resultado = {
                "status": "failure",
                "reason": "invalid_data"
            }
            print(json.dumps(resultado))
            return

        if gen == 2:
            print("\033[1m"+"/!\\ "+ "\033[2m" + "\033[33m" +"SEGUNDA "+ "\033[37m" + "GENERACION " + "\033[36m" + "DETECTADA.\n\n" + "\033[0m" +
            "\033[32m"+"PROCESADO DE SRAM EN CRUDO PARA GENERAR ARCHIVO DE GUARDADO:\n\n" +
            "Agregado de Bloque RTC Fijo al total de los 32816 bytes..."+ "\033[0m")
            # SRAM: 32768 bytes
            partida_base = raw_sram[idx_datos : idx_datos + 32768]
            
            # RTC: Saltamos 64 bytes de protocolo tras la SRAM
            idx_rtc = idx_datos + 32768 + 64
            # Extraemos exactamente 48 bytes (estándar Epilogue)
            rtc_final = raw_sram[idx_rtc : idx_rtc + 48]
            
            partida_final = partida_base + rtc_final
        else:
            print("\033[1m"+ "/!\\ "+ "\033[31m" +"PRIMERA "+ "\033[34m" + "GENERACION " + "\033[33m" + "DETECTADA.\n\n" +
            "\033[32m"+"PROCESADO DE SRAM EN CRUDO PARA GENERAR ARCHIVO DE GUARDADO:\n\n\n" + 
            "Alineación de los 81 ceros en cabecera de memoria fija al bloque total de 32768 bytes..."+ "\033[0m")
            inicio = idx_datos - 81
            if inicio < 0:
                partida_final = (b'\x00' * 81) + raw_sram[idx_datos : idx_datos + (32768 - 81)]
            else:
                partida_final = raw_sram[inicio : inicio + 32768]
            
            partida_final = partida_final.ljust(32768, b'\x00')[:32768]

        # STEP  4. GUARDADO ---
        nombre_cart = "UNKNOWN"
        if target_chk in PKM_RED: nombre_cart = "ROJO"
        elif target_chk in PKM_BLUE: nombre_cart = "AZUL"
        elif target_chk in PKM_YELLOW: nombre_cart = "AMARILLO"
        elif target_chk in PKM_GOLD: nombre_cart = "ORO"
        elif target_chk in PKM_SILVER: nombre_cart = "PLATA"
        elif target_chk in PKM_CRYSTAL: nombre_cart = "CRISTAL"
        relative_path = '../../user_data/'+USR_PROFILE+'/saves/'+SAVE_BOX+"/"+nombre_cart
        DUMP_DIR = os.path.join(BASE_DIR, relative_path)
        if not os.path.exists(DUMP_DIR):
            os.makedirs(DUMP_DIR)
        
        filename = f"{target_chk}_current.sav"
        timestamp_str = datetime.datetime.now().strftime("%d-%m-%Y_%H-%M")
        filename_backup = f"{target_chk}_"+timestamp_str+".bak"
        full_path_current = os.path.join(DUMP_DIR, filename)
        full_path_backup = os.path.join(DUMP_DIR, filename_backup)
        with open(full_path_current, 'wb') as f:
            f.write(partida_final)
        with open(full_path_backup, 'wb') as f:
            f.write(partida_final)
        
        print("-" * 65)
        print(f"VOLCADO COMPLETADO: {filename}")
        print(f"Tamaño final: {len(partida_final)} bytes")
        resultado = {
            "status": "success",
            "reason": "dumped",
            "juego": nombre,
            "folder": relative_path,
            "cartucho": nombre_cart,
            "checksum": target_chk,
            "file": filename
        }
        print(json.dumps(resultado))

    except Exception as e:
        print(f"Error: {e}")
        resultado = {
            "status": "failure",
            "reason": "write_error"
        }
        print(json.dumps(resultado))


if __name__ == "__main__":
    multigen_dumper()