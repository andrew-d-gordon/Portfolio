
'''This data contains features describing posts from a cosmetic brand's Facebook page. The authors use the following features: 

* Category,
* Page total likes: Number of people who have liked the company's page), 
* Type: Type of content (Link, Photo, Status, Video), 
* Post month: Month the post was published (January, February, March, …, December), 
* Post hour: Hour the post was published (0, 1, 2, 3, 4, …, 23) , 
* Post weekday: Weekday the post was published (Sunday, Monday, …,
Saturday) , 
* Paid: If the company paid to Facebook for advertising (yes, no)

to model: 

'Lifetime Post Total Reach', 'Lifetime Post Total Impressions', 'Lifetime Engaged Users', 'Lifetime Post Consumers',
'Lifetime Post Consumptions', 'Lifetime Post Impressions by people who have liked your Page', 'Lifetime Post reach by people who like your Page', 'Lifetime People who have liked your Page and engaged with your post', 'comment', 'like', 'share', 'Total Interactions'.

There are many possible features we could try to model, but we will focus on 'Total Interactions'. Our feature space will include: Category, Page total likes, Post month, Post hour, Post weekday, and Paid. We drop "Type" simply to avoid preprocessing.

You can read more about the dataset [here](http://archive.ics.uci.edu/ml/datasets/Facebook+metrics). '''

### Downloading the data

!wget http://archive.ics.uci.edu/ml/machine-learning-databases/00368/Facebook_metrics.zip -O ./Facebook_metrics.zip
import zipfile
with zipfile.ZipFile('./Facebook_metrics.zip', 'r') as zip_ref:
    zip_ref.extractall('./')

"""### Reading in data"""

import pandas as pd
import numpy as np
np.random.seed(144)
'''
Shuffles the data in place 
'''
def shuffle_data(data):
    np.random.shuffle(data)

# Read in the data
lr_dataframe = pd.read_csv('dataset_Facebook.csv',sep=';')
lr_dataframe.dropna(inplace=True)
columns_to_drop = ['Type','Lifetime Post Total Reach', 'Lifetime Post Total Impressions',
       'Lifetime Engaged Users', 'Lifetime Post Consumers',
       'Lifetime Post Consumptions',
       'Lifetime Post Impressions by people who have liked your Page',
       'Lifetime Post reach by people who like your Page',
       'Lifetime People who have liked your Page and engaged with your post',
       'comment', 'like', 'share']
lr_dataframe.drop(columns=columns_to_drop,inplace=True)

# Normalizing all remaining columns
def normalize_col(col):
    return (col - col.min())/(col.max() - col.min())
  
lr_dataframe = lr_dataframe.apply(normalize_col)

# Get entries as a numpy array
lr_data = lr_dataframe.values[:, :]

# Shuffle once for reproducibility
shuffle_data(lr_data)

lr_dataframe.head()

"""### Splitting data into X and Y"""

def bias_trick(X):
    onesCol = np.ones((X.shape[0],1))
    return np.hstack((onesCol, X))

'''
Separates feature vectors and targets 
Takes raw data
Returns X as the matrix of feature vectors and Y as the vector of targets 
'''
def separate_data(data):
     
      X_data = data[:, :-1]
      y_data = data[:,-1]

      return bias_trick(X_data), y_data

'''
Takes raw data in and splits the data into 
X_train, y_train, X_test, y_test
Returns X_train, y_train, X_test, y_test 
'''
def train_test_split(data, train_size=.80):
    X_data, y_data = separate_data(data)

    train_rows = int(np.around(train_size*X_data.shape[0]))
    test_rows = int(np.around((1-train_size)*y_data.shape[0]))

    X_train = X_data[:train_rows]
                     
    y_train = y_data[:train_rows]
                     
    X_test = X_data[(0-test_rows):]
                    
    y_test = y_data[(0-test_rows):]

    '''
    print(X_train.shape)
    print(X_test.shape)
    print(y_train.shape)
    print(y_test.shape)
    '''
    
    return X_train, y_train, X_test, y_test

"""### Training and testing our model"""

'''
Takes the target values and predicted values and calculates the squared error 
between them 
'''
def mse(y_pred, y_true):
    n = len(y_pred)
    return 0.5 * (1/n) * np.sum((y_true - y_pred)**2)

'''
Implementation of the derivative of MSE.
Returns a vector of derivations of loss with respect to each of the dimensions
[\partial loss / \partial \theta_j]
'''
def mse_derivative(X,y,theta):
    y_pred = np.matmul(X, theta)
    n = len(X)
    return 1/n * np.matmul((y_pred - y), X)

