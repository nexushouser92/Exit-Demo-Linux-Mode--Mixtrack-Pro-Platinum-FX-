"""Tests for main.py with a fake mido: no controller is needed.

Run with: python3 -m unittest discover -s tests
"""
import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import main

try:
    import mido as real_mido
except ImportError:
    real_mido = None


class FakePort:
    def __init__(self, fail_send=False):
        self.fail_send, self.sent, self.closed = fail_send, [], False

    def send(self, msg):
        if self.fail_send:
            raise OSError('send failed')
        self.sent.append(msg)

    def close(self):
        self.closed = True


class FakeMido:
    def __init__(self, outputs=(), open_error=None, port=None):
        self.outputs, self.open_error = list(outputs), open_error
        self.port = port or FakePort()
        self.opened = []

    def get_output_names(self):
        return self.outputs

    def open_output(self, name):
        if self.open_error:
            raise self.open_error
        self.opened.append(name)
        return self.port

    @staticmethod
    def Message(kind, data):
        return (kind, list(data))


def with_mido(fake):
    return mock.patch.object(main, 'mido', fake)


class DetectionTests(unittest.TestCase):
    def test_finds_mixtrack(self):
        with with_mido(FakeMido(['Midi Through:Midi Through Port-0 14:0', 'MixTrack Platinum FX:MixTrack Platinum FX MIDI 1 20:0'])):
            self.assertEqual(main.get_numark_port(), 'MixTrack Platinum FX:MixTrack Platinum FX MIDI 1 20:0')

    def test_ignores_other_fx_and_numark_devices(self):
        with with_mido(FakeMido(['Zoom MultiFX 24:0', 'Numark Party Mix 28:0'])):
            self.assertIsNone(main.get_numark_port())

    def test_no_devices(self):
        with with_mido(FakeMido([])):
            self.assertIsNone(main.get_numark_port())


@mock.patch.object(main, 'FLUSH_DELAY', 0)
class SendTests(unittest.TestCase):
    def test_sends_both_messages_and_closes(self):
        fake = FakeMido()
        with with_mido(fake):
            self.assertIsNone(main.exit_demo_mode('MixTrack Pro FX'))
        self.assertEqual(fake.opened, ['MixTrack Pro FX'])
        self.assertEqual(fake.port.sent, [('sysex', main.EXIT_DEMO_SYSEX), ('sysex', main.STATUS_SYSEX)])
        self.assertTrue(fake.port.closed)

    def test_port_busy(self):
        fake = FakeMido(open_error=OSError('Device or resource busy'))
        with with_mido(fake):
            self.assertIn('busy', main.exit_demo_mode('MixTrack Pro FX'))

    def test_send_error_still_closes(self):
        fake = FakeMido(port=FakePort(fail_send=True))
        with with_mido(fake):
            self.assertIn('send failed', main.exit_demo_mode('MixTrack Pro FX'))
        self.assertTrue(fake.port.closed)

    def test_messages_are_valid_sysex_data(self):
        for data in (main.EXIT_DEMO_SYSEX, main.STATUS_SYSEX):
            self.assertTrue(all(b < 0x80 for b in data))


@unittest.skipUnless(real_mido, 'mido is not installed')
class RealMidoTests(unittest.TestCase):
    def test_exact_bytes_on_the_wire(self):
        self.assertEqual(real_mido.Message('sysex', data=main.EXIT_DEMO_SYSEX).bytes(),
                         [0xF0, 0x7E, 0x00, 0x06, 0x01, 0xF7])
        self.assertEqual(real_mido.Message('sysex', data=main.STATUS_SYSEX).bytes(),
                         [0xF0, 0x00, 0x20, 0x7F, 0x03, 0x01, 0xF7])


if __name__ == '__main__':
    unittest.main()
