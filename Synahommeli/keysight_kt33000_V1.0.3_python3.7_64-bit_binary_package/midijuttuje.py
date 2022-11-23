#!/usr/bin/env python3
"""A demonstration MIDI receiver which displays events."""
################################################################
# Written in 2018-2021 by Garth Zeglin <garthz@cmu.edu>

# To the extent possible under law, the author has dedicated all copyright
# and related and neighboring rights to this software to the public domain
# worldwide. This software is distributed without any warranty.

# You should have received a copy of the CC0 Public Domain Dedication along with this software.
# If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.

################################################################
# Standard Python libraries.
import argparse, time, platform

# For documentation on python-rtmidi: https://pypi.org/project/python-rtmidi/
import rtmidi

################################################################
def midi_received(data, unused):
    msg, delta_time = data
    if len(msg) > 2:
        if msg[0] == 153: # note on, channel 9
            key = (msg[1] - 36) % 16
            row = key // 4
            col = key % 4
            velocity = msg[2]
            print("MPD218 Pad (%d, %d): %d" % (row, col, velocity))
            return
    print("MIDI message: ", msg)
    
################################################################
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--midi", type=str, default = "MIDIIN2", help = "Keyword identifying the MIDI input device (default: %(default)s).")
    args = parser.parse_args()

    # Initialize the MIDI input system and read the currently available ports.
    midi_in = rtmidi.MidiIn()
    for idx, name in enumerate(midi_in.get_ports()):
        if args.midi in name:
            print("Found preferred MIDI input device %d: %s" % (idx, name))
            midi_in.open_port(idx)
            midi_in.set_callback(midi_received)
            break
        else:
            print("Ignoring unselected MIDI device: ", name)

    if not midi_in.is_port_open():
        if platform.system() == 'Windows':
            print("Virtual MIDI inputs are not currently supported on Windows, see python-rtmidi documentation.")
        else:
            print("Creating virtual MIDI input.")
            midi_in.open_virtual_port(args.midi)
    
    if not midi_in.is_port_open():
        print("No MIDI device opened, exiting.")

    else:
        print("Waiting for input.")
        while True:
            time.sleep(1)