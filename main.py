import os

if __name__ == "__main__":
    fileList = []

    for file in os.listdir():
        split = file.split(".")
        if split[len(split)-1].lower() == "png":
            fileList.append(file)
            break