import pandas as pd
import seaborn as sns
import ipywidgets as widgets


def unique_sorted_values_plus_ALL(array):
    ALL = "ALL"
    unique = array.unique().tolist()
    unique.sort()
    unique.insert(0, ALL)
    return unique


def unique_sources(array):
    ALL = "ALL"
    unique = set()
    for li in array:
        for l in li:
            unique.add(l)
    ret = list(unique)
    ret.insert(0, ALL)
    return ret


def colour_ge_value(value, comparison):
    if len(value.split()) >= comparison:
        return "color: red"
    else:
        return "color: black"
