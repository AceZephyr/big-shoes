import ctypes.wintypes
import os
import threading
import time
from enum import Enum
from typing import TYPE_CHECKING

import win32process
import win32security

import constants
import stepgraph

if TYPE_CHECKING:
    from main_window import MainWindow

PROCESS_VM_OPERATION = 0x0008
PROCESS_VM_READ = 0x0010
PROCESS_VM_WRITE = 0x0020
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000

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
    SELECTED_TABLE = (6, 0x9AC30, 0x8C0DC4)
    DANGER_DIVISOR_MULTIPLIER = (7, 0x9AC04, 0x8C0D98)
    LURE_RATE = (8, 0x62F19, 0x9BCAD9)
    PREEMPT_RATE = (9, 0x62F1B, 0x9BCADB)
    LAST_ENCOUNTER_FORMATION = (10, 0x7E774, 0x8C1654)


class HookablePlatform:
    def __init__(self, name, is_psx, version, address_func):
        self.name = name
        self.is_psx = is_psx
        self.version = version
        self._address_func = address_func

    def read_int(self, hook, address: Address, size_bits: int):
        a = self._address_func(hook, hook.hooked_process_handle, address, self.version)
        return int.from_bytes(win32process.ReadProcessMemory(hook.hooked_process_handle, a, size_bits // 8),
                              byteorder='little')

    def read_bytes(self, hook, address: Address, size: int):
        a = self._address_func(hook, address, self.version)
        return win32process.ReadProcessMemory(hook.hooked_process_handle, a, size)


def get_emu_process_ids():
    MAX_PATH = 260

    processes = win32process.EnumProcesses()

    pids = {}
    for process_id in processes:
        hProcess = OpenProcess(PROCESS_VM_OPERATION | PROCESS_VM_WRITE | PROCESS_VM_READ, False, process_id)
        if hProcess:
            ImageFileName = (ctypes.c_char * MAX_PATH)()
            if GetProcessImageFileName(hProcess, ImageFileName, MAX_PATH) > 0:
                filename_bytes = os.path.basename(ImageFileName.value)
                filename = filename_bytes.decode("ascii")
                if filename in Hook.EMULATOR_MAP.keys():
                    if filename in pids:
                        pids[filename].append(process_id)
                    else:
                        pids[filename] = [process_id]
            CloseHandle(hProcess)
    return pids


def get_pc_process_id():
    MAX_PATH = 260

    processes = win32process.EnumProcesses()

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


def adjust_privilege(name, attr=win32security.SE_PRIVILEGE_ENABLED):
    if isinstance(name, str):
        state = (win32security.LookupPrivilegeValue(None, name), attr)
    else:
        state = name
    hToken = win32security.OpenProcessToken(win32process.GetCurrentProcess(),
                                            win32security.TOKEN_ALL_ACCESS)
    return win32security.AdjustTokenPrivileges(hToken, False, [state])


def psxfin_address_func(hook, process_handle, address: Address, version: str):
    address.psx_address
    if hook.base_cache is None:
        module_handles = win32process.EnumProcessModulesEx(process_handle, 0x03)
        for module_handle in sorted(module_handles):
            filename = win32process.GetModuleFileNameEx(process_handle, module_handle)
            if filename.endswith("psxfin.exe"):
                base1 = module_handle + 0x1899BC
                base2 = int.from_bytes(win32process.ReadProcessMemory(process_handle, base1, 4),
                                       byteorder='little') + 0x30
                hook.base_cache = int.from_bytes(win32process.ReadProcessMemory(process_handle, base2, 4),
                                                 byteorder='little')
                break
    return hook.base_cache + address.psx_address


_BIZHAWK_ADDRESS_MAP = {
    "1": 0x30DF80,
    "2": 0x310F80,
    "3": 0x30DF90,
    "4": 0x11D880,
}


def bizhawk_address_func(hook, process_handle, address: Address, version: str):
    if hook.base_cache is None:
        module_handles = win32process.EnumProcessModulesEx(process_handle, 0x03)
        for module_handle in sorted(module_handles):
            filename = win32process.GetModuleFileNameEx(process_handle, module_handle)
            if filename.lower().endswith("octoshock.dll"):
                if version in _BIZHAWK_ADDRESS_MAP:
                    hook.base_cache = module_handle + _BIZHAWK_ADDRESS_MAP[version]
                else:
                    raise NotImplementedError("BizHawk version not implemented: " + version)
        if hook.base_cache is None:
            raise Exception("asdf")
    return hook.base_cache + address.psx_address


# def epsxe_address_func(hook, process_handle, address: Address, version: str):
#     if hook.base_cache is None:
#         module_handles = win32process.EnumProcessModulesEx(process_handle, 0x03)
#         for module_handle in sorted(module_handles):
#             filename = win32process.GetModuleFileNameEx(process_handle, module_handle)
#             if filename.lower().endswith("epsxe.exe"):
#                 hook.base_cache = module_handle + 0x6579A0
#     return hook.base_cache + address.psx_address
#
#
# def nocashpsx_address_func(hook, process_handle, address: Address, version: str):
#     raise NotImplementedError("no$psx support not implemented yet")


def retroarch_address_func(hook, process_handle, address: Address, version: str):
    if version == "3":
        return 0x30000000 + address.psx_address
    elif version == "4":
        return 0x40000000 + address.psx_address


def pc_address_func(hook, process_handle, address: Address, version: str):
    if hook.base_cache is None:
        module_handles = win32process.EnumProcessModulesEx(process_handle, 0x03)
        for module_handle in sorted(module_handles):
            filename = win32process.GetModuleFileNameEx(process_handle, module_handle)
            if filename.lower().endswith("ff7_en.exe"):
                hook.base_cache = module_handle
    return hook.base_cache + address.pc_address


class Hook:

    def read(self, size: int, address: Address):
        return self.hooked_platform.read_int(self, address, size)

    EMULATOR_MAP = {
        "psxfin.exe": [HookablePlatform("PSXfin v1.13", True, "1.13", psxfin_address_func)],
        "EmuHawk.exe": [HookablePlatform("BizHawk 2.6.2", True, "1", bizhawk_address_func),
                        HookablePlatform("BizHawk 2.5.2 - 2.6.1", True, "2", bizhawk_address_func),
                        HookablePlatform("BizHawk 2.4.1 - 2.5.1", True, "3", bizhawk_address_func),
                        HookablePlatform("BizHawk 2.3.2 - 2.4.0", True, "4", bizhawk_address_func)],
        "retroarch.exe": [HookablePlatform("Base Address 0x30000000", True, "3", retroarch_address_func),
                          HookablePlatform("Base Address 0x40000000", True, "4", retroarch_address_func)],
    }

    PC_PLATFORM = HookablePlatform("PC", False, "", pc_address_func)

    def start(self):
        self.thread = threading.Thread(target=self.main)
        self.thread.start()

    def stop(self):
        self.running = False

    def main(self):
        self.base_cache = None
        adjust_privilege(win32security.SE_DEBUG_NAME)
        # hook into platform
        self.hooked_process_handle = OpenProcess(0x1F0FFF, False, self.hooked_process_id)

        self.app.connected_text.setText(self.app.settings.CONNECTED_TO_TEXT + self.hooked_platform.name)

        self.app.stepgraph.display_mode = stepgraph.DisplayMode.TRACK

        self.running = True

        last_update_time = time.time() - 1
        while self.running:
            try:
                # update display
                new_stepid = self.read(8, Address.STEP_ID)
                new_step_fraction = self.read(8, Address.STEP_FRACTION) // 32
                new_offset = self.read(8, Address.OFFSET)
                new_danger = self.read(16, Address.DANGER)
                new_fmaccum = self.read(8, Address.FORMATION_ACCUMULATOR)
                new_field_id = self.read(16, Address.FIELD_ID)
                new_selected_table = self.read(8, Address.SELECTED_TABLE) + 1
                new_danger_divisor_multiplier = self.read(16, Address.DANGER_DIVISOR_MULTIPLIER)
                new_lure_rate = self.read(8, Address.LURE_RATE)
                new_preempt_rate = self.read(8, Address.PREEMPT_RATE)
                new_last_encounter_formation = self.read(16, Address.LAST_ENCOUNTER_FORMATION)

                update = False
                force_update = time.time() - last_update_time > 1

                if force_update or new_stepid != self.app.current_step_state.step.step_id:
                    update = True
                    self.app.memory_view.cellWidget(0, 1).setText(" " + str(new_stepid))
                    self.app.current_step_state.step.step_id = new_stepid
                if force_update or new_step_fraction != self.app.current_step_state.step_fraction:
                    # update = True  # stepgraph doesn't care about fraction
                    self.app.memory_view.cellWidget(1, 1).setText(" " + str(new_step_fraction))
                    self.app.current_step_state.step_fraction = new_step_fraction
                if force_update or new_offset != self.app.current_step_state.step.offset:
                    update = True
                    self.app.memory_view.cellWidget(2, 1).setText(" " + str(new_offset))
                    self.app.current_step_state.step.offset = new_offset
                if force_update or new_danger != self.app.current_step_state.danger:
                    update = True
                    self.app.memory_view.cellWidget(3, 1).setText(" " + str(new_danger))
                    self.app.current_step_state.danger = new_danger
                if force_update or new_fmaccum != self.app.current_step_state.formation_value:
                    update = True
                    self.app.memory_view.cellWidget(4, 1).setText(" " + str(new_fmaccum))
                    self.app.current_step_state.formation_value = new_fmaccum
                if force_update or new_field_id != self.app.current_step_state.field_id:
                    field_id = new_field_id
                    if field_id in constants.FIELDS:
                        update = True
                        self.app.memory_view.cellWidget(5, 1).setText(" " + str(field_id))
                        self.app.current_step_state.field_id = field_id
                if force_update or new_selected_table != self.app.current_step_state.table_index:
                    update = True
                    self.app.memory_view.cellWidget(6, 1).setText(" " + str(new_selected_table))
                    self.app.current_step_state.table_index = new_selected_table
                if force_update or new_danger_divisor_multiplier != self.app.current_step_state.danger_divisor_multiplier:
                    update = True
                    self.app.memory_view.cellWidget(7, 1).setText(" " + str(new_danger_divisor_multiplier))
                    self.app.current_step_state.danger_divisor_multiplier = new_danger_divisor_multiplier
                if force_update or new_lure_rate != self.app.current_step_state.lure_rate:
                    update = True
                    self.app.memory_view.cellWidget(8, 1).setText(" " + str(new_lure_rate))
                    self.app.current_step_state.lure_rate = new_lure_rate
                if force_update or new_preempt_rate != self.app.current_step_state.preempt_rate:
                    update = True
                    self.app.memory_view.cellWidget(9, 1).setText(" " + str(new_preempt_rate))
                    self.app.current_step_state.preempt_rate = new_preempt_rate
                if force_update or new_last_encounter_formation != self.app.current_step_state.last_encounter_formation:
                    update = True
                    self.app.memory_view.cellWidget(10, 1).setText(" " + str(new_last_encounter_formation))
                    self.app.current_step_state.last_encounter_formation = new_last_encounter_formation

                if update:
                    self.app.stepgraph.signal_update()
                    self.app.update_formation_windows()
                    self.app.update()
                    last_update_time = time.time()

            except Exception as e:
                if e is RuntimeError:
                    self.running = False
                    break
                if str(type(e)) == '<class \'pywintypes.error\'>':
                    if e.args[0] == 299:  # process was closed probably
                        self.running = False
                        break
                raise e
            time.sleep(1 / self.app.settings.UPDATES_PER_SECOND)
        CloseHandle(self.hooked_process_handle)
        try:
            self.hooked_process_handle = None
            self.hooked_process_id = None
            self.hooked_platform = None

            self.app.stepgraph.display_mode = stepgraph.DisplayMode.DEFAULT

            self.app.connected_text.setText(self.app.settings.DISCONNECTED_TEXT)

            self.app.stepgraph.signal_update()
        except RuntimeError as err:
            print("uh oh", err)

    def __init__(self, app: "MainWindow"):
        self.app = app
        self.base_cache = None
        self.thread = threading.Thread(target=self.main)
        self.running = False

        self.hooked_platform = None
        self.hooked_process_id = None
        self.hooked_process_handle = None
