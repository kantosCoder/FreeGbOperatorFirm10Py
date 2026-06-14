import serial
import time
import os
import sys
import zlib

#LOAD SAVE DATA TO CART, THIS IS STILL EXPERIMENTAL AS I'M
#TRYING TO WRITE ON GEN 2 CARTS...

PORT = 'COM8'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def calcular_crc32(datos):
    return zlib.crc32(datos) & 0xFFFFFFFF

def upload_sram(archivo_input=None):
    if not archivo_input: return
    ruta = archivo_input if os.path.isabs(archivo_input) else os.path.join(BASE_DIR, archivo_input)
    
    try:
        with open(ruta, 'rb') as f:
            datos_sram = f.read()[:32768]

        ser = serial.Serial(PORT, 115200, timeout=1)
        
        # TAKE BUS CONTROL
        ser.write(bytes.fromhex("04" + "00"*59 + "b3556b81"))
        ser.flush()
        time.sleep(0.1)

        print(f"\n[FÍSICO] Inyectando partida en {PORT}...")

        bloque_size = 512 
        for i in range(0, len(datos_sram), bloque_size):
            chunk = datos_sram[i : i + bloque_size]
            
            # HEADER(64 bytes total: 60 + 4 CRC)
            header = bytearray(60)
            header[0] = 0x03
            header[1:4] = i.to_bytes(3, 'little')
            header[4] = 0x20 
            header[7] = 0x80 

            trama_completa = bytes(header) + calcular_crc32(header).to_bytes(4, 'little')
            trama_completa += chunk + calcular_crc32(chunk).to_bytes(4, 'little')
            
            ser.write(trama_completa)
            ser.flush()

            # PAUSE FOR SRAM PHYSICAl LATCH)
            time.sleep(0.05) 
            
            if ser.in_waiting > 0:
                ser.read(ser.in_waiting)
            
            # PROGRESS
            p = int(((i + bloque_size) / 32768) * 100)
            sys.stdout.write(f"\r    [{'#' * (p//5)}{'.' * (20-p//5)}] {p}%")
            sys.stdout.flush()

        # 2. CLOSE
        ser.write(bytes.fromhex("04" + "00"*59 + "b3556b81"))
        ser.flush()
        
        ser.close()
        print("\n\n✅ ESCRITURA FINALIZADA.")

    except Exception as e:
        if ser: ser.close()
        print(f"\n\n[ERROR] {str(e)}")

if __name__ == "__main__":
    upload_sram(sys.argv[1] if len(sys.argv) > 1 else None)