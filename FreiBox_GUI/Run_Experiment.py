import serial
from Plot_progress import print_and_plot_session_stats
from Setup_variables import *
from GUI_preparations import *
from Helper_fcts_run_exp import data_to_time_stamps_in_s
from Outputting_data import finalize_output
from Send_parameters import send_parameters_to_arduino

# set path for output file
path = "C:\\Users\\ms823\\My Documents\\Double_lick_spout\\DREADD_OFC_pilot_Aug2022\\raw_data\\"
# specify arduino and transmission parameters
com = 'COM15'
arduino = serial.Serial(com, baudrate=38400, inter_byte_timeout=0.1, timeout=1)


# Prepare GUI
# GUI has 2 windows. The first for parameters we commonly change, the second for parameters we usually keep the same
def prepare_first_GUI_window():
    root.title("Parameter choice")  # title
    root.geometry("750x650")  # size
    # set default for each GUI parameter
    for parameter_default in [[training_stage, training_stage_options], [block_number, block_number_options],
                              [block_length, block_length_options], [first_block, first_block_options],
                              [iti_length, iti_length_options], [response_window, response_window_options],
                              [time_nosepoke_to_gate_open, time_nosepoke_to_gate_open_options],
                              [wait_anticipation, wait_anticipation_options], [post_reward, post_reward_options],
                              [hit_lick_number, hit_lick_number_options],
                              [lick_reading_delay, lick_reading_delay_options],
                              [pump, pump_options], [reward_cue, reward_cue_options],
                              [sliding_window, sliding_window_options], [laser, laser_options],
                              [laser_block, laser_block_options], [laser_prob, laser_prob_options],
                              [walk_time, walk_time_options], [reward_prob, rew_prob_options]]:
        parameter_default[0].set(parameter_default[1][0])
    # save default parameters in user_input dictionary
    user_input["Train"] = training_stage
    user_input["Block_number"] = block_number
    user_input["Block_length"] = block_length
    user_input["First_block"] = first_block
    user_input["ITI_length"] = iti_length
    user_input["Resp"] = response_window
    user_input["To_gate"] = time_nosepoke_to_gate_open
    user_input["Wait_antic"] = wait_anticipation
    user_input["Post_rew"] = post_reward
    user_input["Hit"] = hit_lick_number
    user_input["Lick"] = lick_reading_delay
    user_input["Pump"] = pump
    user_input["Cue"] = reward_cue
    user_input["Las_t"] = laser
    user_input["Las_b"] = laser_block
    user_input["Wind"] = sliding_window
    user_input["Las_p"] = laser_prob
    user_input["Walk"] = walk_time
    user_input["Rew_prob"] = reward_prob
    user_input["Subject"] = "0"
    user_input["Extra_info"] = ""


# Set dropdown menus in the first GUI window
def dropdownmenus():
    # this iterator serves to separate the dropdown menus equally into 2 columns
    iterator = 2  # number of columns in GUI
    # all parameters we want to set in the first GUI window
    for parameter in [[training_stage, training_stage_options, 'Training Stage'],
                      [block_number, block_number_options, "Block nr"],
                      [block_length, block_length_options, 'Block length'],
                      [first_block, first_block_options, 'First block'],
                      [wait_anticipation, wait_anticipation_options, 'Reward anticipation \n time (ms)'],
                      [pump, pump_options, 'Pump opening (ms)'],
                      [sliding_window, sliding_window_options, 'Sliding window'],
                      [laser, laser_options, 'Laser time'], [laser_block, laser_block_options, 'Laser block'],
                      [laser_prob, laser_prob_options, 'Laser probability'],
                      [reward_prob, rew_prob_options, 'Reward probability']]:
        # first 6 dropdown menus go in column 1
        if iterator < 7:
            Label(root, width=20, text=parameter[2], font=("Helvetica", 14)).grid(row=iterator, sticky=W, pady=20)
            dropdown = OptionMenu(root, parameter[0], *parameter[1])
            dropdown.grid(row=iterator, column=1)  # position of each dropdown window
        # after the first 6, all remaining dropdown menus go in column 2
        else:
            Label(root, width=20, text=parameter[2],
                  font=("Helvetica", 14)).grid(row=iterator - 7, column=2, sticky=W, pady=20)
            dropdown = OptionMenu(root, parameter[0], *parameter[1])
            dropdown.grid(row=iterator - 7, column=3)  # position
        dropdown.config(font=("Helvetica", 12))  # font
        iterator += 1
        # keep track of "extra information" user inputs into the GUI, so we can output this later
        user_choice_list.append(parameter[0])
    return user_choice_list  # return updated list of user choices


