import serial
import time
import os
from tkinter import *
import sys
import ctypes
import matplotlib.pyplot as plt
import numpy as np

from Plot_progress_during_session import update_plot
from Setup_variables import *
from GUI_preparations import fields_to_write_in, check_choices
from Helper_fcts_run_exp import check_if_block_changed
from Outputting_data import finalize_output


# Variables for GUI input data
user_input = {'Subject': "5",
              'Extra_info': "5",
              'Block_number': "4",
              'Block_length': "3",
              'First_block': "5",
              'ITI_length': "3",
              'Resp': '2',
              'To_gate': "1",
              'Wait_antic': "1",
              'Post_rew': "5",
              'Hit': "7",
              'Lick': "7",
              'Pump': "9",
              'Cue': "3",
              'Wind': '1',
              'Las_t': '1',
              'Las_b': '1',
              'Las_p': '3',
              'Train': '5',
              'Walk': '4'}


training_stage_options = [
    '1',
    '2',
    '3',
    '4',
    '5',
    '6'
]
block_number_options = [
    "1",
    "2",
    "3",
    "5",
    "10",
    "20"
]
block_length_options = [

    "50",
    "3",
    "5",
    "10"
]
first_block_options = [
    "Right",
    "Left"
]
iti_length_options = [  # in s
    "3",
    "2"
]

response_window_options = [  # in s
    "7",
    "1"
]
walk_time_options = [  # in s
    "5",
    "10"
]
time_nosepoke_to_gate_open_options = [  # in ms
    "500",
    "200"
]
wait_anticipation_options = [  # in ms

    "1",
    "1000",
    "1",
    "700"
]
post_reward_options = [  # in ms

    "4000"
]
hit_lick_number_options = [
    "3",
    "2"
]
lick_reading_delay_options = [  # in ms
    "50"
]
pump_options = [  # in ms
    "50",
    "10",
    "20"
]
reward_cue_options = [  # in kHz
    "5000",
    "3000"
]
moving_window_options = [

    '10',
    '20',
    '50'
]
laser_options = [
    'None',
    'Walking',
    'Response',
    'Anticipation',
    'Post Reward',
    'Antic. + Post Rew.',
    'All periods'
]
laser_block_options = [
    'None',
    '1',
    '2',
    '3'
]
laser_prob_options = [
    '100',
    '50',
    '0'
]

# initialize
last_decoded_string = " "


def send_parameters_to_arduino():
    all_parameters_received = 0  # becomes 1 when all data received
    # stay in this loop until Arduino confirms it got all data OR abort signal is issued
    while all_parameters_received < 1:
        ser_bytes = arduino.readline()
        decoded_strings = str(ser_bytes[:-2].decode("utf-8"))
        #if decoded_strings:
            #print(decoded_strings)
        for key, value in user_input.items():
            arduino.write(key.encode())  # first send description
            arduino.write(value.encode())  # then value
            arduino.write("\n".encode())  # individual values are separated by \n
            time.sleep(0.1)  # with the port open, the response will be buffered
            # simultaneously, we are reading what the arduino is echoing back so we can stop when Arduino has received
            # everything
            ser_bytes = arduino.readline()
            decoded_strings = str(ser_bytes[:-2].decode("utf-8"))
            if decoded_strings:
                print(decoded_strings)
            # wait for Arduino's signal that it got all input from GUI
            if "COMPLETE" in decoded_strings:
                all_parameters_received = 1
                break
            # this would be signal that session needs to be aborted due to hardware problems
            elif "ERROR" in decoded_strings:
                print("ABORT")
                import ctypes

                MessageBox = ctypes.windll.user32.MessageBoxW
                MessageBox(None,
                           'Check hardware, you idiot! \n Did you even turn the box on? \n Lick spouts blocked? \n Use your brain!',
                           'ERROR', 0x70000)
                sys.exit(0)
            if all_parameters_received > 0:
                # all GUI input has been successfully relayed to Arduino
                arduino.write("END".encode())
                arduino.write("\n".encode())
            else:
                time.sleep(0.1)


