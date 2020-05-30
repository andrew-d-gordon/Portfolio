
'''
Image Classification
Small scratch CNN able to distinguish between 10 different classes of images:
airplanes, cars, birds, cats, deer, dogs, frogs, horses, ships, and trucks...
Working with CIFAR-10 dataset from Keras.
'''

# Ignore various warnings coming from tensorflow which can flood inundate outputs.
import warnings
warnings.filterwarnings('always')
warnings.filterwarnings('ignore')

import numpy as np

import matplotlib.pyplot as plt
from matplotlib import style
import seaborn as sns
import random as rn
 
# config some defaults for plotting
style.use('fivethirtyeight')
sns.set(style='whitegrid',color_codes=True)

#Deep learning imports
from tensorflow.keras import backend as K
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import Adam, SGD, Adagrad, Adadelta, RMSprop 
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.layers import Dropout, Flatten, Activation
from tensorflow.keras.layers import Conv2D, MaxPooling2D

import tensorflow as tf

"""Shows some images from set"""

fig, ax = plt.subplots(2, 5)
fig.set_size_inches(10, 6)

for i in range(2):
    for j in range(5):
        c = j + 5*i # Class counter
        l = np.random.choice(np.where(y == c)[0], 1)[0] # Get a random image from class c
        ax[i, j].imshow(X[l])
        ax[i, j].set_title('Class: ' + str(y[l]))
        # Hide grid lines
        ax[i, j].grid(False)
        # Hide axes ticks
        ax[i, j].set_xticks([])
        ax[i, j].set_yticks([])
        
plt.tight_layout()

print('X (images)', X.shape)
print('y (classes)', y.shape)

"""50,000 samples, each image is 32 by 32 pixels with 3 color channels representing R G and B"""

# One-hot encode integer values of class labels
y = to_categorical(y, 10)

# Normalize vals to between 0 and 1
X = X / 255.

# note: model aimed to have less than 500000 parameters

# This is where we define the architecture of our deep neural network.
model = Sequential()

model.add(Conv2D(filters = 16,      
                kernel_size = (3, 3), 
                padding = 'Same',
                activation = 'relu', 
                input_shape = (32, 32, 3)))
model.add(MaxPooling2D(pool_size = (2, 2)))
model.add(Conv2D(filters = 32,      
                kernel_size = (3, 3), 
                padding = 'Same',
                activation = 'relu'))
model.add(MaxPooling2D(pool_size = (2, 2))) #vv 64 vv
model.add(Conv2D(filters = 64,      
                kernel_size = (3, 3), 
                padding = 'Same',
                activation = 'relu'))
model.add(MaxPooling2D(pool_size = (2, 2)))

model.add(Flatten())

model.add(Dense(50, activation = 'relu'))

model.add(Dropout(0.5))

# dense layer with softmax acitivation, 10 for amount of classes
model.add(Dense(10, activation = "softmax"))

# Implementing batch gradient descent
batchsize = 200

# note: had max of 50 epochs to reach val acc of ideally above 70%
epochs = 50

opt = RMSprop(lr = 0.001) #.001

model.compile(optimizer = opt,
              loss = 'categorical_crossentropy',
              metrics = ['accuracy'])

model.summary()

history = model.fit(X, 
                    y,
                    batch_size = batchsize,
                    epochs = epochs, 
                    validation_split = 0.2, # DON'T CHANGE validation_split!
                    verbose = 1)

#plot training and validation loss/accuracies

import matplotlib.gridspec as gridspec

fig = plt.figure()
fig.set_size_inches(15, 15)
gs = gridspec.GridSpec(3, 2, figure=fig)

ax1 = fig.add_subplot(gs[0, 0])
ax1.plot(history.history['loss'])
ax1.plot(history.history['val_loss'])
plt.title('Model Loss for validation against training')
ax1.set_ylabel('Loss')
ax1.legend(['train', 'val'])

