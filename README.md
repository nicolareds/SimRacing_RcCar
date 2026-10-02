# SimRacing RC Car

A Python-based control interface that allows a **sim racing setup** to control an **RC car through an ELRS radio link**.

The system reads inputs from a sim racing steering wheel and pedals, processes them through a Python control layer, and transmits the resulting commands to the RC car using **CRSF over an ELRS radio link**.

The project is intended as a platform for experimenting with **remote vehicle control, radio communication, embedded systems, and human-machine interfaces**.

---

## System Overview

```text
┌──────────────────────┐
│    Sim Racing PC     │
│                      │
│  Logitech G29        │
│  Steering / Pedals   │
└──────────┬───────────┘
           │
           │ USB
           ▼
┌──────────────────────┐
│    Python Control    │
│                      │
│  Input Processing    │
│  Channel Mapping     │
│  Command Generation  │
└──────────┬───────────┘
           │
           │ CRSF
           ▼
┌──────────────────────┐
│  RadioMaster Nomad   │
│      ELRS TX         │
└──────────┬───────────┘
           │
           │ ELRS
           │ Radio Link
           ▼
┌──────────────────────┐
│    ELRS Receiver     │
│  Matek ELRS-R24-P6V  │
└──────────┬───────────┘
           │
           │ CRSF / PWM
           ▼
┌──────────────────────┐
│      RC Vehicle      │
│                      │
│  Controller          │
│  ESC / Motor         │
│  Steering Servo      │
└──────────────────────┘
```

---

## Features

- Read real-time inputs from sim racing peripherals
- Support for steering wheel and pedal inputs
- Python-based input processing
- Configurable channel mapping
- CRSF communication with the ELRS transmitter
- Long-range wireless control through ELRS
- Independent control of steering and throttle
- Modular architecture for additional input devices
- Suitable for experimentation and development of remote vehicle control systems

---

## Hardware

### Control Station

| Component | Model | Function |
|---|---|---|
| Steering wheel | Logitech G29 | Steering and pedal input |
| Computer | Mac / PC | Runs the Python control software |
| ELRS transmitter | RadioMaster Nomad Dual 1 W | Wireless command transmission |
| USB-UART interface | Waveshare USB-to-UART | Serial interface between PC and ELRS transmitter |

### RC Vehicle

| Component | Model | Function |
|---|---|---|
| RC platform | Custom RC car | Vehicle platform |
| ELRS receiver | Matek ELRS-R24-P6V | Receives commands from the transmitter |
| ESC | TBD | Motor control |
| Steering servo | TBD | Steering control |
| Battery | TBD | Vehicle power supply |

---

## Hardware Setup

### Control Station

The Logitech G29 is connected to the computer through USB.

The Python application reads the steering wheel and pedal inputs and maps them to the corresponding vehicle control channels.

The processed commands are sent to the RadioMaster Nomad module using the **CRSF protocol** through a USB-to-UART interface.

### RC Car

The ELRS receiver receives the commands transmitted by the RadioMaster Nomad.

The received commands are then passed to the vehicle control system, which generates the appropriate steering and throttle outputs.

---

## Software Architecture

The project is divided into several Python modules:

```text
SimRacing_RcCar/
│
├── main.py
├── steering_wheel.py
├── crsf_nomad.py
├── test_waveshare.py
├── requirements.txt
├── README.md
└── .gitignore
```

### `main.py`

Main application responsible for coordinating the different software components.

### `steering_wheel.py`

Handles input acquisition from the sim racing steering wheel and pedals.

### `crsf_nomad.py`

Handles communication with the RadioMaster Nomad through the CRSF protocol.

### `test_waveshare.py`

Contains tests for the USB-UART interface and serial communication.

---

## Communication

The control chain is:

```text
Sim Racing Device
       │
       │ USB
       ▼
Python Application
       │
       │ CRSF
       ▼
RadioMaster Nomad
       │
       │ ELRS
       ▼
Matek ELRS Receiver
       │
       │ CRSF / PWM
       ▼
RC Car Controller
```

The use of **CRSF** provides a digital communication interface between the control software and the ELRS transmitter while ELRS provides the wireless radio link between the control station and the vehicle.

---

## Installation

Clone the repository:

```bash
git clone git@github.com:nicolareds/SimRacing_RcCar.git
cd SimRacing_RcCar
```

Install the required Python packages:

```bash
pip install -r requirements.txt
```

---

## Usage

Connect the sim racing steering wheel and the USB-to-UART interface to the computer.

Then run:

```bash
python main.py
```

The application will:

1. Detect the connected sim racing device.
2. Read steering and pedal inputs.
3. Map the inputs to the corresponding control channels.
4. Generate CRSF commands.
5. Transmit the commands through the ELRS radio link.

---

## Channel Mapping

The current channel mapping can be configured according to the vehicle setup.

Example:

| Channel | Function |
|---|---|
| CH1 | Steering |
| CH2 | Throttle / Brake |
| CH6 | Drive command |

The mapping can be extended to support additional vehicle functions.

---

## Development

The project is currently under development.

Potential future developments include:

- [ ] Improved input filtering
- [ ] Configurable channel mapping
- [ ] Input dead-zone and scaling configuration
- [ ] Real-time telemetry feedback
- [ ] Vehicle status monitoring
- [ ] Fail-safe handling
- [ ] Automatic device detection
- [ ] Graphical user interface
- [ ] Additional sim racing peripherals
- [ ] Autonomous driving experiments

---

## Project Goals

The main goal is to create a flexible interface between **sim racing hardware and physical RC vehicles**, combining:

- Human-machine interfaces
- Python programming
- Serial communication
- CRSF
- ExpressLRS
- Embedded systems
- Remote vehicle control

The project can serve as a foundation for further experimentation with **robotics, remote-controlled vehicles, and autonomous systems**.

---

## License

This project is currently intended for personal research and development.

License information will be added in a future release.


Further Infos:

```text
SteeringNomad/
├── main.py
├── steering_wheel.py
├── crsf_nomad.py
└── requirements.txt
```

## Installazione

```bash
cd SteeringNomad
python3 -m pip install -r requirements.txt
```

## 1. Identifica la porta seriale su macOS

```bash
ls /dev/cu.*
```

Imposta la porta in `main.py`, per esempio:

```python
SERIAL_PORT = "/dev/cu.usbserial-XXXX"
```

## 2. Testa il volante senza Nomad

```bash
python3 steering_wheel.py
```

Il programma mostra i valori nel terminale e apre un grafico live di:

- steering
- throttle
- brake
- drive command

Se gli assi non corrispondono, modifica in `main.py`:

```python
STEERING_AXIS = 0
THROTTLE_AXIS = 2
BRAKE_AXIS = 3
```

## 3. Testa solo CRSF/Nomad

Modifica `SERIAL_PORT` alla fine di `crsf_nomad.py`, quindi:

```bash
python3 crsf_nomad.py
```

Invia continuamente 16 canali neutri.

## 4. Avvia tutto

```bash
python3 main.py
```

Mapping:

```text
CH1 -> steering
CH2 -> drive command
```

`drive` vale:

```text
+1 = acceleratore massimo
 0 = neutro
-1 = freno/reverse massimo
```

## Nota di sicurezza

Durante le prime prove scollega il motore/solleva le ruote del veicolo. Verifica prima i valori ricevuti dal lato RX e configura anche il failsafe del ricevitore/controllore.
