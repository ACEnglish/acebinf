from setuptools import setup
#from Cython.Build import cythonize

setup(
    name='ACEBinf',
    version='0.1dev.1',
    author="ACEnglish",
    author_email="acenglish@gmail.com",
    url="https://github.com/ACEnglish/acebinf",
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
