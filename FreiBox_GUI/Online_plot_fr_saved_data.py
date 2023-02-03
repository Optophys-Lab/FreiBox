import matplotlib.pyplot as plt
import numpy as np
import os
from put_date_in_right_format import write_files_w_correct_date_format
from read_all_raw_data_into_dictionary import read_raw_data_into_df
from calculate_stats import calculate_stats
from pasupathy_plot import make_single_pasupathy_plot
from laser_analysis import extract_trials_to_crit_laser
from laser_plots import plot_trials_to_criterion__laser_vs_no_laser, plot_how_many_times_criterion_reached,\
    plot_RT_laser_vs_no_laser


def make_online_plot(data_single_mouse, mouse, file_location):
    print(mouse)
    number_of_sessions = len(data_single_mouse['Experiment'])
    # go through all sessions and extract data
    for session in range(0, number_of_sessions):
        date = data_single_mouse['Start_Date'][session]
        date_fixed = date[2:4] + "_" + date[5:7] + "_" + date[8:]
        time = data_single_mouse['Start_Time'][session]
        time_fixed = time[0:2] + "_" + time[3:5] + "_" + time[6:]
        print(date)
        print(date_fixed)
        print(time)
        print(time_fixed)
        if not os.path.exists(file_location + "\\Pasupathy_plots\\{}".format(
                mouse)):
            os.makedirs(file_location + "\\Pasupathy_plots\\{}".format(
                mouse))
        if not os.path.isfile(file_location + "\\Pasupathy_plots\\{}\\{}_Perf_aross_blocks_{}_{}.png".format(
                mouse, mouse, date_fixed, time_fixed)):
            number_of_blocks = data_single_mouse['Started_blocks'][session]
            miss_counts = []
            reward_counts = []
            error_counts = []
            miss_percs = []
            reward_percs = []
            error_percs = []
            error_percs_moving_window = []
            reward_percs_moving_window = []
            miss_percs_moving_window = []
            for iteration in range(1, number_of_blocks + 1):
                miss_counts.append(data_single_mouse['Miss_time_developing_counts_Block_nr_' + str(iteration)][session])
                reward_counts.append(
                    data_single_mouse['Reward_delivery_developing_counts_Block_nr_' + str(iteration)][session])
                error_counts.append(
                    data_single_mouse['Error_time_developing_counts_Block_nr_' + str(iteration)][session])
                miss_percs.append(
                    data_single_mouse['Miss_time_developing_percentage_Block_nr_' + str(iteration)][session])
                reward_percs.append(
                    data_single_mouse['Reward_delivery_developing_percentage_Block_nr_' + str(iteration)][session])
                error_percs.append(
                    data_single_mouse['Error_time_developing_percentage_Block_nr_' + str(iteration)][session])
                miss_percs_moving_window.append(
                    data_single_mouse['Miss_time_developing_percentage_moving_window_Block_nr_'
                                      + str(iteration)][session])
                reward_percs_moving_window.append(
                    data_single_mouse['Reward_delivery_developing_percentage_moving_window_Block_nr_'
                                      + str(iteration)][session])
                error_percs_moving_window.append(
                    data_single_mouse['Error_time_developing_percentage_moving_window_Block_nr_' + str(iteration)][
                        session])

            miss_counts_joined = list(itertools.chain.from_iterable(miss_counts))
            reward_counts_joined = list(itertools.chain.from_iterable(reward_counts))
            error_counts_joined = list(itertools.chain.from_iterable(error_counts))
            miss_percs_joined = list(itertools.chain.from_iterable(miss_percs))
            reward_percs_joined = list(itertools.chain.from_iterable(reward_percs))
            error_percs_joined = list(itertools.chain.from_iterable(error_percs))
            miss_percs_moving_window_joined = list(itertools.chain.from_iterable(miss_percs_moving_window))
            reward_percs_moving_window_joined = list(itertools.chain.from_iterable(reward_percs_moving_window))
            error_percs_moving_window_joined = list(itertools.chain.from_iterable(error_percs_moving_window))

            fig, (ax1, ax2, ax3) = plt.subplots(3, sharex=True, figsize=(30, 30))
            xaxis = np.arange(1, len(error_percs_joined) + 1)
            ax1.plot(xaxis, miss_percs_joined, color="blue", label="Miss", linewidth=10)
            ax1.plot(xaxis, reward_percs_joined, color="green", label="Reward", linewidth=10)
            ax1.plot(xaxis, error_percs_joined, color="red", label='Error', linewidth=10)
            ax1.set_xlim([0, len(error_percs_joined) + 1])
            ax1.set_ylim([-10, 110])
            ax1.set_ylabel("Performance in \n % (total)", fontsize=45)
            ax1.set_yticks(np.arange(0, 120, 20))
            ax1.set_yticklabels(["0", "20", "40", "60", "80", "100"], fontsize=45)

            ax2.plot(xaxis, miss_counts_joined, color="blue", label="Miss", linewidth=10)
            ax2.plot(xaxis, reward_counts_joined, color="green", label="Reward", linewidth=10)
            ax2.plot(xaxis, error_counts_joined, color="red", label='Error', linewidth=10)
            ax2.set_xlim([0, len(error_counts_joined) + 1])
            ax2.set_ylim([-10, 70])
            ax2.set_ylabel("Cumulative \n count", fontsize=45)
            ax2.set_yticks(np.arange(0, 70, 20))
            ax2.set_yticklabels(np.arange(0, 70, 20), fontsize=45)

            xaxis2 = np.arange(1, len(reward_percs_moving_window_joined) + 1)
            ax3.plot(xaxis2, miss_percs_moving_window_joined, color="blue", label="Miss", linewidth=10)
            ax3.plot(xaxis2, reward_percs_moving_window_joined, color="green", label="Reward", linewidth=10)
            ax3.plot(xaxis2, error_percs_moving_window_joined, color="red", label='Error', linewidth=10)
            ax3.set_ylim([-10, 110])
            ax3.set_ylabel("Performance in  % \n (moving window", fontsize=45)
            ax3.set_xticks(np.arange(0, len(miss_percs_joined) + 1, 10))
            ax3.set_xticklabels(np.arange(0, len(miss_percs_joined) + 1, 10), fontsize=45)
            ax3.set_yticks(np.arange(0, 120, 20))
            ax3.set_yticklabels(["0", "20", "40", "60", "80", "100"], fontsize=45)
            ax3.set_xlabel('Session number', fontsize=45)
            ax3.set_xlim(0, len(xaxis) + 1)
            ax3.set_xlabel('Trial number', fontsize=45)
            lines2, labels2 = ax1.get_legend_handles_labels()
            lines, labels = ax2.get_legend_handles_labels()
            lines6, labels6 = ax3.get_legend_handles_labels()
            ax1.legend(lines2, labels2, bbox_to_anchor=(1, 1.05), loc=2, fontsize=45)
            ax2.legend(lines, labels, bbox_to_anchor=(1, 1.05), loc=2, fontsize=45)
            ax3.legend(lines6, labels6, bbox_to_anchor=(1, 1.05), loc=2, fontsize=45)
            fig.suptitle(str(mouse) + " Performance", fontsize=60, weight='bold')
            if len(miss_counts) > 1:
                ax1.axvspan(len(reward_percs[0]), len(reward_percs[0]) + len(reward_percs[1]), facecolor='0.2',
                            alpha=0.2)
                ax2.axvspan(len(miss_counts[0]), len(miss_counts[0]) + len(miss_counts[1]), facecolor='0.2', alpha=0.2)
                ax3.axvspan(len(reward_percs[0]),
                            len(reward_percs[0]) + len(reward_percs[1]), facecolor='0.2', alpha=0.2)

            plt.savefig(
                file_location + "\\Pasupathy_plots\\{}\\{}_Perf_aross_blocks_{}_{}.png".format(
                    mouse, mouse, date_fixed, time_fixed), bbox_inches='tight')
            plt.close('all')


