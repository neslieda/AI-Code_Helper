from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM

# Initialize the constructor
model = Sequential()

# Add an input layer and LSTM layer
# 100 represents the dimensionality of the output space
model.add(LSTM(100, input_shape=(timesteps, input_dim)))

# Add an output layer 
model.add(Dense(1, activation='sigmoid'))

# Compile the model
model.compile(loss='binary_crossentropy',
              optimizer='adam',
              metrics=['accuracy'])