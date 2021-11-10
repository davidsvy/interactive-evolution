from functools import partial
import math
import matplotlib.pyplot as plt
from PIL import Image, ImageTk
import re
import sys
import tkinter as tk


class GUI(object):
    """A tkinter GUI that displays images and supports image selection.

    Attributes:
        img_size (tuple(int, int)): Size of the displayed images.
        selected_color (str): Color that is applied to selected images.
        unselected_color (str): Color of the background of the unselected images.
        reset_flag (bool): True if the user pressed the Reset button.
        exit_flag (bool): True if the user pressed the Exit button.
        img_status (list(bool)): i-th element is True if the i-th image has been selected.
        img_buttons: List of image buttons.
        root: root of the tkinter GUI
        scrollbar: schrollbar of the tkinter GUI
    """

    def __init__(self, img_size=(175, 175), selected_color='cornflower blue',
                 unselected_color='floral white', **kwargs):
        """Initialized a GUI object.

        Args:
            img_size (tuple(int, int)): Size of the displayed images.
            selected_color (str): Color that is applied to selected images.
            unselected_color (str): Color of the background of the unselected images.
        """
        self.img_size = img_size
        self.selected_color = selected_color
        self.unselected_color = unselected_color

    def on_closing_callback(self):
        """Closes GUI.
        """
        self.exit_flag = True
        self.root.destroy()

    def render_init(self, n_images):
        """Initizlizes necessary variables.

        Args:
            n_images (int): Number of images to be displayed.
        """
        self.reset_flag = False
        self.exit_flag = False

        self.img_status = [False] * n_images
        self.img_buttons = []

        self.root = tk.Tk()
        self.root.protocol('WM_DELETE_WINDOW', self.on_closing_callback)

        self.root.state('zoomed')
        self.root.title('Interactive Evolution')

        self.scrollbar = tk.Scrollbar(self.root)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def render_text(self):
        """Renders large text message at the top of the window.
        """
        text_box = tk.Text(self.root, height=1, font=('Helvetica', 32), wrap="char", borderwidth=0,
                           highlightthickness=0, exportselection=False, cursor="arrow",
                           yscrollcommand=self.scrollbar.set, fg=self.selected_color)

        text_box.tag_configure('center', justify='center')
        text_box.insert('1.0', 'Select the images with the desired traits.')
        text_box.tag_add('center', '1.0', 'end')
        text_box.pack(fill='both', expand=False, side='top')

    def render_images(self, images):
        """Renders images.

        Args:
            images (list(PIL.Image)):
        """
        img_wrapper = tk.Text(self.root, wrap='char', borderwidth=0, highlightthickness=0,
                              state='disabled', cursor='arrow', yscrollcommand=self.scrollbar.set,
                              pady=10)
        img_wrapper.pack(fill='both', expand=True)

        def img_command(idx):
            """Overwritted #n_images times to create a function for each image.
            """
            self.img_status[idx] = not self.img_status[idx]
            color = self.selected_color if self.img_status[idx] else self.unselected_color
            self.img_buttons[idx].config(bg=color)

        def render_image(image, commmand):
            label = tk.Label(image=image)
            label.image = image
            button = tk.Button(image=image, command=commmand,
                               borderwidth=5, bg=self.unselected_color,
                               relief=tk.FLAT)

            self.img_buttons.append(button)
            img_wrapper.window_create('end', window=button)

        for idx, image in enumerate(images):
            resized = image.resize(self.img_size, Image.ANTIALIAS)
            tkimage = ImageTk.PhotoImage(resized)
            command = partial(img_command, idx=idx)
            render_image(tkimage, command)

        self.scrollbar.config(command=img_wrapper.yview)

    def render_buttons(self):
        """Renders buttons at the bottom of the window.
        """
        button_wrapper = tk.Text(self.root, wrap="char", borderwidth=0, highlightthickness=0,
                                 state="disabled", cursor="arrow", yscrollcommand=self.scrollbar.set,
                                 height=1)
        button_wrapper.pack(fill="both", expand=True)

        def continue_command():
            self.root.destroy()

        def reset_command():
            self.reset_flag = True
            self.root.destroy()

        def exit_command():
            self.exit_flag = True
            self.root.destroy()

        def render_button(text, command):
            button = tk.Button(text=text, command=command, font=('Helvetica', 15),
                               borderwidth=0, bg=self.unselected_color, fg=self.selected_color)

            button_wrapper.window_create('end', window=button, padx=5, pady=5)

        buttons = ['Continue', 'Reset', 'Exit']
        button_commands = [continue_command, reset_command, exit_command]

        for button, command in zip(buttons, button_commands):
            render_button(button, command)

    def render(self, images):
        """Creates interactive GUI that displays images and returns the user's input.

        grid stolen from
        https://stackoverflow.com/questions/47704736/tkinter-grid-dynamic-layout
        scrollbar stolen from
        https://www.tutorialspoint.com/python/tk_scrollbar.htm

        Args:
            images (list(PIL.Image)):

        Returns:
            reset_flag (bool): True if the Reset button was pressed.
            exit_flag (bool): True if the Exit button was pressed.
            img_status (list(bool)): i-th element is True if the i-th image was selected.
        """
        self.render_init(len(images))
        self.render_text()
        self.render_images(images)
        self.render_buttons()
        self.root.mainloop()

        return self.reset_flag, self.exit_flag, self.img_status