# read data, transfer time stamps into seconds and save in respective lists
def data_to_s_time_stamps_in_list(data_description, list_to_append):
    # isolate value from its description
    my_data = decoded_strings.strip(data_description)
    # safety precaution so code does not freeze when parts of the string accidentally end up here
    try:
        float(my_data)
        # different procedure for first value in a list and all the following.
        # reason: in order to find duplicates or truncated values, i compare new values to previous ones
        # this is impossible for first value, so i just save that one
        if len(list_to_append) > 0:
            # check if there are already enough values in this list to ignore duplicate values
            if len(list_to_append) > current_trial_number:
                pass
            # in case we DO still need a new value for this list / parameter
            else:
                # only for lists of time stamps: ignore truncated time stamps, which are much smaller than previous ones
                if data_description in lists_of_timestamps:
                    # not necessary for 0 values because those are boolean
                    if float(my_data) != 0:
                        # new time stamp needs to be larger than preceding one in time stamp list, otherwise it is
                        # truncated or something else went wrong with data transfer
                        if list_to_append[-1]:  # check if last value was None
                            if (float(my_data) / 1000 / 1000) > list_to_append[-1]:
                                # print("appending ", data_description, my_data)
                                list_to_append.append(float(my_data) / 1000 / 1000)  # in seconds
                            # this would be a truncated time stamp
                            elif (float(my_data) / 1000 / 1000) <= list_to_append[-1]:
                                # print('truncated time stamp or duplicate!')
                                list_of_read_variables.remove(data_description)
                        else:
                            list_to_append.append(float(my_data) / 1000 / 1000)

                    else:
                        list_to_append.append(float(-1))
                # all those safety precautions not necessary for logical values (non time stamps)
                else:
                    list_to_append.append(float(my_data))
                    # print("appending non timestamp")
        # for first value in any of the lists, no comparison with previous values possible, so the first value goes in
        # unchecked
        else:
            if data_description in lists_of_timestamps:
                if float(my_data) != 0:
                    list_to_append.append((float(my_data) / 1000 / 1000))  # in seconds
                else:
                    list_to_append.append(float(-1))
            else:
                list_to_append.append(float(my_data))
    # safety for when letters end up here
    except ValueError:
        pass


def print_and_plot_session_stats(current_block_nr_local, trials_in_old_block_local):
    # check if we have a new block
    is_it_new_block = check_if_block_changed(lickingBlockType_list)
    if is_it_new_block > 0:
        trials_in_old_block_local.append(current_trial_number)
        current_block_nr_local += 1
    # these lists will summarize what happened only in most recent block
    omissionTime_list_current_block = omissionTime_list[trials_in_old_block_local[current_block_nr_local - 1]:]
    hit_time_list_current_block = hit_time_list[trials_in_old_block_local[current_block_nr_local - 1]:]
    missTime_list_current_block = missTime_list[trials_in_old_block_local[current_block_nr_local - 1]:]
    errorTime_list_current_block = errorTime_list[trials_in_old_block_local[current_block_nr_local - 1]:]
    trials_current_block = (current_trial_number + 1) - trials_in_old_block_local[current_block_nr_local - 1]
    current_time = time.time()  # in seconds
    update_plot(current_block_nr_local, trials_in_old_block_local,user_input, rewardDeliveryTime_list, missTime_list, errorTime_list)
    print("Time passed: {} min".format((current_time - start_time) / 60.0))  # in minutes
    print("Current Block: {}".format(current_block_nr_local))
    print("Total Trials: {}; This Block: {}".format(current_trial_number + 1, trials_current_block))
    print("Total Omissions: {}; This Block: {}".format(sum(i > 0 for i in omissionTime_list),
                                                       sum(i > 0 for i in omissionTime_list_current_block)))
    print("Total Hits: {}; This Block: {}".format(sum(i > 0 for i in hit_time_list),
                                                  sum(i > 0 for i in hit_time_list_current_block)))
    print("Total Misses: {}; This Block: {}".format(sum(i > 0 for i in missTime_list),
                                                    sum(i > 0 for i in missTime_list_current_block)))
    print("Total Errors: {}; This Block: {}".format(sum(i > 0 for i in errorTime_list),
                                                    sum(i > 0 for i in errorTime_list_current_block)))

    try:
        lickingResult_w_number_list[-1]
        # translate code into description of scenario
        if int(lickingResult_w_number_list[-1]) >= float(user_input["Hit"]):
            licking_result_list_translated = 'Success'
        elif int(lickingResult_w_number_list[-1]) < 0:
            licking_result_list_translated = 'Error'
        else:
            licking_result_list_translated = 'Miss'
        print("Last trial's licking result: {}".format(licking_result_list_translated))
    except IndexError:
        pass
    return current_block_nr_local, trials_in_old_block_local


