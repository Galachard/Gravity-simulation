# Gravity Simulation Project
# ----------------------------------------------------------------------------------------------------------------------
# This script is the one that should be ran in order to run the program. It is responsible for the whole GUI.

import sys
import subprocess
import simulation
import scenarios
import os
import time
import tkinter as tk
from tkinter import ttk
from shutil import rmtree

HEIGHT = 600
WIDTH = 800

YEAR = 31557600
DAY = 86400

TEMP_PATH = os.path.dirname(os.path.abspath(__file__)) + '/temp'

is_calculating = False

scenario = None

# Creating a function that opens a given directory (by default the '/temp' directory) in the default file explorer of
# the user's operating system
if sys.platform == 'darwin':
    def open_folder(path=TEMP_PATH):  # I don't own a MacOS device so I couldn't check if this works
        subprocess.check_call(['open', '--', path])
    os_identified = True
elif sys.platform == 'linux' or 'linux2':
    def open_folder(path=TEMP_PATH):
        subprocess.check_call(['xdg-open', path])
    os_identified = True
elif sys.platform == 'win32':
    def open_folder(path=TEMP_PATH):
        subprocess.check_call(['explorer', path])
    os_identified = True
else:
    os_identified = False


def is_int(string):
    try:
        int(string)
    except ValueError:
        return False
    return True


def is_float(string):
    try:
        float(string)
    except ValueError:
        return False
    return True