class PLT_GUI(object):
    """Alternative GUI that only plots the images with matplotlib. Only option for colab.

    Attributes:
        colab (bool): Whether the code will be run on Google Colab or not. 
    """

    def __init__(self, colab=False, **kwargs):
        self.colab = colab

    def render_images(self, images):
        """Renders images within a plt.figure.

        Args:
            images ([type]): [description]
        """
        n_columns = 7
        n_rows = math.ceil(len(images) / n_columns)

        fig = plt.figure(figsize=(16, 3 * n_rows))

        for step, image in enumerate(images, 1):
            ax = fig.add_subplot(n_rows, n_columns, step)
            ax.title.set_text(f'{step}')
            plt.axis('off')
            plt.imshow(image)

        plt.subplots_adjust(wspace=0, hspace=0)
        plt.show(block=False)
        if self.colab:
            plt.close('all')
            plt.pause(1)

    def get_user_input(self, n_images):
        """Receives user's input to select images/press buttons.

        Args:
            n_images (int): Number of images displayed.

        Returns:
            reset_flag (bool): True if the Reset button was pressed.
            exit_flag (bool): True if the Exit button was pressed.
            img_status (list(bool)): i-th element is True if the i-th image was selected.
        """
        msg = 'Select images by typing their numbers separated by space. Press x/X to quit, r/R to restart.\n'
        exit_flag = False
        reset_flag = False
        img_status = [False] * n_images

        while True:
            user_input = input(msg)
            user_input = user_input.strip().lower()

            if user_input == 'x':
                exit_flag = True
                break

            if user_input == 'r':
                reset_flag = True
                break

            match = re.match(r'^(\s*\d+\s*)+$', user_input)
            if not match:
                print('Invalid input.')
                continue

            idxs = set([int(idx) - 1 for idx in user_input.split()])
            if min(idxs) < 0 or max(idxs) >= n_images:
                print(f'Input must be between 0 and {n_images - 1}')
                continue

            for idx in idxs:
                img_status[idx] = True
            break

        plt.close('all')

        return reset_flag, exit_flag, img_status

    def render(self, images):
        """Creates uninteractive GUI with plt.

        Args:
            images (list(PIL.Image)):

        Returns:
            reset_flag (bool): True if the Reset button was pressed.
            exit_flag (bool): True if the Exit button was pressed.
            img_status (list(bool)): i-th element is True if the i-th image was selected.
        """
        self.render_images(images)
        reset_flag, exit_flag, img_status = self.get_user_input(len(images))

        return reset_flag, exit_flag, img_status
