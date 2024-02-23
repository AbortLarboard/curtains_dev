import os
import platform
import shutil
import sys
import importlib

# run at least once before using pyinstaller/flet pack to create an .exe file

def patch_pyinjector():
    """a patch to make pyinjector work with pyinstaller"""
    patch_code = ['import platform\n',
                  '\n',
                  '# patch_code for pyinstaller: detect if frozen to find the right pyd binary\n',
                  "if getattr(sys, 'frozen', False):\n",
                  '    os_bit = platform.machine().lower()\n',
                  "    py_runtime = str(sys.version[0:4]).replace('.', '')\n",
                  "    bin_name = f'libinjector.cp{py_runtime}-win_{os_bit}.pyd'\n",
                  "    libinjector_path = os.path.join(sys._MEIPASS, 'assets') + '/' + bin_name\n",
                  'else:\n',
                  "    libinjector_path = find_spec('.libinjector', __package__).origin\n"]
    spec = importlib.util.find_spec("pyinjector")
    pyfile_path = spec.submodule_search_locations[0] + r'\pyinjector.py'

    with open(pyfile_path, "r") as f_r:
        contents = f_r.readlines()
        if contents[5:16] == patch_code:
            print('skip patching. pyinjector.py has already been patched')
        else:
            contents.insert(0, "import sys\n")
            contents.insert(6, "#")
            patch_code.reverse()
            for line in patch_code:
                contents.insert(5, line)

            with open(pyfile_path, "w") as f_w:
                contents = "".join(contents)
                f_w.write(contents)
            print('pyinjector.py has been patched successfully')


def copy_binary_to_assets():
    """copy the libinjector binary to assets folder for freezing with pyinstaller"""
    spec = importlib.util.find_spec("pyinjector")
    os_bit = platform.machine().lower()
    py_runtime = str(sys.version[0:4]).replace('.', '')
    bin_name = f'libinjector.cp{py_runtime}-win_{os_bit}.pyd'
    libinjector_path = spec.submodule_search_locations[0] + r'/' + bin_name
    basedir = os.path.dirname(os.path.abspath(__file__))
    assets_path = basedir + "/assets"
    shutil.copy(libinjector_path, assets_path)
    print('libinjector pyd-file has been copied to the assets folder')


if __name__ == "__main__":
    patch_pyinjector()
    copy_binary_to_assets()
