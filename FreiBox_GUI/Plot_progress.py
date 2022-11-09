import matplotlib.pyplot as plt
import numpy as np
import matplotlib
from Setup_variables import *
from Helper_fcts_run_exp import check_if_block_changed


# moves the update plot to desired location on screen
def move_figure(f, x, y):
    backend = matplotlib.get_backend()
    if backend == 'TkAgg':
        f.canvas.manager.window.wm_geometry("+%d+%d" % (x, y))
    elif backend == 'WXAgg':
        f.canvas.manager.window.SetPosition((x, y))
    else:
        f.canvas.manager.window.move(x, y)


# finds out which side (left/right) was correct in each block to add into the update plot
def get_lick_block_types(correct_block_list):
    # list for correct block identities
    list_of_lick_blocks = []
    # list for trial numbers where the blocks changed
    list_of_lick_blocks_x = [1]
    first_bl = correct_block_list[0]
    # translate identity of first block from numbers into words
    if first_bl == 1:
        list_of_lick_blocks.append('left')
    else:
        list_of_lick_blocks.append('right')
    if len(correct_block_list) > 1:
        for index, value in enumerate(correct_block_list):
            if index > 0:
                if value != correct_block_list[index-1]:
                    # check when the block changed as x value for the update plot
                    list_of_lick_blocks_x.append(index)
                    corr_side_this_block = value
                    if corr_side_this_block == 1:
                        corr_side_this_block_transl = 'left'
                    else:
                        corr_side_this_block_transl = 'right'
                    list_of_lick_blocks.append(corr_side_this_block_transl)
    return list_of_lick_blocks, list_of_lick_blocks_x


