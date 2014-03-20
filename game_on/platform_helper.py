import os

# Determine platform flags

WIN32 = DARWIN = DARWIN_INTEL = POSIX = LINUX = FOUNDATION = WIN64 = False
KERNEL32 = None

if os.name == 'nt':
    WIN32 = True
    try:
        import ctypes
        KERNEL32 = ctypes.windll.LoadLibrary("Kernel32.dll")
    except:
        pass
elif os.name == 'posix':
    ORG_UMASK = os.umask(18)
    os.umask(ORG_UMASK)
    POSIX = True
    import platform
    if platform.system().lower() == 'linux':
        LINUX = True
    elif platform.system().lower() == 'darwin':
        DARWIN = True
        try:
            import Foundation
            FOUNDATION = True
        except:
            pass
        if platform.machine() == 'i386':
            DARWIN_INTEL = True
else:
    raise Exception('Unrecognised os: %s' % os.name)
