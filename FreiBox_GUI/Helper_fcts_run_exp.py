def check_if_block_changed(lickingBlockType_list):
    if len(lickingBlockType_list) > 1:
        if lickingBlockType_list[-1] != lickingBlockType_list[-2]:
            new_block = 1
        else:
            new_block = 0
    else:
        new_block = 0
    return new_block
