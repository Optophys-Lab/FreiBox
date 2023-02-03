import time


# Variables for output data
# prepare lists for output file
day = time.strftime("%d/%m/%Y")
start_time_clock = time.strftime("%H:%M:%S")
daylist = [str(day)]
date_and_time = str(time.strftime("%Y_%m_%d")) + "__" + str(time.strftime("%H_%M_%S"))
start_t_list = [str(start_time_clock)]

# Variables needed throughout experiment
trials_in_old_block = [0]
first_trial_over = 0

# for GUI
user_choice_list = []
user_choices_window2 = []

# initialize lists which will hold the output of each trial, sent from Arduino
lickingResult_w_number_list = []
TOTAL_TRIAL_list = []
lickingBlockType_list = []
lightONTime_list = []
enter_npp_list = []
leave_npp_list = []
enter_lick_chamber_list = []
omissionTime_list = []
auditoryCueTime_list = []
errorTime_list = []
missTime_list = []
hit_time_list = []
rewardDeliveryTime_list = []
trialEnd_list = []
pythonTransfer_StartTime_list = []
pythonTransfer_EndTime_list = []
lick_array_list = []
lick_array_incorrect_spout_list = []
lick_array_CorrectSpout_Anticipation_list = []
lick_array_UnCorrectSpout_Anticipation_list = []
lick_array_CorrectSpout_PostReward_list = []
lick_array_UnCorrectSpout_PostReward_list = []
ChamberLeave_array_Response_Window_list = []
ChamberLeave_array_Anticipation_list = []
ChamberLeave_array_PostReward_list = []
laser_off_list = []
laser_on_list = []
# this is to make results of previous trial readable later
current_block_number = 1

# initialization of other variables to coordinate Arduino communication
done = 0  # this becomes 1 at end of sessions
current_trial_number = 0  # this counts trials. important when looking for duplicate output values from Arduino

# Header for output CSV file
header = ["Subject", "Start_Date", "Start_Time", "End_Time", "Training_Stage", 'Trial_nr',
                 'Licking_block_type',  "Lick_result",
                 'Light_on', 'Enter_NPP_time', 'Leave_NPP_time', 'Enter_LC_time', 'Omission_time',
                 'Auditory_cue', 'Error_time', 'Miss_time', 'Hit_time', 'Reward_delivery', 'Laser_on_time',
                 'Laser_off_time', 'Trial_end',
                 'Python_transfer_start', 'Python_transfer_end',
                 'Lick_array_correct_spout_response_window', 'Lick_array_incorrect_spout_response_window',
                 "Lick_array_correct_spout_anticipation", "Lick_array_wrong_spout_anticipation",
                 "Lick_array_correct_spout_post_reward", "Lick_array_wrong_spout_post_reward",
                 "ChamberLeave_array_Response_Window", "Chamber_leave_array_anticipation",
                 "Chamber_leave_array_post_reward", "Block_number", "Block_length", "First_block", "ITI_length",
                 "Response_Window", "Walking_time",
                 "Time_to_gate", "Wait_antic", "Post_rew", "Hit", "Lick", "Pump", "Cue",
                 "Moving_window", "Laser_time", "Laser_block","Laser_prob","Reward_prob", "Extra_info"]

# this here will save all (single-value) data exported from the Arduino into a dictionary of lists
dict_data = {
    "lio": lickingResult_w_number_list,
    "blo": lickingBlockType_list,
    "light": lightONTime_list,
    "enp": enter_npp_list,
    "lnp": leave_npp_list,
    "elc": enter_lick_chamber_list,
    "om": omissionTime_list,
    "cue": auditoryCueTime_list,
    "err": errorTime_list,
    "mi": missTime_list,
    "hit": hit_time_list,
    "rew": rewardDeliveryTime_list,
    "tel": trialEnd_list,
    "lon": laser_on_list,
    "loff": laser_off_list,
    "pts": pythonTransfer_StartTime_list,
    "pte": pythonTransfer_EndTime_list
}

# save all the lists in the dictionary that consist of time stamps in here
lists_of_timestamps = ["light", "enp", "lnp", "elc", "om", "cue", "err", "mi", "hit", "rew",
                       "tel", "pts", "pte", "lon", "loff"]

# dictionary of arrays
dict_output_arrays = {
    "lal": lick_array_list,
    'lar': lick_array_incorrect_spout_list,
    "cs": lick_array_CorrectSpout_Anticipation_list,
    "ua": lick_array_UnCorrectSpout_Anticipation_list,
    "clp": lick_array_CorrectSpout_PostReward_list,
    "up": lick_array_UnCorrectSpout_PostReward_list,
    "crw": ChamberLeave_array_Response_Window_list,
    "ca": ChamberLeave_array_Anticipation_list,
    "cpr": ChamberLeave_array_PostReward_list
}