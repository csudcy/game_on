import os

from team_not_found.utils import mount as mount_utils

class Tree(mount_utils.SelfDoc):
    pass

def mount_tree():
    mount_utils.add_all_trees(
        os.path.dirname(os.path.abspath(__file__)),
        globals(),
        Tree)
    return Tree()
