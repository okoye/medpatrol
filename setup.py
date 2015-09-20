__author__ = 'Humanly.co'
__version__ = '0.1'

METADATA = dict(
    name = 'medpatrol',
    version = __version__,
    py_modules = ['lib'],
    author = __author__,
    author_email = 'contact@chookah.org',
    description = 'Libraries supporting medpatrol app',
    url = 'https://github.com/okoye/medpatrol',
    keyword = 'humanly medpatrol pharmacy'
)

def main():
    try:
        from setuptools import setup, find_packages
        SETUPTOOLS_METADATA = dict(
            install_requires = ['setuptools',
                                'requests',
                                'python-twitter',
                                'couchdbkit',
                                'nltk',
                                'zerorpc',
                                'elasticsearch'],
            include_package_data = True,
            package_dir = {'':'lib'},
            packages = find_packages(where='lib'),
            test_suite = 'tests'
        )
        METADATA.update(SETUPTOOLS_METADATA)
        setup(**METADATA)
    except ImportError:
        import distutils.core
        distutils.core.setup(**METADATA)

if __name__ == '__main__':
    main()
