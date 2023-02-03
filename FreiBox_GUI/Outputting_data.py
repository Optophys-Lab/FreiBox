import os
import csv
import time
import itertools



# check if appropriate folder for output exists
# if not make it
def make_output_folders(first_trial_or_not, user_input, path):
    if first_trial_or_not < 1:

        if not os.path.exists(path + str(user_input["Subject"])):
            os.makedirs(path + str(user_input["Subject"]))
    else:
        pass


def write_output_into_csv(my_zipped_list, first_trial_over_bool, user_input, date_and_time, header,path):
    make_output_folders(first_trial_over_bool, user_input,path)
    if first_trial_over_bool < 1:
        with open(path + str(user_input["Subject"]) + '\\' + str(date_and_time)+ '_' + str(user_input["Subject"]+'_behavior.csv'), "w", newline='') as f:
            # first, we fill in all headers
            f.write(','.join(header))
            f.write('\n')
            writer = csv.writer(f, delimiter=",")
            # then add all data below headers
            for i in my_zipped_list:
                writer.writerow(i)
    else:
        with open(path + str(user_input["Subject"]) + '\\' + str(date_and_time)+ '_' + str(user_input["Subject"]+'_behavior.csv'), "a", newline='') as f:
            writer = csv.writer(f, delimiter=",")
            # then add all data below headers
            for i in my_zipped_list:
                writer.writerow(i)


def finalize_output(first_trial_bool,user_input, daylist, start_t_list,current_trial_number, laser_in_words, \
                        laser_b_in_words,date_and_time, header,lickingBlockType_list, lickingResult_w_number_list, \
                        lightONTime_list,enter_npp_list,leave_npp_list, enter_lick_chamber_list, omissionTime_list,\
                        auditoryCueTime_list,errorTime_list, missTime_list, hit_time_list, rewardDeliveryTime_list,\
                        laser_on_list,laser_off_list,trialEnd_list, pythonTransfer_StartTime_list,\
                        pythonTransfer_EndTime_list, lick_array_list, lick_array_incorrect_spout_list, \
                        lick_array_CorrectSpout_Anticipation_list, lick_array_UnCorrectSpout_Anticipation_list,\
                        lick_array_CorrectSpout_PostReward_list,lick_array_UnCorrectSpout_PostReward_list,\
                        ChamberLeave_array_Response_Window_list,ChamberLeave_array_Anticipation_list,\
                        ChamberLeave_array_PostReward_list, path):

    # time of session end
    end_time = time.strftime("%H:%M:%S")
    end_t_list = [str(end_time)]

    my_zipped_list = zip([user_input["Subject"]], daylist, start_t_list, end_t_list,
                                               user_input['Train'], [current_trial_number],
                                               [lickingBlockType_list[-1]],
                                               [lickingResult_w_number_list[-1]],
                                               [lightONTime_list[-1]], [enter_npp_list[-1]],
                                               [leave_npp_list[-1]], [enter_lick_chamber_list[-1]],
                                               [omissionTime_list[-1]], [auditoryCueTime_list[-1]],
                                               [errorTime_list[-1]], [missTime_list[-1]],
                                               [hit_time_list[-1]], [rewardDeliveryTime_list[-1]],
                                               [laser_on_list[-1]], [laser_off_list[-1]],
                                               [trialEnd_list[-1]], [pythonTransfer_StartTime_list[-1]],
                                               [pythonTransfer_EndTime_list[-1]], [lick_array_list[-1]],
                                               [lick_array_incorrect_spout_list[-1]],
                                               [lick_array_CorrectSpout_Anticipation_list[-1]],
                                               [lick_array_UnCorrectSpout_Anticipation_list[-1]],
                                               [lick_array_CorrectSpout_PostReward_list[-1]],
                                               [lick_array_UnCorrectSpout_PostReward_list[-1]],
                                               [ChamberLeave_array_Response_Window_list[-1]],
                                               [ChamberLeave_array_Anticipation_list[-1]]  ,
                                               [ChamberLeave_array_PostReward_list[-1]],
                                               [user_input["Block_number"]], [user_input["Block_length"]],
                                               [user_input["First_block"]],
                                               [user_input["ITI_length"]], [user_input["Resp"]],
                                               [user_input["Walk"]], [user_input["To_gate"]],
                                               [user_input["Wait_antic"]], [user_input["Post_rew"]],
                                               [user_input["Hit"]], [user_input["Lick"]], [user_input["Pump"]],
                                               [user_input["Cue"]], [user_input["Wind"]], [laser_in_words],
                                               [laser_b_in_words], user_input['Las_p'],
                                               [user_input["Rew_prob"]],[user_input["Extra_info"]])

    # write experimental data into csv file
    write_output_into_csv(my_zipped_list, first_trial_bool, user_input, date_and_time, header,path)