from pathlib import Path
from shutil import copy2

import datastructure_tools.utils
from datastructure_tools.DataBaseAccess import DataBaseAccess
from datastructure_tools.FileCommander import FileCommander

DB = DataBaseAccess()

fav_project = DB.cfg['project']
fav_experiment = DB.cfg['experiment_template']
fav_sub_experiment = DB.cfg['sub_experiment']


users2check = ['ms823', 'bd1033']

animals = list()
animals.extend('0')
for user in users2check:
    animals.extend((DB.Animal.User - DB.Animal.Death & {"user": user}).fetch('animal_id'))

projects = DB.Project.fetch('project')

exp_templates = DB.ExperimentTemplate.fetch('experiment_template')
exp_templates = [exp for exp in exp_templates if "Reversal" in exp] #only reversal types

sub_experiments = {}
for project in projects:
    sub_experiments[project] = [folder.name for folder in (DB.server_path / project).glob('*') if folder.is_dir() and folder.name != 'misc']
print(sub_experiments)
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
    if session.weight:
        session.pushWeights()
    block = [block for block in session.pipeline['0_raw'] if 'beh' in block]
    # copy the file
    target_path = Path(DB.server_path) / session.session_dir / block[0]
    if target_path.exists():
        copy2(resulting_file, target_path)
        print('file was copied')
    else:
        raise FileNotFoundError('path %s was not found'%target_path)

    #filecommander = FileCommander(DB=DB, session=session.session_id)
    return True
