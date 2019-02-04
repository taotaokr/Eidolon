# Eidolon Biomedical Framework
# Copyright (C) 2016-8 Eric Kerfoot, King's College London, all rights reserved
#
# This file is part of Eidolon.
#
# Eidolon is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Eidolon is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program (LICENSE.txt).  If not, see <http://www.gnu.org/licenses/>
'''
Eidolon is the experimental medical imaging visualization framework.
'''

__appname__='Eidolon Biomedical Framework'
__version_info__=(0,5,99) # global application version, major/minor/patch, patch value 99 means development code directly from the repo
__version__='%i.%i.%i'%__version_info__
__author__='Eric Kerfoot'
__copyright__="Copyright (c) 2016-8 Eric Kerfoot, King's College London, all rights reserved. Licensed under the GPL (see LICENSE.txt)."
__website__="https://ericspod.github.io/Eidolon"
__verurl__="https://api.github.com/repos/ericspod/Eidolon/releases"

# top-level constants, these are hard-coded environment variable or file names
APPDIRVAR='APPDIR' # environment variable defining the application's directory, set by the start up script and is needed at init time
LIBSDIR='EidolonLibs' # directory name containing the application's libraries
CONFIGFILE='config.ini' # config file name

from eidolon.Utils import isWindows, isLinux, addPathVariable

import os, sys
scriptdir=os.path.dirname(os.path.abspath(__file__))

# the application directory is given by pyinstaller in _MEIPASS, if not present use the directory two levels up
__appdir__=getattr(sys,'_MEIPASS',os.path.abspath(scriptdir+'/../..')) 

#if not os.environ.get(APPDIRVAR): # set the APPDIR environment variable if not set by the run script
#    if getattr(sys,'_MEIPASS',None):
#        os.environ[APPDIRVAR]=sys._MEIPASS # pyinstaller support
#    else:
#        os.environ[APPDIRVAR]=os.path.abspath(scriptdir+'/../..')

if isWindows:
    # add the library directory to PATH so that DLLs can be loaded whe the renderer is imported
    addPathVariable('PATH',os.path.abspath(os.path.join(scriptdir,'..','..',LIBSDIR,'win64_mingw','bin')))
elif isLinux:
    import glob,ctypes
    
    # load all linux libraries so that LD_LIBRARY_PATH doesn't need to be set
    for lib in glob.glob(os.path.join(__appdir__,LIBSDIR,'linux','lib','*.so*')):
        try:
            _=ctypes.cdll.LoadLibrary(lib)
        except OSError:
            pass

from renderer import *
from eidolon.VisualizerUI import *

from eidolon.Concurrency import *
from eidolon.SceneUtils import *
from eidolon.MeshAlgorithms import *
from eidolon.ImageAlgorithms import *
from eidolon.ImageObject import *
from eidolon.MathDef import *
from eidolon.Camera2DView import *
from eidolon.SceneManager import *
from eidolon.SceneObject import *
from eidolon.ScenePlugin import *
from eidolon.SceneComponents import *
from eidolon.Application import *



