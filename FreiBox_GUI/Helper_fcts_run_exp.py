from Setup_variables import lists_of_timestamps


def check_if_block_changed(licking_block_type_list):
    if len(licking_block_type_list) > 1:
        # check if correct side (left/right) has changed
        # if so, new block
        if licking_block_type_list[-1] != licking_block_type_list[-2]:
            new_block = 1
        else:
            new_block = 0
    else:
        new_block = 0
    return new_block


# read data, transfer time stamps into seconds and save in respective dictionary
def data_to_time_stamps_in_s(decoded_strings,data_description, list_to_append):
    # isolate value from its description
    my_data = decoded_strings.strip(data_description)
    # safety precaution so code does not freeze when parts of the string accidentally end up here
    try:
        float(my_data)
        # only time stamps need to be transferred into s
        if data_description in lists_of_timestamps:
            # transfer time stamps into seconds
            if float(my_data) != 0:
                list_to_append.append(float(my_data) / 1000 / 1000)  # in seconds
            else:
                list_to_append.append(float(-1))  # marker for absence of task event
        #  logical values (non time stamps) do not need transferring
        else:
            list_to_append.append(float(my_data))
    # safety for when letters end up here
    except ValueError:
        pass
    # return updated lists for dictionary
    return list_to_append