def call_finalize(first_trial_bool):
    finalize_output(first_trial_bool, user_input, daylist, start_t_list, current_trial_number, laser_in_words, \
                    laser_b_in_words, date_and_time, header, lickingBlockType_list, lickingResult_w_number_list, \
                    lightONTime_list, enter_npp_list, leave_npp_list, enter_lick_chamber_list, omissionTime_list, \
                    auditoryCueTime_list, errorTime_list, missTime_list, hit_time_list, rewardDeliveryTime_list, \
                    laser_on_list, laser_off_list, trialEnd_list, pythonTransfer_StartTime_list, \
                    pythonTransfer_EndTime_list, lick_array_list, lick_array_incorrect_spout_list, \
                    lick_array_CorrectSpout_Anticipation_list, lick_array_UnCorrectSpout_Anticipation_list, \
                    lick_array_CorrectSpout_PostReward_list, lick_array_UnCorrectSpout_PostReward_list, \
                    ChamberLeave_array_Response_Window_list, ChamberLeave_array_Anticipation_list, \
                    ChamberLeave_array_PostReward_list)

# function for GUI parts with dropdown menus
def dropdownmenus():
    # this iterator serves to separate the dropdownmenus equally into 2 columns
    iterator = 2
    for parameter in [[training_stage, training_stage_options, 'Training Stage'],
                      [block_number, block_number_options, "Block nr"],
                      [block_length, block_length_options,'Block length'],
                      [first_block, first_block_options, 'First block'],
                      [wait_anticipation, wait_anticipation_options, 'Reward anticipation \n time (ms)'],
                      [pump, pump_options, 'Pump opening (ms)'],
                      [moving_window, moving_window_options, 'Moving window'],
                      [laser, laser_options, 'Laser time'], [laser_block, laser_block_options, 'Laser block'],
                      [laser_prob, laser_prob_options, 'Laser probability']]:
        # first 5 dropdownmenus go in column 1
        if iterator < 6:
            lab = Label(root, width=20, text=parameter[2], font=("Helvetica", 14)).grid(row=iterator, sticky=W, pady=20)
            dropdown = OptionMenu(root, parameter[0], *parameter[1])
            dropdown.grid(row=iterator, column=1)
        # after the first 6, all remaining dropdown menus go in column 2
        else:
            lab = Label(root, width=20, text=parameter[2], font=("Helvetica", 14)).grid(row=iterator - 6, column=2,
                                                                                        sticky=W, pady=20)
            dropdown = OptionMenu(root, parameter[0], *parameter[1])
            dropdown.grid(row=iterator - 6, column=3)
        dropdown.config(font=("Helvetica", 12))
        iterator += 1
        user_choice_list.append(parameter[0])
    return user_choice_list


def prepare_GUI():
    root.title("Parameter choice")
    root.geometry("750x650")

    for parameter_default in [[training_stage, training_stage_options],
                              [block_number, block_number_options], [block_length, block_length_options],
                              [first_block,first_block_options], [iti_length,iti_length_options],[response_window,response_window_options],
                              [time_nosepoke_to_gate_open,  time_nosepoke_to_gate_open_options], [wait_anticipation,
                              wait_anticipation_options], [post_reward, post_reward_options], [hit_lick_number,
                              hit_lick_number_options], [lick_reading_delay, lick_reading_delay_options],
                              [pump, pump_options], [reward_cue, reward_cue_options],
                              [moving_window, moving_window_options], [laser, laser_options],
                              [laser_block, laser_block_options], [laser_prob, laser_prob_options], [walk_time,walk_time_options]]:
        parameter_default[0].set(parameter_default[1][0])

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
    user_input["Wind"] = moving_window
    user_input["Las_p"] = laser_prob
    user_input["Walk"] = walk_time
    user_input["Subject"] = "0"
    user_input["Extra_info"] = ""


