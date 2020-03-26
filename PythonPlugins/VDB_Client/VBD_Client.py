import nclib
import struct
import time

VBD_vlType = {
    # Get current project data
    "VBD_GetVBProject" : 1,
    # Set current project data
    "VBD_SetVBProject" : 2,
    # Get File Name
    "VBD_GetFileName"		: 3,         # (v3.5+)
    # Get Compilation Type (if : 1 then Native Code)
    "VBD_IsNativeCompilation"		: 4,         # (v3.5+)
    "VBD_ClearAllBuffers"             : 5,         # need if your plugin decompile new language and need to clear all structures (v3.9+)
    "VBD_GetCompiler"                 : 6,         # 1 - vb, 2 - .net, 3 - delphi, 4 - unknown (v3.9+)
    "VBD_IsPacked"                    : 7,         # 1 - packed, 0 - not packed (v3.9+)
    "VBD_SetStackCheckBoxValue"       : 8,         # 0 - unchecked, 1 - checked (v3.9+)
    "VBD_SetAnalyzerCheckBoxValue"    : 9,         # 0 - unchecked, 1 - checked (v3.9+)
    # Get Form Name 
    "VBD_GetVBFormName"		: 10,
    # Set Form Name 
    "VBD_SetVBFormName"		: 11,
    # Get Form Content 
    "VBD_GetVBForm"			: 12,
    # Set Form Content 
    "VBD_SetVBForm"			: 13,
    # Get Forms Count 
    "VBD_GetVBFormCount"	: 14,
    # Get Sub Main() 
    "VBD_GetSubMain"		: 20,
    # Set Sub Main() 
    "VBD_SetSubMain"		: 21,
    # Get Name of Module 
    "VBD_GetModuleName"		: 30,
    # Set Name of Module  
    "VBD_SetModuleName"		: 31,
    # Get Module (.bas) 
    "VBD_GetModule"			: 32,
    # Set Module (.bas) 
    "VBD_SetModule"			: 33,
    # Get Module String References 
    "VBD_GetModuleStringReferences"	: 34,
    # Set Module String References 
    "VBD_SetModuleStringReferences"	: 35,
    # Get Modules Count 
    "VBD_SetModuleCount"		: 36,
    # Get Module Function Name 
    "VBD_GetModuleFunctionName"	: 40,
    # Set Module Function Name 
    "VBD_SetModuleFunctionName"	: 41,
    # Get Module Function Address 
    "VBD_GetModuleFunctionAddress"	: 42,
    # Set Module Function Address 
    "VBD_SetModuleFunctionAddress"	: 43,
    # Get Module Function 
    "VBD_GetModuleFunction"		: 44,
    # Set Module Function 
    "VBD_SetModuleFunction"		: 45,
    # Get Module Function String Reference 
    "VBD_GetModuleFunctionStrRef"	: 46,
    # Set Module Function String Reference 
    "VBD_SetModuleFunctionStrRef"	: 47,
    # Get Module Functions Count 
    "VBD_GetModuleFunctionCount"	: 48,
    # Get Text in active window 
    "VBD_GetActiveText"		: 50,
    # Set Text in active window 
    "VBD_SetActiveText"		: 51,
    # Get disasm listing from the active window 
    "VBD_GetActiveDisasmText"	: 52,
    # Set disasm listing to the active window 
    "VBD_SetActiveDisasmText"	: 53,
    # Set Line in active text 
    "VBD_SetActiveTextLine" : 54,
    # Get active module coordinats (vlNumber,vlFnNumber) 
    "VBD_GetActiveModuleCoordinats"	: 55,          # (v3.5+)
    # Get VB Decompiler path 
    "VBD_GetVBDecompilerPath"		: 56,          # (v3.5+)
    "VBD_GetModuleFunctionCode"       : 57,          # in "fast decompilation" mode (v3.5+) \
    "VBD_SetStatusBarText"            : 58,          # (v3.5+) \
    "VBD_GetFrxIconCount"             : 60,          # (v5.0+) \
    "VBD_GetFrxIconOffset"            : 61,          # (v5.0+) \
    "VBD_GetFrxIconSize"              : 62,          # (v5.0+)
    # Get Module Function Disasm
    "VBD_GetModuleFunctionDisasm"     : 70,          # (v9.4+)
    # Set Module Function Disasm
    "VBD_SetModuleFunctionDisasm"     : 71,          # (v9.4+)
    # Update changed window content
    "VBD_UpdateAll"			: 100}


class VBD_Client():
    def __init__(self, verbose=False):
        self.nc = None
        self.open(verbose)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()
        return isinstance(value, TypeError)

    def open(self, verbose=False):
        tries = 5
        _tries = tries
        while tries:
            try:
                self.nc = nclib.Netcat(('localhost', 6868), verbose=verbose)
                return
            except Exception as e:
                tries -= 1
                print(f"Connection Error {_tries-tries}/{_tries}. Sleeping 3 seconds and trying again")
                if not tries:
                    raise Exception(e)
                time.sleep(3)

    def close(self):
        try:
            self.nc.send(b"END")
            self.nc.close()
        except:
            pass

    def call(self, f, param1=0, param2=0, param3=b"\x00"):
        if isinstance(f, int):
            if f not in VBD_vlType.values():
                raise Exception(f"No ordinal found: {f}")
        elif isinstance(f, str):
            if f not in VBD_vlType.keys():
                raise Exception(f"No function name found: {f}")
            f = VBD_vlType[f]
        else:
            raise Exception(f"Unexpected function type: {type(f)}")

        if not isinstance(param1, int):
            raise Exception("Param1 should bt integer!")
        if not isinstance(param2, int):
            raise Exception("Param2 should bt integer!")

        if (not isinstance(param3, bytes)) and (not isinstance(param3, bytearray)):
            raise Exception("Param3 should be bytes or bytearray!")

        msg = b"VBD\x00" + struct.pack("<I", f) + struct.pack("<I", param1) + struct.pack("<I", param2) + param3
        self.nc.send(msg)

        rcv = b""
        while (not rcv) or (rcv[-1] != 0 or rcv[-2] != 0):
            rcv += self.nc.recv()
        return rcv[:-4] # the last four are zeroes



def single_call(func_id =VBD_vlType["VBD_SetVBProject"], param1=0, param2=0, param3=b"\x00"):
    with VBD_Client() as client:
        return client.call(func_id, param1, param2, param3)



def single_call_old(func_id=VBD_vlType["VBD_SetVBProject"], param1=0, param2=0, param3=b"\x00"):
    nc = nclib.Netcat(('localhost', 6868), verbose=True)
    msg = b"VBD\x00" + struct.pack("<I", func_id) + struct.pack("<I", param1) + struct.pack("<I", param2) + param3
    #print(msg)
    nc.send(msg)
    time.sleep(0.5)
    rcv = b""
    while (not rcv) or (rcv[-1] != 0 or rcv[-2] != 0):
        rcv += nc.recv()
    #print(rcv)
    time.sleep(0.5)
    nc.send(b"END")
    time.sleep(0.5)
    #print(nc.recv())
    nc.close()
    return rcv