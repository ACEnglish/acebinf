from setuptools import setup
#from Cython.Build import cythonize

setup(
    name='ACEBinf',
    version='1.0.2',
    author="ACEnglish",
    author_email="acenglish@gmail.com",
    url="https://github.com/ACEnglish/acebinf",
    packages=['acebinf',],
    license='Unlicense',
    description=open('README.txt').readline().strip(),
    long_description=open('README.txt').read(),
    long_description_content_type='text/markdown',
    install_requires=[
        "pyvcf>=0.6.8"
    ],
)
#setup(
    #ext_modules = cythonize("fast_vcf.pyx")
#)
