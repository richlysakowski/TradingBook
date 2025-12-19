
# DONE: Builds and User Guides

## DONE:  Create detailed instructions named "TradeBook_Portable_Version_Builder_Guide.md" that gives step-by-step instructions how to build the portable version.  Modify the existing build script for the portable version to store all portable version code in a folder named "portable_version_kit"; check to make sure the folder exists and if not then create it. 

    # DONE:  Create a "QuickStart_Portable_Instructions_Guide.md" that has instructions for how to run the portable version.  Store it in the folder "portable_version_kit"

    # DONE: Provide detailed step-by-step instructions to build the complete TradeBook Windows Installer saved into a document named "Build_TradeBook_Windows_Installer_Guide.md".

Provide a "Tradebook_Windows_Installer_QuickStart_Guide.md" that provides step-by-step instructions how to run the Tradebook_Windows_Installer and then start the application. 

Identify existing build or installation scripts that may be redundant or obsolete, and make sure only the latest versions of the build scripts are stored in the folders for the portable version and the installer version.  Move all obsolete scripts to a folder named "obsolete_scripts" within the "scripts" directory.

Are you clear what you need to do?  Give me your plan and wait for my confirmation before proceeding.

#######################################

Next I want you to run the build scripts to create the portable version and the Windows installer version that you just created according to the documentation Guides.  
Run both build scripts, one after the other, to verify that they work as documented.  
Run them in a new terminal, and make sure that logging is turned on and catching all operations with any errors to a timestamped file.  
If there are any errors, then fix the errors after the scripts finish running and then run them again.  
Repeat this process until the scripts run without error.  
Update both the build scripts and each documentation Guide to include any changes that are required for a new user to  run the updated scripts.  

Are you clear what to do?  Give me your plan and wait for me to confirm it. 
#############################################################################

## Minor Enhancements Needed
The "Trades Page" should be renamed "Trades Ledger" to better reflect its purpose.
The Trades Ledger Table must have a "Date Closed" column added to show the date when the trade was closed.  
The Trades Ledger Table must have all the columns be sortable columns. 
The Trades Ledger Table must be "tighter" so there is more "information density" and more data and controls can be displayed within the same area
The trading symbol in each row must be a clickable hyperlink that jumps to the Trade Analysis Page for that trade.  


# Day Trading and Swing Trading Support Enhancements

Much more trading analytics and reporting are required.  Calculating and displaying more statistics and details for the lifecycle of each individual trade is important.  

# Trade Statistics


## Swing Trading Support
The Days In Trade (DIT) is important for Swing Trading. 


## Day Trading Support
Time-In-Trade (TIT) is important for Day Trading.  
We need to a lot more support for Day Trading where stocks or futures are traded for a short as a few seconds up to many hours, but all positions are closed before the end of the day or the current session.  

