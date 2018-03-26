import time
import pandas as pd
import numpy as np

from keras.layers.core import Dense, Activation, Dropout
from keras.layers.recurrent import LSTM
from keras.models import Sequential
from sklearn.metrics import mean_squared_error
from sklearn.utils import shuffle

from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error
epochs = [30, 50, 100, 200]
for epoch in epochs:
    # Load data
    train = pd.read_csv('trips_train_3.csv', header=None)
    test = pd.read_csv('trips_test_2.csv', header=None )
    scaler = MinMaxScaler(feature_range=(-1, 1))
    window_size = 78  # 78 steps in one day
    # normalize features
    scaled = scaler.fit_transform(train.values)
    train = pd.DataFrame(scaled)

    series_s = train.copy()
    for i in range(window_size):
        train = pd.concat([train, series_s.shift(-(i+1))], axis=1)

    train.dropna(axis=0, inplace=True)
    # Hacer lo mismo para los datos de prueba
    test = test.iloc[:24624, :]  # The rest are all 0s
    scaled = scaler.fit_transform(test.values)
    test = pd.DataFrame(scaled)

    series_s = test.copy()
    for i in range(window_size):
        test = pd.concat([test, series_s.shift(-(i+1))], axis = 1)

    test.dropna(axis=0, inplace=True)
    train = shuffle(train)
    train_X = train.iloc[:,:-1]
    train_y = train.iloc[:,-1]
    test_X = test.iloc[:,:-1]
    test_y = test.iloc[:,-1]
    train_X = train_X.values
    train_y = train_y.values
    test_X = test_X.values
    test_y = test_y.values
    train_X = train_X.reshape(train_X.shape[0],train_X.shape[1],1)
    test_X = test_X.reshape(test_X.shape[0],test_X.shape[1],1)

    # Define the LSTM model
    model = Sequential()
    model.add(LSTM(input_shape=(window_size, 1), output_dim=window_size, return_sequences=True))
    model.add(Dropout(0.5))
    model.add(LSTM(256))
    model.add(Dropout(0.5))
    model.add(Dense(1))
    model.add(Activation("linear"))
    model.compile(loss="mse", optimizer="adam")
    model.summary()
    # Train
    start = time.time()
    model.fit(train_X, train_y, batch_size=window_size, epochs=epoch, validation_split=0.1)
    print("> Compilation Time : ", time.time() - start)

    def moving_test_window_preds(n_future_preds):
        ''' n_future_preds - Represents the number of future predictions we want to make
                            This coincides with the number of windows that we will move forward
                            on the test data
        '''
        preds_moving = []                                    # Use this to store the prediction made on each test window
        moving_test_window = [test_X[0,:].tolist()]          # Creating the first test window
        moving_test_window = np.array(moving_test_window)    # Making it an numpy array

        for i in range(n_future_preds):
            preds_one_step = model.predict(moving_test_window) # Note that this is already a scaled prediction so no need to rescale this
            preds_moving.append(preds_one_step[0,0]) # get the value from the numpy 2D array and append to predictions
            preds_one_step = preds_one_step.reshape(1,1,1) # Reshaping the prediction to 3D array for concatenation with moving test window
            moving_test_window = np.concatenate((moving_test_window[:,1:,:], preds_one_step), axis=1) # This is the new moving test window, where the first element from the window has been removed and the prediction  has been appended to the end

        preds_moving = scaler.inverse_transform(np.array(preds_moving).reshape(-1, 1))

        return preds_moving

    preds_moving = moving_test_window_preds(500)
    actuals = scaler.inverse_transform(test_y.reshape(-1, 1))
    mse = mean_squared_error(actuals[74:150], preds_moving[74:150])
    mae = mean_absolute_error(actuals[74:150], preds_moving[74:150])

    # Save data
    with open('f_%s_%s_%s.txt' % (epoch, mse, mae), 'w') as f:
        for i in preds_moving:
            f.write("%s\n" % i)

def moving_test_window_preds(n_future_preds):

    ''' n_future_preds - Represents the number of future predictions we want to make
                         This coincides with the number of windows that we will move forward
                         on the test data
    '''
    preds_moving = []                                    # Use this to store the prediction made on each test window
    moving_test_window = [test_X[0,:].tolist()]          # Creating the first test window
    moving_test_window = np.array(moving_test_window)    # Making it an numpy array

    for i in range(n_future_preds):
        preds_one_step = model.predict(moving_test_window) # Note that this is already a scaled prediction so no need to rescale this
        preds_moving.append(preds_one_step[0,0]) # get the value from the numpy 2D array and append to predictions
        preds_one_step = preds_one_step.reshape(1,1,1) # Reshaping the prediction to 3D array for concatenation with moving test window
        moving_test_window = np.concatenate((moving_test_window[:,1:,:], preds_one_step), axis=1) # This is the new moving test window, where the first element from the window has been removed and the prediction  has been appended to the end

    preds_moving = scaler.inverse_transform(np.array(preds_moving).reshape(-1, 1))

    return preds_moving