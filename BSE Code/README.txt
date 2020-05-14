Please install these Libraries and run with Python 3 and above:
1. Numpy
2. Pandas
3. matplotlib.pyplot


# Running the program
1. Please run the BSE.py file only for experiments. 
2. Run the unit tests in the "Tests" folder individually to perform unit testing. 



# Configuration of Agents
To run the system, you can change the number of agents on line 479. However, please be aware that because the current configuration is setting both buyer and seller side to equal, by setting it on line 479 will give the number of agents on ONLY one side.

For example, if there are 10 Liquidity consumers on line 479, there will be 20 in total in the market.

If the user wants to change this, please uncomment line 481-482 and comment line 483


# Configuration of time
This can be done by changing line 442. Note that this is in McG time not BSE time


# Saving results
The results will be saved in a folder called Result. If there already exist such folder, then it will be saved in
folder "Result0", or "Result1" and so on.

The files in those folder will be ordered as follow for {x}th run:
    1. folder spike_{x} will be the possible price spikes
    2. fig_mid_price_{x} is the mid price pattern
    3. price_swing_{x} is orders that cause a price swings of 0.05
    4. mr_mt_stats are the statistics overall of how many order each Mean Reversion, Momentum and Noise traders submitted
    5. mid_price_returns_autocorrelation.txt is the mid pirce and transaction price return auto correlation numbers
    6. mid_price_{x} and transaction_{x} is the csv files for the numbers over the time period
    7. return_{x} is the mid price return series