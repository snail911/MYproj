import os
import pathlib

dir_path = pathlib.Path.cwd()
workbooks_dir = os.path.abspath(os.path.join(dir_path, '..'))
print(dir_path)
print(workbooks_dir)