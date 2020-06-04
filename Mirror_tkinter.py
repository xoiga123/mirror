from tkinter import *
import tkinter.font as tkFont
from tkinter import ttk
import keyboard
import os
import subprocess
from PIL import Image
import mss
import shutil
from pystray import MenuItem as item
import pystray
from ctypes import windll, byref, create_unicode_buffer, create_string_buffer
FR_PRIVATE = 0x10
FR_NOT_ENUM = 0x20


class Mirror:
    def __init__(self):
        self.root = Tk()
        self.root.wm_title("Mirror")
        self.top = Toplevel(self.root)
        self.top.overrideredirect(
            1)  # removes border but undesirably from taskbar too (usually for non toplevel windows)
        self.root.attributes("-alpha", 0.0)
        self.root.iconphoto(True, PhotoImage(file=self.resource_path('mirror_assets/logo.png')))

        self.root.bind("<Unmap>", self.onRootIconify)
        self.root.bind("<Map>", self.onRootDeiconify)

        self.hotkey = None
        self.screen = '1'
        self.read_file()
        if self.hotkey == None:
            self.hotkey = "ctrl+q"
            self.write_file()
        keyboard.add_hotkey(self.hotkey, self.capture, args=())

        self.x = 440
        self.y = 440 + 27  # title bar height is 27
        self.top.geometry('{}x{}+200+200'.format(self.x, self.y))

        # style of combobox
        self.combostyle = ttk.Style()

        # set background color of title bar
        self.back_ground = "#1F1F1F"

        self.choose_box_color = "#707070"

        # set background of window
        self.content_color = "#121212"

        # set font color
        self.font_color = "#CBCBCB"
        self.font_color_side = '#707070'

        # set font
        # https://stackoverflow.com/questions/3954223/platform-independent-way-to-get-font-directory
        self.included_fonts = ['Roboto-Black.ttf', 'Roboto-Light.ttf', 'Roboto-LightItalic.ttf', 'Roboto-Medium.ttf',
                               'ROboto-Regular.ttf']
        if sys.platform == 'win32':
            for _font in self.included_fonts:
                self.loadfont(self.resource_path('mirror_assets/'+_font))
        elif sys.platform == 'darwin':
            for _font in self.included_fonts:
                shutil.copy(self.resource_path('mirror_assets/'+_font), '/Library/Fonts')
                shutil.copy(self.resource_path('mirror_assets/'+_font), '~/Library/Fonts')
        else:  # unix
            for _font in self.included_fonts:
                shutil.copy(self.resource_path('mirror_assets/'+_font), '/usr/share/fonts')
                shutil.copy(self.resource_path('mirror_assets/'+_font), '/usr/local/share/fonts')
                shutil.copy(self.resource_path('mirror_assets/'+_font), '~/.fonts')

        self.font = tkFont.Font(family="Roboto", size=20)
        self.font_title = tkFont.Font(family="Roboto", size=12)

        # make a frame for the title bar
        self.title_bar = Frame(self.top, bg=self.back_ground, bd=0, highlightcolor=self.back_ground,
                               highlightthickness=0)

        self.close_button = Button(self.title_bar, text='x', command=self.close_program, bg=self.back_ground, padx=5,
                                   activebackground="red", bd=0, fg=self.font_color, activeforeground="white",
                                   highlightthickness=0, font=self.font_title)

        # put a minimize button on the title bar
        self.minimize_button = Button(self.title_bar, text='_', command=self.withdraw_window, bg=self.back_ground, padx=5,
                                      activebackground="red",
                                      bd=0, fg=self.font_color, activeforeground="white", highlightthickness=0,
                                      font=self.font_title)

        # window title
        '''
        title_window = "Mirror"
        title_name = Label(title_bar, text=title_window, bg=back_ground, fg=font_color, font=font_title,
                           highlightcolor=back_ground, highlightthickness=1)
        '''
        # frames
        self.start_frame = Frame(self.top, bg=self.content_color, highlightthickness=0)
        self.about_frame = Frame(self.top, bg=self.content_color, highlightthickness=0)
        self.setting_frame = Frame(self.top, bg=self.content_color, highlightthickness=0)
        self.sct = mss.mss()

        # animation
        self.run_gif_gear = False
        self.run_gif_arrow = False

        self.gear_frame = 0
        self.gear_frames = [PhotoImage(file=self.resource_path('mirror_assets/gear_icon.gif'), format='gif -index %i' % (i)) for i in
                            range(300)]

        self.arrow_frame = 0
        self.arrow_frames = [PhotoImage(file=self.resource_path('mirror_assets/arrow_icon.gif'), format='gif -index %i' % (i)) for i in
                             range(300)]

        self.info_hover = PhotoImage(file=self.resource_path('mirror_assets/info_icon_hover.png'))


        # pack the widgets
        self.top.columnconfigure(0, minsize=440)
        self.title_bar.grid(row=0, column=0, sticky="news")
        # title_name.pack(side=LEFT)
        self.close_button.pack(side=RIGHT)
        self.minimize_button.pack(side=RIGHT)
        for frame in (self.start_frame, self.about_frame, self.setting_frame):
            frame.grid(row=1, column=0, sticky="news")
        self.x_axis = None
        self.y_axis = None

        # start frame
        self.start_frame.rowconfigure(0, minsize=50)
        self.start_frame.rowconfigure(4, minsize=55)
        self.start_frame.rowconfigure(1, minsize=131)
        self.start_frame.rowconfigure(3, minsize=150)
        self.start_frame.columnconfigure(0, minsize=50)
        self.start_frame.columnconfigure(1, minsize=340)
        self.start_frame.columnconfigure(2, minsize=50)

        self.gear_icon = PhotoImage(file=self.resource_path("mirror_assets/gear_icon.png"))
        self.start_frame_gear = Label(self.start_frame, image=self.gear_icon, bg=self.content_color)
        self.start_frame_gear.bind("<Button-1>", self.to_setting)
        self.start_frame_gear.bind("<Enter>", self.enter_gear)
        self.start_frame_gear.bind("<Leave>", self.leave_gear)
        self.start_frame_gear.place(x=15, y=15)

        self.start_frame_label_1 = Label(self.start_frame, bg=self.content_color, fg=self.font_color_side,
                                         font=("Roboto Light", -20),
                                         text="Use")
        self.start_frame_label_1.place(relx=0.5, rely=0.38, anchor="center")
        self.start_frame_label_2 = Label(self.start_frame, bg=self.content_color, fg=self.font_color,
                                         font=("Roboto Black", -40),
                                         text=self.hotkey.upper())
        self.start_frame_label_2.grid(row=2, column=1)

        self.start_frame_label_3 = Label(self.start_frame, bg=self.content_color, fg=self.font_color_side,
                                         font=("Roboto Light", -20),
                                         text="to mirror and close")
        self.start_frame_label_3.place(relx=0.5, rely=0.57, anchor="center")

        self.info_icon = PhotoImage(file=self.resource_path("mirror_assets/info_icon.png"))
        self.start_frame_info = Label(self.start_frame, image=self.info_icon, bg=self.content_color)
        self.start_frame_info.bind("<Button-1>", self.to_about)
        self.start_frame_info.bind("<Enter>", self.enter_info)
        self.start_frame_info.bind("<Leave>", self.leave_info)
        self.start_frame_info.place(rely=1.0, relx=1.0, x=-10, y=-10, anchor=SE)

        # about frame
        self.arrow_icon = PhotoImage(file=self.resource_path("mirror_assets/arrow_icon.png"))
        self.about_frame_arrow = Label(self.about_frame, image=self.arrow_icon, bg=self.content_color)
        self.about_frame_arrow.bind("<Button-1>", self.to_start)
        self.about_frame_arrow.bind("<Enter>", self.enter_arrow)
        self.about_frame_arrow.bind("<Leave>", self.leave_arrow)
        self.about_frame_arrow.place(x=15, y=15)

        self.about_frame_label_1 = Label(self.about_frame, bg=self.content_color, fg=self.font_color,
                                         font=("Roboto Medium", -20, "underline"),
                                         text="About the app")
        self.about_frame_label_1.place(relx=0.15, y=92)

        self.about_frame_label_2 = Label(self.about_frame, bg=self.content_color, fg=self.font_color_side,
                                         font=("Roboto Light", -20),
                                         text="A simple mirror program")
        self.about_frame_label_2.place(relx=0.15, y=132)

        self.about_frame_label_3 = Label(self.about_frame, bg=self.content_color, fg=self.font_color_side,
                                         font=("Roboto Light", -20, "italic"),
                                         text="github link")
        self.about_frame_label_3.bind("<Button-1>", self.open_web)
        self.about_frame_label_3.place(relx=0.15, y=172)

        self.about_frame_label_4 = Label(self.about_frame, bg=self.content_color, fg=self.font_color,
                                         font=("Roboto Medium", -20, "underline"),
                                         text="About us", anchor=E)
        self.about_frame_label_4.place(relx=0.9, height=30, y=244, anchor=E)

        self.about_frame_label_5 = Label(self.about_frame, bg=self.content_color, fg=self.font_color_side,
                                         font=("Roboto Light", -20, "italic"),
                                         text="your link", anchor=E)
        self.about_frame_label_5.bind("<Button-1>", self.open_web)
        self.about_frame_label_5.place(relx=0.9, height=30, y=284, anchor=E)

        self.about_frame_label_6 = Label(self.about_frame, bg=self.content_color, fg=self.font_color_side,
                                         font=("Roboto Light", -20, "italic"),
                                         text="my link", anchor=E)
        self.about_frame_label_6.bind("<Button-1>", self.open_web)
        self.about_frame_label_6.place(relx=0.9, height=30, y=324, anchor=E)

        # setting frame
        self.setting_frame_icon = Label(self.setting_frame, image=self.arrow_icon, bg=self.content_color)
        self.setting_frame_icon.bind("<Button-1>", self.to_start)
        self.setting_frame_icon.bind("<Enter>", self.enter_arrow)
        self.setting_frame_icon.bind("<Leave>", self.leave_arrow)
        self.setting_frame_icon.place(x=15, y=15)

        self.setting_frame_label_1 = Label(self.setting_frame, bg=self.content_color, fg=self.font_color,
                                           font=("Roboto", -35),
                                           text="Button")
        self.setting_frame_label_1.place(x=43, y=72)

        self.setting_frame_entry_1 = Entry(self.setting_frame, bg=self.content_color, fg=self.font_color,
                                           font=("Roboto Light", -35),
                                           state=NORMAL, disabledbackground=self.content_color, justify='center')
        self.setting_frame_entry_1.insert(0, self.hotkey.upper())
        self.setting_frame_entry_1.config(state=DISABLED)
        self.setting_frame_entry_1.bind("<Button-1>", self.set_hotkey)
        self.setting_frame_entry_1.place(x=45, y=145, relwidth=0.8)

        self.setting_frame_label_2 = Label(self.setting_frame, bg=self.content_color, fg=self.font_color,
                                           font=("Roboto", -35),
                                           text="Screen")
        self.setting_frame_label_2.place(relx=0.93, y=260, relwidth=0.3, anchor=SE)

        self.combostyle.theme_create('combostyle', parent='alt',
                                     settings={'TCombobox':
                                                   {'configure':
                                                        {'selectbackground': self.content_color,  # Here
                                                         'selectforeground': self.font_color,  # Here
                                                         'fieldbackground': self.content_color,  # Here
                                                         'fieldforeground': "red",  # Here
                                                         'background': self.choose_box_color  # Here
                                                         }
                                                    }
                                               }
                                     )
        self.combostyle.theme_use('combostyle')
        self.setting_frame_combo_box = ttk.Combobox(self.setting_frame, font=("Roboto Light", -35), justify='center',
                                                    width=267)
        self.setting_frame_combo_box['state'] = 'readonly'
        self.setting_frame_combo_box['values'] = [num + 1 for num, monitors in enumerate(self.sct.monitors[1:])]
        self.root.option_add("*TCombobox*Listbox*Foreground", self.font_color)  # For drop down list Here
        self.root.option_add("*TCombobox*Listbox*Background", self.content_color)  # For drop down list Here
        self.root.option_add('*TCombobox*Listbox.font', ("Roboto Light", -35))
        self.setting_frame_combo_box.place(x=43, y=260, relwidth=0.5, anchor=SW)

        # title_name.bind('<Button-1>', get_pos)
        self.title_bar.bind('<Button-1>', self.get_pos)

        self.close_button.bind('<Enter>', self.change_on_hovering)
        self.minimize_button.bind('<Enter>', self.change_on_hovering)

        self.close_button.bind('<Leave>', self.return_to_normal_state)
        self.minimize_button.bind('<Leave>', self.return_to_normal_state)


        self.to_start()
        self.root.mainloop()

    # toplevel follows root taskbar events (minimize, restore)
    def onRootIconify(self, event):
        self.top.withdraw()

    def onRootDeiconify(self, event):
        self.top.deiconify()

    # put a close button on the title bar
    def close_program(self):
        self.sct.close()
        self.root.destroy()

    def to_start(self, event=None):
        self.start_frame.tkraise()

    def to_setting(self, event=None):
        self.setting_frame.tkraise()

    def to_about(self, event=None):
        self.about_frame.tkraise()

    def open_web(self, event):
        url = event.widget['text']
        if sys.platform == 'win32':
            os.startfile(url)
        elif sys.platform == 'darwin':
            subprocess.Popen(['open', url])
        else:
            try:
                subprocess.Popen(['xdg-open', url])
            except OSError:
                print('Please open a browser on: ' + url)

    def set_hotkey(self, event):
        keyboard.call_later(self.set_hotkey2, args=[event], delay=0.001)

    def set_hotkey2(self, event):
        event.widget.config(state=NORMAL)
        event.widget.delete(0, END)
        try:
            keyboard.unhook_all_hotkeys()
        except:
            pass
        self.hotkey = keyboard.read_hotkey()
        keyboard.stash_state()
        keyboard.add_hotkey(self.hotkey, self.capture, args=())
        self.write_file()
        self.start_frame_label_2['text'] = self.hotkey.upper()
        event.widget.delete(0, END)
        event.widget.insert(0, self.hotkey.upper())
        event.widget.config(state=DISABLED)
        self.calculate_width()

    ''' 
    def lock_capture(self):
        _lock = threading.Thread(target=self.capture)
        # _lock.setDaemon(True)
        _lock.start()
        _lock.join()
        print("after lock")
    '''

    def capture(self):
        if self.setting_frame_combo_box.get() == '':
            monitor = self.sct.monitors[int(self.screen)]
        else:
            monitor = self.sct.monitors[int(self.setting_frame_combo_box.get())]
        sct_img = self.sct.grab(monitor)
        im = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
        print("to here")
        im.save('Mirrored.png')
        path = os.path.join(os.getcwd(), "Mirrored.png")
        openimg = None

        if sys.platform == "win32":
            openimg = subprocess.Popen(["rundll32.exe", "shimgvw.dll,ImageView_Fullscreen", path])
        ### NEED FIXING
        elif sys.platform == "darwin":
            with open(path, "r") as f:
                openimg = subprocess.Popen(
                    ["im=$(cat); open -a Preview.app $im; sleep 20; rm -f $im"],
                    shell=True,
                    stdin=f,
                )
        ### NEED FIXING
        else:
            with open(path, "r") as f:
                if shutil.which("display"):
                    openimg = subprocess.Popen(
                        ["im=$(cat);" + "display" + " $im; rm -f $im"], shell=True, stdin=f
                    )
                if shutil.which("eog"):
                    openimg = subprocess.Popen(
                        ["im=$(cat);" + "eog" + " $im; rm -f $im"], shell=True, stdin=f
                    )
                if shutil.which("xv"):
                    openimg = subprocess.Popen(
                        ["im=$(cat);" + "xv" + " $im; rm -f $im"], shell=True, stdin=f
                    )

        keyboard.unhook_all_hotkeys()
        keyboard.add_hotkey(self.hotkey, self.destroy_img, args=(openimg, path))

    def destroy_img(self, openimg, file):
        print("into destroy img")
        openimg.terminate()
        openimg.kill()
        try:
            os.remove(file)
        except:
            pass
        keyboard.unhook_all_hotkeys()
        keyboard.add_hotkey(self.hotkey, self.capture, args=())

    def enter_arrow(self, e):
        self.run_gif_arrow = True
        self.root.after(200, self.run_arrow, e)

    def run_arrow(self, e):
        if not self.run_gif_arrow:
            return
        self.about_frame_arrow["image"] = self.arrow_frames[self.arrow_frame]
        self.setting_frame_icon["image"] = self.arrow_frames[self.arrow_frame]
        self.arrow_frame += 1
        if self.arrow_frame >= 300:
            self.arrow_frame = 0
        self.root.after(10, self.run_arrow, e)

    def leave_arrow(self, e):
        self.run_gif_arrow = False
        self.about_frame_arrow["image"] = self.arrow_icon
        self.setting_frame_icon["image"] = self.arrow_icon

    def enter_gear(self, e):
        self.run_gif_gear = True
        self.root.after(200, self.run_gear, e)

    def run_gear(self, e):
        if not self.run_gif_gear:
            return
        self.start_frame_gear["image"] = self.gear_frames[self.gear_frame]
        self.gear_frame += 1
        if self.gear_frame >= 300:
            self.gear_frame = 0
        self.root.after(10, self.run_gear, e)

    def leave_gear(self, e):
        self.run_gif_gear = False
        self.start_frame_gear["image"] = self.gear_icon

    def enter_info(self, e):
        self.start_frame_info["image"] = self.info_hover
        self.start_frame_info.image = self.info_hover
        self.start_frame_info.place(rely=1.0, relx=1.0, x=-7, y=-7, anchor=SE)

    def leave_info(self, e):
        self.start_frame_info["image"] = self.info_icon
        self.start_frame_info.image = self.info_icon
        self.start_frame_info.place(rely=1.0, relx=1.0, x=-10, y=-10, anchor=SE)

    # bind title bar motion to the move window function
    def get_pos(self, event):
        xwin = self.top.winfo_x()
        ywin = self.top.winfo_y()
        startx = event.x_root
        starty = event.y_root

        ywin = ywin - starty
        xwin = xwin - startx

        def move_window(event):
            self.top.geometry(
                "{}x{}".format(self.x, self.y) + '+{0}+{1}'.format(event.x_root + xwin, event.y_root + ywin))

        self.title_bar.bind('<B1-Motion>', move_window)
        # title_name.bind('<B1-Motion>', move_window)

    def change_on_hovering(self, event):
        event.widget.config(bg="red")

    def return_to_normal_state(self, event):
        event.widget.config(bg=self.back_ground)

    def calculate_width(self):
        self.root.update()
        label_width = self.start_frame_label_2.winfo_width()
        if label_width > 340:
            self.x = label_width + 100
        else:
            self.x = 440
        self.top.geometry("{}x{}".format(self.x, self.y))
        self.root.update()

    def read_file(self):
        try:
            with open('mirror_hotkey.txt') as f:
                text = f.read().split(' ')
                self.hotkey = text[0]
                self.screen = text[1]
        except:
            pass

    def write_file(self):
        with open('mirror_hotkey.txt', 'w') as f:
            f.write(self.hotkey + ' ' + self.screen)

    def quit_window(self, icon, item):
        icon.stop()
        self.root.destroy()

    def show_window(self, icon, item):
        icon.stop()
        self.root.after(0, self.root.deiconify)

    def withdraw_window(self):
        self.root.withdraw()
        image = Image.open(self.resource_path("mirror_assets/logo.png"))
        menu = pystray.Menu(item('Quit', self.quit_window), item('Show', self.show_window, default=True))
        icon = pystray.Icon("Mirror", image, "Mirror", menu)
        icon.run()

    def resource_path(self, relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

    def loadfont(self, fontpath, private=True, enumerable=False):
        '''
        Makes fonts located in file `fontpath` available to the font system.

        `private`     if True, other processes cannot see this font, and this
                      font will be unloaded when the process dies
        `enumerable`  if True, this font will appear when enumerating fonts

        See https://msdn.microsoft.com/en-us/library/dd183327(VS.85).aspx

        '''
        # This function was taken from
        # https://github.com/ifwe/digsby/blob/f5fe00244744aa131e07f09348d10563f3d8fa99/digsby/src/gui/native/win/winfonts.py#L15
        # This function is written for Python 2.x. For 3.x, you
        # have to convert the isinstance checks to bytes and str
        if isinstance(fontpath, bytes):
            pathbuf = create_string_buffer(fontpath)
            AddFontResourceEx = windll.gdi32.AddFontResourceExA
        elif isinstance(fontpath, str):
            pathbuf = create_unicode_buffer(fontpath)
            AddFontResourceEx = windll.gdi32.AddFontResourceExW
        else:
            raise TypeError('fontpath must be of type str or unicode')

        flags = (FR_PRIVATE if private else 0) | (FR_NOT_ENUM if not enumerable else 0)
        numFontsAdded = AddFontResourceEx(byref(pathbuf), flags, 0)
        return bool(numFontsAdded)


if __name__ == "__main__":
    mirror_instance = Mirror()
