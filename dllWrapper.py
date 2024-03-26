# -*- coding: utf-8 -*-
"""
Created on Fri Mar 22 10:03:36 2024

@author: lastline
"""

import ctypes


class dllWrapper:
    
    def __init__(self, dllPath):
        self.dll = ctypes.CDLL(dllPath)
                
    def addFunction(self, functionDeclaration):
        (fun, funName) = dllWrapper.create_dll_function(self.dll, functionDeclaration)
        setattr(self, funName, fun)
    
    @staticmethod
    def create_dll_function(dll, c_function_declaration):
        """
        Creates a Python function that calls a C function from a DLL.
    
        Args:
            dll (ctypes.CDLL): the DLL file.
            c_function_declaration (str): Declaration of the C function (e.g., "int32_t Check_HeadSerial(uint8_t bID, char HeadSerial[], int32_t CharSize)").
    
        Returns:
            function: A Python function that calls the specified C function from the DLL.
        """
        # Parse the C function declaration
        return_type, function_name, args = dllWrapper.parse_c_function_declaration(c_function_declaration)

        # Load the DLL
        if type(dll) == str:    
            dll = ctypes.CDLL(dll)
    
        # Get the C function from the DLL
        c_function = getattr(dll, function_name)
    
        # Set argument types and return type
        c_function.argtypes = args
        if return_type != type(None):
            c_function.restype = return_type
    
        # Create a Python function that wraps the C function
        def python_function(*args):
            
            ret_args = [0] * len(args)
            # c_args = [arg_type(arg) for arg, arg_type in zip(args, c_function.argtypes)]
            for i in range(len(args)):
                if str(type(c_function.argtypes[i])) == "<class '_ctypes.PyCPointerType'>":
                    try:
                        l = len(args[i])
                        ret_args[i] = (c_function.argtypes[i]._type_ * l)(*args[i])
                    except:
                        ret_args[i] = (c_function.argtypes[i]._type_ * 1)(args[i]) 
                        
                elif c_function.argtypes[i] == ctypes.c_void_p:
                    ret_args[i] = ctypes.cast(args[i], c_function.argtypes[i])
                else:        
                    ret_args[i] = c_function.argtypes[i](args[i])
            # Call the C function
            
            if return_type != type(None):
                retVal = c_function(*ret_args)
            else:
                c_function(*ret_args)
            
            
            updatedInputs = [None] * len(args)
            for i in range(len(args)):
                if str(type(c_function.argtypes[i])) == "<class '_ctypes.PyCPointerType'>":
                    updatedInputs[i] = list(ret_args[i])
                else:
                    updatedInputs[i] = ret_args[i].value
            if len(args) == 1:
                updatedInputs = updatedInputs[0]
            if return_type != type(None):
                return retVal, updatedInputs
            else:
                return updatedInputs
    
        return python_function, function_name
    
    @staticmethod
    def parse_c_function_declaration(c_function_declaration):
        """
        Parses a C function declaration and extracts the return type, function name, and argument types.
    
        Args:
            c_function_declaration (str): Declaration of the C function.
    
        Returns:
            tuple: (return_type, function_name, argument_types)
        """
        # Split the declaration into tokens
        tokens = c_function_declaration.split()
    
        # Extract return type and function name
        return_type = dllWrapper.parse_argument_type(tokens[0])
        function_name = tokens[1].split("(")[0]
    
        # Extract argument types
        argument_types = []
        tokens[1] = tokens[1].split("(")[1]
        types = tokens[1::2]
        names = tokens[2::2]
        
        
        for i in range(len(names)):
            
            argument_types.append(dllWrapper.parse_argument_type(types[i]))
            
            if "[]" in names[i] or "*" in names[i] or "*" in types[i]:
                if argument_types[-1] == type(None):
                    argument_types[-1] = ctypes.c_void_p
                else:
                    argument_types[-1] = ctypes.POINTER(argument_types[-1])
        
        return return_type, function_name, argument_types
    
    @staticmethod
    def parse_argument_type(token):
        """
        Parses an argument type from a token.
    
        Args:
            token (str): Token representing an argument type.
    
        Returns:
            type: Python type corresponding to the argument type.
        """
        
        if "uint8_t" in token:
            return ctypes.c_uint8
        if "int32_t" in token:
            return ctypes.c_int32
        if "uint32_t" in token:
            return ctypes.c_uint32
        if "char" in token:
            return ctypes.c_char
        if "double" in token:
            return ctypes.c_double
        if "float" in token:
            return ctypes.c_float
        if "void" in token:
            return type(None)
        
        print("type '"+token+"' not recognized, defaulting to int32")
        return ctypes.c_int32
        
    @staticmethod
    def voidPointerTo(array, arrayType = ctypes.c_uint8):
        return (arrayType * len(array))(*array)

