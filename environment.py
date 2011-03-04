# coding: UTF-8
#
# Environment-related utility functions
#

# Copyright © 2011 Timothy Baldock. All Rights Reserved.

import ctypes

def getenvvar(name):
    n= ctypes.windll.kernel32.GetEnvironmentVariableW(name, None, 0)
    if n==0:
        return None
    buf= ctypes.create_unicode_buffer(u'\0'*n)
    ctypes.windll.kernel32.GetEnvironmentVariableW(name, buf, n)
    return buf.value

