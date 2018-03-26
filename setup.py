from setuptools import setup

setup(
    name="Pymessenger",
    version='0.1',
    description='Simple messenger.',
    url='https://github.com/GrSerg/Pymessenger',
    author='Sergey Gribkov',
    packages=[
        'client',
        'JIM',
        'log',
        'repo',
        'server',
    ],

    include_package_data=True,
    python_requires='>=3.5',
    install_requires=[
        'PyQt5==5.10.1',
        'SQLAlchemy==1.2.5',
    ],
)