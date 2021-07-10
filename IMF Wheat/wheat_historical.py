# importing csv module
import csv
from dateutil import parser
from datetime import datetime
from datetime import date
from datetime import timedelta
  
# csv file name
filename = "../wheatdata.csv"

# reading csv file
with open(filename, 'r') as csvfile:
    # creating a csv reader object
    csvreader = csv.reader(csvfile)
    
    # skip header row [Date, Price of Wheat/MT]
    next(csvreader) 

    buckets = {'bin1': 0, 'bin2': 0, 'bin3': 0, 'bin4': 0, 'bin5': 0}
    tot = 0

    # iterate through dates JUST past 10 years and group into buckets
    for row in csvreader:
        dte = parser.parse(row[0]) # date of data
        
        if(dte > datetime.now() - timedelta(weeks=(52*20))): # if past 10 years
            price = float(row[1]) # price of wheat
            tot += 1

            if price < 220.0:
                buckets['bin1'] += 1
            elif price < 260.0:
                buckets['bin2'] += 1
            elif price < 300.0:
                buckets['bin3'] += 1
            elif price < 340.0:
                buckets['bin4'] += 1
            else:
                buckets['bin5'] += 1
    
    # calculate probabilities of each bin 
    probabilities = {}
    for key, val in buckets.items():
        probabilities[key] = round(100*float(val)/float(tot), 3)

    print(probabilities)
