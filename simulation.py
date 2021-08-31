# Gravity Simulation Project
# ----------------------------------------------------------------------------------------------------------------------
# This script is responsible for simulating the gravity.

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
import cv2

# Video frames' resolution setting
DPI = 240

# Defining gravitational constant
G = 6.67430e-11

SCALE_MULTIPLIER = 1  # Scale multiplier for the size of simulated bodies
LIMITS_MULTIPLIER = 1.25  # Multiplier of axis' limits


# Function to scale masses for their sizes
def scale_the_array(masses, min_=5 * SCALE_MULTIPLIER, max_=20 * SCALE_MULTIPLIER):
    """
    Function scaling radii of the bodies according to their mass
    :param masses: Numpy array containing masses of the bodies
    :param min_: Float, the minimum size of a body
    :param max_: Float, the maximum size of the body
    :return: Numpy array containing sizes of the bodies
    """
    size = []
    max_mass = masses.max()
    min_mass = masses.min()
    for mass in masses:
        if mass != 0 and max_mass != min_mass:
            calculated_size = ((mass - min_mass) / (max_mass - min_mass)) * (max_ - min_) + min_
            size.append(calculated_size)
        else:  # Default size
            size = [min_, min_]

    return np.array(size)


# Calculating positions of all the bodies after a given time dt
def step(masses, x0, y0, vx0, vy0, dt):
    """
    Function calculating bodies' orbital parameters after a given time dt
    :param masses: Array containing masses of the bodies
    :param x0: Numpy array containing x coordinates of the bodies
    :param y0: Numpy array containing y coordinates of the bodies
    :param vx0: Numpy array containing x components of the velocities of the bodies
    :param vy0: Numpy array containing y components of the velocities of the bodies
    :param dt: Time for which the motion should be calculated
    :return: Tuple of numpy arrays containing bodies' x and y coordinates and their x and y components of velocity
    """

    # Calculating bodies' position after time dt
    x1 = x0 + vx0 * dt
    y1 = y0 + vy0 * dt

    # Creating empty lists for velocities' components
    vx1 = []
    vy1 = []

    # Looping over all the bodies and calculating their velocity after a given timeframe
    for i in range(len(masses)):
        # Setting variables for acceleration's components equal to 0
        a_x = 0
        a_y = 0

        # Looping over all the bodies and adding their acceleration component to body's acceleration
        for j in range(len(masses)):
            if masses[i] == 0 or i == j:
                continue
            x_r = x1[j] - x1[i]
            y_r = y1[j] - y1[i]
            r = (x_r ** 2 + y_r ** 2) ** 0.5

            # Contribution from the jth mass
            a = G * masses[j] / (r * r)
            a_x += a * x_r / r
            a_y += a * y_r / r

        # Appending newly calculated velocities to velocities' lists
        vx1.append(vx0[i] + a_x * dt)
        vy1.append(vy0[i] + a_y * dt)

    return x1, y1, np.array(vx1), np.array(vy1)


def plot(df, num_of_bodies):
    """
    Function plotting the graph of the motion of the bodies
    :param df: Pandas dataframe containing time in the 0 column, x and y coordinates of every body in the 1 column and
    2 column respectively
    :param num_of_bodies: Amount of bodies for which to plot the graph
    :return: None
    """
    fig = plt.figure()
    ax = fig.add_subplot()
    for i in range(num_of_bodies):
        x = []
        y = []
        for j in range(len(df)):
            x.append(df.iloc[j][1][i])
            y.append(df.iloc[j][2][i])
        x = np.array(x)
        y = np.array(y)
        plt.plot(x, y, linewidth=0.8)
    ax.set_aspect('equal', adjustable='box')
    plt.savefig('./temp/plot.png', dpi=800, bbox_inches='tight')


