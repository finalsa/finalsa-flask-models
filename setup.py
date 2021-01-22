from setuptools import setup

setup(
    name='finalsa-flask',
    version='1.0.0',
    url='https://github.com/finalsa/finalsa-flask-models/',
    license='BSD',
    author='Timothee Peignier',
    author_email='timothee.peignier@tryphon.org',
    description='Flask simple mysql client',
    packages=['flaskext'],
    namespace_packages=['flaskext'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask',
        'mysql-connector-python',
        'python-dotenv'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)