def update_plot(curr_block_number, nr_trials_in_old_block, user_choices, hits, miss, error, omissions, com,
                corr_block_list):
    # for each block, find out whether left or right or side was correct,to display in plot
    list_of_lick_blocks, list_of_lick_blocks_x = get_lick_block_types(corr_block_list)
    # start computing performance averages for each block
    # these will be nested lists with 1 list per block
    hits_per_block_lists = []
    misses_per_block_lists = []
    errors_per_block_lists = []
    omissions_per_block_lists = []
    omission_indices_per_block_lists = []
    # compute block-wise performance averages
    for block in range(1, curr_block_number + 1):
        # if we have more than 1 block, we need to slice from beginning of one block to beginning of next
        if curr_block_number > 1 and block < curr_block_number:
            hit_timestamps_this_block = hits[nr_trials_in_old_block[block - 1]:nr_trials_in_old_block[block]]
            miss_timestamps_this_block = miss[nr_trials_in_old_block[block - 1]:nr_trials_in_old_block[block]]
            om_timestamps_this_block = omissions[nr_trials_in_old_block[block - 1]:nr_trials_in_old_block[block]]
            error_timestamps_this_block = error[nr_trials_in_old_block[block - 1]:nr_trials_in_old_block[block]]
        # if only 1 block, we slice from its beginning to end of all data
        else:
            hit_timestamps_this_block = hits[nr_trials_in_old_block[block - 1]:]
            miss_timestamps_this_block = miss[nr_trials_in_old_block[block - 1]:]
            error_timestamps_this_block = error[nr_trials_in_old_block[block - 1]:]
            om_timestamps_this_block = omissions[nr_trials_in_old_block[block - 1]:]
        binary_hits_this_block = [1 if i > 0 else 0 for i in hit_timestamps_this_block]
        binary_misses_this_block = [1 if i > 0 else 0 for i in miss_timestamps_this_block]
        binary_errors_this_block = [1 if i > 0 else 0 for i in error_timestamps_this_block]
        binary_om_this_block = [1 if i > 0 else 0 for i in om_timestamps_this_block]
        hits_per_block_lists.append(binary_hits_this_block)  # nested list
        misses_per_block_lists.append(binary_misses_this_block)   # nested list
        errors_per_block_lists.append(binary_errors_this_block)   # nested list
        omissions_per_block_lists.append(binary_om_this_block)  # nested list
        # get omission indices, so we can exclude these from the update plot
        # (since omissions do not count into performance averages)
        om_indices = np.where(np.array(binary_om_this_block) > 0)[0]
        omission_indices_per_block_lists.append(om_indices)
    # prepare plot
    # x values for plot
    x_axis = np.arange(1, len(hits) + 1)
    # y values for plot
    hit_values_for_plot = []
    error_values_for_plot = []
    miss_values_for_plot = []
    hit_values_for_window_plot = []
    error_values_for_window_plot = []
    miss_values_for_window_plot = []
    slid_window_size = float(user_choices["Wind"])
    # regard performance in each block separately
    for block in range(1, len(hits_per_block_lists) + 1):
        omissions_this_bl = sum(omissions_per_block_lists[block - 1])
        # in each block, compute overall percentages
        for index, value in enumerate(hits_per_block_lists[block - 1]):
            all_trials_this_bl = index + 1
            # ignore omission trials from performance averages
            omissions_until_this_trial = sum(omissions_per_block_lists[block - 1][:index+1])
            if all_trials_this_bl - omissions_until_this_trial > 0:
                trials_no_om = all_trials_this_bl - omissions_until_this_trial
            else:
                trials_no_om = 1
            # for sliding window percentages
            if index > slid_window_size - 2:
                om_curr_win = omissions_per_block_lists[block - 1][int(index - (slid_window_size - 1)): int(index+1)]
                rewards_curr_window = hits_per_block_lists[block - 1][int(index - (slid_window_size-1)):int(index+1)]
                reward_perc_curr_window = sum(rewards_curr_window) / (slid_window_size - sum(om_curr_win)) * 100
                errors_curr_window = errors_per_block_lists[block - 1][int(index - (slid_window_size-1)):int(index+1)]
                error_perc_curr_window = (sum(errors_curr_window) / (slid_window_size - sum(om_curr_win))) * 100
                misses_curr_window = misses_per_block_lists[block-1][int(index - (slid_window_size - 1)):int(index+1)]
                miss_perc_curr_window = (sum(misses_curr_window) / (slid_window_size - sum(om_curr_win))) * 100
                hit_values_for_window_plot.append(reward_perc_curr_window)
                error_values_for_window_plot.append(error_perc_curr_window)
                miss_values_for_window_plot.append(miss_perc_curr_window)
            else:
                hit_values_for_window_plot.append(None)
                miss_values_for_window_plot.append(None)
                error_values_for_window_plot.append(None)
            # general performance averages, regardless of sliding window
            hit_percentage_so_far = (sum(hits_per_block_lists[block - 1][:all_trials_this_bl]) / trials_no_om) * 100
            hit_values_for_plot.append(hit_percentage_so_far)
            miss_percentage_so_far = (sum(misses_per_block_lists[block-1][:all_trials_this_bl]) / trials_no_om) * 100
            miss_values_for_plot.append(miss_percentage_so_far)
            error_percentage_so_far = (sum(errors_per_block_lists[block-1][:all_trials_this_bl])/trials_no_om) * 100
            error_values_for_plot.append(error_percentage_so_far)
    # first, close all other plots
    plt.close('all')
    # start new update plots
    # 2 subplots, one for overall performance averages, one for averages within sliding window
    fig, (ax1, ax2) = plt.subplots(2, sharex=True, figsize=(7, 5))
    # set position of update plot on the screen, depending on the utilized arduino
    if com == 'COM15':
        move_figure(fig, 2800, 10)
    else:
        move_figure(fig, 2800, 500)
    # AX1 - GENERAL PERFORMANCE PERCENTAGE
    ax1.plot(x_axis, hit_values_for_plot, linewidth=3, linestyle='dotted', color='green', label='Hit', marker="o",
             markersize=8, alpha=0.5)
    ax1.plot(x_axis, miss_values_for_plot, linewidth=3, linestyle='dashed', color='blue', label='Miss', marker="v",
             markersize=8, alpha=0.5)
    ax1.plot(x_axis, error_values_for_plot, linewidth=3, linestyle='-.', color='red', label='Error', marker="x",
             markersize=8, alpha=0.5)
    ax1.set_title('Online performance summary {} {}'.format(user_choices['Subject'], com), fontsize=12, pad=20)
    ax1.set_xlabel('Trial number', fontsize=10)
    ax1.set_ylabel('Performance in %', fontsize=10)
    # shading to visualize individual blocks
    total_trial_count = 0
    for block in range(0, curr_block_number):
        total_trial_count += len(misses_per_block_lists[block])
        if (block % 2) == 0 and (curr_block_number - block > 1):
            for ax in [ax1, ax2]:
                ax.axvspan(total_trial_count, total_trial_count + len(misses_per_block_lists[block + 1]),
                           facecolor='0.2', alpha=0.2)
    # AX2 - SLIDING WINDOW PERFORMANCE AVERAGES
    ax2.plot(x_axis, hit_values_for_window_plot, linewidth=3, linestyle='dotted', color='green', label='Hit',
             marker="o", markersize=8, alpha=0.5)
    ax2.plot(x_axis, miss_values_for_window_plot, linewidth=3, linestyle='dashed', color='blue', label='Miss',
             marker="v", markersize=8, alpha=0.5)
    ax2.plot(x_axis, error_values_for_window_plot, linewidth=3, linestyle='-.', color='red', label='Error', marker="x",
             markersize=8, alpha=0.5)
    ax2.set_title('Sliding window summary {} {}'.format(user_choices['Subject'], com), fontsize=12)
    ax2.set_xlabel('Trial number', fontsize=10)
    ax2.set_ylabel('Sliding window \n Performance (%)', fontsize=10)
    # legend
    lines2, labels2 = ax1.get_legend_handles_labels()
    ax1.legend(lines2, labels2, fontsize=10)
    # indicator which side was correct (left/right)
    for block_index, val in enumerate(list_of_lick_blocks_x):
        ax1.text(val, 110, list_of_lick_blocks[block_index], family='serif', weight='bold', wrap=True)
    plt.pause(0.02)
    plt.show(block=False)


