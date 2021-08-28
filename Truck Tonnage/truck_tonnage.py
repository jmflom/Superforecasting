import requests
import numpy as np
from dateutil import parser
from datetime import datetime
from datetime import timedelta

def get_pct_gains(index_list, months):
    pct_gains = []
    for i in range(len(index_list) - months):
        pct_gains.append(100*(index_list[i+1] - index_list[i])/(index_list[i]))
    return np.array(pct_gains)

response = requests.get("https://data.bts.gov/resource/crem-w557.json").json() # ATA Trucking Numbers API

truck_tonnage = [] # reports monthly on the 1st
historical_cutoff = 30 # how many years back are we considering

for data in response:
    if 'truck_tonnage_index' in data:
        dte = parser.parse(data['date'])
        
        ## append cpis after historical cuttoff to our price list
        if(dte > datetime.now() - timedelta(weeks=(52*historical_cutoff))):
            truck_tonnage.append(float(data['truck_tonnage_index']))

percent_gains_fivemo = get_pct_gains(truck_tonnage, 5) # np.array of rolling 5-month % gains (aug, sep, oct, nov, dec)
percent_gains_onemo = get_pct_gains(truck_tonnage, 1) # np.array of rolling 1-month % gains

# hist = np.histogram(percent_gains_onemo, 6)
# print(hist)

gains_mean_fivemo, gains_std_fivemo = np.mean(percent_gains_fivemo), np.std(percent_gains_fivemo)
gains_mean_onemo, gains_std_onemo = np.mean(percent_gains_onemo), np.std(percent_gains_onemo)

## run monte carlo simulation for diff buckets using normal sampling
## of percentage gain (1+that sample)
## RUN X times and categorize probability of each bin
above120_fivemo = 0
above120_onemo = 0
X = 1000000
curr_value = 110

for i in range(X):
    # six month estimate using normal distribution
    tonnage_estimate_fivemo = (1 + (np.random.normal(gains_mean_fivemo, gains_std_fivemo)/100)) * curr_value
    
    ## random walk from one month normal distribution to estimate
    ## the five month change
    tonnage_estimate_onemo = curr_value
    for j in range(5):
        tonnage_estimate_onemo *= (1 + (np.random.normal(gains_mean_onemo, gains_std_onemo)/100))

    if tonnage_estimate_onemo > 120:
        above120_onemo += 1
    if tonnage_estimate_fivemo > 120:
        above120_fivemo += 1

probability_onemo = round(100*above120_onemo/X, 3)
probability_fivemo = round(100*above120_fivemo/X, 3)


print("Six Month Rolling Prob.:", probability_fivemo)
print("One Month Rolling Prob.:", probability_onemo)


