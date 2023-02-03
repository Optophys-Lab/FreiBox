import matplotlib.pyplot as plt
import numpy as np
import matplotlib


def move_figure(f, x, y):
    backend = matplotlib.get_backend()
    if backend == 'TkAgg':
        f.canvas.manager.window.wm_geometry("+%d+%d" % (x, y))
    elif backend == 'WXAgg':
        f.canvas.manager.window.SetPosition((x, y))
    else:
        f.canvas.manager.window.move(x, y)


def get_lick_block_types(licking_BlockType_list):
    list_of_lick_blocks = []
    list_of_lick_blocks_x = [1]
    first_bl = licking_BlockType_list[0]
    if first_bl == 1:
        list_of_lick_blocks.append('left')
    else:
        list_of_lick_blocks.append('right')
    if len(licking_BlockType_list) > 1:
        for index, value in enumerate(licking_BlockType_list):
            if index > 0:

                if value != licking_BlockType_list[index-1]:
                    list_of_lick_blocks_x.append(index)
                    corr_side_this_block =value
                    if corr_side_this_block == 1:
                        corr_side_this_block_transl = 'left'
                    else:
                        corr_side_this_block_transl = 'right'
                    list_of_lick_blocks.append(corr_side_this_block_transl)
    return list_of_lick_blocks, list_of_lick_blocks_x


def update_plot(curr_block_number, nr_trials_in_old_block, user_input, hits, miss, error, omissions, com,
                licking_BlockType_list):

    # save correct sides left vs right) from each block to display in plot
    list_of_lick_blocks, list_of_lick_blocks_x = get_lick_block_types(licking_BlockType_list)
    # get all data
    moving_window_size = float(user_input["Wind"])
    # these lists will have 1 list per block each
    hits_per_block_lists = []
    misses_per_block_lists = []
    errors_per_block_lists = []
    omissions_per_block_lists = []
    omission_indeces_per_block_lists = []

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
        # get omission indeces
        om_indeces = np.where(np.array(binary_om_this_block) > 0)[0]
        omission_indeces_per_block_lists.append(om_indeces)

    x_axis = np.arange(1, len(hits) + 1)
    hit_values_for_plot = []
    error_values_for_plot = []
    miss_values_for_plot = []
    hit_values_for_window_plot = []
    error_values_for_window_plot = []
    miss_values_for_window_plot = []
    # regard performance in each block separately
    for block in range(1, len(hits_per_block_lists) + 1):
        omissions_this_bl = sum(omissions_per_block_lists[block - 1])
        # in each block, compute percentages
        for index, value in enumerate(hits_per_block_lists[block - 1]):
            all_trials_this_bl = index + 1
            omissions_until_this_trial = sum(omissions_per_block_lists[block - 1][:index+1])
            if all_trials_this_bl - omissions_until_this_trial > 0:
                trials_sofar_no_om = all_trials_this_bl - omissions_until_this_trial
            else:
                trials_sofar_no_om = 1
            # for moving window percentages
            if index > moving_window_size - 2:
                om_curr_win = omissions_per_block_lists[block - 1][int(index - (moving_window_size - 1)): int(index+1)]
                rewards_curr_window = hits_per_block_lists[block - 1][int(index - (moving_window_size-1)):int(index+1)]
                reward_perc_curr_window = sum(rewards_curr_window) / (moving_window_size - sum(om_curr_win)) * 100
                errors_curr_window = errors_per_block_lists[block - 1][int(index - (moving_window_size-1)):int(index+1)]
                error_perc_curr_window = (sum(errors_curr_window) / (moving_window_size - sum(om_curr_win))) * 100
                misses_curr_window = misses_per_block_lists[block-1][int(index - (moving_window_size - 1)):int(index+1)]
                miss_perc_curr_window = (sum(misses_curr_window) / (moving_window_size - sum(om_curr_win))) * 100
                hit_values_for_window_plot.append(reward_perc_curr_window)
                error_values_for_window_plot.append(error_perc_curr_window)
                miss_values_for_window_plot.append(miss_perc_curr_window)
            else:
                hit_values_for_window_plot.append(None)
                miss_values_for_window_plot.append(None)
                error_values_for_window_plot.append(None)

            # general %
            hit_percentage_so_far = (sum(hits_per_block_lists[block - 1][:all_trials_this_bl])/ trials_sofar_no_om)*100
            hit_values_for_plot.append(hit_percentage_so_far)
            miss_percentage_so_far = (sum(misses_per_block_lists[block-1][:all_trials_this_bl]) / trials_sofar_no_om)*100
            miss_values_for_plot.append(miss_percentage_so_far)
            error_percentage_so_far = (sum(errors_per_block_lists[block-1][:all_trials_this_bl])/trials_sofar_no_om)*100
            error_values_for_plot.append(error_percentage_so_far)

    plt.close('all')
    fig, (ax1, ax2) = plt.subplots(2, sharex=True, figsize=(8, 6))
    if com == 'COM7':
        move_figure(fig, 2800, 10)
    else:
        move_figure(fig, 2800, 500)
    #plt.ion()
    # AX1 - GENERAL PERCENTAGE
    ax1.plot(x_axis, hit_values_for_plot, linewidth=3, linestyle='dotted', color='green', label='Hit', marker="o",
             markersize=8, alpha=0.5)
    ax1.plot(x_axis, miss_values_for_plot, linewidth=3, linestyle='dashed', color='blue', label='Miss', marker="v",
             markersize=8, alpha=0.5)
    ax1.plot(x_axis, error_values_for_plot, linewidth=3, linestyle='-.', color='red', label='Error', marker="x",
             markersize=8, alpha=0.5)
    ax1.set_title('Online performance summary {} {}'.format(user_input['Subject'],com), fontsize=16, pad=20)
    ax1.set_xlabel('Trial number', fontsize=12)
    ax1.set_ylabel('Performance in %', fontsize=12)

    # shading to visualize individual blocks
    total_trial_count = 0
    for block in range(0, curr_block_number):
        total_trial_count += len(misses_per_block_lists[block])

        if (block % 2) == 0 and (curr_block_number - block > 1):
            for ax in [ax1, ax2]:
                ax.axvspan(total_trial_count, total_trial_count + len(misses_per_block_lists[block + 1]),
                           facecolor='0.2', alpha=0.2)

    # AX2 - MOVING WINDOW
    ax2.plot(x_axis, hit_values_for_window_plot, linewidth=3, linestyle='dotted', color='green', label='Hit', marker="o",
             markersize=8, alpha=0.5)
    ax2.plot(x_axis, miss_values_for_window_plot, linewidth=3, linestyle='dashed', color='blue', label='Miss', marker="v",
             markersize=8, alpha=0.5)
    ax2.plot(x_axis, error_values_for_window_plot, linewidth=3, linestyle='-.', color='red', label='Error', marker="x",
             markersize=8, alpha=0.5)
    ax2.set_title('Sliding window summary {} {}'.format(user_input['Subject'],com), fontsize=16)
    ax2.set_xlabel('Trial number', fontsize=12)
    ax2.set_ylabel('Moving window \n Performance (%)', fontsize=12)
    lines2, labels2 = ax1.get_legend_handles_labels()
    ax1.legend(lines2, labels2, fontsize=12)

    for indx, val in enumerate(list_of_lick_blocks_x):
        ax1.text(val, 110, list_of_lick_blocks[indx], family='serif', weight='bold', wrap=True)
    fig.tight_layout()

    if com == 'COM7':
        move_figure(fig, 2200, 10)
    else:
        move_figure(fig, 2200, 700)
    plt.pause(0.02)
    plt.show(block=False)

