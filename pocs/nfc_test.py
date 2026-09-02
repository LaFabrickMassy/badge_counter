# main.py
import time
from machine import I2C, Pin
from nfc.i2c import PN532_I2C

def main():
    # Inicializa o I2C no Raspberry Pi Pico W:
    # SDA em GP0, SCL em GP1 (ajuste conforme sua montagem)
    i2c = I2C(0, scl=Pin(21), sda=Pin(20), freq=400000)
    
    # Verifica os dispositivos I2C
    devices = i2c.scan()
    if devices:
        print("Dispositivos I2C encontrados:", [hex(device) for device in devices])
    else:
        print("Nenhum dispositivo I2C encontrado!")
        return
    
    # Configura o pino de reset (opcional)
    reset_pin = Pin(2, Pin.OUT)  # Exemplo: GP2 para reset
    
    # Cria a instância do PN532 via I2C
    pn532 = PN532_I2C(i2c, address=0x24, reset=reset_pin, debug=False)
    
    # Tenta ler a versão do firmware
    try:
        fw = pn532.firmware_version
        print("Firmware PN532:", fw)
    except Exception as e:
        print("Erro ao ler o firmware:", e)
        return
    
    # Configura o PN532 para operação (SAM configuration)
    pn532.SAM_configuration()
    print("Aproxime um cartão NFC do leitor...")
    
    # Loop principal: lê e imprime o UID do cartão (se detectado)
    while True:
        uid = pn532.read_passive_target(timeout=1)
        if uid is not None:
            print("Cartão detectado! UID:", [hex(b) for b in uid])
            time.sleep(2)
        time.sleep(0.5)

if __name__ == "__main__":
    main()