path = "C:\\Users\\ms823\\My Documents\\Double_lick_spout\\Two_ports\\New_opto_Nov2020\\"
path_raw_data = path + "raw_data\\"
max_block_nr = 3
markers_unwanted_sessions = ['Problem']
opto_mice = []
NPHR = ['7902', '7901', '7900', '7898', '7920']
EYFP = ['7196', '7896', '7895', '7339', '7340']
write_files_w_correct_date_format(path_raw_data)
dataframes_raw_data_all_animals = read_raw_data_into_df(path_raw_data)

# calculate stats and put in 1 dataframe per mouse
dataframes_stats_all_animals = {}
dataframes_stats_all_animals5 = {}
for mouse in dataframes_raw_data_all_animals.keys():
    if mouse in EYFP + NPHR:
        dataframes_stats_all_animals[mouse] = calculate_stats(dataframes_raw_data_all_animals[mouse], max_block_nr,
                                                              markers_unwanted_sessions, 0)
        dataframes_stats_all_animals5[mouse] = calculate_stats(dataframes_raw_data_all_animals[mouse], max_block_nr,
                                                              markers_unwanted_sessions, 5)

# save stats to csv file
for mouse in dataframes_stats_all_animals.keys():

    dataframes_stats_all_animals5[mouse].to_csv(path + "Performance_Stats\\{}_stats5.csv".format(mouse), index=False)
    dataframes_stats_all_animals[mouse].to_csv(path + "Performance_Stats\\{}_stats.csv".format(mouse), index=False)


# Plots
for mouse in dataframes_stats_all_animals.keys():
    make_online_plot(dataframes_stats_all_animals[mouse], mouse, path + "Performance_Stats")
