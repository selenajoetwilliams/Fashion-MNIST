# this class will create the neural network
# link to pytorch tutorial: https://pytorch.org/tutorials/beginner/basics/intro.html

'''
WELCOME!
This is my first attempt at making a neural network in pytorch using the fashion MNIST
dataset.

TODO
1. I have questions listed throughout this file that I would like help with 
search for 'question' to find a full list of them.

2. I am getting a terminal error because my use of 'pretrained' somewhere has
been deprecated and I should use weights instead. The lines that cause the terminal
error don't have 'pretrained' anywhere in them, so I'm not sure what line I should 
change to eliminate this. Any & all help is apprecaited. Thank you!

'''


import os
import torch
from torch import nn
import numpy as np
from torch.utils.data import Dataset
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from torchvision.transforms import ToTensor
import matplotlib.pyplot as plt
import torchvision.models as models

###########################################
# TENSORS

training_data = datasets.FashionMNIST(
    root="data",
    train=True,
    download=True,
    transform=ToTensor()
)

test_data = datasets.FashionMNIST(
    root="data",
    train=False,
    download=True,
    transform=ToTensor()
)

train_dataloader = DataLoader(training_data, batch_size=64)
test_dataloader = DataLoader(test_data, batch_size=64)

labels_map = {
    0: "T-Shirt",
    1: "Trouser",
    2: "Pullover",
    3: "Dress",
    4: "Coat",
    5: "Sandal",
    6: "Shirt",
    7: "Sneaker",
    8: "Bag",
    9: "Ankle Boot",
}

figure = plt.figure(figsize=(8, 8))
cols, rows = 3, 3

# question: can someone walk me through what each line this block of code means? 
for i in range(1, cols * rows + 1): # for each item in the 2D array
    sample_idx = torch.randint(len(training_data), size=(1,)).item() # sample a random index
    img, label = training_data[sample_idx] # set the image and label to = the image and label of the data at the randomly sampled index
    figure.add_subplot(rows, cols, i) # add a subplot?
    plt.title(labels_map[label]) # title the plot?
    plt.axis("off") # axis formatting
    plt.imshow(img.squeeze(),cmap="gray") # image formatting
plt.show() # show it!

###########################################
# TRANSFORMS 

ds = datasets.FashionMNIST(
    root="data",
    train=True,
    download=True,
    transform=ToTensor(),
    target_transform=(lambda y: torch.zeros(10, dtype=torch.float).scatter_(0, torch.tensor(y), value=1))
)

###########################################
# BUILD MODEL

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using {device} device") # note: I am still using cpu 

class NeuralNetwork(nn.Module):

    # initializing the model
    def __init__(self):
        super(NeuralNetwork, self).__init__()
        self.flatten = nn.Flatten()
        self.linear_relu_stack = nn.Sequential(
            # these are the different model layers
            nn.Linear(28*28, 512), # image dimensions, # of model dimentions?
            nn.ReLU(),
            nn.Linear(512, 512),
            nn.ReLU(),
            nn.Linear(512, 10),
        )

    # defining the forward pass
    def forward(self, x):
        x = self.flatten(x)
        logits = self.linear_relu_stack(x)
        return logits

model = NeuralNetwork().to(device)
# should the line above be: model = NeuralNetwork()
print(model)

X = torch.rand(1, 28, 28, device=device)
logits = model(X) 
pred_probab = nn.Softmax(dim=1)(logits)
y_pred = pred_probab.argmax(1)
print(f"Predicted class: {y_pred}")

###########################################
# MODEL LAYERS

# sampling a mini batch to see what happens as it goes through the model
input_image = torch.rand(3, 28, 28)
print(input_image.size()) 

# flattening the dimensions from 28x28 2D array to a 1D array of 784 pixels
flatten = nn.Flatten() 
flat_image = flatten(input_image)
print(flat_image.size())

# linear layer
layer1 = nn.Linear(in_features=28*28, out_features=20)
hidden1 = layer1(flat_image)
print(hidden1.size())

# relu layer 
print(f"Before ReLU: {hidden1}\n\n")
hidden1 = nn.ReLU()(hidden1)
print(f"After ReLU: {hidden1}") 
# question: is the hidden layer meant to improve the assumptions, as seen in smaller abs vals of the values in each index of the tensor?

# sequential layer
# TODO: look up seq_modules in pytorch documentation
seq_modules = nn.Sequential(
    flatten,
    layer1,
    nn.ReLU(),
    nn.Linear(20,10)
)
input_image = torch.rand(3,28,28)
logits = seq_modules(input_image)