class Application(tk.Frame):
    def __init__(self, master=None):
        """
        Method initializing an Application class object
        :param master: tk.Tk() object
        """
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()

        # Protocol preventing the user from closing the application without terminating all the processes
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        """
        Method creating all the widgets
        """
        self.canvas = tk.Canvas(self.master, height=HEIGHT, width=WIDTH)
        self.canvas.pack()

        self.scenario_choice = tk.Button(self.master, text="Choose scenario", font=40, command=lambda:
                                         self.choose_scenario())
        self.scenario_choice.place(relx=0.15, rely=0.2, relheight=0.1, relwidth=0.3)

        self.scenario_create = tk.Button(self.master, text="Create scenario\n(Still in development)", font=40,
                                         command=lambda: self.choose_scenario())
        self.scenario_create.place(relx=0.55, rely=0.2, relheight=0.1, relwidth=0.3)

        self.chosen = tk.StringVar()
        self.chosen.set(f'Scenario: {scenario}')
        self.chosen_label = tk.Label(self.master, textvariable=self.chosen, font=80)
        self.chosen_label.place(relx=.5, rely=.4, anchor='center')

        self.length = tk.Label(self.master, text='Length of the animation\n Years - Days - Seconds')
        self.length.place(relx=.5, rely=.6, anchor='center')

        self.seconds = tk.Entry(self.master)
        self.seconds.place(relx=0.8, rely=.65, anchor='center')
        self.days = tk.Entry(self.master)
        self.days.place(relx=0.5, rely=.65, anchor='center')
        self.years = tk.Entry(self.master)
        self.years.place(relx=0.2, rely=.65, anchor='center')

        self.samples = tk.Label(self.master, text='Samples\n(has to be a multiple of frames if frames != 0)')
        self.samples.place(relx=.3, rely=.75, anchor='center')
        self.samples_ent = tk.Entry(self.master)
        self.samples_ent.place(relx=0.3, rely=.8, anchor='center')

        self.frames = tk.Label(self.master, text='Frames\n(0 if you do not want to create a video)')
        self.frames.place(relx=.7, rely=.75, anchor='center')
        self.frames_ent = tk.Entry(self.master)
        self.frames_ent.place(relx=0.7, rely=.8, anchor='center')

        self.run_button = tk.Button(self.master, text="Run the simulation", font=40, command=lambda:
                                    self.run_simulation())
        self.run_button.place(relx=0.5, rely=0.9, relheight=0.1, relwidth=0.4, anchor='center')

        self.bar = ttk.Progressbar(self.master, length=100, mode='determinate')
        self.bar.place(relx=.5, rely=.07, anchor='center')

        self.status = tk.StringVar()
        self.status.set('Waiting')
        self.status_label = tk.Label(self.master, textvariable=self.status)
        self.status_label.place(relx=.5, rely=.12, anchor='center')

    def on_closing(self):
        """
        Method terminating all the processes of the program
        """
        if is_calculating:
            if tk.messagebox.askokcancel("Quit", "Quitting will abort the simulation. Do you wish to quit?"):
                self.master.destroy()
                sys.exit(0)
        else:
            self.master.destroy()
            sys.exit(0)

    def run_simulation(self):
        """
        Method running the simulation
        """

        seconds = self.seconds.get()
        days = self.days.get()
        years = self.years.get()

        if seconds == '':
            seconds = 0
        if days == '':
            days = 0
        if years == '':
            years = 0

        samples = self.samples_ent.get()
        frames = self.frames_ent.get()
        if not (is_float(seconds) and is_float(days) and is_float(years)
                and is_int(self.samples_ent.get()) and is_int(self.frames_ent.get())):
            tk.messagebox.showwarning(title='Error', message='Incorrect input')
            return
        else:
            length = float(seconds) + float(days) * DAY + float(years) * YEAR
            samples = int(samples)
            frames = int(frames)
        if length == 0 or samples == 0:
            tk.messagebox.showwarning(message='Length or samples cannot be equal 0')
            return
        if length < samples:
            tk.messagebox.showwarning(message='Each sample has to be at least 1 second long')
        if frames != 0 and samples % frames != 0:
            tk.messagebox.showwarning(message='Amount of samples has to be a multiple of amount of frames')
            return

        if tk.messagebox.askquestion(
            "Do you wish to proceed?",
                "Proceeding will delete all the previous files in '/temp' directory. Do you wish to proceed?",
                icon='warning') == 'no':
            return

        global is_calculating
        is_calculating = True

        start_time = time.time()
        self.update_progress_bar(0)
        self.update_status('Initializing the simulation')
        print('Starting the simulation')
        if os.path.isdir('temp'):
            print('\nDeleting "/temp"')
            self.update_status("Deleting '/temp'")
            rmtree('./temp')
        print('Creating "/temp" for temporary files.\n')
        self.update_status("Creating '/temp' for temporary files.")
        os.mkdir('./temp')
        os.mkdir('./temp/frames')
        data = scenarios.load_scenario(scenario)
        simulation.main(app, data[0], data[1], data[2], data[3], data[4], length, samples, frames, True)
        print(f'\nTime elapsed: {time.time() - start_time} s')
        self.update_status(f'Done! Time elapsed: {round(time.time() - start_time, 2)} s')
        # Opening the folder with created files
        if os_identified:
            open_folder()
            self.open_temp = tk.Button(self.master, text='View the\nsimulation', command=open_folder)
            self.open_temp.place(relx=0.85, rely=0.9, relheight=0.1, relwidth=0.2, anchor='center')
        else:
            self.update_status(f"Couldn't open the '/temp' folder. You can find it in the directory this program is"
                               f"located.\nDone! Time elapsed: {round(time.time() - start_time, 2)} s")

        is_calculating = False

    def set_scenario(self, scen):
        """
        Method setting currently selected scenario to the one user chose
        :param scen: Scenario chosen by the user
        """
        global scenario
        scenario = scen
        self.chosen.set(f'Scenario: {scenario[:-4]}')

        values = scenarios.show_scenario(scen)

        self.seconds.delete(0, tk.END)
        self.days.delete(0, tk.END)
        self.years.delete(0, tk.END)
        self.samples_ent.delete(0, tk.END)
        self.frames_ent.delete(0, tk.END)

        seconds = float(values[0])
        days = 0
        years = 0
        while seconds >= YEAR / 2:
            seconds -= YEAR / 2
            years += 0.5
        while seconds >= DAY / 2:
            seconds -= DAY / 2
            days += 0.5

        if seconds == int(seconds):
            seconds = int(seconds)
        if days == int(days):
            days = int(days)
        if years == int(years):
            years = int(years)

        self.seconds.insert(0, seconds)
        self.days.insert(0, days)
        self.years.insert(0, years)

        self.samples_ent.insert(0, values[1])
        self.frames_ent.insert(0, values[2])

    def choose_scenario(self):
        """
        Method creating a new windows with available scenarios for the user to choose
        """
        self.top = tk.Toplevel(self.master)
        self.top.geometry('400x800')
        canvas = tk.Canvas(self.top, height=HEIGHT, width=WIDTH)
        canvas.pack()
        rel_height = 0.8 / len(scens)
        rel_y = 0
        for scen in scens:
            tk.Button(self.top, text=scen[:-4], font=40, command=lambda scen=scen:
                      [self.set_scenario(scen), self.top.destroy()]).place(rely=rel_y, relx=0,
                                                                           relheight=rel_height, relwidth=1)
            rel_y += rel_height * 1.25
        self.top.mainloop()

    def update_progress_bar(self, percent):
        """
        Method updating the progress bar
        :param percent: Float
        """
        self.bar['value'] = percent

    def update_status(self, text):
        """
        Method updating the status label and updating the whole app
        :param text: String
        """
        self.status.set(text)
        self.update()


if __name__ == '__main__':
    # Getting the name of all the default scenarios
    scens = scenarios.get_scenarios()

    # Initializing the GUI
    root = tk.Tk()
    root.title('Gravity simulation')
    app = Application(master=root)

    app.mainloop()
