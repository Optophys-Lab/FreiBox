import matplotlib.pyplot as plt
import numpy as np


def update_plot(curr_block_number, nr_trials_in_old_block, user_input, rewards, miss, error):
    plt.close('all')
    plt.figure()
    plt.ion()
    moving_window_size = float(user_input["Wind"])
    # these lists will have 1 list per block each, with the time stamps for the respective parameter
    list_of_rewards_per_block_lists = []
    list_of_misses_per_block_lists = []
    list_of_errors_per_block_lists = []

    for block in range(1, curr_block_number + 1):
        # if we have more than 1 block, we need to slice from beginning of one block to beginning of next
        if curr_block_number > 1 and block < curr_block_number:
            reward_timestamps_this_block = rewards[nr_trials_in_old_block[block - 1]:
                                                                   nr_trials_in_old_block[block]]
            miss_timestamps_this_block = miss[nr_trials_in_old_block[block - 1]:
                                                       nr_trials_in_old_block[block]]
            error_timestamps_this_block = error[nr_trials_in_old_block[block - 1]:
                                                         nr_trials_in_old_block[block]]
        # if only 1 block, we slice from its beginning to end of all data
        else:
            reward_timestamps_this_block = rewards[nr_trials_in_old_block[block - 1]:]
            miss_timestamps_this_block = miss[nr_trials_in_old_block[block - 1]:]
            error_timestamps_this_block = error[nr_trials_in_old_block[block - 1]:]

        binary_rewards_this_block = [1 if i > 0 else 0 for i in reward_timestamps_this_block]
        binary_misses_this_block = [1 if i > 0 else 0 for i in miss_timestamps_this_block]
        binary_errors_this_block = [1 if i > 0 else 0 for i in error_timestamps_this_block]
        list_of_rewards_per_block_lists.append(binary_rewards_this_block)
        list_of_misses_per_block_lists.append(binary_misses_this_block)
        list_of_errors_per_block_lists.append(binary_errors_this_block)

    x_axis = np.arange(1, len(rewards) + 1)
    reward_values_for_plot = []
    error_values_for_plot = []
    miss_values_for_plot = []
    # regard performance in each block separately
    for block in range(1, len(list_of_rewards_per_block_lists) + 1):
        # in each block, compute percentages
        for index, value in enumerate(list_of_rewards_per_block_lists[block - 1]):
            all_trials_so_far = index + 1
            reward_percentage_so_far = (sum(
                list_of_rewards_per_block_lists[block - 1][:all_trials_so_far]) / all_trials_so_far) * 100
            reward_values_for_plot.append(reward_percentage_so_far)
            miss_percentage_so_far = (sum(
                list_of_misses_per_block_lists[block - 1][:all_trials_so_far]) / all_trials_so_far) * 100
            miss_values_for_plot.append(miss_percentage_so_far)
            error_percentage_so_far = (sum(
                list_of_errors_per_block_lists[block - 1][:all_trials_so_far]) / all_trials_so_far) * 100
            error_values_for_plot.append(error_percentage_so_far)

    plt.plot(x_axis, reward_values_for_plot, linewidth=3, linestyle='dotted', color='green', label='Reward', marker="o",
             markersize=8, alpha=0.5)
    plt.plot(x_axis, miss_values_for_plot, linewidth=3, linestyle='dashed', color='blue', label='Miss', marker="v",
             markersize=8, alpha=0.5)
    plt.plot(x_axis, error_values_for_plot, linewidth=3, linestyle='-.', color='red', label='Error', marker="x",
             markersize=8, alpha=0.5)
    plt.legend()
    plt.xlabel('Trial number', fontsize=14)
    plt.ylabel('Performance in %', fontsize=14)
    if 3 > curr_block_number > 1:
        plt.axvspan(nr_trials_in_old_block[1] + 1, x_axis[-1], facecolor='0.2', alpha=0.2)
    elif curr_block_number == 3:
        plt.axvspan(nr_trials_in_old_block[1] + 1, nr_trials_in_old_block[2], facecolor='0.2', alpha=0.2)
    plt.title('Online performance summary {}'.format(user_input['Subject']), fontsize=18)
    # plt.draw()
    plt.pause(0.02)
    plt.show(block=False)

