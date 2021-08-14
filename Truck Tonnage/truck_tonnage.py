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

percent_gains_sixmo = get_pct_gains(truck_tonnage, 6) # np.array of rolling 7-month % gains (jul, aug, sep, oct, nov, dec)
percent_gains_onemo = get_pct_gains(truck_tonnage, 1) # np.array of rolling 1-month % gains

gains_mean_sixmo, gains_std_sixmo = np.mean(percent_gains_sixmo), np.std(percent_gains_sixmo)
gains_mean_onemo, gains_std_onemo = np.mean(percent_gains_onemo), np.std(percent_gains_onemo)

## run monte carlo simulation for diff buckets using normal sampling
## of percentage gain (1+that sample)
## RUN X times and categorize probability of each bin
above120_sixmo = 0
above120_onemo = 0
X = 1000000
curr_value = 112

for i in range(X):
    # six month estimate using normal distribution
    tonnage_estimate_sixmo = (1 + (np.random.normal(gains_mean_sixmo, gains_std_sixmo)/100)) * curr_value
    
    ## random walk from one month normal distribution to estimate
    ## the six month change
    tonnage_estimate_onemo = curr_value
    for j in range(5):
        tonnage_estimate_onemo *= (1 + (np.random.normal(gains_mean_onemo, gains_std_onemo)/100))

    if tonnage_estimate_onemo > 120:
        above120_onemo += 1
    if tonnage_estimate_sixmo > 120:
        above120_sixmo += 1

probability_onemo = round(100*above120_onemo/X, 3)
probability_sixmo = round(100*above120_sixmo/X, 3)


print("Six Month Rolling Prob.:", probability_sixmo)
print("One Month Rolling Prob.:", probability_onemo)


