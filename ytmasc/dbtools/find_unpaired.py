from os import listdir


def find_unpaired_files(directory):
    "Finds unpaired MP3 or JPG files"
    files = listdir(directory)

    mp3_files = {f[:-4] for f in files if f.endswith(".mp3")}
    jpg_files = {f[:-4] for f in files if f.endswith(".jpg")}

    unpaired_mp3 = mp3_files - jpg_files
    unpaired_jpg = jpg_files - mp3_files

    print("Unpaired MP3 files:", *unpaired_mp3)
    print("Unpaired JPG files:", *unpaired_jpg)
