import argparse
from matplotlib import pyplot as plt

parser = argparse.ArgumentParser(description="Nes bot")
parser.add_argument("-g", "--game", type=str, default="HAI")
parser.add_argument("-n", "--num-steps", type=int, default=10000, help="total number of training steps")
parser.add_argument("-l", "--learn-freq", type=int, default=4, help="number of steps between each training step")
parser.add_argument("--history", action="store_true", help="output previous performance")

#Net variables
learning_rate = 1e-3
batch_size = 64

#Memory addresses one byte values
distance = 0x00
dpad_input = 0x08 
lives = 0x3F

#From keras docs visalization example
def showHistory() -> void:
    history = model.fit(x, y, validation_split=0.25, epochs=50, batch_size=16)

    # Plot training & validation accuracy values
    plt.plot(history.history['acc'])
    plt.plot(history.history['val_acc'])
    plt.title('Model accuracy')
    plt.ylabel('Accuracy')
    plt.xlabel('Epoch')
    plt.legend(['Train', 'Test'], loc='upper left')
    plt.show()

    # Plot training & validation loss values
    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])
    plt.title('Model loss')
    plt.ylabel('Loss')
    plt.xlabel('Epoch')
    plt.legend(['Train', 'Test'], loc='upper left')
    plt.show()
