from pympler import summary
from pympler import muppy


def memusage(o):
    summary.print_(
        summary.summarize(o))


def memusage_overall():
    all_objects = muppy.get_objects()
    memusage(all_objects)
