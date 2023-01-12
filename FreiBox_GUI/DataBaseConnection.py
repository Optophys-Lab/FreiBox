from pathlib import Path
from shutil import copy2

import datastructure_tools.utils
from datastructure_tools.DataBaseAccess import DataBaseAccess
DB = DataBaseAccess()

user = 'as153'
project = DB.cfg['project']
experiment = DB.cfg['experiment']
sub_experiment = DB.cfg['sub_experiment']

animals = (DB.Animal - DB.Animal.Death & {"user": user}).fetch('animal_id')


def finalize_session(session: datastructure_tools.utils.SessionClass, resulting_file: str) -> bool:
    """
    This function creates session paths, pushes data to DB using SessionClass from utils
    also copies behavioral data to server
    :param session: Object from datastructure_tools.utils.SessionClass
    :param resulting_file: filepath to behavioral data to be copied
    :return: True if success
    """
    session.createSession_path()
    session.checkInputs()
    # copy the file
    target_path = Path(DB.cfg['Server_path']) / session.session_dir
    copy2(resulting_file, target_path)
    return True
