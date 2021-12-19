# Dromedaris Race

[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=CasperStar_dromedaris-race&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=CasperStar_dromedaris-race) [![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=CasperStar_dromedaris-race&metric=reliability_rating)](https://sonarcloud.io/summary/new_code?id=CasperStar_dromedaris-race) [![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=CasperStar_dromedaris-race&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=CasperStar_dromedaris-race) [![Technical Debt](https://sonarcloud.io/api/project_badges/measure?project=CasperStar_dromedaris-race&metric=sqale_index)](https://sonarcloud.io/summary/new_code?id=CasperStar_dromedaris-race)

This is a hobby project that recreates the dutch fairgound attraction the 'kamelen race' in a do-it-yourself manner.

The fairground game has a visual representation of multiple figures that need to race to the finish line in a straight line. The figure will move when the player scores a point. The player can score points by rolling the ball in to a certain hole and represents a number of points. The figure will move a few steps depending on the number of points the player score. The player who finish first will win the game.

The scope of this repository is only the software and electronic hardware side of the project.

## Getting Started

The project is run an a Raspberry Pi and some additional hardware components to get the everything going. The [Technical Documentation](#technical-documentation) describes all the needed components and should be sufficient enough recreate the circuit or even make a experimental PCB.

Install the lastest [Raspberry Pi OS](https://www.raspberrypi.com/software/) and enable the I2C interface.

```shell
sudo raspi-config
# Go to; Advanced Options > Interfacing Options > I2C

# Install the SMBUS package for python
sudo apt-get install python-smbus
```

Clone the repository on to the Raspberry Pi and run the [main.py]("src/__main__.py") on from the Pi.

```shell
git clone https://github.com/CasperStar/dromedaris-race.git
python ./src/__main__.py
```

## Technical Documentation

For now the documentation is consise and focussed on what hardware components are used and how these different sub systems are connected with each other.

### Block Diagram

This diagram shows an overview of the whole system.

![BlockDiagram.svg](./docs/BlockDiagram.svg)

### Hardware

This section describes how the sensors, leds and buttons are connected to the IO extenders.

#### Sensor Pinout Table

This table describes to which sensor connects to what MCP23017 pin.

| Sensor Name       | Pin Out | Device Address |
|-------------------|---------|----------------|
| Lane 01 Sensor 01 | GPB7    | 0x20           |
| Lane 01 Sensor 02 | GPB6    | 0x20           |
| Lane 01 Sensor 03 | GPB5    | 0x20           |
| Lane 02 Sensor 01 | GPB4    | 0x20           |
| Lane 02 Sensor 02 | GPB3    | 0x20           |
| Lane 02 Sensor 03 | GPB2    | 0x20           |
| Lane 03 Sensor 01 | GPA7    | 0x21           |
| Lane 03 Sensor 02 | GPA6    | 0x21           |
| Lane 03 Sensor 03 | GPA5    | 0x21           |
| Lane 04 Sensor 01 | GPA0    | 0x20           |
| Lane 04 Sensor 02 | GPA1    | 0x20           |
| Lane 04 Sensor 03 | GPA2    | 0x20           |
| Lane 05 Sensor 01 | GPA3    | 0x20           |
| Lane 05 Sensor 02 | GPA4    | 0x20           |
| Lane 05 Sensor 03 | GPA5    | 0x20           |
| Lane 06 Sensor 01 | GPB0    | 0x21           |
| Lane 06 Sensor 02 | GPB1    | 0x21           |
| Lane 06 Sensor 03 | GPB2    | 0x21           |

#### LED Pinout Table

This table describes to which LED connects to what MCP23017 pin.

| LED Name   | Pin Out | Device Address |
|------------|---------|----------------|
| LED Red    | GPA3    | 0x21           |
| LED Yellow | GPA2    | 0x21           |
| LED Green  | GPA1    | 0x21           |
| LED Blue   | GPA0    | 0x21           |

#### Button Pinout Table

This table describes to which button connects to what MCP23017 pin.

| Button Name | Pin Out | Device Address |
|-------------|---------|----------------|
| Start       | GPB4    | 0x21           |
| Pause       | GPB5    | 0x21           |
| Reset       | GPB6    | 0x21           |

## License

Dromedarice Race is licensed under the [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.html). See the [LICENSE](/LICENSE) for more details.
