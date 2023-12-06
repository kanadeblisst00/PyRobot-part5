import os
import time
import platform
import sys
import shutil 
import psutil
from .winapi import *
from .offset import CALL_OFFSET


def DelayCreateRemoteThread(*args):
    CreateRemoteThread(*args)
    time.sleep(0.05)


def get_pid_by_name(process_name):
    '''通过进程名查找第一个进程PID'''
    is_64bit = "64" in platform.architecture()[0] 
    for process in psutil.process_iter(['pid', 'name']):
        if process.info['name'] == process_name:
            pid = process.info['pid']
            exe_path = psutil.Process(pid).exe()
            wechat_version = GetWeChatVersion(exe_path)
            if wechat_version not in CALL_OFFSET:
                raise Exception(f"当前微信的版本({wechat_version})不在支持的列表，目前支持的版本列表: {list(CALL_OFFSET.keys())}")
            if is_64bit != IsProcess64Bit(pid):
                raise Exception("Python位数和查找进程的位数不符，请同时使用32位或64位!")
            return pid

def get_func_offset(dll, export_func_name):
    '''获取dll导出函数的偏移'''
    a = c_void_p.in_dll(dll, export_func_name)
    b = dll._handle
    return addressof(a) - b

def init_python_in_process(hProcess, dll_addr, dllpath, py_code_path=None, open_console=True):
    '''在进程内初始化Python'''
    # 定义 injectpy.dll内的导出函数
    dll = CDLL(dllpath)
    SetDllPath =  dll_addr + get_func_offset(dll, "SetDllPath")
    SetOpenConsole =  dll_addr + get_func_offset(dll, "SetOpenConsole")
    RunPythonConsole =  dll_addr + get_func_offset(dll, "RunPythonConsole")
    RunPythonFile = dll_addr + get_func_offset(dll, "RunPythonFile")
    # 设置Python的路径
    PythonPath = os.path.dirname(sys.executable)
    lpPythonPath = VirtualAllocEx(hProcess, None, MAX_PATH, MEM_COMMIT, PAGE_READWRITE)
    WriteProcessMemory(hProcess, lpPythonPath, c_wchar_p(PythonPath), MAX_PATH, byref(c_ulong()))
    hRemote = DelayCreateRemoteThread(hProcess, None, 0, SetDllPath, lpPythonPath, 0, None)
    VirtualFreeEx(hProcess, lpPythonPath, 0, MEM_RELEASE)
    CloseHandle(hRemote)
    hRemote = DelayCreateRemoteThread(hProcess, None, 0, SetOpenConsole, int(open_console), 0, None)
    CloseHandle(hRemote)
    time.sleep(0.1)
    if not py_code_path:
        hRemote = DelayCreateRemoteThread(hProcess, None, 0, RunPythonConsole, None, 0, None)
        CloseHandle(hRemote)
    else:
        lpPyCodePath = VirtualAllocEx(hProcess, None, MAX_PATH, MEM_COMMIT, PAGE_READWRITE)
        WriteProcessMemory(hProcess, lpPyCodePath, c_wchar_p(py_code_path), MAX_PATH, byref(c_ulong()))
        hRemote = DelayCreateRemoteThread(hProcess, None, 0, RunPythonFile, lpPyCodePath, 0, None)
        time.sleep(0.5)
        VirtualFreeEx(hProcess, lpPyCodePath, 0, MEM_RELEASE)
        CloseHandle(hRemote)


def inject_dll(pid, open_console, py_code_path, dllpath=None):
    '''注入dll到给定的进程，返回http端口'''
    if not dllpath:
        raise Exception("给定的dllpath不存在")
    dllpath = os.path.abspath(dllpath)
    if not os.path.exists(dllpath):
        raise Exception('给定的dllpath不存在')
    dllname = os.path.basename(dllpath)
    dll_addr = getModuleBaseAddress(dllname, pid)
    if dll_addr:
        print("当前进程已存在相同名称的dll")
        return dll_addr
    # 通过微信进程pid获取进程句柄
    hProcess = OpenProcess(PROCESS_ALL_ACCESS, False, pid)
    # 在微信进程中申请一块内存
    lpAddress = VirtualAllocEx(hProcess, None, MAX_PATH, MEM_COMMIT, PAGE_READWRITE)
    # 往内存中写入要注入的dll的绝对路径
    WriteProcessMemory(hProcess, lpAddress, c_wchar_p(dllpath), MAX_PATH, byref(c_ulong()))
    # 在微信进程内调用LoadLibraryW加载dll
    hRemote = DelayCreateRemoteThread(hProcess, None, 0, LoadLibraryW, lpAddress, 0, None)
    VirtualFreeEx(hProcess, lpAddress, 0, MEM_RELEASE)
    CloseHandle(hRemote)
    dll_addr = getModuleBaseAddress(dllname, pid)
    init_python_in_process(hProcess, dll_addr, dllpath, py_code_path, open_console)
    # 关闭句柄
    CloseHandle(hProcess)
    return dll_addr


def uninject_dll(pid, dllname):
    dll_addr = getModuleBaseAddress(dllname, pid)
    hProcess = OpenProcess(PROCESS_ALL_ACCESS, False, pid)
    while dll_addr:
        hRemote = DelayCreateRemoteThread(hProcess, None, 0, FreeLibrary, dll_addr, 0, None)
        CloseHandle(hRemote)
        dll_addr = getModuleBaseAddress(dllname, pid)
    CloseHandle(hProcess)


def inject_python_to_process(pid, open_console=True, py_code_path=None):
    if not pid:
        raise Exception("请先启动微信后再注入!")
    python_bit = platform.architecture()[0][:2]
    dll_new_path = os.path.abspath(f"dll\\injectpy{python_bit}.dll")
    addr = inject_dll(pid, open_console, py_code_path, dllpath=dll_new_path)
    print("注入后的dll基址: ", addr)


if __name__ == "__main__":
    pid = get_pid_by_name("WeChat.exe")
    print("查找到的微信进程pid: ", pid)
    inject_python_to_process(pid)
    