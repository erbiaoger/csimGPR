with open("README.md", "r") as fh:
    long_description = fh.read()

    
setuptools.setup(
    name="csimGPR",
    version="1.0.12",
    author="Zhiyu Zhang",
    author_email="erbiaoger@gmail.com",
    description="csimGPR - open source ground penetrating radar processing and visualization",
    entry_points={'console_scripts': ['csimGPR = csimGPR.__main__:main']},
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/erbiaoger/csimGPR",
    packages=['csimGPR'],
    package_data={'csimGPR': ['exampledata/GSSI/*.DZT',
                            'exampledata/GSSI/*.txt',
                            'exampledata/SnS/ComOffs/*.xyz',
                            'exampledata/SnS/ComOffs/*.DT1',
                            'exampledata/SnS/ComOffs/*.HD',
                            'exampledata/SnS/WARR/*.DT1',
                            'exampledata/SnS/WARR/*.HD',
                            'exampledata/pickedSurfaceData/*.txt',
                            'examplescripts/*.py',
                            'toolbox/StartGUIdat/*.png',
                            'toolbox/*.py',
                            'irlib/*.py',
                            'irlib/external/*.py',
                            'kirchhoff/*.py',
                            ]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=['tqdm','numpy','scipy','matplotlib','Pmw','pyevtk']
)
