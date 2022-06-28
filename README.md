# Note:
This is an ongoing project, I am making an application for windows on behalf of a friend. I am experimenting with tkinter and other libraries.

# GW2TT
GWT22 is a windows application which allows the user to enter an item ID and then set a price for that item, the application will make periodic API calls to fetch the item price, if the price the user set is met, the user will be emailed a notification.

## Screenshots



### Changes made:
Version 0.83 Changelog

Changes:
	-Changed format of current price
	-Reduced window size by changing text font
	-Added placeholder price for current price until first update is received
	-Can no longer set item to be tracked if no price has been entered
	-Added some checks and blocks to stop tracking of items with target price of 0

Buf fixes:
	-Fixed a graphical glitch if no items are in the watchlist on boot up
	-Fixed bug where 'Item ID' is not reporting incorrect ID
	-Fixed placeholder for target price entry boxes not showing correctly

Version 0.82 Changelog

Changes:
	-Price now in colours and displays images for gold, silver, copper

Bug fixes:
	-Fixed the ungraceful closing of update thread
	-Fixed incorrect price conversion (+- 1 copper)


### Changes to implement:
Possiblly split itemId data and price data into two different database files
Change database population method
Fix issue if opening without images folder
Add scrollbar
Fix placeholder text for target price fields
