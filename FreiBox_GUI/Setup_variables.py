import time

# Variables for GUI input
# initial dictionary
user_input = {
    'Subject': "5",
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
    'Walk': '4',
    'Rew_prob': '5'
}
# available options for each parameter in the dictionary
training_stage_options = [
    '1',
    '2',
    '3',
    '4',
    '5',
    '6',
    '7'
]
block_number_options = [
    "4",
    "2",
    "3",
    "1"
]
block_length_options = [
    "20",
    '30'
]
first_block_options = [
    "Random",
    "Right",
    "Left"
]
iti_length_options = [  # in s
    "3",
    "2"
]
response_window_options = [  # in s
    "2",
    '1'
]
walk_time_options = [  # in s
    "5",
    "15"
]
time_nosepoke_to_gate_open_options = [  # in ms
    "500",
    "2000"
]
wait_anticipation_options = [  # in ms
    "1000",
    "2000"
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
    "10",
    "20"
]
reward_cue_options = [  # in kHz
    "5000",
    "3000"
]
sliding_window_options = [  # sliding window sizes
    '15'
]
laser_options = [  # available periods for laser stimulation
    'None',
    'Walking',
    'Response',
    'Anticipation',
    'Post Reward',
    'Antic. + Post Rew.',
    'Walk + Resp.',
    'Resp + Antic. + Post Rew.',
    'All periods'
]
laser_block_options = [  # available blocks for laser stimulation
    'None',
    '1',
    '2',
    '3',
    '123'
]
laser_prob_options = [  # available laser probabilities
    '100',
    '50',
    '0'
]
rew_prob_options = [  # available reward probabilities
    '75',
    '100',
    '50',
    '0'
]
# initialize variable for incoming data
last_decoded_string = " "
# Variables for output data, e.g. date and time of experiment
day = time.strftime("%d/%m/%Y")
start_time_clock = time.strftime("%H:%M:%S")
daylist = [str(day)]
date_and_time = str(time.strftime("%Y_%m_%d")) + "__" + str(time.strftime("%H_%M_%S"))
start_t_list = [str(start_time_clock)]
# Variables needed throughout experiment
trials_in_old_block = [0]
first_trial_over = 0
# initialize variables for GUI
user_choice_list = []
user_choices_window2 = []
# this is to make results of previous trial readable later
current_block_number = 1
# initialization of other variables to coordinate Arduino communication
done = 0  # this becomes 1 at end of sessions
current_trial_number = 0  # this counts trials. important when looking for duplicate output values from Arduino
# Header for output CSV file
header = ["Subject", "Start_Date", "Start_Time", "End_Time", "Training_Stage", 'Trial_nr', 'Licking_block_type',
          "Lick_result", 'Light_on', 'Enter_NPP_time', 'Leave_NPP_time', 'Enter_LC_time', 'Omission_time',
          'Auditory_cue', 'Error_time', 'Miss_time', 'Hit_time', 'Reward_delivery', 'Laser_on_time',
          'Laser_off_time', 'Trial_end', 'Python_transfer_start', 'Python_transfer_end',
          'Lick_array_correct_spout_response_window', 'Lick_array_incorrect_spout_response_window',
          "Lick_array_correct_spout_anticipation", "Lick_array_wrong_spout_anticipation",
          "Lick_array_correct_spout_post_reward", "Lick_array_wrong_spout_post_reward",
          "ChamberLeave_array_Response_Window", "Chamber_leave_array_anticipation",
          "Chamber_leave_array_post_reward", "Block_number", "Block_length", "First_block", "ITI_length",
          "Response_Window", "Walking_time", "Time_to_gate", "Wait_antic", "Post_rew", "Hit", "Lick", "Pump", "Cue",
          "Sliding_window", "Laser_time", "Laser_block", "Laser_prob", "Reward_prob", "Extra_info"]

# this here will save all (single-value) data exported from the Arduino into a dictionary of lists
dict_data = {
    "lio": [],
    "blo": [],
    "light": [],
    "enp": [],
    "lnp": [],
    "elc": [],
    "om": [],
    "cue": [],
    "err": [],
    "mi": [],
    "hit": [],
    "rew": [],
    "tel": [],
    "lon": [],
    "loff": [],
    "pts": [],
    "pte": []
}
# save all the lists in the dictionary that consist of time stamps in here
lists_of_timestamps = ["light", "enp", "lnp", "elc", "om", "cue", "err", "mi", "hit", "rew",
                       "tel", "lon", "loff", "pts", "pte"]
# dictionary of arrays
dict_output_arrays = {
    "lal": [],
    'lar': [],
    "cs": [],
    "ua": [],
    "clp": [],
    "up": [],
    "crw": [],
    "ca": [],
    "cpr": []
}
