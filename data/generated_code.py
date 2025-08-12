from keras.models import Sequential
from keras.layers import LSTM, Dense

def create_model(input_shape):
    """
    Create a simple LSTM model.
    :param tuple input_shape: Tuple representing the shape of input (timesteps, features)
    :return: Keras model instance
    """
    model = Sequential()
    model.add(LSTM(50, input_shape=input_shape))  # 50 units in LSTM layer
    model.add(Dense(1))  # output layer with 1 unit

    # compile the model with appropriate loss function, optimizer and metrics
    model.compile(loss='mean_squared_error', optimizer='adam', metrics=['accuracy'])

    return model

# usage: create_model((100, 1))