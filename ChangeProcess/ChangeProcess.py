"""
Created on Sat Nov 23 21:15:08 2019

"""

# ------------------------------------------------------------------------------------------------------------------
# Import modules
# ------------------------------------------------------------------------------------------------------------------

import PIDSearcher
import struct
import ctypes as c
from ctypes import wintypes as w

# ------------------------------------------------------------------------------------------------------------------
# Define variables
# ------------------------------------------------------------------------------------------------------------------

k32 = c.windll.kernel32

OpenProcess = k32.OpenProcess
OpenProcess.argtypes = [w.DWORD,w.BOOL,w.DWORD]
OpenProcess.restype = w.HANDLE

ReadProcessMemory = k32.ReadProcessMemory
ReadProcessMemory.argtypes = [w.HANDLE,w.LPCVOID,w.LPVOID,c.c_size_t,c.POINTER(c.c_size_t)]
ReadProcessMemory.restype = w.BOOL

WriteProcessMemory = k32.WriteProcessMemory
WriteProcessMemory.argtypes = [w.HANDLE,w.LPCVOID,w.LPVOID,c.c_size_t,c.POINTER(c.c_size_t)]
WriteProcessMemory.restype = w.BOOL

GetLastError = k32.GetLastError
GetLastError.argtypes = None
GetLastError.restype = w.DWORD

CloseHandle = k32.CloseHandle
CloseHandle.argtypes = [w.HANDLE]
CloseHandle.restype = w.BOOL

# ------------------------------------------------------------------------------------------------------------------
# Define functions
# ------------------------------------------------------------------------------------------------------------------

def GetValueFromAddress(processHandle, address, isFloat=False, is64bit=False, isString=False):
        if isString:
            data = c.create_string_buffer(16)
            bytesRead = c.c_ulonglong(16)
        elif is64bit:
            data = c.c_ulonglong()
            bytesRead = c.c_ulonglong()
        else:
            data = c.c_ulong()
            bytesRead = c.c_ulonglong(4)

        successful = ReadProcessMemory(processHandle, address, c.byref(data), c.sizeof(data), c.byref(bytesRead))
        if not successful:
            e = GetLastError()
            print("ReadProcessMemory Error: Code " + str(e))

        value = data.value

        if isFloat:
            return struct.unpack("<f", value)[0]
        elif isString:
            try:
                return value.decode('utf-8')
            except:
                print("ERROR: Couldn't decode string from memory")
                return "ERROR"
        else:
            return int(value)
        
def WriteValueToAddress(processHandle, address, value):
    data = c.c_ulong(value)
    successful = WriteProcessMemory(processHandle, address, c.byref(data), c.sizeof(data), None) 
    if not successful:
        e = GetLastError()
        print("WriteProcessMemory Error: Code " + str(e))

# ------------------------------------------------------------------------------------------------------------------
# Change value in Process
# ------------------------------------------------------------------------------------------------------------------
      
pid = PIDSearcher.GetPIDByName(b'TekkenGame-Win64-Shipping.exe')
if pid > -1:
    print("Tekken pid acquired: " + str(pid))
else:
    print("Tekken pid not acquired.")

processHandle = OpenProcess(0x10 | 0x20 | 0x08, False, pid) #0x10 = ReadProcess Privileges | 0x20 = WriteProcess Privileges | 0x08 = Operation Privileges
address = 0x48160010
try:
    value = GetValueFromAddress(processHandle, address)
    print(value)
    WriteValueToAddress(processHandle, address, 22)
finally:
    CloseHandle(processHandle)