'''
Gradient descent step. 
Takes X, y, theta vector, and alpha. 
Returns an updated theta vector.
'''
def gradient_descent_step(X, y, theta, alpha):

    y_pred = np.matmul(X, theta)

    theta = theta - alpha * mse_derivative(X, y, theta)

    return theta

def linear_regression(data, num_epochs=30000, alpha=0.00005):
    # Get training and testing set by calling train_test_split()
    X_train, y_train, X_test, y_test = train_test_split(lr_data)

    # Record training and test errors in lists
    train_errors = []
    test_errors = []

    # Define theta
    theta = np.zeros((X_train.shape[1]))

    # Carry out training loop
    for i in range(num_epochs):
        train_error = mse(np.matmul(X_train, theta), y_train)
        train_errors.append(train_error)

        test_error = mse(np.matmul(X_test, theta), y_test)
        test_errors.append(test_error)

        # Do gradient descent on the training set
        theta = gradient_descent_step(X_train, y_train, theta, alpha)
    return theta, train_errors, test_errors

# Carry out training task
theta_final, train_errors, test_errors = linear_regression(lr_data)

# Plot the training error and test error for different epochs (iterations of the
# algorithm). Your plot be MSE error vs epochs.

import matplotlib.pyplot as plt
plt.xlabel("Number of Epochs")
plt.ylabel("MSE Error")

largestMSE = max(train_errors)
if largestMSE < max(test_errors):
    largestMSE = max(test_errors)

plt.axis([0, len(test_errors), 0, largestMSE+.0001])

plt.plot(train_errors, "b", label = "train_errors")
plt.plot(test_errors, "r", label = "test_errors")
plt.legend()
plt.show()

### Fitting non-linear data

import numpy as np
import matplotlib.pyplot as plt

def normalize_data(data):
    return (data - np.min(data))/(np.max(data) - np.min(data))

np.random.seed(33)
x = np.random.uniform(-10, 10, 1000)
poly_coeffs = np.random.uniform(-1,1, size=(4,1))
y = poly_coeffs[0] + poly_coeffs[1]*x + poly_coeffs[2]*(x ** 2) + poly_coeffs[3]*(x ** 3) + np.random.normal(0, 250, 1000)

x2 = np.random.uniform(-10, 10, 1000)
poly_coeffs = np.random.uniform(-1,1, size=(3,1))
y2 = poly_coeffs[0] - 2000 + poly_coeffs[1]*x2 + 50*poly_coeffs[2]*(x2 ** 2)  + np.random.normal(0, 250, 1000)

x = np.concatenate([x,x2])
y = np.concatenate([y,y2])
x = normalize_data(x)
y = normalize_data(y)

plt.scatter(x,y, s=10)
plt.show()

poly_data = np.hstack((x.reshape(-1,1),y.reshape(-1,1)))
np.random.shuffle(poly_data)
x = poly_data[:,0]
y = poly_data[:,1]

import numpy as np
from sklearn.linear_model import LinearRegression

reg = LinearRegression().fit(x.reshape(-1,1), y)

def compute_line_from_regr(X_data, y_data, regr):
    l_bound = np.min(X_data)
    r_bound = np.max(X_data)
    return [l_bound, r_bound], [l_bound * regr.coef_ + regr.intercept_, r_bound * regr.coef_ + regr.intercept_]

plt.scatter(x,y, s=10)
line_x, line_y = compute_line_from_regr(x.reshape(-1,1),y,reg)
plt.plot(line_x, line_y, color='r')
plt.show()

def bias_trick2(X):
    #print("X.shape pre bias", X.shape)
    onesCol = np.ones_like(X)
    #print("Ones column.shape for bias", onesCol.shape)
    #print(np.column_stack((onesCol, X)))
    return np.column_stack((onesCol, X))

def separate_data2(data):
      X_data = data[:,0]
      y_data = data[:,1]
      return bias_trick2(X_data), y_data

def train_test_validation_split(data, test_size=.20, validation_size=.20):
    X_data, y_data = separate_data2(data)

    #X_data, y_data = separate_data(data)
    #print("X.shape after bias ", X_data.shape)
    #print("Y.shape after separation", y_data.shape)

    train_rows = int(np.around((1-test_size-validation_size)*X_data.shape[0]))
    test_rows = int(np.around((test_size)*y_data.shape[0]))
    val_rows = int(np.around((validation_size)*X_data.shape[0]))

    X_train = X_data[:train_rows]
    X_test = X_data[(0-test_rows):]
    X_val = X_data[(0-test_rows-val_rows):(0-test_rows)]

    y_train = y_data[:train_rows]           
    y_test = y_data[(0-test_rows):]
    y_val = y_data[(0-test_rows-val_rows):(0-test_rows)]

    '''
    print(X_train.shape)
    print(X_test.shape)
    print(X_val.shape)
    print()
    print(y_train.shape)
    print(y_test.shape)
    print(y_val.shape)
    '''

    return X_train, y_train, X_test, y_test, X_val, y_val

