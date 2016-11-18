from setuptools import setup, find_packages

setup(
    name='python-highcharts_df-df',
    version='0.1.0',
    description='python-highcharts_df wrapper for customizable pretty plotting quickly from pandas dataframes',
    author="Alex Loosley",
    author_email='a.loosley@reply.de',
    license='GNU',
    packages=find_packages(),
    zip_safe=False,
    install_requires=[],
    dependency_links=[],
    # include_package_data=True,  # should work, but doesn't, I think pip does not recognize git automatically
    package_data={
        'data': ['*/*'],
    }
)
