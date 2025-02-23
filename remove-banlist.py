import os
from struct import pack, unpack
import shutil

# Step 1: Extract
FILENAME = "YGO_2020"
FILES_INCLUDE = ["bin"]
FILES_EXCLUDE = []

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

# Step 2: Replace the banlist file with an empty one
print("Replace the banlist file with an empty one.")
file_path = os.path.join(FILENAME, "bin", "pd_limits.bin")
with open(file_path, "wb") as file:
    file.write(bytes([0x00] * 6))

# Step 3: Recompress
INFOLDER = FILENAME
OUTFILES = FILENAME + "_new"
USE_ARCHIVE = FILENAME

orig_files = {}
with open(USE_ARCHIVE + ".toc", "r") as toc:
    with open(USE_ARCHIVE + ".dat", "rb") as f:
        toc.readline()
        while line := toc.readline():
            sz = int(line.strip().split(" ")[0], 16)
            try:
                path_len = int(line.strip().split(" ")[1], 16)
                path = line.strip().split(" ", 2)[-1].split("\\")
            except ValueError:
                path = line.strip().split(" ", 3)[-1].split("\\")

            orig_files[os.path.join(*path)] = [f.tell(), sz]
            f.seek(sz, 1)
            if f.tell() % 0x4 > 0:
                f.seek(4 - (f.tell() % 0x4), 1)

toc = ["UT"]
total_write_size = 0
with open(USE_ARCHIVE + ".dat", "rb") as f:
    with open(OUTFILES + ".dat", "wb") as fd:
        for path, data in orig_files.items():
            path = os.path.join(INFOLDER, path)
            if ".zib" in path:
                if os.path.exists(path):
                    tmp = bytearray()
                    tmp_toc = bytearray()
                    for _, _, sub_files in os.walk(path):
                        file_cnt = len(sub_files)
                        base_data = (len(sub_files) * 0x40) + 0x10
                        i = 0
                        for sub_file in sub_files:
                            with open(os.path.join(path, sub_file), "rb") as f2:
                                sub_fd = f2.read()
                            fname = bytes(sub_file, "utf8")
                            if len(fname) < 0x38:
                                fname += bytes(0x38 - len(fname))

                            pos = base_data + len(tmp)
                            sz = len(sub_fd)
                            if i == 0:
                                pos += 1
                                sz -= 1

                            tmp_toc += pack(">I", pos)
                            tmp_toc += pack(">I", sz)
                            tmp_toc += fname
                            tmp += sub_fd
                            tmp += bytes(
                                0x10 - (len(tmp) % 0x10) if len(tmp) % 0x10 > 0 else 0
                            )
                            i += 1
                        del sub_fd
                    tmp_toc += bytes(0x10)

                    path = os.path.join(*path.split(os.sep)[1:])
                    path = path.replace(os.sep, "\\")

                    path_len = len(path)
                    toc.append(
                        f"{hex(len(tmp) + len(tmp_toc))[2:]:>12s} {hex(path_len)[2:]:>2} {path}"
                    )
                    fd.write(tmp_toc + tmp)
                    total_write_size += len(tmp_toc) + len(tmp)
                    if total_write_size % 0x4 > 0:
                        fd.write(bytes(0x4 - (total_write_size % 0x4)))
                        total_write_size += 0x4 - (total_write_size % 0x4)

                    del tmp
                    del tmp_toc
                else:
                    f.seek(data[0], 0)
                    path = os.path.join(*path.split(os.sep)[1:])

                    path = path.replace(os.sep, "\\")

                    path_len = len(path)
                    toc.append(f"{hex(data[1])[2:]:>12s} {hex(path_len)[2:]:>2} {path}")
                    fd.write(f.read(data[1]))
                    total_write_size += data[1]
                    if total_write_size % 0x4 > 0:
                        fd.write(bytes(0x4 - (total_write_size % 0x4)))
                        total_write_size += 0x4 - (total_write_size % 0x4)
            else:
                if os.path.exists(path):
                    with open(path, "rb") as f2:
                        sub_fd = f2.read()
                else:
                    f.seek(data[0], 0)
                    sub_fd = f.read(data[1])
                path = os.path.join(*path.split(os.sep)[1:])

                path = path.replace(os.sep, "\\")

                path_len = len(path)
                toc.append(f"{hex(len(sub_fd))[2:]:>12s} {hex(path_len)[2:]:>2} {path}")
                fd.write(sub_fd)
                total_write_size += len(sub_fd)
                if total_write_size % 0x4 > 0:
                    fd.write(bytes(0x4 - (total_write_size % 0x4)))
                    total_write_size += 0x4 - (total_write_size % 0x4)
                del sub_fd

with open(OUTFILES + ".toc", "w", newline="\n") as f:
    f.write("\n".join(toc))
    f.write("\n")


# Step 4: Clean up
print("Clean up.")
print("Deleting working directory:", FILENAME)
shutil.rmtree(FILENAME)
print("Deleting old files:", FILENAME + ".toc", FILENAME + ".dat")
os.remove(FILENAME + ".toc")
os.remove(FILENAME + ".dat")
print("Renaming new files:", FILENAME + "_new" + ".toc", FILENAME + "_new" + ".dat")
os.rename(FILENAME + "_new" + ".toc", FILENAME + ".toc")
os.rename(FILENAME + "_new" + ".dat", FILENAME + ".dat")

print("Done!")
