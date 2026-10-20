"""Exit Demo Mode for the Numark Mixtrack Pro FX / Platinum FX (Linux): a small window that finds the controller
and sends the SysEx commands that turn off its light demo mode.
"""
import locale
import sys
import time
import tkinter as tk
import tkinter.font as tkfont
import webbrowser

try:
    import mido
except ImportError:  # shown in the window with install instructions
    mido = None

REPO_URL = 'https://github.com/nexushouser92/Exit-Demo-Linux-Mode--Mixtrack-Pro-Platinum-FX-'
POLL_MS = 1500  # how often the window looks for the controller
FLUSH_DELAY = 0.1  # seconds to let ALSA deliver the SysEx messages before the port is closed

# ==============================================================================
# SYSTEM LANGUAGE DETECTION
# ==============================================================================
try:
    sys_lang = locale.getlocale()[0]
except Exception:
    sys_lang = None

IS_SPANISH = bool(sys_lang and sys_lang.lower().startswith(('es', 'spanish')))

# ==============================================================================
# MULTILINGUAL MESSAGES DICTIONARY
# ==============================================================================
LANG = {
    'title': 'Exit Demo Mode',
    'heading': 'Exit Demo Mode',
    'subheading': (
        'Numark Mixtrack Pro FX / Platinum FX. Cierra tu software de DJ antes de continuar.'
        if IS_SPANISH
        else 'Numark Mixtrack Pro FX / Platinum FX. Close your DJ software before continuing.'
    ),
    'not_found': (
        'No se detecta el controlador. Conecta tu Mixtrack por USB; se detectará automáticamente.'
        if IS_SPANISH
        else 'Controller not detected. Connect your Mixtrack via USB; it will be detected automatically.'
    ),
    'detected': (
        'Controlador detectado: {name}' if IS_SPANISH else 'Controller detected: {name}'
    ),
    'button': 'Salir del modo demo' if IS_SPANISH else 'Exit demo mode',
    'sending': 'Enviando comandos...' if IS_SPANISH else 'Sending commands...',
    'success': (
        'Listo: el modo demo está desactivado. Tu controlador está listo para usarse.'
        ' Si lo desconectas, vuelve a ejecutar esta herramienta.'
        if IS_SPANISH
        else 'Done: demo mode is off and your controller is ready to use.'
        ' If you unplug it, run this tool again.'
    ),
    'failed': (
        'No se pudo salir del modo demo: {err}\nDesconecta y vuelve a conectar el controlador e inténtalo de nuevo.'
        if IS_SPANISH
        else 'Could not exit demo mode: {err}\nUnplug the controller, plug it back in and try again.'
    ),
    'port_open_err': (
        'no se pudo abrir el puerto MIDI ({err}). Revisa si el software de DJ ya lo tiene abierto'
        if IS_SPANISH
        else 'could not open the MIDI port ({err}). Check if DJ software is using it'
    ),
    'midi_err': (
        'Error del sistema MIDI: {err}' if IS_SPANISH else 'MIDI system error: {err}'
    ),
    'missing_deps': (
        'Faltan las librerías MIDI de Python. Instálalas con:\n'
        'sudo apt install python3-mido python3-rtmidi'
        if IS_SPANISH
        else 'The Python MIDI libraries are missing. Install them with:\n'
        'sudo apt install python3-mido python3-rtmidi'
    ),
    'footer': (
        'Proyecto no oficial, sin relación con Numark ni inMusic.'
        if IS_SPANISH
        else 'Unofficial project, not affiliated with Numark or inMusic.'
    ),
}

# SysEx messages definition (mido adds the F0 ... F7 framing)
# Universal Identity Request: the controller leaves its light demo mode when a host asks who it is.
EXIT_DEMO_SYSEX = [0x7E, 0x00, 0x06, 0x01]
STATUS_SYSEX = [0x00, 0x20, 0x7F, 0x03, 0x01]


# ==============================================================================
# MIDI DEVICE AUTOMATIC DETECTION (LINUX / ALSA)
# ==============================================================================
def get_numark_port():
    """Returns the name of the first MIDI output whose name contains "Mixtrack", or None."""
    for port_name in mido.get_output_names():
        if 'mixtrack' in port_name.lower():
            return port_name
    return None


def exit_demo_mode(port_name):
    """Opens the MIDI port, sends both SysEx messages and closes it. Returns None on success or an error message."""
    try:
        port = mido.open_output(port_name)
    except Exception as e:
        return LANG['port_open_err'].format(err=e)
    try:
        for data in (EXIT_DEMO_SYSEX, STATUS_SYSEX):
            port.send(mido.Message('sysex', data=data))
        time.sleep(FLUSH_DELAY)
    except Exception as e:
        return str(e)
    finally:
        port.close()
    return None


# ==============================================================================
# WINDOW
# ==============================================================================
class App:
    def __init__(self, root):
        self.root = root
        self.port = None
        self.done = False  # keeps the last result on screen until the controller is unplugged
        family = tkfont.nametofont('TkDefaultFont').actual()['family']
        root.title(LANG['title'])
        root.resizable(False, False)
        frame = tk.Frame(root, padx=20, pady=16)
        frame.pack()
        tk.Label(frame, text=LANG['heading'], font=(family, 14, 'bold')).pack(anchor='w')
        tk.Label(frame, text=LANG['subheading'], font=(family, 9), fg='#555',
                 wraplength=440, justify='left').pack(anchor='w', pady=(2, 8))
        self.status = tk.Label(frame, font=(family, 11), wraplength=440, justify='left')
        self.status.pack(anchor='w', pady=(8, 14))
        self.action = tk.Button(frame, text=LANG['button'], font=(family, 10, 'bold'), width=22,
                                command=self.run)
        self.action.pack(anchor='w')
        footer = tk.Frame(frame)
        footer.pack(fill='x', pady=(16, 0))
        tk.Label(footer, text=LANG['footer'], font=(family, 8), fg='#777').pack(side='left')
        link = tk.Label(footer, text='GitHub', font=(family, 8, 'underline'), fg='#0563c1', cursor='hand2')
        link.pack(side='right')
        link.bind('<Button-1>', lambda _: webbrowser.open(REPO_URL))
        if mido is None:
            self.show(LANG['missing_deps'], '#b00', False)
        else:
            self.poll()

    def show(self, text, color, can_run):
        self.status.config(text=text, fg=color)
        self.action.config(state='normal' if can_run else 'disabled')

    def poll(self):
        """Looks for the controller every POLL_MS, so plugging it in is enough."""
        try:
            port = get_numark_port()
        except Exception as e:  # e.g. no MIDI backend or ALSA sequencer
            self.port, self.done = None, False
            self.show(LANG['midi_err'].format(err=e), '#b00', False)
        else:
            if port != self.port:
                self.port, self.done = port, False
            if not self.done:
                if port is None:
                    self.show(LANG['not_found'], '#b00', False)
                else:
                    self.show(LANG['detected'].format(name=port), '#000', True)
        self.root.after(POLL_MS, self.poll)

    def run(self):
        self.show(LANG['sending'], '#555', False)
        self.root.config(cursor='watch')
        self.root.update()
        try:
            error = exit_demo_mode(self.port)
        finally:
            self.root.config(cursor='')
        self.done = True  # the next poll keeps this result on screen
        if error:
            self.show(LANG['failed'].format(err=error), '#b00', True)
        else:
            self.show(LANG['success'], '#070', True)


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()
    return 0


if __name__ == '__main__':
    sys.exit(main())
