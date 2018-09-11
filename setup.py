from distutils.core import setup
#from Cython.Build import cythonize

setup(
    name='ACEBinf',
    version='0.1dev',
    packages=['acebinf',],
    license='Unlicense',
    long_description=open('README.txt').read(),
    install_requires=[
        "pyvcf>=0.6.8"
    ],
)
#setup(
    #ext_modules = cythonize("fast_vcf.pyx")
#)