ax2 = fig.add_subplot(gs[0, 1])
ax2.plot(history.history['accuracy'])
ax2.plot(history.history['val_accuracy'])
plt.title('Model Accuracy for validation against training')
ax2.set_ylabel('Accuracy')
ax2.legend(['train', 'val'])

plt.show()

''' Now below we learned to utilize transfer learning with Keras's VGG16 model '''

from tensorflow.keras.layers import Input
from tensorflow.keras.applications.vgg16 import VGG16, preprocess_input
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import Model

''' 
We do not keep top layer of the VGG16 imagenet as we're only classifying 10 classes. 
We also use 224 for image dimension because imported model was trained on imagenet dataset that has images with this dimension
'''
base_model = VGG16(weights = 'imagenet', 
                   include_top = False, 
                   input_shape = (32, 32, 3), 
                   pooling = None)

base_model.summary()

# Freeze weights as weights have already been trained of course
for layer in base_model.layers:  
    layer.trainable = False

'''
Now we add a flatten layer, a trainable dense layer, and a final softmax layer. 
This is the Keras functional approach to building networks. 
Supposedly more strong the sequential model and allows for the implementation transfer learning.
'''

x = base_model.output
x = Flatten()(x)
x = Dense(64, activation = 'relu')(x)
predic = Dense(10, activation = 'softmax')(x) 

# And now put this all together to create our new model.
model = Model(inputs = base_model.input, outputs = predic) 
model.summary()

# Compile the model.
model.compile(loss = 'categorical_crossentropy',
              optimizer = RMSprop(lr = 0.001),
              metrics = ['acc'])

'''
As mentioned in docs below, we need to preprocess the image data in the specified way to use this pretrained model.
https://keras.io/api/applications/vgg/#vgg16-function
'''

(X, y), (_, _) = cifar10.load_data()
X = preprocess_input(X)
y = to_categorical(y, 10)

epochs = 20
batchsize = 200

history = model.fit(X, 
                    y,
                    batch_size = batchsize,
                    epochs = epochs, 
                    validation_split = 0.2,
                    verbose = 1)

plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Model Loss')
plt.ylabel('Loss')
plt.xlabel('Epochs')
plt.legend(['train', 'test'])
plt.show()

plt.plot(history.history['acc'])
plt.plot(history.history['val_acc'])
plt.title('Model Accuracy')
plt.ylabel('Accuracy')
plt.xlabel('Epochs')
plt.legend(['train', 'test'])
plt.show()

''' Now I added on to this pretrained model to try and achieve some greater training and validation accuracy for set. '''

base_model = VGG16(weights = 'imagenet', 
                   include_top = False, 
                   input_shape = (32, 32, 3), 
                   pooling = None)

''' Not refreezing the weights does improve training for this set '''

x = base_model.output
x = Flatten()(x)

x = Dense(50, activation = 'relu')(x)

x = Dropout(0.05)(x) #.1

predic = Dense(10, activation = 'softmax')(x) 

model = Model(inputs = base_model.input, outputs = predic) 
model.summary()

opt2a = RMSprop(lr = 0.00001) #.0001

model.compile(loss = 'categorical_crossentropy',
              optimizer = opt2a,
              metrics = ['acc'])

epochs = 20 ### Leave the epochs at 20 ###

batchsize = 200

history = model.fit(X, 
                    y,
                    batch_size = batchsize,
                    epochs = epochs, 
                    validation_split = 0.2,
                    verbose = 1)

fig = plt.figure()
fig.set_size_inches(15, 15)
gs = gridspec.GridSpec(3, 2, figure=fig)

ax1 = fig.add_subplot(gs[0, 0])
ax1.plot(history.history['loss'])
ax1.plot(history.history['val_loss'])
plt.title('Model Loss for validation against training')
ax1.set_ylabel('Loss')
ax1.legend(['train', 'val'])

ax2 = fig.add_subplot(gs[0, 1])
ax2.plot(history.history['acc'])
ax2.plot(history.history['val_acc']) 
plt.title('Model Accuracy for validation against training')
ax2.set_ylabel('Accuracy')
ax2.legend(['train', 'val'])

plt.show()
