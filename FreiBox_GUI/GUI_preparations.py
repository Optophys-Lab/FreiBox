from tkinter import *
import random 


# function for GUI parts with write-in option
def fields_to_write_in(root):
    # set variables for the 2 write-in options, subject number and extra information
    global subject_nr
    global extra_info
    for field in ["Subject", "Extra info"]:
        if field == "Subject":
            # set up write-in field
            Label(root, width=20, text=field, font=("Helvetica", 14)).grid(row=0, sticky=W, pady=20)
            subject_nr = StringVar()
            # set default value
            subject_nr.set("0")
            ent = Entry(root)
            ent.grid(row=0, column=1)
            subject_nr = ent
        elif field == "Extra info":
            # set up write-in field
            Label(root, width=20, text=field, font=("Helvetica", 14)).grid(row=1, sticky=W, pady=20)
            extra_info = StringVar()
            # set default value
            extra_info.set("")
            ent = Entry(root)
            ent.grid(row=1, column=1)
            extra_info = ent
    return subject_nr, extra_info


# function to check user input into GUI
def check_choices(input_first_window, input_second_window, user_input):
    # go through all parameters in the order in which they appear in the GUI
    user_input["Train"] = input_first_window[0].get()
    user_input["Block_number"] = input_first_window[1].get()
    user_input["Block_length"] = input_first_window[2].get()
    # First block direction (Right, left or random) needs to be coded into numbers
    first_block_in_words = input_first_window[3].get()
    if first_block_in_words == 'Right':
        user_input["First_block"] = '-1'
    elif first_block_in_words == 'Left':
        user_input["First_block"] = '1'
    # in case of "random", we need a random number generator to determine first block
    else:
        # set up list of options
        left_right_list = ['-1', '1']
        # pull randomly from list
        rand_index = random.randint(0, 1)
        rand_left_right = left_right_list[rand_index]
        # save into dictionary
        user_input["First_block"] = rand_left_right
    user_input["Wait_antic"] = input_first_window[4].get()
    user_input["Pump"] = input_first_window[5].get()
    user_input["Wind"] = input_first_window[6].get()
    # the task period where laser is applied also needs to be coded from words into numbers
    laser_in_words = input_first_window[7].get()
    # we distinguish between 4 different task periods and their combinations
    if laser_in_words == 'None':
        user_input["Las_t"] = '0'
    elif laser_in_words == 'Walking':
        user_input["Las_t"] = '1'
    elif laser_in_words == 'Response':
        user_input["Las_t"] = '2'
    elif laser_in_words == 'Anticipation':
        user_input["Las_t"] = '3'
    elif laser_in_words == 'Post Reward':
        user_input["Las_t"] = '4'
    elif laser_in_words == 'Antic. + Post Rew.':
        user_input["Las_t"] = '34'
    elif laser_in_words == 'Walk + Resp.':
        user_input["Las_t"] = '12'
    elif laser_in_words == 'Resp + Antic. + Post Rew.':
        user_input["Las_t"] = '234'
    elif laser_in_words == 'All periods':
        user_input["Las_t"] = '1234'
    # the block in which laser is applied
    laser_b_in_words = input_first_window[8].get()
    if laser_b_in_words == 'None':
        user_input['Las_b'] = '0'
    else:
        user_input['Las_b'] = laser_b_in_words
    user_input["Las_p"] = input_first_window[9].get()
    user_input["Rew_prob"] = input_first_window[10].get()
    # SECOND WINDOW
    user_input["To_gate"] = input_second_window[0].get()
    user_input["Walk"] = input_second_window[1].get()
    user_input["Resp"] = input_second_window[2].get()
    user_input["Hit"] = input_second_window[3].get()
    user_input["Lick"] = input_second_window[4].get()
    user_input["Cue"] = input_second_window[5].get()
    user_input["Post_rew"] = input_second_window[6].get()
    user_input["ITI_length"] = input_second_window[7].get()
    user_input["Subject"] = subject_nr.get()
    if user_input["Subject"] == "":
        user_input["Subject"] = "0"
    user_input["Extra_info"] = extra_info.get()
    # return user choices
    return user_input, laser_in_words, laser_b_in_words


