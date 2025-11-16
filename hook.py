import ctypes.wintypes
import os
import re
import threading
import time

import win32api
import win32con
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

CreateToolhelp32Snapshot = ctypes.windll.kernel32.CreateToolhelp32Snapshot
Process32First = ctypes.windll.kernel32.Process32First
Process32Next = ctypes.windll.kernel32.Process32Next

CloseHandle = Kernel32.CloseHandle


class MEMORY_BASIC_INFORMATION(ctypes.Structure):
    _fields_ = [("BaseAddress", ctypes.wintypes.LPVOID),
                ("AllocationBase", ctypes.wintypes.LPVOID),
                ("AllocationProtect", ctypes.wintypes.DWORD),
                ("PartitionId", ctypes.wintypes.WORD),
                ("RegionSize", ctypes.c_size_t),
                ("State", ctypes.wintypes.DWORD),
                ("Protect", ctypes.wintypes.DWORD),
                ("Type", ctypes.wintypes.DWORD)]

    def __repr__(self):
        return f'MEMORY_BASIC_INFORMATION(BaseAddress={self.BaseAddress if self.BaseAddress is not None else 0:#x}, ' \
               f'AllocationBase={self.AllocationBase if self.AllocationBase is not None else 0:#x}, ' \
               f'AllocationProtect={self.AllocationProtect:#x}, ' \
               f'PartitionId={self.PartitionId:#x}, ' \
               f'RegionSize={self.RegionSize:#x}, ' \
               f'State={self.State:#x}, ' \
               f'Protect={self.Protect:#x}, ' \
               f'Type={self.Type:#x})'


VirtualQueryEx = ctypes.windll.kernel32.VirtualQueryEx
VirtualQueryEx.restype = ctypes.c_size_t
VirtualQueryEx.argtypes = (ctypes.wintypes.HANDLE,
                           ctypes.wintypes.LPCVOID,
                           ctypes.POINTER(MEMORY_BASIC_INFORMATION),
                           ctypes.c_size_t)


class MODULEINFO(ctypes.Structure):
    _fields_ = [
        ("lpBaseOfDll", ctypes.wintypes.LPVOID),
        ("SizeOfImage", ctypes.wintypes.DWORD),
        ("EntryPoint", ctypes.wintypes.LPVOID)
    ]


GetModuleInformation = Psapi.GetModuleInformation
GetModuleInformation.restype = ctypes.c_bool
GetModuleInformation.argtypes = (ctypes.wintypes.HANDLE,
                                 ctypes.wintypes.HMODULE,
                                 ctypes.POINTER(MODULEINFO),
                                 ctypes.wintypes.DWORD)


class PROCESSENTRY32(ctypes.Structure):
    _fields_ = [('dwSize', ctypes.wintypes.DWORD),
                ('cntUsage', ctypes.wintypes.DWORD),
                ('th32ProcessID', ctypes.wintypes.DWORD),
                ('th32DefaultHeapID', ctypes.POINTER(ctypes.wintypes.ULONG)),
                ('th32ModuleID', ctypes.wintypes.DWORD),
                ('cntThreads', ctypes.wintypes.DWORD),
                ('th32ParentProcessID', ctypes.wintypes.DWORD),
                ('pcPriClassBase', ctypes.wintypes.LONG),
                ('dwFlags', ctypes.wintypes.DWORD),
                ('szExeFile', ctypes.c_char * 260)]


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


def get_process_list():
    hProcessSnap = CreateToolhelp32Snapshot(0x00000002, 0)

    pEntry = PROCESSENTRY32()
    pEntry.dwSize = ctypes.sizeof(PROCESSENTRY32)

    process_list_out = []

    if Process32First(hProcessSnap, ctypes.byref(pEntry)):
        while True:
            yield pEntry
            if not Process32Next(hProcessSnap, ctypes.byref(pEntry)):
                break
    CloseHandle(hProcessSnap)
    return process_list_out


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
    hProcessSnap = CreateToolhelp32Snapshot(0x00000002, 0)

    pEntry = PROCESSENTRY32()
    pEntry.dwSize = ctypes.sizeof(PROCESSENTRY32)

    if Process32First(hProcessSnap, ctypes.byref(pEntry)):
        while True:
            exe_name_str = pEntry.szExeFile.decode("ascii")
            if "ff7_en.exe".casefold() == exe_name_str.casefold():
                CloseHandle(hProcessSnap)
                return pEntry.th32ProcessID
            if not Process32Next(hProcessSnap, ctypes.byref(pEntry)):
                break
    CloseHandle(hProcessSnap)
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
    "2.9.1": 0x124b30,
    "2.7": 0x317F80,
    "2.6.2": 0x30DF80,
    "2.5.2": 0x310F80,
    "2.4.1": 0x30DF90,
    "2.3.2": 0x11D880,
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