def open_second_GUI_window():
    # Toplevel object which will be treated as a new window
    new_window = Toplevel(root)
    # sets the title of the
    # Toplevel widget
    new_window.title("Extra Parameters")
    # sets the geometry of toplevel
    new_window.geometry("700x500")
    iterator = 1
    for parameter in [ [time_nosepoke_to_gate_open, time_nosepoke_to_gate_open_options, 'Time to gate opening (s)'],
                       [walk_time, walk_time_options, 'Walk Time (s)'],
                       [response_window, response_window_options, 'Response \n window (s)'],
                       [hit_lick_number, hit_lick_number_options, 'Nr of licks for Hit'],
                       [lick_reading_delay, lick_reading_delay_options, 'Lick reading \n delay (ms)'],
                       [reward_cue, reward_cue_options, 'Cue (kHz)'],
                       [post_reward, post_reward_options, 'Post reward  \n time (ms)'],
                       [iti_length, iti_length_options, 'ITI (s)']]:
        # first 4 dropdownmenus go in column 1
        if iterator < 5:
            lab = Label(new_window, width=20, text=parameter[2], font=("Helvetica", 14)).grid(row=iterator, sticky=W, pady=20)
            dropdown = OptionMenu(new_window, parameter[0], *parameter[1])
            dropdown.grid(row=iterator, column=1)
        # after the first 6, all remaining dropdown menus go in column 2
        else:
            lab = Label(new_window, width=20, text=parameter[2], font=("Helvetica", 14)).grid(row=iterator - 4, column=2,
                                                                                        sticky=W, pady=20)
            dropdown = OptionMenu(new_window, parameter[0], *parameter[1])
            dropdown.grid(row=iterator - 4, column=3)

        dropdown.config(font=("Helvetica", 12))
        iterator += 1
        user_choices_window2.append(parameter[0])
    button = Button(new_window, text="Start Experiment", width=17, height=3, font=('Helvetica', '18', 'bold'),foreground='Green', command=root.quit)
    button.grid(row=20, column=1, columnspan=2, sticky=W + S + E + N, pady=15)




def run_GUI(user_input):

    # extract user input
    user_input, laser_in_words, laser_b_in_words = check_choices(user_choices_window1,user_choices_window2, user_input)
    return user_input, laser_in_words, laser_b_in_words


# start GUI, this needs to be out here as global variables
root = Tk()

# set default values for each parameter
#First window
block_number = StringVar(root)
block_length = StringVar(root)
first_block = StringVar(root)
wait_anticipation = StringVar(root)
pump = StringVar(root)
moving_window = StringVar(root)
laser = StringVar(root)
laser_block = StringVar(root)
training_stage = StringVar(root)
laser_prob = StringVar(root)
#second window
time_nosepoke_to_gate_open = StringVar(root)
walk_time = StringVar(root)
response_window = StringVar(root)
hit_lick_number = StringVar(root)
lick_reading_delay = StringVar(root)
reward_cue = StringVar(root)
post_reward = StringVar(root)
iti_length = StringVar(root)
prepare_GUI()

# add empty fields for subject number and experiment
subjectnr, extra_info = fields_to_write_in(root)

# OK button first window - for now disabled because it sucked
#button = Button(root, text="Start Experiment", width=7, height=3, font=('Helvetica', '18', 'bold'),foreground='Green', command=root.quit)
#button.grid(row=20, column=1, columnspan = 2, sticky=W+S+E+N, pady=15)
btn = Button(root,text="Continue to extra parameters",  width=5, height=2, font=('Helvetica', '18', 'italic'),
             command=open_second_GUI_window)
btn.grid(row=9, column=1, columnspan = 2, sticky=W+S+E+N, pady=15)

# add dropdown menus
user_choices_window1 = dropdownmenus()

# a button widget which will open a new window on button click

mainloop()
user_input, laser_in_words, laser_b_in_words = run_GUI(user_input)

# kill GUI
root.destroy()