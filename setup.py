from setuptools import setup, find_packages

setup(name='dbexplorer',
      version='1.2',
      packages=find_packages(),
      entry_points={
          'console_scripts': [
              'dbexplorer = dbexplorer.__main__:main'
          ]
      },
      install_requires=[
          "pyodbc==4.0.23",
          "setuptools==38.5.1",
          "typing==3.6.4",
          "PyMySQL==0.8.0",
          "psycopg2==2.7.4",
          "simplejson==3.14.0"
      ],
      include_package_data=True,
      python_requires='>=3.6',
      author='Karol Prusinowski, Paweł Pollak, Karol Szczawiński'
      )