def print_and_plot_session_stats(my_dict_data, user_choice, current_trial_number_local, current_block_nr_local,
                                 trials_in_old_block_local, com, start_time):
    # check if we have a new block because performance percentages are computed within a given block
    is_it_new_block = check_if_block_changed(my_dict_data['blo'])
    if is_it_new_block > 0:
        trials_in_old_block_local.append(current_trial_number_local)
        current_block_nr_local += 1  # keeps track of number of trials in current block
    # these lists will summarize performance in most recent block
    omission_list_current_block = my_dict_data['om'][trials_in_old_block_local[current_block_nr_local - 1]:]
    hit_list_current_block = my_dict_data['hit'][trials_in_old_block_local[current_block_nr_local - 1]:]
    miss_list_current_block = my_dict_data['mi'][trials_in_old_block_local[current_block_nr_local - 1]:]
    error_list_current_block = my_dict_data['err'][trials_in_old_block_local[current_block_nr_local - 1]:]
    trials_current_block = (current_trial_number_local + 1) - trials_in_old_block_local[current_block_nr_local - 1]
    current_time = time.time()  # in seconds
    # make update plot
    update_plot(current_block_nr_local, trials_in_old_block_local, user_choice, my_dict_data['hit'], my_dict_data['mi'],
                my_dict_data['err'], my_dict_data['om'], com, my_dict_data['blo'])
    # print out session statistics
    print("Time passed: {} min".format((current_time - start_time) / 60.0))  # in minutes
    print("Current Block: {}".format(current_block_nr_local))
    print("Total Trials: {}; This Block: {}".format(current_trial_number_local + 1, trials_current_block))
    print("Total Omissions: {}; This Block: {}".format(sum(i > 0 for i in my_dict_data['om']),
                                                       sum(i > 0 for i in omission_list_current_block)))
    print("Total Hits: {}; This Block: {}".format(sum(i > 0 for i in my_dict_data['hit']),
                                                  sum(i > 0 for i in hit_list_current_block)))
    print("Total Misses: {}; This Block: {}".format(sum(i > 0 for i in my_dict_data['mi']),
                                                    sum(i > 0 for i in miss_list_current_block)))
    print("Total Errors: {}; This Block: {}".format(sum(i > 0 for i in my_dict_data['err']),
                                                    sum(i > 0 for i in error_list_current_block)))
    # print out result of last trial
    try:
        my_dict_data['lio'][-1]
        # translate code into description of scenario
        if int(my_dict_data['lio'][-1]) >= float(user_choice["Hit"]):
            licking_result_list_translated = 'Success'
        elif int(my_dict_data['lio'][-1]) < 0:
            licking_result_list_translated = 'Error'
        else:
            if my_dict_data['mi'][-1] > 0:
                licking_result_list_translated = 'Miss'
            else:
                licking_result_list_translated = 'Omission'
        print("Last trial: {}".format(licking_result_list_translated))
    except IndexError:
        pass
    return current_block_nr_local, trials_in_old_block_local

