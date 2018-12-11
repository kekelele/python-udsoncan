#coding:utf-8
import sys, os
import platform
import ctypes as ct

if sys.platform.startswith('win'):
    # The _winreg module has been renamed to winreg in Python 3.
    try:
        import _winreg as winreg
    except ImportError:
        import winreg as winreg
if (platform.architecture()[0] == '32bit'):
    PASSTHRU_REG = r"Software\\PassThruSupport.04.04\\"
else:
    PASSTHRU_REG = r"Software\\Wow6432Node\\PassThruSupport.04.04\\"

DEFAULT = object()
def annotate(dll_object, function_name, argtypes,
             restype=DEFAULT, errcheck=DEFAULT):
    """Fully annotate a dll function using ctypes

    To "annotate" a function is to set its `argtypes`, `restype`, and
    `errcheck` attributes, which should always be done for all used functions.

    This function is used internally by `MyDll`, which only allows access to
    annotated dll functions.

    If `restype` and/or `errcheck` arguments are not specified, the
    `dll_object` argument must have a `default_restype` and/or
    `default_errcheck`, respectively. These values will then be used when
    setting the function's `argtypes` and `restype` attributes.

    """
    function = getattr(dll_object._dll, function_name)
    function.argtypes = argtypes
    # restype and errcheck is optional in the function_prototypes list
    if restype is DEFAULT:
        restype = ct.c_long ##dll_object.default_restype ##
    function.restype = restype
    if errcheck is DEFAULT:
        errcheck = dll_object.default_errcheck
    function.errcheck = errcheck
    setattr(dll_object, function_name, function)

class MyDll(object):
    """Wrapper around a ctypes dll, `MyDll` only allows annotated functions to be called

    The first argument to the `__init__` function, `ct_dll`, is the ctypes dll
    that this object should wrap. It also takes an arbitrary number of keyword
    arguments as "function prototypes". The keyword should match a function in
    the ctypes dll, and the value should be an annotation in the form of
    ``[argtypes, restype, errcheck]``. These values are passed on to
    `dllLoader.annotate`. Note that `restype` and `errcheck` are optional if
    `default_restype` and `default_errcheck` attributes are defined in a
    subclass (respectively).

    After the `MyDll` object has been created, all functions annotated by
    function prototypes are available as attributes, while all other functions
    are not. This effectively forces a function to have been annotated (which
    all functions should be to avoid ctypes defaults) before being used, or an
    `AttributeError` is raised.

    """
    def __init__(self, ct_dll, **function_prototypes):
        self._dll = ct_dll
        for name, prototype in function_prototypes.items():
            annotate(self, name, *prototype)

def getDevices():
    """TODO:
    获取更多key，比如支持测protocols；
    """
    BaseKey = winreg.OpenKeyEx(winreg.HKEY_LOCAL_MACHINE, PASSTHRU_REG)
    count = winreg.QueryInfoKey(BaseKey)[0]
    J2534_Device_Reg_Info = dict()
    for i in range(count):
        DeviceKey = winreg.OpenKeyEx(BaseKey, winreg.EnumKey(BaseKey, i))
        singleDll = dict()
        singleDll['Name'] = winreg.QueryValueEx(DeviceKey, 'Name')[0]
        singleDll['FunctionLibrary'] = winreg.QueryValueEx(DeviceKey, 'FunctionLibrary')[0]
        J2534_Device_Reg_Info[i] = singleDll
    return J2534_Device_Reg_Info

def load_dll(dll_path = None):
    """Load dll or shared object file as appropriate.
    """
    dir = os.getcwd()
    path, name = os.path.split( dll_path )

    if path is not None:
        try:
            os.chdir(path)
        except:
            pass  # Specified directory was not found, but it could have been empty...
        else:
            # Some DLL's are loaded "manually" so we add installDir to the PATH in
            # order to allow the OS to find them later when needed
            os.environ["PATH"] += os.pathsep + path

    # Load our dll and all dependencies
    loadedDll = None
    try:
        # Windows supports all dll
        dllFile = name
        loadedDll = ct.WinDLL(dllFile)
    except Exception as e:
        print(e)
        print("Could be a missing dependancy dll for '%s'." % dllFile)
        print("(Directory for dll: '%s')\n" % dll_path)
        os.chdir(dir)
        exit(1)
    os.chdir(dir)
    return loadedDll