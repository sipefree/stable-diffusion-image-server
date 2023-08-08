import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sdis",
    author="Simon Free",
    author_email="sipefree@gmail.com",
    description="Stable Diffusion Image Server - Simple HTTP Image Server for Stable Diffusion output",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sipefree/stable-diffusion-image-server/",
    packages=setuptools.find_packages(),
    package_data={'sdis': ['templates/*', 'templates/*/*']},
    license="MIT",
    install_requires=['Pillow>=10.0.0', 'Jinja2==3.1.2', 'tqdm==4.65.0', 'imagesize==1.4.1', 'piexif==1.1.3'],
    setup_requires=['setuptools-git-versioning'],
    version_config=True,
    python_requires='>=3.8',
    project_urls={
        'Documentation': 'https://shis.readthedocs.io/',
        'Source': 'https://github.com/sipefree/stable-diffusion-image-server/',
    },
    classifiers=[
        "Programming Language :: Python :: 3.6",
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Image Processing",
        "Environment :: Console",
        "Environment :: MacOS X",
        "Environment :: Win32 (MS Windows)",
        "Framework :: Sphinx",
        "Natural Language :: English",
        "Typing :: Typed"
    ]
)