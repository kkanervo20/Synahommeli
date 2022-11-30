import argparse
import time
import platform

import rtmidi

import keysight_kt33000
import numpy as np  # For keysight_kt33000 arrays

from audiolazy import midi2freq

num = 0

def midi_received(data, unused):
    global num
    msg, delta_time = data
    if len(msg) > 2:
        if msg[0] == 153:  # note on, channel 9
            key = (msg[1] - 36) % 16
            row = key // 4
            col = key % 4
            velocity = msg[2]
            print("FREQuency %d" % (row*10))
            print("MPD218 Pad (%d, %d): %d" % (row, col, velocity))
            return
    print("MIDI message: ", msg)
    print("FREQuency: %f \t Midi: %d \t I: %d" % (midi2freq(msg[1]-36 % 16), msg[1]-36 % 16, num))
    if msg[2] > 70:
        driver.system.write_string("FREQuency %f" % (midi2freq(msg[1]-36 % 16)))
        driver.system.write_string("OUTPut ON")
        num += 1
    else:
        num -= 1
    if num <= 0:
        driver.system.write_string("OUTPut OFf")
        num = 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--midi", type=str, default="MIDIIN2",
                        help="Keyword identifying the MIDI input device (default: %(default)s).")
    parser.add_argument("--ks", type=str, default="USB0::0x0957::0x0407::MY44016868::0::INSTR", help="KS Resource name")
    args = parser.parse_args()

    # Keysight options
    resource_name = args.ks
    #resource_name = "TCPIP0::<IP_Address>::INSTR"
    idQuery = True
    reset   = True
    options = "QueryInstrStatus=true, Simulate=false, Trace=true"

    

    # Call driver constructor with options
    global driver # May be used in other functions
    driver = None
    driver = keysight_kt33000.Kt33000(resource_name, idQuery, reset, options)

    driver.status.standard_event.enable_register = keysight_kt33000.StatusStandardEventFlags.OPERATION_COMPLETE
    driver.status.service_request_enable_register = keysight_kt33000.StatusByteFlags.STANDARD_EVENT_SUMMARY
    driver.status.clear() # Clear error queue and event registers for new events

    driver.system.write_string("FUNCtion SINusoid")
    driver.system.write_string("OUTPut:HIGH Z")
    driver.system.write_string("VOLTage 1")
    driver.system.write_string("OUTPut OFf")


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
            print(
                "Virtual MIDI inputs are not currently supported on Windows, see python-rtmidi documentation.")
        else:
            print("Creating virtual MIDI input.")
            midi_in.open_virtual_port(args.midi)

    if not midi_in.is_port_open():
        print("No MIDI device opened, exiting.")

    else:
        print("Waiting for input.")
        while True:
            time.sleep(1)

