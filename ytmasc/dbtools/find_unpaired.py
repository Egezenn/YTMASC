import os


def find_unpaired_files(directory):
    files = os.listdir(directory)

    mp3_files = {f[:-4] for f in files if f.endswith(".mp3")}
    jpg_files = {f[:-4] for f in files if f.endswith(".jpg")}

    unpaired_mp3 = mp3_files - jpg_files
    unpaired_jpg = jpg_files - mp3_files

    return unpaired_mp3, unpaired_jpg


if __name__ == "__main__":
    directory_path = "downloads"
    unpaired_mp3, unpaired_jpg = find_unpaired_files(directory_path)

    print("Unpaired MP3 files:", unpaired_mp3)
    print("Unpaired JPG files:", unpaired_jpg)
