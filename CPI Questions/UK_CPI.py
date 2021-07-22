# importing csv module
import csv
import numpy as np
from dateutil import parser
from datetime import datetime
from datetime import timedelta
  
# Months table
MONTHS = {'JAN': '01', 'FEB': '02', 'MAR': '03', 'APR': '04', 'MAY': '05', 'JUN': '06', 'JUL': '07', 'AUG': '08', 'SEP': '09', 'OCT': '10', 'NOV': '11', 'DEC': '12'}

# csv file name
filename = "CPI Questions/UK_CPI_data.csv"

# reading csv file
with open(filename, 'r') as csvfile:
    # creating a csv reader object
    csvreader = csv.reader(csvfile)

    cpis = [] # list of historical CPI nums

    historical_cutoff = 50 # how many years back are we considering
    for row in csvreader:
        dte_raw = row[0]
        if len(dte_raw) == 8:
            dte_temp = str(dte_raw[:4]) + '-' + MONTHS[dte_raw[5:]] + '-01'
            dte = parser.parse(dte_temp)
        
            ## append cpis after historical cuttoff to our price list
            if(dte > datetime.now() - timedelta(weeks=(52*historical_cutoff))):
                cpis.append(float(row[1]))

    percent_gains = [] # list of rolling 5-month % gains (jul, aug, sep, oct, nov)
    for i in range(len(cpis) - 5):
        percent_gains.append(100*(cpis[i+5] - cpis[i])/(cpis[i]))
    
    np_gains = np.array(percent_gains)
    gains_mean, gains_std = np.mean(np_gains), np.std(np_gains)

    ## run monte carlo simulation for diff buckets using normal sampling
    ## of percentage gain (1+that sample)
    ## RUN X times and categorize probability of each bin
    buckets = [0, 0, 0, 0, 0, 0]
    X = 1000000
    curr_value = 111.3
    cpi_nov2020 = 108.9
    for i in range(X):
        
        cpi_estimate = (1 + (np.random.normal(gains_mean, gains_std)/100)) * curr_value
        pct_change = 100*(cpi_estimate - cpi_nov2020)/cpi_nov2020

        if pct_change < 1.7:
            buckets[0] += 1
        elif pct_change <= 2.2:
            buckets[1] += 1
        elif pct_change < 2.9:
            buckets[2] += 1
        elif pct_change <= 3.4:
            buckets[3] += 1
        elif pct_change < 4.1:
            buckets[4] += 1
        else:
            buckets[5] += 1

probabilities = [round(100*float(occurances)/float(X), 3) for occurances in buckets]
print(probabilities)
