Explain in ELI10 terms about all the complications we had when building this Javascript  application.   ELI10 explain the portable build process, and the installer build process. I don't have those problems with Python applications.  Python does not have as many packages to install either.  

Explain the problems with better-sqlite3 package and how it needs to be compiled on Windows.  

Explain the problems with node-gyp and how it needs Python and Visual Studio Build Tools.  

Explain how all these complications make building a portable Windows executable much more difficult than a Python application that can be bundled with PyInstaller.  

Explain how Electron applications have many more dependencies than Python applications.  Explain how Electron applications need to bundle Chromium and Node.js runtimes, which makes them larger in size compared to Python applications.  
Explain how the build tools for Electron are more complex and require more setup compared to Python packaging tools.  

Explain how the cross-platform nature of Electron adds additional layers of complexity in ensuring compatibility across different operating systems, which is less of an issue with Python applications.

Explain the problems with file locks trying to overwrite files that are in use during the build process on Windows.  Python does nseem to have these file locks.  

## BUGFIX: 
Error getting debug status: TypeError: can't access property "getDatabaseStatus", window.electronAPI is undefined

##### Help me fix up all the scripts so they work with the newly built portable and native Windows Installer.  
##################################################################
# TODO: add simple launch or QuickStart Utility and QuickStart Guide.
# Adding functionality to support importing trades from Charles Schwab accounts.

TODO: Need to parse and import Schwab trading data from Charles Schwab account statements in CSV format.

## FUTURES TRADES SUPPORT:
TODO: Need to support Futures trades.  This includes parsing the Schwab CSV format for Futures trades, which may differ from stock trades.
TODO: Futures trades have different point-values depending on the contract.  
Futures need a mapping table to convert futures contract point-values to currency value.  
Focus on Top 10 contracts traded by volume.  
Default to standard values for popular contracts, and allow user to add a table of point-values for less common contracts.

TODO: Need to support Options trades.

TODO: Add support for tab-separated values (TSV) since Schwab exports TSV files with a ".csv" extension.

TODO: Create sample Schwab CSV file with at least 100 stock trades for testing.

TODO: Add instructions in the Import Dialog Box about column formatting for Schwab CSV files.


TODO: Make the import capabilities must more fault-tolerant and robust.

# Import Dialog Box WITH ERROR MESSAGE:

Import CSV from Schwab

Upload a CSV file exported from Schwab with trading data. The file should be tab-separated with columns: Date, Action, Symbol, Description, Quantity, Price, Fees & Comm, Amount.

Select CSV File
2025-11-26-AcctStmt-D-70029726_(IRA)-NQ-FUTURES-TOS-SIMULATED-TRADE-transactions-NOComments.csv
Parse File
Parsing Errors:
Missing required columns: Date, Action, Symbol, Quantity, Price. Found headers: Account Statement for D-70029726 (ira) since 10/28/25 through 11/26/25

# Schwab Developer API Applications: 

TODO: Develop a Schwab Developer API application to access account data programmatically.

TODO: Get the Schwab API access approved for TradingBook application, for both the paper trading and the live trading environments.  


######################################################################


We want extract a set of detailed requirements functionality specifications from this codebase.  Ingest the entire codebase and then using the attached requirements template, backfill requirements from the working codebase.   






