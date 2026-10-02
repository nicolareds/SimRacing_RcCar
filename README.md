# SteeringNomad

Struttura:

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
