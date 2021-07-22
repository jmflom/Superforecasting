from fredapi import Fred # get cpi historical data
import numpy as np
import pandas as pd
import sys
import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets
from torchvision.transforms import ToTensor, Lambda, Compose
import torch.utils.data as data_utils

## use command line arg
assert(len(sys.argv) == 2)
fred = Fred(api_key=sys.argv[1])

# get CPI data as first was released (will be verifier) and convert 
data = fred.get_series_first_release('CPIAUCSL')
df = data.to_frame()
df.columns = ['CPI']

# add past inflation as parameters
years = 10
for i in range(1, 12 * years):
    if i < 24 or (i < 60 and i%2 == 0) or i%4 == 0:
        mom_label = str(i) + " Mon Inflation"
        df[mom_label] = (df['CPI'] - df['CPI'].shift(i))/df['CPI'].shift(i)

## get UMICH 1 year inflation expectations
um_df = fred.get_series_first_release('MICH').to_frame()

## add previous 1 year inflation expectations as parameters
for i in range(1, int(12 * (years/4))):
    if i < (24/4) or (i < (60/4) and i%2 == 0) or i%4 == 0:
        mom_label = str(i) + " Mon Ago MICH Infl. Exp."
        um_df.columns = [mom_label]
        df = pd.concat([df, um_df], axis=1)
        um_df = um_df.shift(1)

# drop rows without usable data
df = df.dropna()

### START OF ML
batch_size = 64 # set batch size (splitting of training/test data)

# train and test separation of CPI as well as tensoring for Pytorch functions
train = df.sample(frac=0.8, random_state=0)
test = df.drop(train.index)
train_target = torch.tensor(train['CPI'].values.astype(np.float32))
test_target = torch.tensor(test['CPI'].values.astype(np.float32))
train = torch.tensor(train.drop('CPI', axis = 1).values.astype(np.float32)) 
test = torch.tensor(test.drop('CPI', axis = 1).values.astype(np.float32)) 
train_tensor = data_utils.TensorDataset(train, train_target) 
test_tensor = data_utils.TensorDataset(test, test_target) 

# final data loades
train_loader = data_utils.DataLoader(dataset = train_tensor, batch_size = batch_size, shuffle = True)
test_loader = data_utils.DataLoader(dataset = test_tensor, batch_size = batch_size, shuffle = True)

# define model
class NeuralNetwork(nn.Module):
    def __init__(self):
        super(NeuralNetwork, self).__init__()
        
        self.linear_relu_stack = nn.Sequential(
            nn.Linear(len(train[0]), 512),
            nn.ReLU(),
            nn.Linear(512, 20),
            nn.ReLU(),
            nn.Linear(20, 1),
            nn.ReLU()
        )

    def forward(self, x):
        logits = self.linear_relu_stack(x)
        return logits

model = NeuralNetwork()

# set loss and optimizer
loss_fn = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

# train dataloader
def train(dataloader, model, loss_fn, optimizer):
    size = len(dataloader.dataset)
    for batch, (X, y) in enumerate(dataloader):
        
        # Compute prediction error
        pred = model(X)
        loss = loss_fn(pred, y)

        # Backpropagation
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        if batch % 100 == 0:
            loss, current = loss.item(), batch * len(X)
            print(f"loss: {loss:>7f}  [{current:>5d}/{size:>5d}]")

# test dataloader
def test(dataloader, model, loss_fn):
    size = len(dataloader.dataset)
    num_batches = len(dataloader)
    model.eval()
    test_loss, correct = 0, 0
    with torch.no_grad():
        for X, y in dataloader:
            pred = model(X)
            test_loss += loss_fn(pred, y).item()
            correct += (pred.argmax(1) == y).type(torch.float).sum().item()
    test_loss /= num_batches
    correct /= size
    print(f"Test Error: \n Accuracy: {(100*correct):>0.1f}%, Avg loss: {test_loss:>8f} \n")

# determine # of epochs and train/test model
epochs = 100
for t in range(epochs):
    print(f"Epoch {t+1}\n-------------------------------")
    train(train_loader, model, loss_fn, optimizer)
    test(test_loader, model, loss_fn)