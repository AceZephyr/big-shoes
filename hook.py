import settings

import ctypes.wintypes
import win32process as wproc
import os
from enum import Enum

PROCESS_VM_OPERATION = 0x0008
PROCESS_VM_READ = 0x0010
PROCESS_VM_WRITE = 0x0020

Psapi = ctypes.WinDLL('Psapi.dll')
GetProcessImageFileName = Psapi.GetProcessImageFileNameA
GetProcessImageFileName.restype = ctypes.wintypes.DWORD

Kernel32 = ctypes.WinDLL('kernel32.dll')
OpenProcess = Kernel32.OpenProcess
OpenProcess.restype = ctypes.wintypes.HANDLE

CloseHandle = Kernel32.CloseHandle

_BASE_ADDRESS_CACHE = None


class Address(int, Enum):
    def __new__(cls, value, psx_address, pc_address):
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.psx_address = psx_address
        obj.pc_address = pc_address
        return obj

    STEP_ID = (0, 0x9C540, 0x8C165C)
    OFFSET = (1, 0x9AD2C, 0x8C1660)
    STEP_FRACTION = (2, 0x9C6D8, 0x8C1664)
    DANGER = (3, 0x7173C, 0x8C1668)
    FORMATION_ACCUMULATOR = (4, 0x71C20, 0x8C1650)
    FIELD_ID = (5, 0x9A05C, 0x8C15D0)
    SELECTED_TABLE = (6, 0x9AC30, None)  # TODO: find on PC
    DANGER_DIVIDEND_MULTIPLIER = (7, 0x9AC04, None)  # TODO: find on PC


class HookablePlatform:
    def __init__(self, name, is_psx, version, address_func):
        self.name = name
        self.is_psx = is_psx
        self.version = version
        self._address_func = address_func

    def read_int(self, process_handle, address: Address, size_bits: int):
        a = self._address_func(process_handle, address, self.version)
        return int.from_bytes(wproc.ReadProcessMemory(process_handle, a, size_bits // 8), byteorder='little')

    def read_bytes(self, process_handle, address: Address, size: int):
        a = self._address_func(address, self.version)
        return wproc.ReadProcessMemory(process_handle, a, size)


def psxfin_address_func(process_handle, address: Address, version: str):
    global _BASE_ADDRESS_CACHE
    a = address.psx_address
    if _BASE_ADDRESS_CACHE is None:
        module_handles = wproc.EnumProcessModulesEx(process_handle, 0x03)
        for module_handle in sorted(module_handles):
            filename = wproc.GetModuleFileNameEx(process_handle, module_handle)
            if filename.endswith("psxfin.exe"):
                base1 = module_handle + 0x1899BC
                base2 = int.from_bytes(wproc.ReadProcessMemory(process_handle, base1, 4), byteorder='little') + 0x30
                _BASE_ADDRESS_CACHE = int.from_bytes(wproc.ReadProcessMemory(process_handle, base2, 4),
                                                     byteorder='little')
                break
    return _BASE_ADDRESS_CACHE + address.psx_address


def bizhawk_address_func(process_handle, address: Address, version: str):
    if version == "2.3.2":
        base = 0x7FF888750000 + 0x11D880
    elif version == "2.5.2":
        base = 0x7FF88ABD0000 + 0x310F80
    elif version == "2.6.1":
        base = 0x7FF888A10000 + 0x310F80
    else:
        raise NotImplementedError("BizHawk version not implemented: " + version)
    return base + address.psx_address


def epsxe_address_func(process_handle, address: Address, version: str):
    global _BASE_ADDRESS_CACHE
    if _BASE_ADDRESS_CACHE is None:
        module_handles = wproc.EnumProcessModulesEx(process_handle, 0x03)
        for module_handle in sorted(module_handles):
            filename = wproc.GetModuleFileNameEx(process_handle, module_handle)
            if filename.lower().endswith("epsxe.exe"):
                _BASE_ADDRESS_CACHE = module_handle + 0x6579A0
    return _BASE_ADDRESS_CACHE + address.psx_address


def nocashpsx_address_func(process_handle, address: Address, version: str):
    raise NotImplementedError("no$psx support not implemented yet")


def retroarch_address_func(process_handle, address: Address, version: str):
    if version == "Base Address 0x30000000":
        return 0x30000000 + address.psx_address
    elif version == "Base Address 0x40000000":
        return 0x40000000 + address.psx_address


def pc_address_func(process_handle, address: Address, version: str):
    global _BASE_ADDRESS_CACHE
    if _BASE_ADDRESS_CACHE is None:
        module_handles = wproc.EnumProcessModulesEx(process_handle, 0x03)
        for module_handle in sorted(module_handles):
            filename = wproc.GetModuleFileNameEx(process_handle, module_handle)
            if filename.lower().endswith("ff7_en.exe"):
                _BASE_ADDRESS_CACHE = module_handle
    return _BASE_ADDRESS_CACHE + address.pc_address


EMULATOR_MAP = {
    "psxfin.exe": [HookablePlatform("PSXfin v1.13", True, "1.13", psxfin_address_func)],
    "ePSXe.exe": [HookablePlatform("ePSXe", True, "", epsxe_address_func)],
    "EmuHawk.exe": [HookablePlatform("BizHawk 2.6.1", True, "2.6.1", bizhawk_address_func),
                    HookablePlatform("BizHawk 2.5.2", True, "2.5.2", bizhawk_address_func),
                    HookablePlatform("BizHawk 2.3.2", True, "2.3.2", bizhawk_address_func)],
    "NO$PSX.EXE": [HookablePlatform("no$psx", True, "", nocashpsx_address_func)],
    "retroarch.exe": [HookablePlatform("RetroArch", True, "Base Address 0x30000000", retroarch_address_func),
                      HookablePlatform("RetroArch", True, "Base Address 0x40000000", retroarch_address_func)]
}

PC_PLATFORM = HookablePlatform("PC", False, "", pc_address_func)


def get_emu_process_ids():
    MAX_PATH = 260

    processes = wproc.EnumProcesses()

    pids = {}
    for process_id in processes:
        hProcess = OpenProcess(PROCESS_VM_OPERATION | PROCESS_VM_READ | PROCESS_VM_WRITE, False, process_id)
        if hProcess:
            ImageFileName = (ctypes.c_char * MAX_PATH)()

            if GetProcessImageFileName(hProcess, ImageFileName, MAX_PATH) > 0:
                filename_bytes = os.path.basename(ImageFileName.value)
                filename = filename_bytes.decode("ascii")
                if filename in EMULATOR_MAP.keys():
                    if filename in pids:
                        pids[filename].append(process_id)
                    else:
                        pids[filename] = [process_id]
            CloseHandle(hProcess)
    return pids


def get_pc_process_id():
    MAX_PATH = 260

    processes = wproc.EnumProcesses()

    for process_id in processes:
        hProcess = OpenProcess(PROCESS_VM_OPERATION | PROCESS_VM_READ | PROCESS_VM_WRITE, False, process_id)
        if hProcess:
            ImageFileName = (ctypes.c_char * MAX_PATH)()

            if GetProcessImageFileName(hProcess, ImageFileName, MAX_PATH) > 0:
                filename_bytes = os.path.basename(ImageFileName.value)
                filename = filename_bytes.decode("ascii")
                if filename.lower() == "ff7_en.exe":
                    CloseHandle(hProcess)
                    return process_id
            CloseHandle(hProcess)
    return None
