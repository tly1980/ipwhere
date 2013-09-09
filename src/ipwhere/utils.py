import socket
import struct

from pympler import summary
from pympler import muppy


def memusage(o):
    summary.print_(
        summary.summarize(o))


def memusage_overall():
    all_objects = muppy.get_objects()
    memusage(all_objects)


def ip2long(ip):
    """
    Convert an IP string to long
    """
    packedIP = socket.inet_aton(ip)
    return struct.unpack("!L", packedIP)[0]
