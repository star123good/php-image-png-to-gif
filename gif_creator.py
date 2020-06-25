#!/usr/bin/python

import os, sys
import csv
import glob
from datetime import datetime
from subprocess import Popen, PIPE
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox

script_version="3.1"
bin_dir = "/usr/local/bin/"

class GIF_creator(Frame):
    def __init__(self, main_window, master = None):
        Frame.__init__(self, master)
        self.pack()
        self.main_window = main_window
        self.create_widgets()
        self.input_folder_path = ""
        self.output_file_path = ""
        self.input_file_path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "GIF_schedule.csv") 
        self.high_res = False
        self.image_size = ()

    def get_folder_path(self, output_file_button):
        self.input_folder_path = filedialog.askdirectory(title = "Select input folder", 
                                                         initialdir = os.path.abspath(sys.argv[0]), 
                                                         mustexist = True, 
                                                         parent = self)
        if 0 < len(self.input_folder_path):
            self.output_file_button["state"] = NORMAL

    def get_schedule_file_path(self):
        csv_file_path = filedialog.askopenfilename(title = "Select animation schedule CSV file",
                                initialfile = "GIF_schedule.csv", 
                                filetypes = (("CSV Files","*.csv"), ("All Files","*.*")))
        if len(csv_file_path):
            self.input_file_path = csv_file_path

    def set_status(self, status_label, idle = True):
        if idle:
            self.main_window.config(cursor = "")
            self.main_window.update()
            status_label["text"] = "STATUS: Idle"
            status_label.update()
        else:
            status_label["text"] = "STATUS: Processing..."
            status_label.update()
            self.main_window.config(cursor = "watch")
            self.main_window.update()

    def get_list_from_file(self):
        data = []
        if not os.path.isfile(self.input_file_path):
            messagebox.showerror("Non-existing file", "'" + self.input_file_path + "' does not exist")
            return data
        try:
            with open(self.input_file_path, 'r') as f:
                csv_reader = csv.reader(f, delimiter=',', quotechar='"')
                next(csv_reader)
                for row in csv_reader:
                    frame_file_path = os.path.join(self.input_folder_path, row[1])
                    if not os.path.isfile(frame_file_path) or not row[2].replace(".", "", 1).isdigit():
                        messagebox.showerror("Invalid CSV", "Missing duration or non-existing file name:\n" + str(row))
                        data = []
                        return data
                    else:
                        row[1] = frame_file_path
                    row = row[1:]
                    if len(row):
                        data.append(row)
        except Exception as err:
            if len(err):
                messagebox.showerror("Failure", str(err))
        finally:
            if 0 == len(data):
                messagebox.showerror("", "The file creation is canceled")
                data = []
            return data

    def get_image_size(self, image_file_path):
        # command = bin_dir + "identify -ping -format '%w %h' " + image_file_path
        command = "identify -ping -format '%w %h' " + image_file_path
        exit_code, stdout, stderr = run_command(command)
        if 0 != exit_code:
            messagebox.showerror("Failure", "Couldn't get the first frame width and height.\n\nReason: " + stderr)
            return ()
        return tuple(stdout.split())

    def generate_fade_in_LTR_frames(self, sizes, fg_file_path, status_label):
        counter = len(glob.glob(os.path.join(tmp_dir, "fade_in_LTR_*.miff"))) + 1
        fade_in_LTR_file_path = os.path.join(tmp_dir, "fade_in_LTR_" + str(counter) + ".miff")
        width = int(sizes[0])
        one_tenth_width = int(width / 10 )
        for i in range(one_tenth_width, width, one_tenth_width):
            # Creating gradient image and using as a transparency mask
            color1_stop = str((-1 * one_tenth_width) + i)
            masked_file = os.path.join(tmp_dir, "fade_in_LTR_" + str(i) + ".png")
            # command = bin_dir + "convert " + fg_file_path + " \( \( -size " + str(width) + "x" + color1_stop + \
            #           " canvas:white \) \( -size " + str(width) + "x" + str(one_tenth_width) + " gradient:white-black \) " + \
            #           "\( -size " + str(width) + "x" + str((width - i)) + " canvas:black \) -append -rotate -90 \) " + \
            #           "-compose CopyOpacity -composite " + masked_file
            command = "convert " + fg_file_path + " \( \( -size " + str(width) + "x" + color1_stop + \
                      " canvas:white \) \( -size " + str(width) + "x" + str(one_tenth_width) + " gradient:white-black \) " + \
                      "\( -size " + str(width) + "x" + str((width - i)) + " canvas:black \) -append -rotate -90 \) " + \
                      "-compose CopyOpacity -composite " + masked_file
            exit_code, stdout, stderr = run_command(command)
            if 0 != exit_code:
                self.set_status(status_label, idle = True)
                messagebox.showerror("Failure", stderr)
                exit(1)
        # Aggregating the created frames
        files_list = sorted(glob.glob(os.path.join(tmp_dir, "fade_in*png")))
        # command = bin_dir + "convert -duration 0 -alpha on " + " ".join(files_list) + " " + \
        #           fg_file_path + " " + os.path.join(tmp_dir, fade_in_LTR_file_path)
        command = "convert -duration 0 -alpha on " + " ".join(files_list) + " " + \
                  fg_file_path + " " + os.path.join(tmp_dir, fade_in_LTR_file_path)
        exit_code, stdout, stderr = run_command(command)
        if 0 != exit_code:
            self.set_status(status_label, idle = True)
            messagebox.showerror("Failure", stderr)
            exit(1)
            return ""
        return fade_in_LTR_file_path

    def generate_gif(self, status_label):
        self.output_file_path = filedialog.asksaveasfilename(title = "Specify GIF file path",
                                initialfile = os.path.basename(self.input_folder_path), 
                                filetypes = (("GIF Files","*.gif"), ("All Files","*.*")))
        self.output_file_path = self.output_file_path.replace(" ", "_")
        animation_schedule_list = self.get_list_from_file()
        if [] == animation_schedule_list:
            return
        start_time = datetime.today()
        if 0 == len(self.output_file_path):
            return
        elif not self.output_file_path.endswith(".gif"):
            self.output_file_path += ".gif"
        self.image_size = self.get_image_size(animation_schedule_list[0][0])
        if () == self.image_size:
            return
        self.set_status(status_label, idle = False)

        commands = []
        key_frames_indices = []
        # cmd = bin_dir + "convert"
        cmd = "convert"
        previous_frame_effect = False
        last_key_index = -1
        frame_files_count = len(animation_schedule_list)
        for i in range(frame_files_count):
            item = animation_schedule_list[i]
            frame = item[0]
            # Check for transition effect
            if i < frame_files_count - 1: 
                if "Fade in" == animation_schedule_list[i + 1][2]:
                    next_frame_effect = True 
                else:
                    next_frame_effect = False 

            if "Fade LTR" == item[2]:
                fg_file_path = frame
                fade_in_LTR_file_path = self.generate_fade_in_LTR_frames(self.image_size, fg_file_path, status_label)
                if "" == fade_in_LTR_file_path:
                    self.set_status(status_label, idle = True)
                    return
                cmd += " \( -delay 0 " + fade_in_LTR_file_path + " \)"
                previous_frame_effect = False
                if next_frame_effect:
                    last_key_index += 10
                else:
                    last_key_index += 11
                    key_frames_indices.append([i, last_key_index])
                    cmd += " \( -delay " + str(int(float(item[1]) * 100)) + " " + frame + " \)"
            if "Fade in" == item[2] and next_frame_effect:
                last_key_index += 6
                key_frames_indices.append([i, last_key_index])
                if previous_frame_effect:
                    cmd += " " + frame
                else:
                    previous_frame_effect = True
                    cmd += " \( -delay 0 -morph 5 " + frame
            elif "Fade in" != item[2] and next_frame_effect:
                last_key_index += 1
                key_frames_indices.append([i, last_key_index])
                if previous_frame_effect:
                    cmd += " \) \( -delay 0 -morph 5 " + frame
                else:
                    cmd += " \( -delay 0 -morph 5 " + frame
                previous_frame_effect = True
            elif "Fade in" == item[2] and not next_frame_effect:
                if previous_frame_effect:
                    cmd += " " + frame + " \)"
                    last_key_index += 6
                    key_frames_indices.append([i, last_key_index])
                else:
                    last_key_index += 1
                    cmd += " -delay " + str(int(float(item[1]) * 100)) + " " + frame
                    key_frames_indices.append([i, last_key_index])
                previous_frame_effect = False
            elif "Fade LTR" != item[2]:
                if previous_frame_effect:
                    cmd += " \)"
                previous_frame_effect = False
                last_key_index += 1
                cmd += " -delay " + str(int(float(item[1]) * 100)) + " " + frame

        commands.append(cmd + " " + os.path.join(tmp_dir, "tmp_1.miff"))
        # Setup delay durations for morphing start and end key frames
        # cmd = bin_dir + "convert " + os.path.join(tmp_dir, "tmp_1.miff")
        cmd = "convert " + os.path.join(tmp_dir, "tmp_1.miff")
        for item in key_frames_indices:
            duration = animation_schedule_list[item[0]][1]
            key = item[1]
            cmd += " \( -clone " + str(key) + " -set delay " + str(int(float(duration) * 100)) + \
                   " \)" + " -swap " + str(key) + ",-1 +delete" 
        commands.append(cmd + " " + os.path.join(tmp_dir, "tmp_2.miff"))

        for command in commands:
            exit_code, stdout, stderr = run_command(command)
            if 0 != exit_code:
                self.set_status(status_label, idle = True)
                messagebox.showerror("Failure", stderr)
                return

        # Set optimization parameters
        if self.high_res:
            # cmd = bin_dir + "convert -loop 0 " + os.path.join(tmp_dir, "tmp_2.miff")
            cmd = "convert -loop 0 " + os.path.join(tmp_dir, "tmp_2.miff")
        else:
            # cmd = bin_dir + "convert -loop 0 -layers optimize +dither -depth 64 -alpha on " + os.path.join(tmp_dir, "tmp_2.miff")
            cmd = "convert -loop 0 -layers optimize +dither -depth 64 -alpha on " + os.path.join(tmp_dir, "tmp_2.miff")
        # Apply the optimization and create GIF file
        exit_code, stdout, stderr = run_command(cmd + " " + self.output_file_path)
        self.set_status(status_label, idle = True)
        if 0 != exit_code:
            messagebox.showerror("Failure", stderr)
            return
        end_time = datetime.today()
        process_duration = divmod((end_time - start_time).seconds, 60)
        # Get GIF file size in MB
        file_size = round(float(os.stat(self.output_file_path).st_size / (1024.0 ** 2)), 2)
        file_size = "{:.2f}".format(file_size)
        messagebox.showinfo("Completed", "The animated GIF file is created.\n\nPath: " + \
                            self.output_file_path + "\n\nSize: " + str(file_size) + " MB" \
                            "\n\nSpent time: " + str(process_duration[0]) + " min(s) " + \
                            str(process_duration[1]) + " sec(s)")
        # Remove the temporary files
        remove_dir_content(tmp_dir)

    def info(self):
        cmd = bin_dir + "identify -list resource"
        exit_code, stdout, stderr = run_command(cmd)
        if 0 == exit_code:
            messagebox.showinfo("Resource Limits", str(stdout.decode()) + "\n\n" + \
                                "Configuration file:\n/etc/ImageMagick-6/policy.xml" + \
                                "\n/usr/local/etc/ImageMagick-7/policy.xml")
        else:
            messagebox.showerror("Error", stderr)

    def set_resolution(self, value):
        self.high_res = value

    def create_widgets(self):
        self.status_label = Label(self, text="STATUS: Idle")
        self.status_label.grid(row = 1, column = 1, ipady = 12)

        self.input_folder_button = Button(self, width = 20, height = 1, 
                                          command = lambda: self.get_folder_path(self.output_file_button))
        self.input_folder_button["text"] = "Select Input Folder..."
        self.input_folder_button.grid(row = 2, column = 1, pady = 5)

        self.input_file_button = Button(self, width = 20, height = 1, command = self.get_schedule_file_path)
        self.input_file_button["text"] = "Select Schedule File..."
        self.input_file_button.grid(row = 3, column = 1, pady = 5)

        self.res_group = LabelFrame(self, text = "Resolution")
        res = IntVar()
        self.low_res_radio_button = Radiobutton(self.res_group, text = "Low", variable = res, value = 0, 
                                                command = lambda: self.set_resolution(res.get()))
        self.high_res_radio_button = Radiobutton(self.res_group, text = "High", variable = res, value = 1,
                                                command = lambda: self.set_resolution(res.get()))
        self.low_res_radio_button.grid(row = 4, column = 1, ipadx = 16)
        self.high_res_radio_button.grid(row = 4, column = 2, ipadx = 16)
        self.res_group.grid(row = 4, column = 1)
        self.low_res_radio_button.select()

        self.output_file_button = Button(self, width = 20, height = 1, 
                                         command = lambda: self.generate_gif(self.status_label))
        self.output_file_button["text"] = "Create Animated GIF..."
        self.output_file_button["state"] = DISABLED
        self.output_file_button.grid(row = 5, column = 1, pady = 5)

        self.info_button = Button(self, width = 20, height = 1)
        self.info_button["text"] = "Resource Limits..."
        self.info_button["command"] =  self.info
        self.info_button.grid(row = 6, column = 1, pady = (25, 5))

        self.quit_button = Button(self, width = 20, height = 1)
        self.quit_button["text"] = "Quit"
        self.quit_button["fg"]   = "darkred"
        self.quit_button["command"] =  self.quit
        self.quit_button.grid(row = 7, column = 1, pady = 5)

        self.info_label = Label(self, text="Based on ImageMagick")
        self.info_label["font"]  = ", 8"
        self.info_label["fg"]   = "grey"
        self.info_label.grid(row = 8, column = 1, ipady = 12)

