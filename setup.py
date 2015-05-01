from distutils.core import setup
from distutils.extension import Extension

setup(
    name='racecaptureapp',
    ext_modules = [Extension("blah.testit", ["blah/testit.c"], 
                             extra_compile_args=['-std=c99']
                              )]
)

#setup(
#    name='racecaptureapp',
#    ext_modules = [Extension("autosportlabs.racecapture.data.sampledata", ["autosportlabs/racecapture/data/sampledata.c"], 
#                             extra_compile_args=['-std=c99']
#                              )]
#)
