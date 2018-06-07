# DatabaseExplorer

## Description

### Info
The program was created for *Team project - development of data analysis system* course run by [Prof. P. Biecek](https://github.com/pbiecek).


### Program description

The aim of the created program is to generate a summary report of provided database.
It extracts basic or extended information such as:
 
* table, column names
* data stats (top values, mean, quartiles etc.)
* types of data and number of rows

#### Further information

Full specification and more detailed description of summarization features can be found in `docs/Specyfikacja wymagań.pdf`.


 

## Installation

1. Clone repository: `git clone https://github.com/ppollakr/dbexplorer.git`
2. Change to directory: `cd dbexplorer`
3. Install package: `pip install .`
4. Run program with proper arguments: `dbexplorer -s 192.2.3.4 -p 5432 -n dvdrental -u dbadmin -pass password -t postgres -o out.html`


## Usage

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

Examples:

* Postgres: 

`dbexplorer -s 192.2.3.4 -p 5432 -n dvdrental -u dbadmin
-pass password -t postgres -o out.html`

* Teradata: 

`dbexplorer -e -t teradata -s 192.168.44.128 -u dbc -n
sample1 -pass dbc -o test.html -d 'Teradata Database ODBC
Driver 16.20'`

## Authors

* Karol Prusinowski
* Paweł Pollak
* Karol Szczawiński

