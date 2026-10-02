import time
from collections import deque

import pygame
import matplotlib.pyplot as plt


class SteeringWheel:
    """
    Legge un volante/pedaliera USB tramite pygame.

    Output di read():
        steering : -1.0 ... +1.0
        throttle :  0.0 ...  1.0
        brake    :  0.0 ...  1.0
        drive    : -1.0 ... +1.0

    drive = throttle - brake
    """

    def __init__(
        self,
        steering_axis=0,
        throttle_axis=2,
        brake_axis=3,
        throttle_inverted=True,
        brake_inverted=True,
        steering_deadzone=0.02,
        enable_plot=True,
        plot_window_seconds=10.0,
    ):
        self.steering_axis = steering_axis
        self.throttle_axis = throttle_axis
        self.brake_axis = brake_axis

        self.throttle_inverted = throttle_inverted
        self.brake_inverted = brake_inverted
        self.steering_deadzone = steering_deadzone

        pygame.init()
        pygame.joystick.init()

        count = pygame.joystick.get_count()
        if count == 0:
            raise RuntimeError("Nessun volante/joystick USB rilevato da pygame.")

        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()

        print("Dispositivo:", self.joystick.get_name())
        print("Numero assi:", self.joystick.get_numaxes())
        print("Numero pulsanti:", self.joystick.get_numbuttons())
        print("Numero hat:", self.joystick.get_numhats())

        self.start_time = time.perf_counter()

        self.enable_plot = enable_plot
        self.plot_window_seconds = plot_window_seconds

        self.t_history = deque(maxlen=2000)
        self.steer_history = deque(maxlen=2000)
        self.throttle_history = deque(maxlen=2000)
        self.brake_history = deque(maxlen=2000)
        self.drive_history = deque(maxlen=2000)

        if self.enable_plot:
            plt.ion()
            self.fig, self.ax = plt.subplots()

            self.line_steer, = self.ax.plot([], [], label="Steering")
            self.line_throttle, = self.ax.plot([], [], label="Throttle")
            self.line_brake, = self.ax.plot([], [], label="Brake")
            self.line_drive, = self.ax.plot([], [], label="Drive command")

            self.ax.set_xlabel("Time [s]")
            self.ax.set_ylabel("Normalized value")
            self.ax.set_ylim(-1.05, 1.05)
            self.ax.grid(True)
            self.ax.legend(loc="upper right")
            self.fig.tight_layout()

    @staticmethod
    def _clamp(value, low, high):
        return max(low, min(high, value))

    @staticmethod
    def _pedal_to_01(raw, inverted):
        """
        pygame normalmente restituisce assi in [-1, +1].

        Per molti volanti:
            pedale rilasciato = +1
            pedale premuto    = -1

        In tal caso inverted=True.
        """
        raw = SteeringWheel._clamp(raw, -1.0, 1.0)

        if inverted:
            value = (1.0 - raw) / 2.0
        else:
            value = (raw + 1.0) / 2.0

        return SteeringWheel._clamp(value, 0.0, 1.0)

    def _apply_deadzone(self, value):
        value = self._clamp(value, -1.0, 1.0)

        if abs(value) < self.steering_deadzone:
            return 0.0

        # Rimappa la parte restante per mantenere l'intero range.
        sign = 1.0 if value >= 0 else -1.0
        magnitude = (
            abs(value) - self.steering_deadzone
        ) / (1.0 - self.steering_deadzone)

        return sign * self._clamp(magnitude, 0.0, 1.0)

    def read(self):
        pygame.event.pump()

        steering_raw = self.joystick.get_axis(self.steering_axis)
        throttle_raw = self.joystick.get_axis(self.throttle_axis)
        brake_raw = self.joystick.get_axis(self.brake_axis)

        steering = self._apply_deadzone(steering_raw)

        throttle = self._pedal_to_01(
            throttle_raw,
            self.throttle_inverted,
        )

        brake = self._pedal_to_01(
            brake_raw,
            self.brake_inverted,
        )

        # +1 accelerazione, -1 frenata/reverse
        drive = self._clamp(throttle - brake, -1.0, 1.0)

        return {
            "steering": steering,
            "throttle": throttle,
            "brake": brake,
            "drive": drive,
            "raw": {
                "steering": steering_raw,
                "throttle": throttle_raw,
                "brake": brake_raw,
            },
        }

    def update_plot(self, state):
        if not self.enable_plot:
            return

        now = time.perf_counter() - self.start_time

        self.t_history.append(now)
        self.steer_history.append(state["steering"])
        self.throttle_history.append(state["throttle"])
        self.brake_history.append(state["brake"])
        self.drive_history.append(state["drive"])

        self.line_steer.set_data(self.t_history, self.steer_history)
        self.line_throttle.set_data(self.t_history, self.throttle_history)
        self.line_brake.set_data(self.t_history, self.brake_history)
        self.line_drive.set_data(self.t_history, self.drive_history)

        xmin = max(0.0, now - self.plot_window_seconds)
        xmax = max(self.plot_window_seconds, now)

        self.ax.set_xlim(xmin, xmax)

        # Mantiene viva la GUI senza bloccare il loop.
        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()
        plt.pause(0.001)

    def close(self):
        if self.enable_plot:
            plt.close(self.fig)

        pygame.joystick.quit()
        pygame.quit()


if __name__ == "__main__":
    """
    Permette di testare SOLO il volante, senza Nomad.

    Avvio:
        python3 steering_wheel.py
    """
    wheel = SteeringWheel(enable_plot=True)

    try:
        while True:
            state = wheel.read()
            wheel.update_plot(state)

            print(
                f"\rsteer={state['steering']:+.3f}  "
                f"throttle={state['throttle']:.3f}  "
                f"brake={state['brake']:.3f}  "
                f"drive={state['drive']:+.3f}",
                end="",
            )

            time.sleep(0.01)

    except KeyboardInterrupt:
        print()

    finally:
        wheel.close()