# def duckstation_manual_address_func(hook, process_handle, address: Address, version: str):
#     if hook.manual_address is None:
#         raise Exception("No manual address")
#     if hook.base_cache is None:
#         module_handles = win32process.EnumProcessModulesEx(process_handle, 0x03)
#         for module_handle in sorted(module_handles):
#             filename = win32process.GetModuleFileNameEx(process_handle, module_handle)
#             filename = filename[filename.rfind("\\") + 1:]
#             if "duckstation" in filename.lower() and ".exe" in filename.lower():
#                 hook.base_cache = int.from_bytes(
#                     win32process.ReadProcessMemory(process_handle, module_handle + hook.manual_address, 8),
#                     byteorder='little')
#     return hook.base_cache + address.psx_address


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
    0x20000000,
    0x30000000,
    0x7FFF0000,
    0x80000000
]


def manual_try_address(process_handle, addr: int):
    for x in range(0, len(constants.RNG)):
        try:
            if int.from_bytes(win32process.ReadProcessMemory(process_handle, 0xE0638 + addr + x, 1),
                              byteorder='little') != constants.RNG[x]:
                return False
        except Exception as e:  # memory probably wasn't mapped so it errored
            return False
    return True


def find_base_address_candidates(b: bytes):
    i = 0
    while i < len(b):
        i = b.find(constants.RNG_BYTES, i)
        if i < 0:
            return
        # print(sum(b[i - 0xD0638:i - 0xC0638]))
        if sum(b[i - 0xD0638:i - 0xD0638 + 128]) == 9178:
            yield i - 0xE0638
        i += len(constants.RNG_BYTES)


def manual_search(process_id):
    adjust_privilege(win32security.SE_DEBUG_NAME)
    hooked_process_handle = OpenProcess(0x1F0FFF, False, process_id)
    mbi = MEMORY_BASIC_INFORMATION()
    mi = MODULEINFO()

    module_starts = {0: ""}

    module_handles = win32process.EnumProcessModulesEx(hooked_process_handle, 0x03)
    for module_handle in sorted(module_handles):
        filename = win32process.GetModuleFileNameEx(hooked_process_handle, module_handle)
        res = GetModuleInformation(hooked_process_handle, module_handle, ctypes.byref(mi), ctypes.sizeof(mi))
        if not res:
            continue
        module_starts[mi.lpBaseOfDll] = filename.split(os.path.sep)[-1]
        # print(f"{filename} {mi.lpBaseOfDll:X} {mi.SizeOfImage:X}")

    address = 0
    while True:
        result = VirtualQueryEx(hooked_process_handle, address, ctypes.byref(mbi), ctypes.sizeof(mbi))
        if result:
            try:
                # print(f"{address:x} {mbi.BaseAddress:x} {mbi}")
                fname = module_starts[max(k for k in module_starts.keys() if k <= mbi.AllocationBase)]
                b = win32process.ReadProcessMemory(hooked_process_handle, address, mbi.RegionSize)
                for base in find_base_address_candidates(b):
                    yield fname, address + base
            except Exception as _:
                pass
            address += mbi.RegionSize
        else:
            # print(f'err={ctypes.get_last_error()}')
            break
    CloseHandle(hooked_process_handle)


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
                # HookablePlatform("BizHawk 2.9.1", True, "2.9.1", bizhawk_address_func),
                # HookablePlatform("BizHawk 2.7", True, "2.7", bizhawk_address_func),
                # HookablePlatform("BizHawk 2.6.2 - 2.6.3", True, "2.6.2", bizhawk_address_func),
                # HookablePlatform("BizHawk 2.5.2 - 2.6.1", True, "2.5.2", bizhawk_address_func),
                # HookablePlatform("BizHawk 2.4.1 - 2.5.1", True, "2.4.1", bizhawk_address_func),
                # HookablePlatform("BizHawk 2.3.2 - 2.4.0", True, "2.3.2", bizhawk_address_func),
                HookablePlatform("BizHawk Manual", True, "__MANUAL__", manual_address_func)
            ]
        ),
        "Retroarch": (
            "[Rr]etro[Aa]rch",
            [
                HookablePlatform("Retroarch (Manual)", True, "__MANUAL__", manual_address_func),
            ]
        ),
        "DuckStation": (
            "[Dd][Uu][Cc][Kk][Ss][Tt][Aa][Tt][Ii][Oo][Nn]",
            [
                HookablePlatform("DuckStation (Manual)", True, "__MANUAL__", manual_address_func)
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

        # hook into platform
        self.hooked_process_handle = OpenProcess(win32con.PROCESS_ALL_ACCESS, False, self.hooked_process_id)
        if self.hooked_process_handle is None or self.hooked_process_handle == 0:
            err = win32api.GetLastError()
            error_message = f"Error on OpenProcess: {err}\n{win32api.FormatMessage(err)}\n\n"
            if err == 5:
                error_message += (f"""For some reason, your computer has decided that I need admin privileges to be able to hook into this process. Please rerun this program with _run_big_shoes_admin.bat.

If you are currently running with admin privileges, please contact the developer.""")
            else:
                error_message += """Unknown error. Please contact the developer."""
            win32api.MessageBox(None, error_message, "Error on OpenProcess")
            raise Exception(error_message)

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
