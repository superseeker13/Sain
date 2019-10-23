import argparse
import neat
from matplotlib import pyplot as plt

parser = argparse.ArgumentParser(description="Nes bot")
parser.add_argument("-g", "--game", type=str, default="HAI")
parser.add_argument("-n", "--num-steps", type=int, default=10000, help="total number of training steps")
parser.add_argument("-l", "--learn-freq", type=int, default=4, help="number of steps between each training step")
parser.add_argument("--history", action="store_true", help="output previous performance")

#Net variables
learning_rate = 1e-3
batch_size = 64

# Memory addresses one byte values
distance = 0x00
dpad_input = 0x08 
lives = 0x3F

def run():
    # Load configuration.
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(5))
