import os
import matplotlib.pyplot as plt
import numpy as np
import keras
from sklearn.model_selection import train_test_split

from DataAugmentation import DataAugmentation
from ModelPrediction import ModelPrediction
from ModelTraining import ModelTraining
from ResultAnalysis import ResultAnalysis


class ModelPipeline:
    def __init__(self):
        pass

    # This method will receive the dataset and annotate them with numbers
    def prepareAnnotation(self):
        data_dir = input("Please enter the dataset path (eg:/home/aswin/PycharmProjects/HandGestureClassification"
                         "/depthGestRecog/depthGestRecog): ")
        label_dict = dict()

        for label in os.listdir(data_dir):
            for sub_dir in os.listdir(os.path.join(data_dir, label)):
                for i in range(0,len(os.listdir(os.path.join(data_dir, label, sub_dir)))):
                    class_num = int(os.listdir(os.path.join(data_dir, label, sub_dir))[i][5:7])

            label_dict[label] = class_num

        print(label_dict)
        return data_dir

    # This method will prepare formatted X and Y for CNN
    def prepareData(self, data_dir):
        x = []
        y = []
        dataset = 0
        for root, _, files in os.walk(data_dir):
            for i in range(len(files)):
                x.append((plt.imread((os.path.join(root, files[i])))))
                y.append((int(files[i][5:7])))
                dataset = dataset + 1

        x = np.asarray(x, dtype=np.float32)
        y = np.asarray(y)
        x_visualize = x

        # Reshaping and converting y to one hot vector
        y = y.reshape(dataset, 1)
        y = keras.utils.to_categorical(y)
        x = x.reshape((dataset, 100, 100, 1))
        x = x / 255
        return x, y, x_visualize

    # This method will visualize the np array image
    def visualizeImage(self, image):

        f, axarr = plt.subplots()
        f.suptitle("Raw Hand image with Depth ", fontsize=16)
        axarr.imshow(image)
        axarr.set_title("")
        plt.show()

    # This method will split the data set 80-10-10
    def splitData(self, x, y):
        x_train, x_split, y_train, y_split = train_test_split(x, y, test_size=0.2)
        x_validate, x_test, y_validate, y_test = train_test_split(x_split, y_split, test_size=0.5)
        return x_train, x_validate, y_train, y_validate,x_test,y_test


# Pre Processing and Data set preparation
model_pipeline = ModelPipeline()
data_dir = model_pipeline.prepareAnnotation()
x, y, x_visualize = model_pipeline.prepareData(data_dir)
data_augmentation = DataAugmentation()

# Visualize the data set and Augmentation
model_pipeline.visualizeImage(x_visualize[0])
data_augmentation.rotateImage(x_visualize[100])
data_augmentation.translateImage(x_visualize[200])


# Train and validation data for CNN
x_train,x_validate,y_train,y_validate,x_test,y_test = model_pipeline.splitData(x,y)



# Model Training
model_training = ModelTraining()
history=model_training.trainCNNModel(x_train,y_train,x_validate,y_validate,x_test,y_test)


# Model Prediction
model_prediction = ModelPrediction()
model_prediction.LoadModelandPredict(x_test,y_test)


# Result Analysis
result_analysis = ResultAnalysis()
result_analysis.plotAccuracy(history)
result_analysis.plotLoss(history)
