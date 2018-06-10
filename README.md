# DatabaseExplorer

## Description

### Info
The program was created for *Team project - development of data analysis system* course run by [@pbiecek](https://github.com/pbiecek).


### Program description

The aim of the created program is to generate a summary report of provided database.
It extracts basic or extended information such as:
 
* table, column names
* data stats (top values, mean, quartiles etc.)
* types of data and number of rows

Generated report has a searching feature which allows to find tables or columns by names and exact values.

#### Further information

Full specification and more detailed description of summarization features (in Polish) can be found in [this file](https://github.com/ppollakr/dbexplorer/blob/master/docs/Specyfikacja%20wymaga%C5%84.pdf).


## Installation

1. Clone repository: `git clone https://github.com/ppollakr/dbexplorer.git`
2. Change to directory: `cd dbexplorer`
3. Install package: `pip install .`
4. Run program with proper arguments: `dbexplorer -s 192.2.3.4 -p 5432 -n dvdrental -u dbadmin -pass password -t postgres -o out.html`


## Usage

### Running

The program can be run from command line with following arguments:
 
* -e (--extended) — generating report in extended format
(default: basic format), parameterless,
* -s (--server) — address of the database host,
* -p (--port) — port of the database host,
* -n (--database_name) — name of the database,
* -u (--user) — user name on behalf of whom the extraction will be done,
* -pass (--password) — password for the user name,
* -t (--database_type) — type of database (currenly supported: Redshift, Postgress,
Mysql and Teradata),
* -o (--output) — output file path,
* -sc (--schema) — schema name (only postgres, default: public),
* -d (--odbc_driver) — odbc driver name for Teradata connection (only TeraData).
* -top (--top_number) — number of desired most frequent values (default: 5)
* -m (--max_text_length) — max length of text in given column that will allow to summarise top values and distinct count (default: 100)

#### Example commands

* Postgres: 

`dbexplorer -s 192.2.3.4 -p 5432 -n dvdrental -u dbadmin
-pass password -t postgres -o out.html`

* Teradata: 

`dbexplorer -e -t teradata -s 192.168.44.128 -u dbc -n
sample1 -pass dbc -o test.html -d 'Teradata Database ODBC
Driver 16.20'`

### Screenshots and live examples

Examples of generated reports can be found [here](https://github.com/ppollakr/dbexplorer/blob/master/misc/example_reports).

#### Basic report

Live example is [here](https://cdn.rawgit.com/ppollakr/dbexplorer/68a9e4ae95159aa132f8156386770aa0e7d19c9c/misc/example_reports/basic/mysql_employees.html)

![basic report screenshot](https://github.com/ppollakr/dbexplorer/blob/master/misc/screenshots/basic.png)

#### Extended report

Live example is [here](https://cdn.rawgit.com/ppollakr/dbexplorer/68a9e4ae95159aa132f8156386770aa0e7d19c9c/misc/example_reports/extended/mysql_employees_extended.html)

![extended report screenshot](https://github.com/ppollakr/dbexplorer/blob/master/misc/screenshots/extended.png)

## Authors

* Karol Prusinowski
* Paweł Pollak
* Karol Szczawiński
