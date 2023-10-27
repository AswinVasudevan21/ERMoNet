import keras
from keras import layers
from keras import models


class ModelTraining:

    def __init__(self):
        pass

    # Training the data set on CNN network
    def trainCNNModel(self, x_train, y_train, x_validate, y_validate, x_test, y_test):
        model = models.Sequential()
        model.add(layers.Conv2D(32, (5, 5), strides=(2, 2), activation='relu', input_shape=(100, 100, 1)))
        model.add(layers.MaxPooling2D((2, 2)))
        model.add(layers.Conv2D(64, (3, 3), activation='relu'))
        model.add(layers.MaxPooling2D((2, 2)))
        model.add(layers.Conv2D(64, (3, 3), activation='relu'))
        model.add(layers.MaxPooling2D((2, 2)))
        model.add(layers.Flatten())
        model.add(layers.Dense(128, activation='relu'))
        model.add(layers.Dense(12, activation='softmax'))

        model.compile(optimizer='rmsprop',
                      loss='categorical_crossentropy',
                      metrics=['accuracy'])
        history = model.fit(x_train, y_train, epochs=30, batch_size=64, verbose=1,
                            validation_data=(x_validate, y_validate))

        [loss, acc] = model.evaluate(x_test, y_test, verbose=1)
        print("Results on Test dataset:")
        print("Loss:" + str(loss))
        print("Accuracy:" + str(acc))

        # serialize model to JSON
        model_json = model.to_json()
        with open("model.json", "w") as json_file:
            json_file.write(model_json)
        # serialize weights to HDF5
        model.save_weights("model.h5")
        print("Saved model to disk")

        return history
