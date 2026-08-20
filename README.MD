Exit Demo Mode - Numark Mixtrack Pro / Platinum FX (Linux)

A lightweight, standalone Python script for Linux that automatically disables the light demo mode on Numark Mixtrack Pro FX and Numark Mixtrack Platinum FX controllers.

When these controllers are plugged in via USB without an active DJ software session, they enter an automatic light demo mode. This tool sends native SysEx MIDI commands to exit that mode, leaving your controller ready for custom MIDI mappings, projects, or integration with any software.

Beginner Guide (Step by Step)

If you use Linux Mint, Ubuntu, or any Debian-based distribution, just follow these simple steps from the terminal:

Step 1: Install required dependencies
Your system needs Python tools to communicate with MIDI devices. Open your terminal and run:

Bash
sudo apt update
sudo apt install -y python3-mido python3-rtmidi python3-pip

Step 2: Connect your controller
Connect your Numark Mixtrack to the PC via USB cable before running the program.

Step 3: Download or clone the script
You can clone this repository or simply download the exit_demo_linux.py file and save it to your computer.

Step 4: Run the script
Open a terminal in the same folder where you saved the file and type the following command:

Bash
python3 exit_demo_linux.py
The script will automatically detect your controller.

It will send the necessary SysEx signals to turn off the LEDs demo mode.

Upon completion, it will automatically open this repository's page in your browser. All set!

What if DJ software (like Mixxx or VirtualDJ) is open?
It is recommended to close any DJ software before running this script, as programs sometimes lock the controller's MIDI port and the script might fail to detect it on the first attempt.