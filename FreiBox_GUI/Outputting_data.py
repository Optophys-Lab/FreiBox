import os
import csv
import time
from Setup_variables import daylist, start_t_list,date_and_time, header


# check if appropriate folder for output exists
# if not make it
def make_output_folders(user_input, path):
    if not os.path.exists(path + str(user_input["Subject"])):
        os.makedirs(path + str(user_input["Subject"]))
    else:
        pass


def write_output_into_csv(my_zipped_list, first_trial_over_bool, user_input, path):
    # make folders to store output data in
    make_output_folders(user_input, path)
    # one folder per subject
    path_name = path + str(user_input["Subject"])
    # during the first trial, the csv file needs to be generated
    # later it will only be appended
    if first_trial_over_bool < 1:
        # csv file is named via subject, date and time of session
        with open(path_name + '\\' + str(date_and_time)+ '_' + str(user_input["Subject"] + '_behavior.csv'), "w",
                  newline='') as f:
            # first, fill in all headers
            f.write(','.join(header))
            f.write('\n')
            # then add all data below headers
            writer = csv.writer(f, delimiter=",")
            for i in my_zipped_list:
                writer.writerow(i)
    # after the first trial, csv file is merely appended
    else:
        with open(path_name + '\\' + str(date_and_time) + '_' + str(user_input["Subject"] + '_behavior.csv'), "a",
                  newline='') as f:
            writer = csv.writer(f, delimiter=",")
            for i in my_zipped_list:
                writer.writerow(i)


def finalize_output(first_trial_bool, user_input, current_trial_number, laser_in_words,  laser_b_in_words, dict_data,
                    dict_output_arrays, path):

    # keep track of time when trial ended
    end_time = time.strftime("%H:%M:%S")
    end_t_list = [str(end_time)]
    # zip all data to be exported in the csv file in the desired order
    my_zipped_list = zip([user_input["Subject"]], daylist, start_t_list, end_t_list,
                                               user_input['Train'], [current_trial_number],
                                               [dict_data["blo"][-1]], [dict_data["lio"][-1]],
                                               [dict_data["light"][-1]], [dict_data["enp"][-1]],
                                               [dict_data["lnp"][-1]], [dict_data["elc"][-1]],
                                               [dict_data["om"][-1]], [dict_data["cue"][-1]],
                                               [dict_data["err"][-1]], [dict_data["mi"][-1]],
                                               [dict_data["hit"][-1]], [dict_data["rew"][-1]],
                                               [dict_data["lon"][-1]], [dict_data["loff"][-1]],
                                               [dict_data["tel"][-1]], [dict_data["pts"][-1]],
                                               [dict_data["pte"][-1]], [dict_output_arrays["lal"][-1]],
                                               [dict_output_arrays["lar"][-1]], [dict_output_arrays["cs"][-1]],
                                               [dict_output_arrays["ua"][-1]], [dict_output_arrays["clp"][-1]],
                                               [dict_output_arrays["up"][-1]], [dict_output_arrays["crw"][-1]],
                                               [dict_output_arrays["ca"][-1]], [dict_output_arrays["cpr"][-1]],
                                               [user_input["Block_number"]], [user_input["Block_length"]],
                                               [user_input["First_block"]],[user_input["ITI_length"]],
                                               [user_input["Resp"]], [user_input["Walk"]], [user_input["To_gate"]],
                                               [user_input["Wait_antic"]], [user_input["Post_rew"]],
                                               [user_input["Hit"]], [user_input["Lick"]], [user_input["Pump"]],
                                               [user_input["Cue"]], [user_input["Wind"]], [laser_in_words],
                                               [laser_b_in_words], user_input['Las_p'],
                                               [user_input["Rew_prob"]], [user_input["Extra_info"]])

    # write experimental data into csv file
    write_output_into_csv(my_zipped_list, first_trial_bool, user_input, path)