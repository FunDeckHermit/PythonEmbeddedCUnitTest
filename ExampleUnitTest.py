import os, sys
import time
from shutil import copyfile, rmtree
from pathlib import Path
import subprocess
import importlib
import unittest
import cffi
import uuid



def preprocess(source):
    gcc = r'C:\NXP\S32DS.3.4\S32DS\build_tools\gcc_v6.3\gcc-6.3-arm32-eabi\bin\arm-none-eabi-g++.exe'
    return subprocess.run([gcc, '-E', '-P', '-'],
                          input=source, stdout=subprocess.PIPE,
                          universal_newlines=True, check=True).stdout

def load(filename):
    # generate random name
    name = 'c_module_' + filename + '_' + uuid.uuid4().hex

    # load source code
    with open(filename + '.c') as f:
       source = f.read() 
    with open(filename + '.h') as f:
       includes = preprocess(f.read())    
    
    ffibuilder = cffi.FFI()
    ffibuilder.cdef(includes)
    ffibuilder.set_source(name, source)
    ffibuilder.compile()
    
    destination = Path(sys.path[-1]) / 'compiled'
    destination.mkdir(parents=True, exist_ok=True)
    copyfile(name + '.cp37-win32.pyd', destination / (name + '.cp37-win32.pyd'))
    module = importlib.import_module('compiled.' + name)
 
    return module.lib




class AddTest(unittest.TestCase):
    @classmethod
    def tearDownClass(AddTest):
        rmtree('Release')
        rmtree(Path(sys.path[-1]) / 'compiled', ignore_errors=True)
        for p in Path(".").glob("c_module_*"):
            p.unlink()
             
    def setUp(self):
        self.module = load('add')
           
    def test_addition_positive(self):
        self.assertEqual(self.module.add(1, 2), 3)
        self.assertEqual(self.module.add(8, 24), 32)
        
    def test_addition_negative(self):
        self.assertEqual(self.module.add(-1, -2), -3)
        self.assertEqual(self.module.add(-30, -36), -66)

    def test_overflow(self):
        self.assertEqual(self.module.add(1, 32767), -32768)


if __name__ == '__main__':
    # change current directory to relative subfolder
    os.chdir(Path('./Example1').resolve())
    unittest.main()