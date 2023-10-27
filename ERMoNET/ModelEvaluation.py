import warnings
warnings.filterwarnings("ignore")
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
import matplotlib.pyplot as plt
plt.style.use('ggplot')

class ModelEvaluation:
    def __init__(self):
        pass

    def calculateMLModelScores(self,model_name,y_test,y_pred):
        print(model_name+" F1score=" + str(f1_score(y_test, y_pred, average="macro")))
        print(model_name+" Precision=" + str(precision_score(y_test, y_pred, average="macro")))
        print(model_name+" Recall=" + str(recall_score(y_test, y_pred, average="macro")))
        return True


    def plot_history(self,history):
        acc = history.history['acc']
        val_acc = history.history['val_acc']
        loss = history.history['loss']
        val_loss = history.history['val_loss']
        x = range(1, len(acc) + 1)

        plt.figure(figsize=(12, 5))
        plt.subplot(1, 2, 1)
        plt.plot(x, acc, 'b', label='Training acc')
        plt.plot(x, val_acc, 'r', label='Validation acc')
        plt.title('Training and validation accuracy')
        plt.legend()
        plt.subplot(1, 2, 2)
        plt.plot(x, loss, 'b', label='Training loss')
        plt.plot(x, val_loss, 'r', label='Validation loss')
        plt.title('Training and validation loss')
        plt.legend()
        return True

