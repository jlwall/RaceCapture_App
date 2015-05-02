from distutils.core import setup
from distutils.extension import Extension

setup(
    name='racecaptureapp',
    ext_modules = [Extension("autosportlabs.racecapture.data.sampledata", ["autosportlabs/racecapture/data/sampledata.c"], extra_compile_args=['-std=c99']),
                   Extension("autosportlabs.racecapture.databus.databus", ["autosportlabs/racecapture/databus/databus.c"], extra_compile_args=['-std=c99'])
                   ]
)