def save_to_video(app, video_path='./temp/simulation.avi', frames_path='./temp/frames/', fps=30):
    """
    Function creating a video from frames
    :param app: tkinter.Tk() class object, GUI app calling the function
    :param video_path: String, path to which the video should be saved
    :param frames_path: String, path where the frames needed for the video are stored
    :param fps: Integer, amount of frames per seconds in which the simulation will be played
    :return: None
    """
    print('\nVideo processing started')
    app.update_status('Video processing started')
    frame_array = []
    files = [f for f in os.listdir(frames_path) if os.path.isfile(os.path.join(frames_path, f))]
    # For sorting the file names properly
    files.sort(key=lambda x: int(x[:-4]))
    frames_count = len(files)
    for i in range(frames_count):
        percent = int(round((i + 1) * 100 / frames_count, 0))
        app.update_progress_bar(percent)
        app.update_status(f'Reading frame {i + 1} out of {frames_count} - {percent}%')
        filename = frames_path + files[i]
        # Reading each file
        img = cv2.imread(filename)
        height, width, layers = img.shape
        size = (width, height)
        # Inserting the frames into an image array
        frame_array.append(img)
    print('Creating the video')
    app.update_status('Creating the video')
    out = cv2.VideoWriter(video_path, cv2.VideoWriter_fourcc(*'DIVX'), fps, size)
    for i in range(len(frame_array)):
        # Writing to a image array
        out.write(frame_array[i])
    out.release()
    print('Video saved')
    app.update_status('Video saved')


def main(app, masses, x0s, y0s, vx0s, vy0s, length, samples, frames=0, plot_graph=True):
    """
    Function responsible for running the whole simulation and updating the GUI
    :param app: tkinter.Tk() class object, GUI app calling the function
    :param masses: Numpy array, masses of the bodies
    :param x0s: Numpy array, X starting coordinates of the bodies
    :param y0s: Numpy array, Y starting coordinates of the bodies
    :param vx0s: Numpy array, X starting velocities' components of the bodies
    :param vy0s: Numpy array, Y starting velocities' components of the bodies
    :param length: Float, length of the simulation in seconds
    :param samples: Integer, amount of samples
    :param frames: Integer, amount of frames (0 if you do not want to create a video)
    :param plot_graph: Boolean, True if a graph should be plotted, False otherwise
    :return: None
    """
    app.update_progress_bar(0)
    df = pd.DataFrame([[0, x0s, y0s]])    # columns=['T+', 'x', 'y']
    dt = int(round(length / samples, 0))
    t = 0
    xs = x0s
    ys = y0s
    vxs = vx0s
    vys = vy0s
    if frames != 0:  # Preparing for video creation
        limits = max(abs(xs).max(), abs(ys).max()) * LIMITS_MULTIPLIER
        app.update_status("Scaling the array, preparing frames' plotting")
        print('Scaling the array, preparing plot\n')
        freq = samples // frames
        scaled_masses = scale_the_array(masses)
        fig = plt.figure(figsize=(5, 5))
        ax = fig.add_subplot()
        ax.set_aspect('equal')
        plt.clf()
    previous_percent = 0
    for sample in range(samples):  # Looping over all the samples
        percent = (sample + 1) * 100 // samples  # Updating the status and progress bar
        if percent != previous_percent:
            app.update_progress_bar(percent)
            previous_percent = percent
        app.update_status(f'Sample {sample + 1} out of {samples} - {percent}%')
        print(f'Sample {sample + 1} out of {samples} - {percent}%')
        xs, ys, vxs, vys = step(masses, xs, ys, vxs, vys, dt)  # Calculating new velocities and positions of the bodies
        if frames != 0 and sample % freq == 0:  # Creating a frame
            print('Creating a frame')
            for i in range(len(masses)):
                plt.scatter(xs[i], ys[i], s=scaled_masses[i],
                            c='r' if scaled_masses[i] == scaled_masses.max() else None)
            plt.axis([-limits, limits, -limits, limits])
            plt.savefig(f'./temp/frames/{t}.tif', bbox_inches='tight', dpi=DPI)
            plt.clf()
        t += dt  # Incrementing the time
        df = df.append([[t, xs, ys, vxs, vys]])  # Appending data to a dataframe
    print('\nSampling done')
    app.update_status('Sampling done')
    if plot_graph:
        print('\nPlotting the graph')
        app.update_status('Plotting the graph')
        plot(df, len(masses))
    if frames != 0:
        save_to_video(app)
    print('\nSaving data into a csv file')
    app.update_status('Saving data into a csv file')
    df.to_csv('./temp/positions.csv', mode='a', index=False, header=False)
    print('Done')