# second GUI window for parameters not usually subject to change
def open_second_GUI_window():
    # Toplevel object which will be treated as a new window
    new_window = Toplevel(root)
    # sets the title
    new_window.title("Extra Parameters")
    # sets size
    new_window.geometry("700x500")
    # iterator to again display options in 2 separate columns
    iterator = 1
    # cycle through all parameters in 2nd GUI window
    for parameter in [[time_nosepoke_to_gate_open, time_nosepoke_to_gate_open_options, 'Time to gate opening (s)'],
                      [walk_time, walk_time_options, 'Walk Time (s)'],
                      [response_window, response_window_options, 'Response \n window (s)'],
                      [hit_lick_number, hit_lick_number_options, 'Nr of licks for Hit'],
                      [lick_reading_delay, lick_reading_delay_options, 'Lick reading \n delay (ms)'],
                      [reward_cue, reward_cue_options, 'Cue (kHz)'],
                      [post_reward, post_reward_options, 'Post reward  \n time (ms)'],
                      [iti_length, iti_length_options, 'ITI (s)']]:
        # first 4 dropdown menus go in column 1
        if iterator < 5:
            Label(new_window, width=20, text=parameter[2],
                  font=("Helvetica", 14)).grid(row=iterator, sticky=W, pady=20)
            dropdown = OptionMenu(new_window, parameter[0], *parameter[1])
            dropdown.grid(row=iterator, column=1)
        # after the first 6, all remaining dropdown menus go in column 2
        else:
            Label(new_window, width=20, text=parameter[2],
                  font=("Helvetica", 14)).grid(row=iterator - 4, column=2, sticky=W, pady=20)
            dropdown = OptionMenu(new_window, parameter[0], *parameter[1])
            dropdown.grid(row=iterator - 4, column=3)
        dropdown.config(font=("Helvetica", 12))  # font
        iterator += 1
        user_choices_window2.append(parameter[0])  # again save "extra information" from user
    # button to start experiment
    button = Button(new_window, text="Start Experiment", width=17, height=3, font=('Helvetica', '18', 'bold'),
                    foreground='Green', command=root.quit)
    button.grid(row=20, column=1, columnspan=2, sticky=W + S + E + N, pady=15)  # positioning


# start GUI, save user choices
def run_GUI(input_local):
    # extract user input
    input_read, laser_in_words_local, laser_b_in_words_local = check_choices(user_choices_window1, user_choices_window2,
                                                                             input_local)
    return input_read, laser_in_words_local, laser_b_in_words_local


# start setting up GUI
root = Tk()
# set default values for each parameter
# First window
block_number = StringVar(root)
block_length = StringVar(root)
first_block = StringVar(root)
wait_anticipation = StringVar(root)
pump = StringVar(root)
sliding_window = StringVar(root)
laser = StringVar(root)
laser_block = StringVar(root)
training_stage = StringVar(root)
laser_prob = StringVar(root)
reward_prob = StringVar(root)
# Second window
time_nosepoke_to_gate_open = StringVar(root)
walk_time = StringVar(root)
response_window = StringVar(root)
hit_lick_number = StringVar(root)
lick_reading_delay = StringVar(root)
reward_cue = StringVar(root)
post_reward = StringVar(root)
iti_length = StringVar(root)
# Set up first GUI window
prepare_first_GUI_window()
# Add fill-in fields for subject number and experiment
subject_nr, extra_info = fields_to_write_in(root)
# a button widget which will open the second window on button click
btn = Button(root, text="Continue to extra parameters", width=5, height=2, font=('Helvetica', '18', 'italic'),
             command=open_second_GUI_window)
btn.grid(row=9, column=1, columnspan=2, sticky=W + S + E + N, pady=15)  # position

