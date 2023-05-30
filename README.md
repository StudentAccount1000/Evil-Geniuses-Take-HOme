# Evil-Geniuses-Take-HOme
Take Home Assessment for Evil Geniuses SWE 2023 Internship Postion - Jake Watson

How to run:
1. Navigate to the correct directory
2. run the command 'py CSGO_position_analysis.py'
3. the program should automatically open the heatmap picture, however if it does not you can find it in the main directory named 'heatmap.png'

If you have any issues running the file, please check that you have all of the dependencies installed below

Dependincies:
1. pyarrow: Used to read in the parquet file
2. pandas: the table is converted into a pandas dataframe for optimized effiency compared to using python's native structures
3. numpy: needed as a base for some of the other libraries here, 
4. mathplotlib: used to generate the heatmap graph for part 2c
5. scipy: used for the 2-D tree to find nearest neighbors much quicker than manual implementation
6. os: used to open the picture file after it is generated

Part 3:
A simple way to make the coaching staff more able to use the product is a UI. A simple UI which would allow them to upload the match replay file and potentially specify a few details such as important threshold values and if they are interested in weapon class data and such. A simple UI is possible with PYthon, and as long as the requirements are kept simple that is feasible within one week of work. 
One thing that will still be difficult for a less technological person is the definition of gameplay boundaries, as they may not know how to find coordinate values from within the game or be able to look into the editor to find them, so that would have to resolved another way
