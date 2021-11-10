from functools import partial
import glob
from PIL import Image, ImageTk
import tkinter as tk


class GUI(object):

    def __init__(self, img_size=(175, 175), selected_color='cornflower blue',
                 unselected_color='floral white'):

        self.img_size = img_size
        self.selected_color = selected_color
        self.unselected_color = unselected_color

    def on_closing_callback(self):
        self.exit_flag = True
        self.root.destroy()

    def render_init(self, n_images):
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
        text_box = tk.Text(self.root, height=1, font=('Helvetica', 32), wrap="char", borderwidth=0,
                           highlightthickness=0, exportselection=False, cursor="arrow",
                           yscrollcommand=self.scrollbar.set, fg=self.selected_color)

        text_box.tag_configure('center', justify='center')
        text_box.insert('1.0', 'Select the images with the desired traits.')
        text_box.tag_add('center', '1.0', 'end')
        text_box.pack(fill='both', expand=False, side='top')

    def render_images(self, images):
        img_wrapper = tk.Text(self.root, wrap='char', borderwidth=0, highlightthickness=0,
                              state='disabled', cursor='arrow', yscrollcommand=self.scrollbar.set,
                              pady=10)
        img_wrapper.pack(fill='both', expand=True)

        def img_command(idx):
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
        """
        grid stolen from
        https://stackoverflow.com/questions/47704736/tkinter-grid-dynamic-layout
        scrollbar stolen from
        https://www.tutorialspoint.com/python/tk_scrollbar.htm
        """
        self.render_init(len(images))
        self.render_text()
        self.render_images(images)
        self.render_buttons()
        self.root.mainloop()

        return self.reset_flag, self.exit_flag, self.img_status
