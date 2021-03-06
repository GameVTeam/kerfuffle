import pathlib
import re
import hashlib
from _hashlib import HASH as Hash
from pathlib import Path
from typing import Union

project_root = pathlib.Path(__file__).parent.parent.absolute()


def merge_to(folder, path, included, pragma_once_counter, output):
    path_tokens = path.split("/")

    current = folder + "/" + path_tokens[-1]
    with open(current, 'r', encoding='utf-8') as input:
        for line in input:

            if line.startswith('#include "'):
                next_included = line[10: -2]

                if next_included not in included:
                    next_tokens = next_included.split("/")
                    included.append(next_tokens[-1])

                    output.write("// inlined '" + path_tokens[-1] + "' -> '" + next_tokens[-1] + "'\n")
                    print("ℹ️ inlining " + next_tokens[-1] + "(included in " + path_tokens[-1] + ")...")

                    if len(next_tokens) == 1:
                        merge_to(folder, next_included, included, pragma_once_counter, output)
                    else:
                        name = next_tokens.pop()
                        merge_to(folder + "/" + "/".join(next_tokens), name, included, pragma_once_counter, output)
            else:
                if line.startswith('\ufeff'):
                    line = line[1:]

                if re.match("^# *pragma", line):
                    pragma = line[8:]

                    if pragma.startswith('once'):
                        pragma_once_counter += 1
                        if pragma_once_counter > 1:
                            continue

                    elif pragma.startswith('region') or pragma.startswith('endregion'):
                        continue

                output.write(line)


def md5_update_from_file(filename: Union[str, Path], hash: Hash) -> Hash:
    assert Path(filename).is_file()
    with open(str(filename), "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash.update(chunk)
    return hash


def md5_file(filename: Union[str, Path]) -> str:
    return str(md5_update_from_file(filename, hashlib.md5()).hexdigest())


def md5_update_from_dir(directory: Union[str, Path], hash: Hash) -> Hash:
    assert Path(directory).is_dir()
    for path in sorted(Path(directory).iterdir(), key=lambda p: str(p).lower()):
        hash.update(path.name.encode())
        if path.is_file():
            hash = md5_update_from_file(path, hash)
        elif path.is_dir():
            hash = md5_update_from_dir(path, hash)
    return hash


def md5_dir(directory: Union[str, Path]) -> str:
    return str(md5_update_from_dir(directory, hashlib.md5()).hexdigest())


def main():
    current_dir_hash = md5_dir(str(project_root) + "/src/kerfuffle")

    try:
        last_generated = open(str(project_root) + "/include/kerfuffle.h", 'r', encoding='utf-8-sig')
    except:
        print("ℹ️ generating...")
        pass
    else:
        print("ℹ️ current hash: " + current_dir_hash)
        if last_generated:
            last_dir_hash = str(last_generated.readline())[3:-1]
            print("ℹ️    last hash: " + last_dir_hash)
            if current_dir_hash == last_dir_hash:
                print("✅ no need to regenerate, exit")
                return
            print("ℹ️ source code changed, regenerating...")
            last_generated.close()

    output = open(str(project_root) + "/include/kerfuffle.h", 'w', encoding='utf-8-sig')
    output.write("// " + current_dir_hash + "\n")
    output.write("// This file is generated by tools/merge.py. DO NOT EDIT!\n\n")
    merge_to(str(project_root) + "/src/kerfuffle", "machine.h", [], 0, output)
    output.close()

    print("✅ done")


if __name__ == "__main__":
    main()
