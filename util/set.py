# flatten a set of sets
def flatten(set_of_sets):
    return set([item for a_set in set_of_sets for item in a_set ])