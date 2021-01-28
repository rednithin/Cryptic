# import os
# os.environ["KERAS_BACKEND"] = "plaidml.keras.backend"
# import plaidml.keras
# plaidml.keras.install_backend()

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Activation, Flatten, LSTM, GRU, Conv1D, Flatten, MaxPooling1D, BatchNormalization, Dropout
from tensorflow.keras.callbacks import TensorBoard, ModelCheckpoint
from tensorflow.keras.optimizers import Adam


def r_lstm_model(window_size, n_inputs, n_outputs):
    model = Sequential()
    model.add(LSTM(32, input_shape=(window_size, n_inputs),
                   activation='tanh', return_sequences=True))
    model.add(LSTM(16, activation='tanh'))
    model.add(Dense(8, activation='tanh'))
    model.add(Dense(4, activation='tanh'))
    model.add(Dense(n_outputs))
    model.compile(optimizer="adam", loss="mse", metrics=['accuracy'])
    return model


def r_gru_model(window_size, n_inputs, n_outputs):
    model = Sequential()
    model.add(GRU(32, input_shape=(window_size, n_inputs),
                  activation='tanh', return_sequences=True))
    model.add(GRU(16, activation='tanh'))
    model.add(Dense(8, activation='tanh'))
    model.add(Dense(4, activation='tanh'))
    model.add(Dense(n_outputs))
    model.compile(optimizer="adam", loss="mse", metrics=['accuracy'])
    return model


def r_conv_model(window_size, n_inputs, n_outputs):
    model = Sequential()
    model.add(Conv1D(64, kernel_size=5))
    model.add(MaxPooling1D(pool_size=3))
    model.add(Flatten())
    model.add(Dense(8, activation='relu'))
    model.add(Dense(4, activation='tanh'))
    model.add(Dense(n_outputs))
    model.compile(optimizer="adam", loss="mse", metrics=['accuracy'])
    return model


def nn(shape, NAME):
    model = Sequential()
    model.add(
        GRU(128, input_shape=shape[1:], return_sequences=True, activation='tanh'))
    model.add(Dropout(0.2))
    model.add(BatchNormalization())

    model.add(
        GRU(128, input_shape=shape[1:], return_sequences=True, activation='tanh'))
    model.add(Dropout(0.1))
    model.add(BatchNormalization())

    model.add(GRU(128, input_shape=shape[1:], activation='tanh'))
    model.add(Dropout(0.2))
    model.add(BatchNormalization())

    model.add(Dense(32, activation='relu'))
    model.add(Dropout(0.2))

    model.add(Dense(2, activation='softmax'))

    opt = Adam(lr=0.001, decay=1e-6)

    model.compile(loss='sparse_categorical_crossentropy',
                  optimizer=opt,
                  metrics=['accuracy'])
    tensorboard = TensorBoard(log_dir=f'logs/{NAME}')

    filepath = "RNN_Final-{epoch:02d}-{val_acc:.3f}"
    checkpoint = ModelCheckpoint(
        "models/{}.model".format(filepath, monitor='val_acc', verbose=1, save_best_only=True, mode='max'))

    print(model.summary)

    return model, tensorboard, checkpoint


def dense_model(input_dim, config):
    model = Sequential()

    model.add(Dense(config["NN"]["num_neurons"],
                    activation=config["NN"]["activation"], input_dim=input_dim))
    model.add(Dense(1))

    model.compile(optimizer=config["NN"]["optimizer"],
                  loss=config["NN"]["loss"],
                  metrics=['mse', 'mae'])
    return model
