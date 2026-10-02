import serial
import time

PORT = "/dev/cu.usbserial-BG00W94Q"
BAUD = 420000

ser = serial.Serial(PORT, BAUD, timeout=1)

test = b"CRSF_TEST_123456789"

ser.reset_input_buffer()
ser.write(test)
ser.flush()

time.sleep(0.1)

received = ser.read(len(test))

print("Sent:    ", test)
print("Received:", received)

if received == test:
    print("OK: USB-UART funziona correttamente a 420000 baud")
else:
    print("ERRORE: dati diversi o mancanti")

ser.close()