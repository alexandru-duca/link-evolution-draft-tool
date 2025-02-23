import os
from struct import pack

#################################################

# input folder to compress
INFOLDER = "YGO_2020"

# output filenames
OUTFILES = "test"

# this archive will be merged with the input folder
# this allows you to compile only a partial folder, and it will be merged
# with the original file
USE_ARCHIVE = "YGO_2020"

#################################################

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
                            if (i + 1) % 100 == 0:
                                print(f"\t{i + 1:>5d} / {file_cnt:<5d}")
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
                    print(f"\t{file_cnt:>5d} / {file_cnt:<5d}")
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
                print(path)
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

print("Done!")
