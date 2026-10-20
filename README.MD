# Exit Demo Mode - Numark Mixtrack Pro / Platinum FX (Linux)

A small Linux app that automatically disables the light demo mode on **Numark Mixtrack Pro FX** and **Numark Mixtrack Platinum FX** controllers.

When these controllers are plugged in via USB without an active DJ software session, they enter an automatic light demo mode. This tool sends native SysEx MIDI commands to exit that mode, leaving your controller ready for custom MIDI mappings, projects, or integration with any software (Mixxx, VirtualDJ, Bitwig, Ardour...).

> [!NOTE]
> This is an unofficial project, not affiliated with or endorsed by Numark or inMusic. It does not flash or change the controller's firmware.

Looking for Windows? See [Exit Demo Mode for Windows](https://github.com/nexushouser92/Exit-Demo-Mode---Mixtrack-Pro-Platinum-FX).

---

## Features

* **Simple window, no terminal needed**: One button. If the controller is not plugged in yet, the window detects it as soon as you connect it.
* **Safe detection**: Only MIDI devices whose name contains "Mixtrack" are used; other devices are never touched.
* **English and Spanish**: Messages follow your system language.

---

## Option 1: Ready-to-run app (recommended)

No Python or extra packages needed. Works on 64-bit (x86_64) distributions such as Ubuntu, Linux Mint, Debian, Fedora or Arch.

1. Download `exit-demo-mode-linux-x86_64.tar.gz` from the [Releases](../../releases) page.
2. Extract it (right click → **Extract Here**, or `tar -xzf exit-demo-mode-linux-x86_64.tar.gz`).
3. Connect your Mixtrack via USB and close any DJ software.
4. Run `exit-demo-mode` (double click, or `./exit-demo-mode` in a terminal).
5. When the window shows **Controller detected**, click **Exit demo mode**.

## Option 2: Run the Python script

On Ubuntu, Linux Mint or any Debian-based distribution:

```bash
sudo apt update
sudo apt install -y python3-mido python3-rtmidi python3-tk
```

Then download `main.py` from the [Releases](../../releases) page (or clone this repository) and run it from the same folder:

```bash
python3 main.py
```

On other distributions, install Tkinter from your package manager and the MIDI libraries with `pip install mido python-rtmidi`.

---

The commands only last until the controller is unplugged or powered off, so run the tool again after reconnecting it.

### What if DJ software (like Mixxx or VirtualDJ) is open?

Close it before running this tool: DJ software can lock the controller's MIDI port, and the window will tell you it could not open the port.

### Verify your download

Every release is built by [GitHub Actions](../../actions) from the code in this repository, and each release includes a `SHA256.txt`:

```bash
sha256sum -c SHA256.txt --ignore-missing
```

---

## Technical Details

This program sends two System Exclusive (SysEx) MIDI messages to the controller:

* **Exit Demo Mode**: `F0 7E 00 06 01 F7` (Universal Identity Request: the controller leaves demo mode when a host asks for its identity, as DJ software does at startup)
* **State Initialization**: `F0 00 20 7F 03 01 F7`

## Development

```bash
python3 -m pip install mido python-rtmidi
python3 -m unittest discover -s tests -v
```

The tests use a fake MIDI backend, so no controller is needed. To publish a release, go to **Releases → Draft a new release** on GitHub, type a new tag (for example `v1.1.0`) and publish; the workflow builds the Linux app and attaches it with `main.py` and `SHA256.txt`.

---

Developed by [nexushouser92](https://github.com/nexushouser92). Released under the [MIT License](LICENSE).