# # Example usage:
# q = dllWrapper("C:/Users/lastline/Desktop/Hamamatsu_SLM/USB_Control_SDK/hpkSLMdaLV_cdecl_64bit/hpkSLMdaLV.dll")

# q.addFunction("uint32_t Write_SDBMPPath(uint8_t bID, uint8_t *Path, uint32_t SDSlotNo)")

# q.Write_SDBMPPath(1, dllWrapper.voidPointerTo([1,2,3]), 3)



# slm = dllWrapper("C:/Users/lastline/Desktop/Hamamatsu_SLM/USB_Control_SDK/hpkSLMdaLV_cdecl_64bit/hpkSLMdaLV.dll")

# slm.addFunction("int32_t Open_Dev(uint8_t bIDList[], int32_t bIDSize)")
# slm.addFunction("int32_t Close_Dev(uint8_t bIDList[], int32_t bIDSize)")
# slm.addFunction("int32_t Check_HeadSerial(uint8_t bID, char HeadSerial[], int32_t CharSize)")
# slm.addFunction("int32_t Write_FMemBMPPath(uint8_t bID, char Path[], uint32_t SlotNo)")
# slm.addFunction("int32_t Write_FMemArray(uint8_t bID, uint8_t ArrayIn[], int32_t ArraySize, uint32_t XPixel, uint32_t YPixel, uint32_t SlotNo)")
# slm.addFunction("int32_t Change_DispSlot(uint8_t bID, uint32_t SlotNo)")
# slm.addFunction("int32_t Check_Temp(uint8_t bID, double *HeadTemp, double *CBTemp)")
# slm.addFunction("int32_t Check_FMem_Slot(uint8_t bID, uint32_t ArraySize, uint32_t XPixel, uint32_t YPixel, uint32_t SlotNo, uint8_t ReadArray[])")
# slm.addFunction("int32_t Check_Disp_IMG(uint8_t bID, uint32_t ArraySize, uint32_t XPixel, uint32_t YPixel, uint8_t ReadArray[])")
# slm.addFunction("int32_t Mode_Select(uint8_t bID, uint8_t Mode)")
# slm.addFunction("int32_t Mode_Check(uint8_t bID, uint32_t *Mode)")
# slm.addFunction("int32_t Check_LED(uint8_t bID, uint32_t *LED_Status)")
# slm.addFunction("int32_t Check_IO(uint8_t bID, uint32_t *IO_Status)")
# slm.addFunction("void Reboot(uint8_t bID)")
# slm.addFunction("int32_t Write_SDBMPPath(uint8_t bID, char Path[], uint32_t SDSlotNo)")
# slm.addFunction("int32_t Write_SDArray(uint8_t bID, uint8_t ArrayIn[], int32_t ArraySize, uint32_t XPixel, uint32_t YPixel, uint32_t SDSlotNo)")
# slm.addFunction("int32_t Check_SD_Slot(uint8_t bID, uint32_t ArraySize, uint32_t XPixel, uint32_t YPixel, uint32_t SDSlotNo, uint8_t ReadArray[])")
# slm.addFunction("int32_t Upload_from_SD_to_FMem(uint8_t bID, uint32_t SDSlotNo, uint32_t FMemSlotNo)")



