from setuptools import setup

setup(
    name='fedorahosted',
    version='0.0.1',
    long_description=__doc__,
    packages=['fedorahosted'],
    scripts=[
      'bin/fedorahosted',
    ],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Flask',
        'python_fedora',
        'Flask-SQLAlchemy',
        'SQLAlchemy',
        'WTForms',
        'Flask-WTF',
    ]
)
