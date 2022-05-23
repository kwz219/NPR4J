# _*_coding:utf-8 _*_
# @Time     :2019/1/26 09:15
# @Author   :聪明的牛
# @FileName :modifyFileTimeModule.py
# @Compile  :Python 2.7.15
from win32file import CreateFile, SetFileTime, GetFileTime, CloseHandle
from win32file import GENERIC_READ, GENERIC_WRITE, OPEN_EXISTING
from pywintypes import Time
import time, sys, os


def changeTime(path, filename):
    pathname = os.path.join(path, filename)
    print(pathname);

    cTime = "2022-04-25 10:20:00"
    aTime = "2022-04-25 10:31:00"
    mTime = "2022-04-25 10:31:00"
    # specify time format
    format = "%Y-%m-%d %H:%M:%S"
    offset = 0  # in seconds

    # create struct_time object
    cTime_t = time.localtime(time.mktime(time.strptime(cTime, format)) + offset)
    aTime_t = time.localtime(time.mktime(time.strptime(aTime, format)) + offset)
    mTime_t = time.localtime(time.mktime(time.strptime(mTime, format)) + offset)
    # change timestamp of file
    fh = CreateFile(pathname, GENERIC_READ | GENERIC_WRITE, 0, None, OPEN_EXISTING, 0, 0)
    createTime, accessTime, modifyTime = GetFileTime(fh)
    # print "Change Create from",createTime,"to %s" % (time.strftime(format,cTime_t))
    # print "Change Access from",accessTime,"to %s" % (time.strftime(format,aTime_t))
    # print "Change Modify from",modifyTime,"to %s" % (time.strftime(format,mTime_t))
    # print ""
    createTime = Time(time.mktime(cTime_t))
    accessTime = Time(time.mktime(aTime_t))
    modifyTime = Time(time.mktime(mTime_t))
    SetFileTime(fh, createTime, accessTime, modifyTime)

    # check if all was ok
    # ctime = time.strftime(format,time.localtime(os.path.getctime(pathname)))
    # mtime = time.strftime(format,time.localtime(os.path.getmtime(pathname)))
    # atime = time.strftime(format,time.localtime(os.path.getatime(pathname)))
    # print "Create:%s,Access:%s,Modify:%s" %(ctime,atime,mtime)
    CloseHandle(fh)


base_dir = 'F:/NPR_DATA0306/Raw_Data/Diversity_Main/fix_classes'


for path, dirs, files in os.walk(base_dir):
    for filename in files:
        changeTime(path, filename)