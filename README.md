# Dromedaris Race

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

## Improvements

The following bullet point list shows improvements that still can be done to the project. Using the issue tracker would be kind of overkill for a small hobby project.

- Add MotorController code for the ATMega328P
- Capture all dependencies in pip
- Add statically typed in python where possible
- Improve technical documentation
- Add PCB schematic to the hardware documentation
- Add testing / mocking to test without required hardware
- Add correct packaging / folder structure for a python project
- Add SonarCloud when repo is public


## Technical Documentation

### Software

### Hardware

## License

Dromedarice Race is licensed under the [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.html). See the [LICENSE](/LICENSE) for more details.