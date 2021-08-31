# Gravity Simulation Project
# ----------------------------------------------------------------------------------------------------------------------
# This script is responsible for showing and loading scenarios into the simulator.

import numpy as np
import os

DEFAULT_PATH = './scenarios/default/'


def get_scenarios(path=DEFAULT_PATH):
    """
    Function reading all the scenarios' names
    :param path: Path of the scenarios
    :return: List containing all the available scenarios
    """
    output = []
    files = os.listdir(path)
    for file in files:
        if file.endswith('.txt'):
            output.append(file)
    return np.array(output)


def show_scenario(name, path=DEFAULT_PATH):
    """
    Function outputting all the information about a given scenario
    :param name: String, name of the scenario ending with '.txt'
    :param path: String, directory where the scenario is located
    :return: Numpy array of floats and numpy arrays
    """
    print(f'Showing scenario "{name}"')
    file = open(path + name, mode='r').readlines()
    timeframe = file[0][:-1]
    samples = file[1][:-1]
    frames = file[2][:-1]
    names = []
    masses = []
    x0s = []
    y0s = []
    vx0s = []
    vy0s = []
    current_line = 3
    while True:
        try:
            if file[current_line][0] == '!':
                names.append(file[current_line][1:])
                masses.append(float(file[current_line + 1]))
                x0s.append(float(file[current_line + 2]))
                y0s.append(float(file[current_line + 3]))
                vx0s.append(float(file[current_line + 4]))
                vy0s.append(float(file[current_line + 5]))
                current_line += 6
            else:
                current_line += 1
        except IndexError:
            break
    return timeframe, samples, frames, np.array(names), np.array(masses), np.array(x0s), np.array(y0s),\
        np.array(vx0s), np.array(vy0s)


def load_scenario(name, path=DEFAULT_PATH):
    """
    Function outputting all the information about a scenario needed to run the simulation
    :param name: String, name of the scenario ending with '.txt'
    :param path: String, directory where the scenario is located
    :return: Numpy array of numpy arrays
    """
    print(f'Loading scenario "{name}"')
    file = open(path + name, mode='r').readlines()
    masses = []
    x0s = []
    y0s = []
    vx0s = []
    vy0s = []
    current_line = 3
    while True:
        try:
            if file[current_line][0] == '!':
                masses.append(float(file[current_line + 1]))
                x0s.append(float(file[current_line + 2]))
                y0s.append(float(file[current_line + 3]))
                vx0s.append(float(file[current_line + 4]))
                vy0s.append(float(file[current_line + 5]))
                current_line += 6
            else:
                current_line += 1
        except IndexError:
            break
    return np.array(masses), np.array(x0s), np.array(y0s), np.array(vx0s), np.array(vy0s)
