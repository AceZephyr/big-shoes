import ctypes.wintypes
import os
import re
import threading
import time

import win32api
import win32process
import win32security

import constants
# from main_window import show_error

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


class Address:

    def __init__(self, psx_address: int, pc_address: int, size: int, name: str):
        self.psx_address = psx_address
        self.pc_address = pc_address
        self.size = size
        self.name = name


class HookablePlatform:
    def __init__(self, name, is_psx, version, address_func):
        self.name = name
        self.is_psx = is_psx
        self.version = version
        self._address_func = address_func

    def read_int(self, hook, address: Address):
        a = self._address_func(hook, hook.hooked_process_handle, address, self.version)
        return int.from_bytes(win32process.ReadProcessMemory(hook.hooked_process_handle, a, address.size // 8),
                              byteorder='little')

    def read_bytes(self, hook, address: Address, size: int):
        a = self._address_func(hook, address, self.version)
        return win32process.ReadProcessMemory(hook.hooked_process_handle, a, size)


def adjust_privilege(name, attr=win32security.SE_PRIVILEGE_ENABLED):
    if isinstance(name, str):
        state = (win32security.LookupPrivilegeValue(None, name), attr)
    else:
        state = name
    hToken = win32security.OpenProcessToken(win32process.GetCurrentProcess(),
                                            win32security.TOKEN_ALL_ACCESS)
    return win32security.AdjustTokenPrivileges(hToken, False, [state])


def get_emu_process_ids():
    adjust_privilege(win32security.SE_DEBUG_NAME)

    MAX_PATH = 260

    processes = win32process.EnumProcesses()

    pids = {}
    for process_id in processes:
        hProcess = OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, process_id)
        if hProcess:
            ImageFileName = (ctypes.c_char * MAX_PATH)()
            if GetProcessImageFileName(hProcess, ImageFileName, MAX_PATH) > 0:
                filename_bytes = os.path.basename(ImageFileName.value)
                filename = filename_bytes.decode("ascii")
                for emu_name in Hook.EMULATOR_MAP.keys():
                    if re.search(Hook.EMULATOR_MAP[emu_name][0], filename):
                        if emu_name in pids:
                            pids[emu_name].append(process_id)
                        else:
                            pids[emu_name] = [process_id]
            CloseHandle(hProcess)
    return pids


def get_pc_process_id():
    adjust_privilege(win32security.SE_DEBUG_NAME)

    MAX_PATH = 260

    processes = win32process.EnumProcesses()

    for process_id in processes:
        hProcess = OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, process_id)
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


def psxfin_address_func(hook, process_handle, address: Address, version: str):
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
            hook.stop()
            raise constants.BadHookException()
    return hook.base_cache + address.psx_address


def retroduck_address_func(hook, process_handle, address: Address, version: str):
    if hook.base_cache is None:
        module_handles = win32process.EnumProcessModulesEx(process_handle, 0x03)
        for module_handle in sorted(module_handles):
            filename = win32process.GetModuleFileNameEx(process_handle, module_handle)
            if filename.lower().endswith("duckstation_libretro.dll"):
                base1 = module_handle + 0x40E078
                hook.base_cache = int.from_bytes(win32process.ReadProcessMemory(process_handle, base1, 8),
                                                 byteorder='little')
                break
    return hook.base_cache + address.psx_address


def manual_address_func(hook, process_handle, address: Address, version: str):
    if hook.manual_address is None:
        raise Exception("No manual address")
    return hook.manual_address + address.psx_address


def pc_address_func(hook, process_handle, address: Address, version: str):
    if hook.base_cache is None:
        module_handles = win32process.EnumProcessModulesEx(process_handle, 0x03)
        for module_handle in sorted(module_handles):
            filename = win32process.GetModuleFileNameEx(process_handle, module_handle)
            if filename.lower().endswith("ff7_en.exe"):
                hook.base_cache = module_handle
    return hook.base_cache + address.pc_address


_RETROARCH_KNOWN_ADDRESSES = [
    0x30000000,
    0x7FFF0000,
    0x80000000
]


def retroarch_try(process_handle, addr: int):
    for x in range(0, len(constants.RNG)):
        try:
            if int.from_bytes(win32process.ReadProcessMemory(process_handle, 0xE0638 + addr + x, 1),
                              byteorder='little') != constants.RNG[x]:
                return False
        except Exception as e:  # memory probably wasn't mapped so it errored
            return False
    return True


