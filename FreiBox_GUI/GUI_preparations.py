from tkinter import *
import random 
from DataBaseConnection import animals, exp_templates, projects, sub_experiments

# function for GUI parts with write-in option
def fields_to_write_in(root):
    global subjectnr
    global extra_info
    global weight
    global weight_note
    global exptype
    global project
    global experiment_root
    global root_menu

    for field_id, field in enumerate(["Subject", "Extra info", 'Project', "ExpType", 'Sub_experiment', "Weight", "Weight Note"]):
        if field == "Subject":
            lab = Label(root, width=20, text=field, font=("Helvetica", 14)).grid(row=field_id, sticky=W, pady=20)
            subjectnr = StringVar()
            subjectnr.set("0")

            animal_menu = OptionMenu(root, subjectnr, *animals)
            animal_menu.grid(row=field_id, column=1)
            subjectnr = animal_menu

        elif field == "Extra info":
            lab = Label(root, width=20, text=field, font=("Helvetica", 14)).grid(row=field_id, sticky=W, pady=20)
            extra_info = StringVar()
            extra_info.set("")
            ent = Entry(root)
            ent.grid(row=field_id, column=1)
            extra_info = ent

        elif field == "Project":
            Label(root, width=20, text=field, font=("Helvetica", 14)).grid(row=field_id, sticky=W, pady=20)
            project = StringVar()
            project.set(projects[0])
            project_menu = OptionMenu(root, project, *projects)
            project_menu.grid(row=field_id, column=1)
            project.trace("w", callback_project)

        elif field == "ExpType":
            Label(root, width=20, text=field, font=("Helvetica", 14)).grid(row=field_id, sticky=W, pady=20)
            exptype = StringVar()
            exptype.set(exp_templates[0])
            exptyp_menu = OptionMenu(root, exptype, *exp_templates)
            exptyp_menu.grid(row=field_id, column=1)

        elif field == "Sub_experiment":
            Label(root, width=20, text=field, font=("Helvetica", 14)).grid(row=field_id, sticky=W, pady=20)
            experiment_root = StringVar()
            experiment_root.set(sub_experiments[project.get()][0])
            root_menu = OptionMenu(root, experiment_root, *sub_experiments[project.get()])
            root_menu.grid(row=field_id, column=1)

        elif field == "Weight":
            Label(root, width=20, text=field, font=("Helvetica", 14)).grid(row=field_id, sticky=W, pady=20)
            weight = StringVar()
            # set default value
            weight.set("")
            ent = Entry(root)
            ent.grid(row=field_id, column=1)
            weight = ent

        elif field == "Weight Note":
            Label(root, width=20, text=field, font=("Helvetica", 14)).grid(row=field_id, sticky=W, pady=20)
            weight_note = StringVar()
            # set default value
            weight_note.set("")
            ent = Entry(root)
            ent.grid(row=field_id, column=1)
            weight_note = ent
    return subjectnr, extra_info

def callback_project(*args):
    new_options = sub_experiments[project.get()]
    update_options(new_options)

def update_options(options_list):
    print('called')
    menu = root_menu.children["menu"]
    menu.delete(0, "end")
    for string in options_list:
        menu.add_command(label=string, command=lambda value=string: experiment_root.set(value))
    try:
        experiment_root.set(options_list[0])
    except IndexError:
        experiment_root.set("")



# function to check user's input into GUI
def check_choices(input_first_window, input_second_window, user_input):
    user_input["Train"] = input_first_window[0].get()
    user_input["Block_number"] = input_first_window[1].get()
    user_input["Block_length"] = input_first_window[2].get()
    first_block_in_words = input_first_window[3].get()
    # here, the code needs to be translated into words
    if first_block_in_words == 'Right':
        user_input["First_block"] = '-1'
    elif first_block_in_words == 'Left':
        user_input["First_block"] = '1'
    # random number generator
    else:
        left_right_list = ['-1', '1']
        rand_indx = random.randint(0, 1)
        print('rand_indx',rand_indx)
        rand_left_right = left_right_list[rand_indx]
        print('rand_left_right',rand_left_right)
        user_input["First_block"] = rand_left_right
    user_input["Wait_antic"] = input_first_window[4].get()
    user_input["Pump"] = input_first_window[5].get()
    user_input["Wind"] = input_first_window[6].get()

    laser_in_words = input_first_window[7].get()

    if laser_in_words == 'None':
        user_input["Las_t"] = '0'
    elif laser_in_words == 'Walking':
        user_input["Las_t"] = '1'
    elif laser_in_words == 'DelayWalking':
        user_input["Las_t"] = '8'
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
    elif laser_in_words =='Trial start':
        user_input["Las_t"] = '5'

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

    user_input["Subject"] = subjectnr.get()
    if user_input["Subject"] == "":
        user_input["Subject"] = "0"
    user_input["Extra_info"] = extra_info.get()
    user_input["weight"] = weight.get()
    user_input["weight note"] = weight_note.get()
    user_input["exp_type"] = exptype.get()
    # return user choices
    return user_input, laser_in_words, laser_b_in_words


