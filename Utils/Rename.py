import os


def renaming(file):
    ext = os.path.splitext(file)

    if ext[1] == '.txt':
        new_name = ext[0] + '.java'
        os.rename(file, new_name)


def batch_opera(folder_path):
    folder = os.listdir(folder_path)
    for file in folder:
        file_path = os.path.join(folder_path, file)
        print(file_path)
        renaming(file_path)


if __name__ == "__main__":
    folder_path = r'D:\RawData_New\new_test\new_test\buggy_classes'
    batch_opera(folder_path)

