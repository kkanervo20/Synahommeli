"""
keysight_kt33000 Python API Status SRQ Example Program

Demonstrates how to setup the instrument status system to request service when
a supported condition occurs and how to detect the SRQ using 2 techniques:
    1. Polling the instrument status byte
    2. Asynchronous SRQ event callback

Runs in simulation mode without an instrument.

Requires Python 3.6 or newer and keysight_kt33000 Python module installed.
"""

import keysight_kt33000
import numpy as np # For keysight_kt33000 arrays
import time


def main():
    """
    Edit resourceName and options as needed.  resourceName is ignored if option Simulate=True
    For this example, resourceName may be a VISA address(e.g. "TCPIP0::<ipAddress or hostName>::INSTR") or a VISA alias.
    For more information on using VISA aliases, refer to the Keysight IO Libraries Connection Expert documentation.
    """
    resource_name = "USB0::0x0957::0x0407::MY44016868::0::INSTR"
    #resource_name = "TCPIP0::<IP_Address>::INSTR"
    idQuery = True
    reset   = True
    options = "QueryInstrStatus=true, Simulate=true, Trace=true"

    try:
        print("\n  keysight_kt33000 Python API Example1\n")

        # Call driver constructor with options
        global driver # May be used in other functions
        driver = None
        driver = keysight_kt33000.Kt33000(resource_name, idQuery, reset, options)
        print("Driver Initialized")

        #  Print a few identity properties
        print('  identifier: ', driver.identity.identifier)
        print('  model:      ', driver.identity.instrument_model)
        print('  resource:   ', driver.driver_operation.io_resource_descriptor)
        print('  options:    ', driver.driver_operation.driver_setup)


        # Configure and test SRQs
        print("\nTesting Service Request (SRQ) on OperationComplete...\n")

        # Configure status system to set StatusByte, RequestService bit on EventStatusRegister, OperationComplete bit.
        # Driver may include a Status.ConfigureServiceRequest method that does this.
        #driver.status.preset();
        driver.status.standard_event.enable_register = keysight_kt33000.StatusStandardEventFlags.OPERATION_COMPLETE
        driver.status.service_request_enable_register = keysight_kt33000.StatusByteFlags.STANDARD_EVENT_SUMMARY
        driver.status.clear() # Clear error queue and event registers for new events

        # Polling for SRQ technique
        # Program polls StatusByte while waiting for SRQ or until max time elapses.
        print("Testing polling status byte for SRQ")

        # Do something that will cause the SRQ event to be fired
        # Most but not all instruments support *OPC...
        driver.system.write_string("*OPC") # Sets ESR Operation Complete bit 0 when all pending operations are complete

        # Polling loop
        srq_occurred = False
        status_byte = keysight_kt33000.StatusByteFlags.NONE
        i=0
        while i < 10: # Wait up to 500ms (iterations * sleep time) for SRQ
            time.sleep(.050) # time sets polling interval
            status_byte = driver.status.serial_poll() # Use ReadstatusByte() on non-488.2 connections (e.g. SOCKET, ASRL)
            if driver.driver_operation.simulate:
                status_byte = keysight_kt33000.StatusByteFlags.REQUEST_SERVICE_SUMMARY # Simulate SRQ

            # StatusByteFlags enums have binary weighted integer values so they can be used for bitwise operations.
            if (status_byte.value & keysight_kt33000.StatusByteFlags.REQUEST_SERVICE_SUMMARY.value) == keysight_kt33000.StatusByteFlags.REQUEST_SERVICE_SUMMARY.value:
                print("  SRQ detected")
                # Service SRQ
                # Your code to query additional status registers to determine the specific source of the SRQ,
                # if needed, and to take appropriate action to service the SRQ.
                print("  SerialPoll(): {} ({})".format(status_byte, int(status_byte)))
                print("  EventStatusRegister:", driver.status.standard_event.read_event_register())
                print()
                srq_occurred = True
                break
            i += 1
        if not srq_occurred:
            print("  ** SRQ did not occur in allotted time\n")


        # Asynchronous SRQ event callback technique
        # Does not work on non-488.2 compliant I/O interface connections (e.g. SOCKET, ASRL)
        # Driver asynchronously calls an event handler method when SRQ occurs.  Program execution may continue.
        print("Testing asynchronous SRQ event callback")
        global handler_called
        handler_called = False

        # Register (add) the SRQ event handler method to be called when the event occurs
        event = driver.status.service_request_event # Get event object
        event.add(srq_event_handler) # Add handler
        #event += srq_event_handler  # Alternate syntax

        # Enable SRQ event callbacks
        driver.status.clear() # Clear error queue and event registers for new events
        driver.status.enable_service_request_events() # Enable SRQ callbacks

        # Do something that will cause the SRQ event to be fired
        # Most but not all instruments support *OPC...
        driver.system.write_string("*OPC") # Sets ESR Operation Complete bit 0 when all pending operations are complete
        time.sleep(.500) # Wait up to 500ms for SRQ but your program can continue to perform other tasks
        if not handler_called:
            print("  ** SRQ did not occur in allotted time\n")

        # Unregister (remove) the SRQ event handler method if done using it
        event.remove(srq_event_handler)
        #event -= srq_event_handler # Alternate syntax

        # End configure and test SRQs


        # Check instrument for errors
        print()
        while True:
            outVal = ()
            outVal = driver.utility.error_query()
            print("  error_query: code:", outVal[0], " message:", outVal[1])
            if(outVal[0] == 0): # 0 = No error, error queue empty
                break

    except Exception as e:
        print("\n  Exception:", e.__class__.__name__, e.args)

    finally:
        if driver is not None: # Skip close() if constructor failed
            driver.close()
        input("\nDone - Press Enter to Exit")


def srq_event_handler(args):
    # SRQ event handler function to be called when the event occurs
    global driver
    global handler_called
    handler_called = True
    print('  srq_event_handler called')

    # args.status_byte is the value of the StatusByte when the SRQ occurred including the ServiceRequest bit 6,
    # value 64.  It can be tested, if multiple StatusByte bits are configured to source SRQs, without interfering
    # with any other instrument IO.
    # Note: When run in simulation, args.status_byte will be set to StatusByteFlags.REQUEST_SERVICE_SUMMARY (64) and
    # and all other status event register queries will return StatusByteFlags.NONE (0).
    print("  args.status_byte: {} ({})".format(args.status_byte, int(args.status_byte)))

    # Code to query additional status registers to determine the specific source of the SRQ, if needed, and to
    # take appropriate action to service the SRQ.  Because this method is called asynchronously, any instrument
    # I/O done here may interfere with any I/O in progress from the main program execution.  Your code must
    # manage this appropriately...
    driver.system.clear_io();
    print("  EventStatusRegister:", driver.status.standard_event.read_event_register())
    print();


if __name__ == "__main__":
    main()