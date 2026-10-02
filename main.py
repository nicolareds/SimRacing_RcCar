import time
from steering_wheel import SteeringWheel
from crsf_nomad import NomadCRSF

# =========================
# CONFIGURAZIONE
# =========================

SERIAL_PORT = "/dev/cu.usbserial-BG00W94Q"   # <-- cambia con la tua porta
BAUDRATE = 400000
SEND_RATE_HZ = 100

# Assi pygame: da verificare sul tuo volante.
STEERING_AXIS = 0
THROTTLE_AXIS = 2
BRAKE_AXIS = 3

# Se un pedale lavora al contrario, cambia True/False.
THROTTLE_INVERTED = True
BRAKE_INVERTED = True

# Dead zone sullo sterzo
STEERING_DEADZONE = 0.02


def main():
    wheel = SteeringWheel(
        steering_axis=STEERING_AXIS,
        throttle_axis=THROTTLE_AXIS,
        brake_axis=BRAKE_AXIS,
        throttle_inverted=THROTTLE_INVERTED,
        brake_inverted=BRAKE_INVERTED,
        steering_deadzone=STEERING_DEADZONE,
        enable_plot=True,
    )

    nomad = NomadCRSF(
        serial_port=SERIAL_PORT,
        baudrate=BAUDRATE,
    )

    period = 1.0 / SEND_RATE_HZ

    print("\nSistema avviato.")
    print("CH1 = sterzo")
    print("CH2 = acceleratore/freno")
    print("Premi Ctrl+C per terminare.\n")

    try:
        while True:
            loop_start = time.perf_counter()

            # 1) Lettura volante
            state = wheel.read()

            # 2) Aggiornamento grafici
            wheel.update_plot(state)

            # 3) Conversione in canali CRSF
            # steering: -1 .. +1
            # drive:    -1 .. +1
            #   +1 = acceleratore
            #    0 = neutro
            #   -1 = freno/reverse
            channels = NomadCRSF.neutral_channels()

            channels[0] = NomadCRSF.normalized_to_crsf(state["steering"])
            channels[5] = NomadCRSF.normalized_to_crsf(state["drive"])

            print(
                f"\rCH1={channels[0]} "
                f"CH6={channels[5]} "
                f"drive={state['drive']:+.2f}",
                end=""
            )

            # 4) Invio al Nomad
            nomad.send_channels(channels)

            # 5) Frequenza di loop costante
            elapsed = time.perf_counter() - loop_start
            remaining = period - elapsed
            if remaining > 0:
                time.sleep(remaining)

    except KeyboardInterrupt:
        print("\nArresto richiesto.")

    finally:
        # Invia alcuni frame neutri prima di chiudere.
        try:
            for _ in range(10):
                nomad.send_channels(NomadCRSF.neutral_channels())
                time.sleep(0.01)
        except Exception:
            pass

        nomad.close()
        wheel.close()
        print("Sistema arrestato.")


if __name__ == "__main__":
    main()
