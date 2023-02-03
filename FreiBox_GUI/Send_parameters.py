import time
import sys
import ctypes


def send_parameters_to_arduino(arduino, user_input):
    all_parameters_received = 0  # becomes 1 when all data received
    # stay in this loop until Arduino confirms it got all data OR abort signal is issued
    while all_parameters_received < 1:
        # send all parameters the user has set in GUI
        for key, value in user_input.items():
            arduino.write(key.encode())  # first send description
            arduino.write(value.encode())  # then value
            arduino.write("\n".encode())  # individual values are separated by \n
            # buffer response
            time.sleep(0.1)
            # simultaneously, we are reading the arduino
            ser_bytes = arduino.readline()
            decoded_strings = str(ser_bytes[:-2].decode("utf-8"))
            if decoded_strings:
                print(decoded_strings)
            # wait for Arduino's signal that it got all input from GUI
            if "COMPLETE" in decoded_strings:
                all_parameters_received = 1
                break
            # alternatively arduino can signal that session needs to be aborted due to hardware problems
            elif "ERROR" in decoded_strings:
                print("ABORT")
                message_box = ctypes.windll.user32.MessageBoxW
                message_box(None,
                            'Check hardware, you idiot! '
                            '\n Did you even turn the box on? '
                            '\n Lick spouts blocked? '
                            '\n Use your brain!',
                            'ERROR', 0x70000)
                sys.exit(0)
            # signal arduino that it can move on to experiment
            if all_parameters_received > 0:
                arduino.write("END".encode())
                arduino.write("\n".encode())
            # if arduino has not yet received everything, stay in loop and keep sending
            else:
                time.sleep(0.1)
