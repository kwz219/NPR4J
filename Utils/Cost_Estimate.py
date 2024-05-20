from pynvml import *
def show_gpu():
    # 初始化
    nvmlInit()
    # 获取GPU个数
    device_count = nvmlDeviceGetCount()
    total_memory = 0
    total_used = 0

    for i in range(device_count):
        handle = nvmlDeviceGetHandleByIndex(i)
        info = nvmlDeviceGetMemoryInfo(handle)

        total_memory += (info.total // 1048576)
        total_used += (info.used // 1048576)



    # 关闭管理工具
    nvmlShutdown()