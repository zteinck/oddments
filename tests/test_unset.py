import copy
import pickle

from oddments.sentinels.unset import Unset, UNSET


if __name__ == '__main__':

    assert UNSET is Unset()
    assert copy.deepcopy(UNSET) is UNSET
    assert copy.copy(UNSET) is UNSET
    assert pickle.loads(pickle.dumps(UNSET)) is UNSET