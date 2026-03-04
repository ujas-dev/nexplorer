from setuptools import setup, find_packages

setup(
    name="nexplorer",
    version="1.0.0",
    author="NexPlorer Contributors",
    description="Intelligent cross-platform file explorer with compression, encryption, secure delete and analytics",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/YOUR_USERNAME/nexplorer",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[],
    extras_require={
        "full": [
            "customtkinter","blake3","zstandard","lz4","brotli","py7zr",
            "python-snappy","python-magic","Pillow","imagehash","piexif",
            "pymupdf","pypdf","python-docx","openpyxl","python-pptx",
            "mutagen","boto3","google-api-python-client",
            "google-auth-httplib2","google-auth-oauthlib","dropbox",
            "zeroconf","watchdog","cryptography","plotly","PyYAML",
            "schedule","psutil",
        ],
        "gui":   ["customtkinter"],
        "crypt": ["cryptography"],
        "image": ["Pillow","imagehash","piexif"],
    },
    entry_points={
        "console_scripts": ["nexplorer=nexplorer.__main__:main"],
        "gui_scripts":     ["nexplorer-gui=nexplorer.__main__:main"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Topic :: Utilities",
        "Topic :: Desktop Environment :: File Managers",
        "Environment :: X11 Applications",
        "Environment :: Win32 (MS Windows)",
    ],
    keywords="file explorer manager compression encryption dedup shred cross-platform",
)