# softmax layer 
softmax = nn.Softmax(dim=1)
pred_probab = softmax(logits)

# model parameters
# here we iterate over each parameter and print the size & a preview of its values
print(f"Model structure: {model}\n\n")

for name, param in model.named_parameters():
    print(f"Layer: {name} | Size: {param.size()} | Values : {param[:2]} \n")
# question: what does the param[:2] in the line above mean?

###########################################
# AUTOGRAD (automatic differentiation)

x = torch.ones(5) # input tensor
y = torch.zeros(3) # expected output
w = torch.randn(5, 3, requires_grad=True)
b = torch.randn(3, requires_grad=True)
z = torch.matmul(x, w)+b
loss = torch.nn.functional.binary_cross_entropy_with_logits(z, y)

# printing out the gradient function?
print(f"Gradient function for z = {z.grad_fn}")
print(f"Gradient function for loss = {loss.grad_fn}")

# computing gradients
print(f"\nComputing the gradients...") # I added this myself
loss.backward()
print("The gradient of the weights is: ")
print(w.grad)
print("The gradient of the biases is: ")
print(b.grad)

"""
 note: I skipped the code in the rest of this part of the tutorial
 because it covered things like disabling gradient tracking which
 I don't think I need for the MNIST neural network
"""

###########################################
# OPTIMIZING MODEL PARAMETERS

"""
Note that the following lines were added in the tensors section in order to 
have all the right code for optimization:
    train_dataloader = DataLoader(training_data, batch_size=64)
    test_dataloader = DataLoader(test_data, batch_size=64)
"""

# question: at this step when I run the program, my output doesn't match the
# output in the tutorial 

# defining the hyper parameters
learning_rate = 1e-3
batch_size = 64
epochs = 5

# defining the type of loss function 
# in this case we use cross entropy loss
loss_fn = nn.CrossEntropyLoss()

# defining the optimizer object 
# in this case we use stochastic gradient descent
optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate)

# full implementation of optimization algorithm
def train_loop(dataloader, model, loss_fn, optimizer):
    size = len(dataloader.dataset)
    for batch, (X, y) in enumerate(dataloader):
        # Compute prediction & loss
        pred = model(X)
        loss = loss_fn(pred, y)

        # Backpropagation
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        if batch % 100 == 0:
            loss, current = loss.item(), batch * len(X)
            print(f"loss: {loss:>7f} [{current:>5d}/{size:>5d}]")
            # question: what do the :>7f, :>5d mean in the line above?

# defining the training & test loop
def test_loop(dataloader, model, loss_fn):
    size = len(dataloader.dataset)
    num_batches = len(dataloader)
    test_loss, correct = 0, 0

    with torch.no_grad():
        for X, y in dataloader:
            pred = model(X)
            test_loss += loss_fn(pred, y).item()
            correct += (pred.argmax(1) == y).type(torch.float).sum().item()
    
    test_loss /= num_batches
    correct /= size
    print(f"Test Error: \n Accuracy: {(100*correct):>0.1f}%, Avg loss: {test_loss:>8f} \n")

# initializing the loss function optimizer
loss_fn = nn.CrossEntropyLoss()
optimizer = torch.optim.SGD(model.parameters(), lr = learning_rate)

epochs = 2
for t in range(epochs):
    print(f"Epoch {t+1}\n---------------------------")
    train_loop(train_dataloader, model, loss_fn, optimizer)
    test_loop(test_dataloader, model, loss_fn)
print("Done!")


###########################################
# Save & Load Model

# saving the model
model = models.vgg16(pretrained=True) # pretrained=True used to be passed into these params
torch.save(model.state_dict(), 'model_weights.pth')

# loading the model
model = models.vgg16() # we do not specify pretrained=True, i.e. we do not load default weights
    # note, Patrick Loeber's youtube tutorial has the line above as: 
    # model = Model(*args, **kwargs)
model.load_state_dict(torch.load('model_weights.pth'))
model.eval()
'''
Question:
I get a terminal error when I run this code saying that 'pre-trained' is deprecated
and to use 'weights' instead. Unfortunately the lines the terminal error points to don't
contain the key-word pretrained, which makes it harder to trouble shoot this issue. 
What should I change to avoid this issue?
'''

# question: these tensors are blank right?
# question: what about loading the acutal data?
# question: this just creates 2 blank 2-D arrays, right? one 1x2 array and another 3x4 array?
# data = [[1,2],[3,4]]
# x_data = torch.tensor(data)
