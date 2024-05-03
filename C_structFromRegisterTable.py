# -*- coding: utf-8 -*-
"""
Created on Thu May  2 09:50:45 2024

@author: lastline
"""
from collections.abc import Iterable   # import directly from collections for Python < 3.3


class memValue:
    def __init__(self, name, address, startBit, bitSize, cType = "uint32_t"):
        for c in list(" .;-:/\\"):
            name = name.replace(c,'_')        
        for c in list("()%=*!#☺&+[]"):
            name = name.replace(c,'')
            
        self.name = name
        self.address = address
        self.startBit = startBit
        self.bitSize = bitSize
        self.cType = cType
    
    def C_structSyntax(self):
        if "[]" in self.cType:
            Type = self.cType.replace("[]", "")
            return f"    {Type} {self.name} [{self.bitSize}];\n"
        else:
            return f"    {self.cType} {self.name} : {self.bitSize};\n"
    def bitAddress(self):
        return self.address * 8 + self.startBit
    
    @staticmethod
    def generateReserved(startBitAddress, bitSize):
        endBitAddress = startBitAddress + bitSize - 1
        wordDistance = (endBitAddress // 32) - (startBitAddress // 32)
        if wordDistance == 0:
            return [memValue("Reserved", startBitAddress // 8, startBitAddress & 31, bitSize)]
        resList = []
        if(startBitAddress & 31):
            partialSize = 32 - (startBitAddress & 31)
            resList.append(memValue("Reserved", (startBitAddress // 32) * 4, startBitAddress & 31, partialSize))
            bitSize -= partialSize
        if(bitSize > 32):
            resList.append(memValue("Reserved", (startBitAddress // 32) * 4 + 4, 0, bitSize // 32, cType="uint32_t[]"))
            bitSize &= 31
        
        if(bitSize > 0):
            resList.append(memValue("Reserved", (startBitAddress // 32) * 4, 0, bitSize))
        
        return resList
    
    
    @staticmethod
    def fillList(memValues):
        currentBitAddress = 0
        finalList = []                  
        for i in range(len(memValues)):
            mv = memValues[i]
            mv.address -= memValues[0].address
            nextBitAddress = mv.bitAddress()
            if currentBitAddress > nextBitAddress:
                print(f"Error: memory value {mv.name} (address {mv.address} bit {mv.startBit}, size {mv.bitSize}) has an overlap with the previous values")
            if currentBitAddress != nextBitAddress:
                reservedList = memValue.generateReserved(currentBitAddress, nextBitAddress-currentBitAddress)
                finalList += reservedList
            finalList.append(mv)
            currentBitAddress = nextBitAddress + mv.bitSize
        return finalList
                
    
    @staticmethod
    def createC_struct(structName, memValues):
        
        string = f"struct {structName}{{\n"
        
        memValues = memValue.fillList(memValues)
        
        reservedIdx = 0
        for mv in memValues:
            #for now, the structure does not have holes
            # if mv.startBit != currentBit:
            #     holeSize = mv.startBit - currentBit if (mv.address == currentAddress) else 32 - currentBit
            #     string += memValue(f"reserved_{reservedIdx}", 0,0, holeSize.C_structSyntax())
            #     reservedIdx += 1
            # if currentBit == 32:
            #     currentBit = 0
            #     currentAddress += 4
                
            # if mv.address > currentAddress:
                
            if("Reserved" in mv.name):
                mv.name += f"_{reservedIdx}"
                reservedIdx += 1
            string += mv.C_structSyntax()
            
            # if currentBit == 32:
            #     currentBit = 0
            #     currentAddress += 4
            
                
        string += f"}} {structName};"
        return string
        
def redPitayaRegisterReader(line):
    #format: relativeAddress, registerName, [valueName, maxBit:minBit, read/write]
    parts = line.strip().split(', ')
    address = int(parts[0], 16)
    registerName = parts[1]
    memVals = []
    for i in range((len(parts) - 2) // 3):
        valueName = parts[2 + 3 * i + 0]
        bitRange =  parts[2 + 3 * i + 1].split(':')
        if(len(bitRange) == 1):
            startBit = int(bitRange[0])
            bitSize = 1
        else:
            startBit = int(bitRange[1])
            bitSize = int(bitRange[0]) - startBit + 1
        memVals.append(memValue(registerName+"_"+valueName, address, startBit, bitSize))
    return memVals[::-1]

def read_registers_from_file(file_path, parsingFunction):
    """
    Reads register information from a file and returns a list of tuples.
    Each tuple contains (variable_name, address, start_bit, bit_size).
    """
    registers = []
    with open(file_path, 'r') as file:
        for line in file:
            memVal = parsingFunction(line)
            if isinstance(memVal, Iterable):
                registers += memVal
            else:
                registers.append(memVal)
    return registers

def generate_c_struct(registers, struct_name):
    """
    Generates a C struct definition based on the list of registers.
    """
    struct_definition = f"struct {struct_name} {{\n"
    for variable_name, _, start_bit, bit_size in registers:
        struct_definition += f"    uint32_t {variable_name}\t: {bit_size};\n"
    struct_definition += f"}} {struct_name};"
    return struct_definition

# Read registers from the file (assuming the file is named "registers.txt")
registers = read_registers_from_file("C:/Users/lastline/Downloads/registers.txt", redPitayaRegisterReader)

# Generate the C struct definition
struct_name = "Oscilloscope"
# c_struct_code = generate_c_struct(registers, struct_name)
c_struct_code = memValue.createC_struct(struct_name, registers)

# Print the C struct code
print(c_struct_code)
