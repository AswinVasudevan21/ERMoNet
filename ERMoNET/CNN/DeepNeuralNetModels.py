import warnings
warnings.filterwarnings("ignore")
from ModelEvaluation import ModelEvaluation
import keras.models as models
import keras.layers as layers

class DeepNeuralNetModels:
    def __init__(self):
        pass

    def trainDenseNets(self,X_train,y_train,X_test,y_test):
        model_eval =ModelEvaluation()
        input_dim = X_train.shape[1]  # Number of features
        model = models.Sequential()
        model.add(layers.Dense(10, input_dim=input_dim, activation='relu'))
        model.add(layers.Dense(1, activation='sigmoid'))

        model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

        history = model.fit(X_train, y_train, epochs=1, verbose=False, validation_data=(X_test, y_test), batch_size=10)
        model_eval.plot_history(history)

        loss, accuracy = model.evaluate(X_train, y_train, verbose=False)
        print("Training Accuracy: {:.4f}".format(accuracy))
        loss, accuracy = model.evaluate(X_test, y_test, verbose=False)
        print("Testing Accuracy:  {:.4f}".format(accuracy))
        return True

    def trainDeepModelOnEmbeddings(self,X_train,y_train,X_test,y_test):
        model_eval = ModelEvaluation()
        embedding_dim = 50
        input_dim = X_train.shape[1]

        model = models.Sequential()
        model.add(layers.Embedding(input_dim=input_dim,
                                   output_dim=embedding_dim,
                                   input_length=None))
        model.add(layers.GlobalMaxPool1D())
        model.add(layers.Dense(10, activation='relu'))
        model.add(layers.Dense(1, activation='sigmoid'))
        model.compile(optimizer='adam',
                      loss='binary_crossentropy',
                      metrics=['accuracy'])
        model.summary()

        history = model.fit(X_train, y_train,
                            epochs=1,
                            verbose=False,
                            validation_data=(X_test, y_test),
                            batch_size=10)
        loss, accuracy = model.evaluate(X_train, y_train, verbose=False)
        print("Training Accuracy: {:.4f}".format(accuracy))
        loss, accuracy = model.evaluate(X_test, y_test, verbose=False)
        print("Testing Accuracy:  {:.4f}".format(accuracy))
        model_eval.plot_history(history)
        return True

    def trainCNNModelOnEmbeddings(self,X_train,y_train,X_test,y_test):
        model_eval=ModelEvaluation()
        embedding_dim = 100
        input_dim = X_train.shape[1]
        model = models.Sequential()
        model.add(layers.Embedding(input_dim, embedding_dim, input_length=None))
        model.add(layers.Conv1D(128, 5, activation='relu'))
        model.add(layers.GlobalMaxPooling1D())
        model.add(layers.Dense(10, activation='relu'))
        model.add(layers.Dense(1, activation='sigmoid'))
        model.compile(optimizer='adam',
                      loss='binary_crossentropy',
                      metrics=['accuracy'])
        model.summary()

        history = model.fit(X_train, y_train,
                            epochs=1,
                            verbose=False,
                            validation_data=(X_test, y_test),
                            batch_size=10)
        loss, accuracy = model.evaluate(X_train, y_train, verbose=False)
        print("Training Accuracy: {:.4f}".format(accuracy))
        loss, accuracy = model.evaluate(X_test, y_test, verbose=False)
        print("Testing Accuracy:  {:.4f}".format(accuracy))
        model_eval.plot_history(history)
        return True