def retroarch_search(process_id):
    adjust_privilege(win32security.SE_DEBUG_NAME)
    hooked_process_handle = OpenProcess(0x1F0FFF, False, process_id)
    # try known addresses first
    for addr in _RETROARCH_KNOWN_ADDRESSES:
        if retroarch_try(hooked_process_handle, addr):
            CloseHandle(hooked_process_handle)
            return addr
    # attempt to search for it anyway
    for addr in range(0, 0xFFFFFFFF, 0x1000):
        if retroarch_try(hooked_process_handle, addr):
            CloseHandle(hooked_process_handle)
            return addr
    CloseHandle(hooked_process_handle)
    return None


class Hook:

    def read(self, address: Address):
        return self.hooked_platform.read_int(self, address)

    EMULATOR_MAP = {
        "PSXFin": (
            "[Pp][Ss][Xx][Ff][Ii][Nn]",
            [
                HookablePlatform("PSXfin v1.13", True, "1.13", psxfin_address_func)
            ]
        ),
        "BizHawk": (
            "[Ee]mu[Hh]awk",
            [
                HookablePlatform("BizHawk 2.6.2", True, "1", bizhawk_address_func),
                HookablePlatform("BizHawk 2.5.2 - 2.6.1", True, "2", bizhawk_address_func),
                HookablePlatform("BizHawk 2.4.1 - 2.5.1", True, "3", bizhawk_address_func),
                HookablePlatform("BizHawk 2.3.2 - 2.4.0", True, "4", bizhawk_address_func)
            ]
        ),
        "Retroarch": (
            "[Rr]etro[Aa]rch",
            [
                HookablePlatform("Retroarch Duckstation", True, "Duck", retroduck_address_func),
                HookablePlatform("Retroarch (Manual)", True, "__MANUAL__", manual_address_func),
            ]
        )
    }

    PC_PLATFORM = HookablePlatform("PC", False, "", pc_address_func)

    def start(self):
        self.thread = threading.Thread(target=self.main)
        self.thread.start()

    def stop(self):
        with self.running_lock:
            self.running = False

    def is_running(self):
        with self.running_lock:
            return self.running

    def read_key(self, key):
        with self.address_state_lock:
            if key not in self.state or key not in self.addresses:
                raise ValueError("Key not present")
            return self.state[key]

    def register_address(self, address, default_value=None):
        with self.address_state_lock:
            new_key = self.next_key
            self.next_key += 1

            self.addresses[new_key] = address
            self.state[new_key] = default_value

            return new_key, self.state[new_key]

    def deregister_address(self, key):
        with self.address_state_lock:
            if key in self.addresses:
                del self.addresses[key]
            if key in self.state:
                del self.state[key]

    def main(self):
        self.base_cache = None
        adjust_privilege(win32security.SE_DEBUG_NAME)
        # hook into platform
        self.hooked_process_handle = OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION | PROCESS_VM_READ, True,
                                                 self.hooked_process_id)
        if self.hooked_process_handle is None:
            err = win32api.GetLastError()
            print(f"Hooked process handle error: {err}")
            # show_error("Bad Hook", f"Hooked process handle error: {err}")

        self.parent_app.update_title(self.parent_app.settings.CONNECTED_TO_TEXT + self.hooked_platform.name)

        with self.running_lock:
            self.running = True

        while self.is_running():
            try:
                with self.address_state_lock:
                    for key in self.addresses:
                        self.state[key] = self.read(self.addresses[key])

            except Exception as e:
                if isinstance(e, constants.BadHookException):
                    # show_error("Bad Hook", "Bad Hook")
                    self.running = False
                    break
                if e is RuntimeError:
                    self.running = False
                    break
                if str(type(e)) == '<class \'pywintypes.error\'>':
                    if e.args[0] == 299:  # process was closed probably
                        self.running = False
                        break
                raise e
            time.sleep(1 / self.parent_app.settings.UPDATES_PER_SECOND)
        CloseHandle(self.hooked_process_handle)
        try:
            self.hooked_process_handle = None
            self.hooked_process_id = None
            self.hooked_platform = None

            self.parent_app.update_title(self.parent_app.settings.DISCONNECTED_TEXT)

        except RuntimeError as err:
            print("uh oh", err)

    def __init__(self, parent_app):
        self.parent_app = parent_app
        self.base_cache = None
        self.manual_address = None
        self.thread = threading.Thread(target=self.main)
        self.running = False
        self.running_lock = threading.Lock()

        self.addresses = {}
        self.state = {}
        self.next_key = 0
        self.address_state_lock = threading.Lock()

        self.hooked_platform = None
        self.hooked_process_id = None
        self.hooked_process_handle = None