def center_window(main_window, width, height):
    x_pos = str(int((main_window.winfo_screenwidth() - width) / 2))
    y_pos = str(int((main_window.winfo_screenheight() - height) / 2))
    main_window.geometry(str(width) + "x" + str(height) + "+" + x_pos + "+" + y_pos)

def run_command(command):
    try:
        process = Popen(command, stdout = PIPE, stderr = PIPE, shell = True)
        stdout, stderr = process.communicate()
        exit_code = process.wait()
        output = str(stdout.decode()) + ' ' + str(stderr.decode()) + ' ' + str(exit_code)
        print("command : ", command)
    except Exception as err:
        print(str(err))
    finally:
        return exit_code, stdout, stderr

def remove_dir_content(dir_path):
    exit_code, stdout, stderr = run_command("rm -f " + os.path.join(dir_path, "*"))
    if 0 != exit_code:
        messagebox.showerror("Failure", "Failed to delete directory content: " + \
                             dir_path + "\n\nReason: " + str(stderr))
        exit(1)

def create_directory(dir_path):
    if not os.path.isdir(dir_path):
        try: 
            os.makedirs(dir_path)
        except OSError as err:
            messagebox.showerror("Error", "Failed to create directory: " + \
                                 dir_path + "\n\nReason: " + str(err))
            main_window.destroy()
            exit(1)
    else:
        # Remove the temporary files
        remove_dir_content(dir_path)

try:
    main_window = Tk()
    main_window.title("GIF Creator v" + script_version)
    try:
        script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        tmp_dir = os.path.join(script_dir, "tmp_dir")
        tool_icon = PhotoImage(file = os.path.join(script_dir, "tool_icon.png"))
        main_window.tk.call('wm', 'iconphoto', main_window._w, tool_icon)
    except:
        pass
    center_window(main_window, 265, 345)
    main_window.resizable(0, 0)
    create_directory(tmp_dir)
    app = GIF_creator(main_window, master = main_window)
    app.mainloop()
    try:
        main_window.destroy()
    except:
        pass
except Exception as err:
    print(err)
