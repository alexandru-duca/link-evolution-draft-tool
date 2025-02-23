import os
from struct import unpack

#################################################

# archive to extract
FILENAME = "YGO_2020"

# add files you want in here, doesn't have to be an exact name
# leave it empty if you want everything
FILES_INCLUDE = []

FILES_EXCLUDE = []

#################################################

with open(FILENAME + ".toc", "r") as f:
    toc = f.readlines()[1:]

if not os.path.exists(FILENAME):
    os.mkdir(FILENAME)

with open(FILENAME + ".dat", "rb") as f:
    pos = 0
    for line in toc:
        sz = int(line.strip().split(" ")[0], 16)
        try:
            path_len = int(line.strip().split(" ")[1], 16)
            path = line.strip().split(" ", 2)[-1].split("\\")
        except ValueError:
            path = line.strip().split(" ", 3)[-1].split("\\")

        wanted = False
        [
            wanted := True
            for x in FILES_INCLUDE
            if x.lower() in line.strip().split(" ")[-1].lower()
        ]
        if len(FILES_INCLUDE) > 0 and not wanted:
            pos += sz
            pos += 4 - (pos % 4) if pos % 4 > 0 else 0
            continue

        wanted = True
        [
            wanted := False
            for x in FILES_EXCLUDE
            if x.lower() in line.strip().split(" ")[-1].lower()
        ]
        if len(FILES_EXCLUDE) > 0 and not wanted:
            pos += sz
            pos += 4 - (pos % 4) if pos % 4 > 0 else 0
            continue

        root = FILENAME + os.sep
        if len(path) > 1:
            for folder in path[:-1]:
                folder_path = os.path.join(root, folder)
                if not os.path.exists(folder_path):
                    os.mkdir(folder_path)
                root = folder_path + os.sep

        print(f"{os.path.join(root, path[-1]):<60s} -> {hex(sz)}")

        f.seek(pos, 0)
        base_pos = pos

        if ".zib" in path[-1]:
            print("\tExtracting sub-archive...")
            root = os.path.join(root, path[-1]) + os.sep
            if not os.path.exists(root):
                os.mkdir(root)

            i = 0
            while True:
                file_pos, file_size = unpack(">II", f.read(8))
                if file_pos == 0 and file_size == 0:
                    break
                if i == 0:
                    file_pos -= 1
                    file_size += 1
                fname = str(f.read(0x38), "utf8").replace("\x00", "")
                print(f"\t{os.path.join(root, fname):<40s} -> {hex(file_size)}")

                toc_pos = f.tell()
                f.seek(base_pos + file_pos, 0)

                with open(os.path.join(root, fname), "wb") as f2:
                    f2.write(f.read(file_size))

                f.seek(toc_pos, 0)
                i += 1

            pos = base_pos

        else:
            with open(os.path.join(root, path[-1]), "wb") as f2:
                f2.write(f.read(sz))

        pos += sz
        pos += 4 - (pos % 4) if pos % 4 > 0 else 0

print("Done!")
