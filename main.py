import os
import psutil
from threading import Event
from module_hot_loading import monitor_dir
from module.inject_dll import get_pid_by_name, inject_python_to_process


def init_monitor():
    '''监听当前文件夹下的代码变化，当变化时重新加载'''
    # 如果需要注入微信就执行robot.py的话，在这里导入
    # import robot
    event = Event()
    event.set()

    path = os.path.dirname(__file__)
    main_path = os.path.abspath(__file__)
    print(f"开始监听目录({path})下的代码文件变化！")
    monitor_dir(path, event, main_path, interval=2, only_import_exist=False)
    
    event.clear()
    
def inject_python(pid):
    py_code_path = os.path.abspath(__file__)
    # py_code_path=None 会打开Python控制台
    inject_python_to_process(pid, py_code_path=py_code_path)

def test(process_name):
    for process in psutil.process_iter(['pid', 'name']):
        if process.info['name'] == process_name:
            pid = process.info['pid']
    inject_python(pid)

def main():
    pid = get_pid_by_name("WeChat.exe")
    if pid == os.getpid():
        init_monitor()
    else:
        print("查找到的微信进程pid: ", pid)
        inject_python(pid)



if __name__ == "__main__":
    test("CtypesTest.exe")