from distutils.core import setup

setup(
    name='matroska',
    version='0.0.1',
    description='Matroska muxer/demuxer for Python',
    author='Brian Sherson',
    author_email='caretaker82@gmail.com',
    url='https://github.com/shersonb/python-matroska',
    packages=['matroska'],
    install_requires=[
            'ebml',
        ],
    license="MIT"
)
