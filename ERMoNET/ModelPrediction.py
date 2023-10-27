from keras.models import model_from_json

class ModelPrediction:
    def __init__(self):
        pass
    def LoadModelandPredict(self,x_test,y_test):
        # load json and create model
        json_file = open('models/model.json', 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        loaded_model = model_from_json(loaded_model_json)
        # load weights into new model
        loaded_model.load_weights("models/model.h5")
        print("Loaded model from models sub folder")

        # evaluate loaded model on test data
        loaded_model.compile(loss='categorical_crossentropy', optimizer='rmsprop', metrics=['accuracy'])
        score = loaded_model.evaluate(x_test, y_test, verbose=0)
        print("%s: %.2f%%" % (loaded_model.metrics_names[1], score[1] * 100))