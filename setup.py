from setuptools import setup

setup(
    name='terramaas',
    version='0.1',
    packages=['src'],
    author='Selim',
    description='Automated Terraform deployment for MAAS',
    install_requires=[
        'pyyaml',  # Add any dependencies you need here
    ],
    entry_points={
        'console_scripts': [
            'terramaas = src.__main__:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)
