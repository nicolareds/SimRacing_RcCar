import serial


class NomadCRSF:
    # CRSF
    CRSF_ADDRESS_TRANSMITTER_MODULE = 0xEE
    CRSF_FRAMETYPE_RC_CHANNELS_PACKED = 0x16

    # Range standard CRSF a 11 bit
    CRSF_MIN = 172
    CRSF_MID = 992
    CRSF_MAX = 1811

    CHANNEL_COUNT = 16

    def __init__(self, serial_port, baudrate=400000):
        self.serial_port = serial_port
        self.baudrate = baudrate

        self.ser = serial.Serial(
            port=self.serial_port,
            baudrate=self.baudrate,
            timeout=0,
            write_timeout=0,
        )

        print(
            f"Seriale Nomad aperta: "
            f"{self.serial_port} @ {self.baudrate} baud"
        )

    @classmethod
    def neutral_channels(cls):
        return [cls.CRSF_MID] * cls.CHANNEL_COUNT

    @classmethod
    def normalized_to_crsf(cls, value):
        """
        Converte -1.0 ... +1.0 nel range CRSF.

        -1.0 -> 172
         0.0 -> 992
        +1.0 -> 1811
        """
        value = max(-1.0, min(1.0, float(value)))

        if value >= 0:
            result = cls.CRSF_MID + value * (
                cls.CRSF_MAX - cls.CRSF_MID
            )
        else:
            result = cls.CRSF_MID + value * (
                cls.CRSF_MID - cls.CRSF_MIN
            )

        return int(round(result))

    @staticmethod
    def crc8_dvb_s2(data):
        crc = 0

        for byte in data:
            crc ^= byte

            for _ in range(8):
                if crc & 0x80:
                    crc = ((crc << 1) ^ 0xD5) & 0xFF
                else:
                    crc = (crc << 1) & 0xFF

        return crc

    @classmethod
    def pack_channels(cls, channels):
        if len(channels) != cls.CHANNEL_COUNT:
            raise ValueError("CRSF richiede esattamente 16 canali.")

        bit_buffer = 0
        bit_count = 0
        output = bytearray()

        for channel in channels:
            channel = int(max(0, min(0x7FF, channel)))

            bit_buffer |= (channel & 0x7FF) << bit_count
            bit_count += 11

            while bit_count >= 8:
                output.append(bit_buffer & 0xFF)
                bit_buffer >>= 8
                bit_count -= 8

        if len(output) != 22:
            raise RuntimeError(
                f"Payload CRSF non valido: {len(output)} bytes anziché 22."
            )

        return bytes(output)

    @classmethod
    def build_rc_frame(cls, channels):
        payload = cls.pack_channels(channels)

        # LENGTH conta TYPE + PAYLOAD + CRC.
        length = len(payload) + 2

        frame_without_crc = bytes([
            cls.CRSF_ADDRESS_TRANSMITTER_MODULE,
            length,
            cls.CRSF_FRAMETYPE_RC_CHANNELS_PACKED,
        ]) + payload

        # Nel CRSF il CRC del frame 0x16 viene calcolato
        # su TYPE + PAYLOAD, non su ADDRESS/LENGTH.
        crc = cls.crc8_dvb_s2(frame_without_crc[2:])

        return frame_without_crc + bytes([crc])

    def send_channels(self, channels):
        frame = self.build_rc_frame(channels)
        self.ser.write(frame)
        return frame

    def close(self):
        if hasattr(self, "ser") and self.ser.is_open:
            self.ser.close()


if __name__ == "__main__":
    """
    Test indipendente del trasmettitore CRSF.

    Prima modifica SERIAL_PORT.

    Avvio:
        python3 crsf_nomad.py
    """
    import time

    SERIAL_PORT = "/dev/cu.usbserial-BG00W94Q"

    nomad = NomadCRSF(
        serial_port=SERIAL_PORT,
        baudrate=400000,
    )

    channels = NomadCRSF.neutral_channels()

    try:
        while True:
            # Tutti i canali neutri.
            frame = nomad.send_channels(channels)
            print("\rTX:", frame.hex(), end="")
            time.sleep(0.02)

    except KeyboardInterrupt:
        print()

    finally:
        nomad.close()