'''
Adds columns to increase data up to the specified degree.
'''
def add_polycols(X,degree):
    x_col = X[:,-1]

    for i in range(2, degree+1):
        X = np.hstack((X,(x_col**i).reshape(-1,1)))
    return X

'''
Takes the target values and predicted values and calculates the absolute error 
between them
'''
def mse(y_pred, y_true):
    n = len(y_pred)
    '''print("y_pred shape, mse", y_pred.shape)
    print("y_true shape, mse", y_true.shape)'''
    return 0.5 * (1/n) * np.sum((y_pred - y_true)**2)

'''
Implementation of the derivative of MSE.
Returns a vector of derivations of loss with respect to each of the dimensions
[\partial loss / \partial \theta_i]
'''
def mse_derivative(X,Y,theta):
    y_pred = np.matmul(X**2, theta)
    n = len(X)
    '''print("y_pred shape, mse_d", y_pred.shape)
    print("y shape, mse_d", Y.shape)
    print("X shape, mse_d", X.shape)'''
    return 1/n * np.matmul((y_pred - Y), X)

'''
Computes L2 norm from theta scaled by lambda.
Returns a scalar L2 norm.
'''
def l2norm(theta, lamb):
    return lamb * np.sum(theta[1:]**2)

'''
Computes derivative of L2 norm scaled by lambda.
Returns a vector of derivative of L2 norms.
'''
def l2norm_derivative(theta, lamb):
    # no regularization on the bias term.
    return 2*lamb*theta

'''
Computes total cost (cost function + regularization term)
'''
def compute_cost(X, Y, theta, lamb):

    return mse(np.matmul(X**2,theta), Y) + l2norm(theta, lamb)

'''
Gradient descent step. 
Takes X, y, theta vector, and alpha. 
Returns an updated theta vector.
'''
def gradient_descent_step(X, y, theta, alpha, lamb):
    
    theta = theta - alpha * (mse_derivative(X, y, theta.copy()) + l2norm_derivative(theta.copy(), lamb))

    return theta


def polynomial_regression(data, degree, num_epochs=100000, alpha=1e-4, lamb=0):
    # Get training, testing, and validation sets by calling train_test_validation_split()
    X_train, y_train, X_test, y_test, X_val, y_val = train_test_validation_split(data)

    # Record training and validation errors in lists
    train_errors = []
    val_errors = []

    # Add the appropriate amount of columns to each of your sets of data.
    X_train = add_polycols(X_train, degree)
    X_val = add_polycols(X_val, degree)
    X_test = add_polycols(X_test, degree)

    # Define theta
    theta = np.zeros((X_train.shape[1]))

    # Carry out training loop
    for i in range(num_epochs):
        train_error = compute_cost(X_train, y_train, theta.copy(), lamb)
        train_errors.append(train_error)

        val_error = compute_cost(X_val, y_val, theta.copy(), lamb)
        val_errors.append(val_error)
        
        # Do gradient descent on the training set
        theta = gradient_descent_step(X_train, y_train, theta, alpha, lamb)

        # This prints the validation loss
        if i % (num_epochs//10) == 0:
            print(f'({i} epochs) Training loss: {train_error}, Validation loss: {val_error}') 
    print(f'({i} epochs) Final training loss: {train_error}, Final validation loss: {val_error}') 
    
    # Compute the testing loss
    test_error = compute_cost(X_test, y_test, theta.copy(), lamb)
    print(f'Final testing loss: {test_error}')
    return theta, train_errors, val_errors

"""As we mentioned above, we use the validation set's loss to tweak our hyperparameters. Carrying out the training task while monitoring the validation loss and varying the polynomial order $d$ and regularization constant $\lambda$. """

# degree d
polynomial_order = 8

# regularization constant lambda
regularization_param = 0.0001

theta, train_errors, val_errors = polynomial_regression(poly_data, polynomial_order, lamb=regularization_param, num_epochs=100000, alpha=1e-4)

#I will note this set up of polynomial order and lambda gives me my lowest losses, alternate setup with bit more loss but maybe a visually "better fit" line is with p_order=6, lambda = .08

# Call plot_results() to see how your polynomial fits.
def plot_results(theta, X, Y):
    y_hat = sum([t*X**i for i,t in enumerate(theta)])
    plt.scatter(X, y_hat, s=10, color='r')
    plt.scatter(X, Y, s=10)
    plt.show()

plot_results(theta, x, y)
