# Description: Main file to run the simulation
from imports import *
from functions import run_simulation

def main():

    file_path = 'Networks/Barcelona/Barcelona_network.csv'
    iterations = 10000
    alpha = 0.1

    run_simulation(file_path, iterations, alpha)

if __name__ == "__main__":
    main()
