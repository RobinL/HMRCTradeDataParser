Instructions for connecting to Azure SQL from Ubuntu

Resources:

http://stackoverflow.com/questions/21891554/sqlalchemy-hangs-while-connecting-to-sql-azure-but-not-always

http://stackoverflow.com/questions/9723656/whats-causing-unable-to-connect-to-data-source-for-pyodbc

https://bitbucket.org/janihur/devoops/wiki/How%20To%20Connect%20Azure%20SQL%20Database%20From%20Ubuntu

http://askubuntu.com/questions/167491/connecting-ms-sql-using-freetds-and-unixodbc-isql-no-default-driver-specified

http://www.gazoakley.com/content/connecting-sql-azure-python-ubuntu-using-freetds-and-unixodbc

###Step 0

Download anaconda and install

Pip install pyodbc



###Step 1

TDS Driver
Microsoft SQL Server uses Tabular Data Stream (TDS) to transfer data between a database server and a client. http://www.freetds.org/ is an open source TDS implementation. 

    $ sudo apt-get install -y freetds-dev freetds-bin



In 
	
	$HOME/.freetds.conf
	/etc/freetds/freetds.conf

`Sudo vim` into `freeds.conf` and make the following edits.

	#   $Id: freetds.conf,v 1.12 2007/12/25 06:02:36 jklowden Exp $
	#
	# This file is installed by FreeTDS if no file by the same 
	# name is found in the installation directory.  
	#
	# For information about the layout of this file and its settings, 
	# see the freetds.conf manpage "man freetds.conf".  
	
	# Global settings are overridden by those in a database
	# server specific section
	[global]
	        # TDS protocol version
	;       tds version = 7.1
	
	        # Whether to write a TDSDUMP file for diagnostic purposes
	        # (setting this to /tmp is insecure on a multi-user system)
	;       dump file = /tmp/freetds.log
	;       debug flags = 0xffff
	
	        # Command and connection timeouts
	;       timeout = 10
	;       connect timeout = 10
	        # If you get out-of-memory errors, it may mean that your client
	        # is trying to allocate a huge buffer for a TEXT field.  
	        # Try setting 'text size' to a more reasonable limit 
	        text size = 64512
	
	[SQLDemo]
	host = sdfmyname.database.windows.net
	port = 1433
	tds version = 8.0
	

At this point we can test the connection:

	
	$ TDSVER=7.1 tsql -H <SERVER_ADDRESS> -p 1433 -D <DBNAME> -U <USER> -P <PASSWORD>
	# using configuration, note username -U requires also @<HOST> part !
	$ tsql -S <SERVERNAME> -D <DBNAME> -U <USER>@<HOST> -P <PASSWORD>


###Step 2 - sort out our ODBC driver.  This is what enables Python to connect

Configure the driver in `/etc/odbcinst.ini:`


`Sudo vim` into `/etc/odbcinst.ini`:

	[ODBC]
	Trace = Yes
	TraceFile = /tmp/odbc.log
	
	[FreeTDS]
	Description = TDS driver (Sybase/MS SQL)
	Driver = /usr/lib/x86_64-linux-gnu/odbc/libtdsodbc.so
	Setup = /usr/lib/x86_64-linux-gnu/odbc/libtdsS.so
	UsageCount = 1
	CPReuse =
	CPTimeout = 0
	FileUsage = 1
	Pooling = No


Configure the data source names (DSN) in `/etc/odbc.ini`


	[SQLDemo]
	Description = my dsn
	Driver = FreeTDS
	Servername = SQLDemo
	database = TRADEDATA


Now we should be ready to connect from python


    cnx = pyodbc.connect("DSN=SQLDemo;UID=<uid>@sdfmyname;PWD=<password>")

If the above works we can now connect through using SQL alchemy.  This is a bit tricky because the connection string is nonstandard:

http://stackoverflow.com/questions/4493614/sqlalchemy-equivalent-of-pyodbc-connect-string-using-freetds

This is how to create an engine in SQLAlchemy


	def connect():
	    return pyodbc.connect("DSN=SQLDemo;UID=<uid>@sdfmyname;PWD=<password>")
	engine = sqlalchemy.create_engine('mssql://', creator=connect)