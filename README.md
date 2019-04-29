## Labels

labels

## Purpose
The purpose of this application is to create labels directly from the Production Plan DocType.

## History
This application was born back when @Tropicalrambler was a complete newbie in ERPNext, and we needed to create printed labels for items we sold, according to the Sales Orders. This need came right after we had just implemented ERPNext and I did not have a clue about how to code with Python and server tech.  So I opted to use the ProductionPlanningTool.csv file output as input for a Python function that created the labels. I installed this python as an executable on a Mac Mini and setup the workflow for it.  We operated like this for 2 and a half years, until the update to Version 11 forced us to code it as a bbackend script in Python for ERPNext. Given the reduced time a CEO has to run the business and startup other projects, it has now become a team effort and this is the result of what has recently been recoded.  

## Functionality
Currently it is a one trick pony working with Production Plan:
-Label size is fixed 50 x 38mm
-Text location and elements are fixed
-Barcode size and type is fixed
-Logo location is fixed (although selectability is variable)

## Future improvements
At some point in the future we wish to create a front end designer page where users can define
-page size
-page elements (color, font, style, etc.)
-variable elements: Multiple items or sales orders from Production Plan, dates, etc. all variable data elements
-Item based style definition:
For each item, user will be able to define a print template based on page size constraint.  This will allow user to print labels on the same page size, but with different styles, making workflows (print runs) go easier and allow variety in your prints.

#### License

GNU General Public License v3.0

>  Icon made by [Pixel perfect](https://www.flaticon.com/authors/pixel-perfect) from www.flaticon.com
