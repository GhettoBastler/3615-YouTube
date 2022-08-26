# 3615-YouTube

![IMG_20220824_145332_1](https://user-images.githubusercontent.com/100698182/186926004-fe1df0db-4177-4769-8e34-dd9ba33bfaf1.jpg)


A Mintel interface to record YouTube videos on a VHS tape. Inspired by [this comic by Boulet](https://english.bouletcorp.com/2011/07/07/formicapunk/). 

You can read the full write-up [here](https://ghettobastler.com/portfolio/3615yt).

## Dependiencies
- git
- lirc
- python-pip
- vlc-bin
- vlc-plugin-base
- ffmpeg

## Installation

1. Create a Raspberry Pi OS Lite SD card, and setup WiFi and SSH. Insert it into the Pi and connect to it using SSH.

2. Upgrade the system
```
sudo apt-get update
sudo apt-get upgrade
```

3. Install dependencies:
```
sudo apt-get install git python-pip lirc vlc-bin vlc-plugin-base ffmpeg
```

4. Run raspi-config:
```
sudo raspi-config
```
Enable the serial port (and disable login shell) and the video composite output.

5. Add/uncomment these lines in /boot/config.txt
```
sdtv_mode=2 # Use the PAL standard
hdmi_ignore_hotplug=1 # Force video through the composite output
dtoverlay=gpio-ir-tx,gpio_pin=24 # Enable IR transmition on GPIO 24
```

6. Clone this repository
```
git clone ttps://github.com/GhettoBastler/3615-YouTube.git
```

7. Install the Python dependencies
```
sudo pip install -r requirements.txt
```

8. Copy lircd/VF28.lircd.conf to /etc/lirc/lircd.conf.d
```
sudo cp lircd/VF28.lircd.conf /etc/lirc/lircd.conf.d
```

9. Inside /etc/lirc/lircd.conf.d, disable devinput.lircd.conf by renaming it to devinput.lircd.dist
```
mv /etc/lirc/lircd.conf.d/devinput.lircd.conf /etc/lirc/lircd.conf.d/devinput.lircd.dist
```

10. Edit /etc/lirc/lircd.conf to change these two values:
```
driver = default
device = /dev/lirc0
```

12. Reboot the Pi
```
sudo reboot
```

## Level shifter

![IMG_20220817_231013](https://user-images.githubusercontent.com/100698182/186925881-42a76b3f-8367-426b-bff0-adc12af79279.jpg)

You need to use a logic level shifter to safely connect a Minitel to a Raspberry Pi. My circuit is based on [Pila's design](https://pila.fr/wordpress/?p=361). You can find the schematics [here](https://github.com/GhettoBastler/3615-YouTube/blob/main/pcb/Schematic.pdf)

## Usage

On the Minitel, set the baudrate to 4800 by pressing ```Fctn + P``` followed by ```4```.

Power up the VCR, making sure that it is set to record on its composite input (you may need to check that by plugging the VCR to a TV)

When everything is set up, run 3615yt
```
./3615yt
```

## Limitations

This project is not meant to be used as an actual way to watch YouTube videos. Therefore it lacks some basic features.

In particular, there is no way for the user to stop the downloading or recording processes: you have to do it by connecting through SSH and killing VLC manually. The same goes for powering the Pi down: you have to do it through SSH.

## Additional ressources

These guides helped me greatly during the making of this project:

- [Pila's article](https://pila.fr/wordpress/?p=361) on connecting a Minitel to a Raspberry Pi
- [This guide](https://www.raspberrypi-spy.co.uk/2014/07/raspberry-pi-model-b-3-5mm-audiovideo-jack/) on how to use the Pi's composite output
- [This tutorial](https://www.raspberry-pi-geek.com/Archive/2015/10/Raspberry-Pi-IR-remote) that explains how to build an IR transmitter for the Raspberry Pi

## Licensing

The code for this project is licensed under the terms of the GNU GPLv3 license.
