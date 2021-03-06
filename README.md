# Download link for v1.03 (latest)
If updating from v0.85 or lower, delete all previous files apart from your config. Run the EXE in the same folder as your config.
The directoy should look as follows:
* GW2TT.exe
* exampleConfig.ini
* config.ini

If you do not have a config.ini, just run the application once to generate it.
* https://github.com/ndj710/GW2-Trading-post-tracker/raw/main/downloads/GW2TT%20v1.03.zip

# Note:
This is an ongoing project, I am making an application for windows on behalf of a friend. I am experimenting with tkinter and other libraries.

# GW2TT
GWT22 is a windows application which allows the user to enter an item ID and then set a price for that item, the application will make periodic API calls to fetch the item price, if the price the user set is met, the user will be emailed a notification.

## Screenshots
<div>
  <h5>Main page</h5>
  <img src="/screenshots/Mainpage.png?raw=true" width="639" height="373"/>
</div>


### Changelog:
#### Version 1.03

Changes:
*	Can now drag items and swap with other items using the hamburger on left (Currently does NOT save positions on app close)

Bug fixes:
*	Pressing add on blank item ID entry field will no longer trigger an error in logs
*	Bug where changing price to 0 while tracking item (green bell) would cause a crash


#### Version 1.02

Changes:
*	Adjusted the padding at bottom of notification button to center the textimage
*	Added a state for notifcation button being triggered
*	Adjusted delete button height to match notification button

Bug fixes:
*	Logs showing same error multiple times


#### Version 1.01

Changes:
*	Changed size of setting input fields to match rest of UI
*	Can now list an item twice (one for selling and one for buying)
*	Title now has capital T's

Bug fixes:
*	Removed leading whitespace from item names


#### Version 1.00
Finished all the basic functionality, application is ready for use.
Changes:
*	Added scrollbar (have to use mouse and drag, scrollwheel not currently working)
*	Added link to item data on https://www.gw2bltc.com/ by clicking itemID
*	Removed priceData base, price will just be checked after each API call. No need for hisotoric data

Bug fixes:
*	Removed items that are not listed in the tradepost from being loaded into memory
* 	Issue where deleting one item and adding another would sometimes overlap current items in the watchlist


#### Version 0.85

Changes:
*	Changed item data population method, Item Data no longer needs to be saved in database. Only price data is saved to database


#### Version 0.84

Changes:
*	Cleaned up source code

Bug fixes:
* 	fix issue if opening without images folder
*	Issue with notification bell being red when should be green (sometimes)


#### Version 0.83

Changes:
* 	Changed format of current price
* 	Reduced window size by changing text font
* 	Added placeholder price for current price until first update is received
* 	Can no longer set item to be tracked if no price has been entered
* 	Added some checks and blocks to stop tracking of items with target price of 0

Bug fixes:
* 	Fixed a graphical glitch if no items are in the watchlist on boot up
* 	Fixed bug where 'Item ID' is not reporting incorrect ID
* 	Fixed placeholder for target price entry boxes not showing correctly

#### Version 0.82

Changes:
* 	Price now in colours and displays images for gold, silver, copper

Bug fixes:
* 	Fixed the ungraceful closing of update thread
* 	Fixed incorrect price conversion (+- 1 copper)