# add dropdown menus
user_choices_window1 = dropdownmenus()
# start GUI!
mainloop()
# save user input
user_input, laser_in_words, laser_b_in_words = run_GUI(user_input)
# kill GUI after it has been used
root.destroy()
# wait a little, then send GUI parameters to arduino
time.sleep(1)
send_parameters_to_arduino(arduino, user_input)
# start session timer
start_time = time.time()  # in seconds
# reset buffer for new incoming data
arduino.reset_input_buffer()
arduino.reset_output_buffer()
# Main loop for python-arduino data exchange
while True:
    # checks for input from Arduino
    if arduino.in_waiting > 0:
        # initialize list to keep track of how many parameters we have already received from the arduino
        list_of_read_variables = []
        # keep checking for arduino input until we have received all expected parameters
        while len(set(list_of_read_variables)) <= (len(dict_output_arrays.keys()) + len(dict_data.keys())) + 1:
            # read Arduino input
            ser_bytes = arduino.readline()
            # decode Arduino input
            decoded_strings = str(ser_bytes[:-2].decode("utf-8"))
            if decoded_strings:
                print(decoded_strings)  # print arduino input
                # first deal with all single-value input parameters
                for key, value in dict_data.items():  # dictionary containing keys to identify each expected parameter
                    if key in decoded_strings:
                        # check only parameters we have not yet received
                        if key not in list_of_read_variables:
                            # keep track of read parameters
                            list_of_read_variables.append(key)
                            # transfer the data to timestamps in s and save it in dictionary
                            data_in_s = data_to_time_stamps_in_s(decoded_strings, key, value)
                            break
                # separate treatment for array-type input because here we have several incoming values to parse
                else:
                    # dictionary containing keys to identify each expected array
                    for description, list_of_arrays in list(dict_output_arrays.items()):
                        if description in decoded_strings and description not in list_of_read_variables:
                            # keep track of read parameters
                            list_of_read_variables.append(description)
                            # strip data from its descriptor
                            data = decoded_strings.strip(description)
                            if data:
                                # values in array separated by ;
                                data_separated = data.split(';')
                                # check if we have any values other than '0' in the array
                                if len(set(data_separated)) > 1:
                                    single_trial_data = []
                                    for number in data_separated:
                                        if number != '0':
                                            try:
                                                float(number)
                                                # transfer the data to timestamps in s
                                                single_trial_data.append(float(number) / 1000 / 1000)
                                            except ValueError:
                                                pass
                                    list_of_arrays.append(single_trial_data)  # save into nested list
                                else:
                                    list_of_arrays.append([float(-1)])
                                # store in array dictionary
                                dict_output_arrays[description] = dict_output_arrays[description] + list_of_arrays
                                break
                    else:
                        # marker from arduino for session end
                        if "done" in decoded_strings:
                            done = 1
                            break
            # check if we have received all expected data, then signal arduino that data transfer had concluded
            if len(set(list_of_read_variables)) == len(dict_output_arrays.keys()) + len(dict_data.keys()):
                # signal for arduino to stop sending data
                arduino.write("rec".encode())
                print("STOP ARDUINO 1")
                # wait for data to arrive at arduino
                time.sleep(0.1)
                # during ITI, print and plot session statistics
                current_block_number, trials_in_old_block = print_and_plot_session_stats(
                    dict_data, user_input, current_trial_number, current_block_number, trials_in_old_block, com,
                    start_time)
                # keep track of current trial number
                current_trial_number = current_trial_number + 1
                # output data into csv file
                finalize_output(first_trial_over, user_input, current_trial_number, laser_in_words,
                                laser_b_in_words, dict_data, dict_output_arrays, path)
                # marker to distinguish first trial
                first_trial_over = 1
                # reset buffers
                time.sleep(3)
                arduino.reset_input_buffer()
                arduino.reset_output_buffer()
                list_of_read_variables = []  # reset for next trial
            # if we have not received all expected data, continue receiving
            else:
                continue
        # if we receive signal from the arduino that session has ended, break out of while loop
        if done > 0:
            break
    # time between each loop iteration
    time.sleep(0.01)
