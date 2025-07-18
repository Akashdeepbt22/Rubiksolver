import customtkinter as ctk
import decimal
import threading
import kociemba
import pywinstyles
import winaccent
from PIL import ImageColor
import functools
import multiprocessing
import win32api
import os
import ctypes


bg = ('#000000','bg')
default = ("#282828",'default') 
theme = (winaccent.accent_normal,'theme')
white = ('#ffffff','white')
green = ('#009b48','green')
yellow = ('#ffd500','yellow')
orange = ('#ff5800','orange')
red = ('#b71234','red')
blue = ('#0046ad','blue')

selector = default


@functools.lru_cache(maxsize=128)
def dark(color):
    """Convert a color to a darker shade by reducing RGB values by 40%.
    
    Args:
        color: A hex color string (e.g. '#ffffff')
    
    Returns:
        A hex color string representing the darker shade
    """
    rgb = list(ImageColor.getrgb(color))
    rgb[0], rgb[1], rgb[2]= int(rgb[0]*0.6), int(rgb[1]*0.6), int(rgb[2]*0.6)
    return '#%02x%02x%02x' % tuple(rgb)

def frange(x, y, jump):
    """Generate a range of float numbers with a specified jump/step.
    
    Args:
        x: Start value
        y: End value
        jump: Step size between values
    
    Yields:
        Float values from x to y with jump intervals
    """
    if x<y:
        while x<y:
            yield float(x)
            x = decimal.Decimal(x)+decimal.Decimal(jump)
    elif x>y:
        while x>y:
            yield float(x)
            x = decimal.Decimal(x)+decimal.Decimal(jump)

def debounce(wait_time):
    """
    Decorator to debounce a function call by waiting for wait_time seconds
    before executing. If the decorated function is called again within the
    wait time, the timer resets.
    """
    def decorator(func):
        timer = None
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal timer
            if timer is not None:
                timer.cancel()
            timer = threading.Timer(wait_time, func, args=args, kwargs=kwargs)
            timer.start()
        return wrapper
    return decorator

def threaded(func):
    """Decorator to automatically launch a function in a thread"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.start()
        return thread
    return wrapper

def multiprocessed(func):
    """Decorator to automatically launch a function in a process"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        process = multiprocessing.Process(target=func, args=args, kwargs=kwargs)
        process.start()
        return process
    return wrapper

@functools.lru_cache(maxsize=64)
def _calculate_animation_params(init_x: float, init_y: float, target_x: float, target_y: float, speed: float):
    """Cache animation calculations for smoother transitions"""
    diff_x = float(target_x - init_x)
    diff_y = float(target_y - init_y)
    time = (((diff_x**2) + (diff_y**2))**(1/2)) * speed
    return diff_x, diff_y, time

def animate(widget, target_x, target_y, speed):
    """Animate a widget's position from its current location to a target location.
    
    Args:
        widget: The widget to animate
        target_x: Target x-coordinate
        target_y: Target y-coordinate
        speed: Speed of the animation
    """
    if f'animation_{widget}' not in globals():
        globals()[f'animation_{widget}'] = 1

    if globals()[f'animation_{widget}'] == 1:
        globals()[f'animation_{widget}'] = 0

        init_x = widget.winfo_x()
        init_y = widget.winfo_y()

        diff_x, diff_y, time = _calculate_animation_params(init_x, init_y, target_x, target_y, speed)

        if not(diff_x == 0 and diff_y == 0):
            for frame in frange(1, time, time/abs(time)):
                widget.place(x=init_x+(frame*(diff_x/time)),
                           y=init_y+(frame*(diff_y/time)))

        widget.place(x=target_x, y=target_y)
        globals()[f'animation_{widget}'] = 1


scale_factor = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100

root = ctk.CTk()
width = 995
height = 560
root.geometry(f'{width}x{height}+{int((root.winfo_screenwidth()/2)-(width/2))}+{int((root.winfo_screenheight()/2)-(height/2))}')
root.maxsize(width, height)
root.minsize(width,height)
root.configure(fg_color=bg[0])
root.title('YARCS')
root.iconbitmap(os.path.join(os.path.dirname(__file__),'icon.ico'))
ctk.set_appearance_mode("dark")
root.maxsize(width=width, height=height)
root.minsize(width=width, height=height)


def solve():
    input_cube = f'{input_frame.frameblue.return_state()}{input_frame.framered.return_state()}{input_frame.framewhite.return_state()}{input_frame.framegreen.return_state()}{input_frame.frameorange.return_state()}{input_frame.frameyellow.return_state()}'
    output_cube = f'{output_frame.frameblue.return_state()}{output_frame.framered.return_state()}{output_frame.framewhite.return_state()}{output_frame.framegreen.return_state()}{output_frame.frameorange.return_state()}{output_frame.frameyellow.return_state()}'
    textboxoutput.configure(state='normal')

    input_cube = input_cube.replace(blue[0],'U').replace(red[0],'R').replace(white[0],'F').replace(green[0],'D').replace(orange[0],'L').replace(yellow[0],'B')
    output_cube = output_cube.replace(blue[0],'U').replace(red[0],'R').replace(white[0],'F').replace(green[0],'D').replace(orange[0],'L').replace(yellow[0],'B')

    textbox_output_string = ''

    if default[0] in input_cube:
        textbox_output_string += 'Unfilled input cube\n'
    else:
        try:
            solve = kociemba.solve(input_cube)
        except:
            textbox_output_string += 'Invalid input cube\n'
    try:
        solve = kociemba.solve(output_cube)
    except:
        textbox_output_string += 'Invalid output cube\n'

    if  textbox_output_string == '':
        if input_cube == output_cube:
            textbox_output_string += 'Already solved\n'
        else:
            textbox_output_string += f'Solution:\n{kociemba.solve(input_cube,output_cube).replace(' ','\n')}'

    textboxoutput.delete("0.0", "end")
    textboxoutput.insert('0.0', textbox_output_string)

    textboxoutput.configure(state='disabled')


class input_button(ctk.CTkButton):
    """A custom button class that represents a clickable cell in the Rubik's cube interface.
    
    This class extends CTkButton to create buttons that can be clicked or filled by hovering
    while holding the spacebar. Each button updates both the main cube view and the small
    preview when its color changes.
    
    Attributes:
        master: The parent widget this button belongs to
        identifier: A number identifying the button's position (1-9) in the face
    """
    def __init__(self, master, identifier):
        # Initialize the button with default styling and disabled state
        super().__init__(master=master,
        bg_color = bg[0],
        text = '',
        height = 50,
        width = 50,
        fg_color = default[0],
        command = self.set_input_button,
        state='disabled')
        self.master = master
        self.identifier = identifier
        self._last_state_update = 0
        self._state_cache = {}
        self.bind('<Enter>', self.fill)

    @functools.lru_cache(maxsize=32)
    def _get_small_frame_label(self):
        """Cache access to small frame label to greenuce attribute lookups"""
        return getattr(self.master.master.small_frame, 
                      f'frame{self.master.color[1]}').__dict__.get(f'label{self.identifier}')

    def set_input_button(self):
        """Change the button's color to the currently selected color and update the small preview.
        Also triggers a solve attempt after the color change."""
        self.configure(fg_color=selector[0])
        label = self._get_small_frame_label()
        if label:
            label.configure(fg_color=selector[0])
        solve()

    def fill(self, x):
        """Handle hover events - if spacebar is pressed, change the button's color.
        
        Args:
            x: The event object (unused but requigreen for binding)
        """
        if win32api.GetKeyState(0x20) < 0:  # Check if spacebar (0x20) is pressed
            self.set_input_button()

    @functools.lru_cache(maxsize=32)
    def _get_reset_color(self):
        """Cache color calculation for reset"""
        return self.master.color[0] if self.master.master.altreset else default[0]

    def reset_button(self):
        """Reset the button's color back to either the face color or default color
        depending on whether this is for the output cube (altreset=True) or input cube."""
        reset_color = self._get_reset_color()
        self.configure(fg_color=reset_color)
        label = self._get_small_frame_label()
        if label:
            label.configure(fg_color=reset_color)


class big_face(ctk.CTkFrame):
    """A frame representing one face of the Rubik's cube with 9 buttons.
    
    Creates a 3x3 grid of buttons representing one face of the cube,
    with the center button being a fixed color label.
    
    Attributes:
        master: Parent widget
        color: Tuple of (hex_color, color_name) for the face's center color
    """
    def __init__(self, master, color):
        super().__init__(master=master, width=160, height=160, fg_color=bg[0])
        self.button1 = input_button(master=self,identifier=1)
        self.button2 = input_button(master=self,identifier=2)
        self.button3 = input_button(master=self,identifier=3)
        self.button4 = input_button(master=self,identifier=4)
        self.button5 = ctk.CTkLabel(master=self,
                                    bg_color=bg[0],
                                    text='',
                                    height=50,
                                    width=50,
                                    fg_color=color[0],
                                    corner_radius=6)
        self.button6 = input_button(master=self,identifier=6)
        self.button7 = input_button(master=self,identifier=7)
        self.button8 = input_button(master=self,identifier=8)
        self.button9 = input_button(master=self,identifier=9)
        self.button1.place(x=0, y=0)
        self.button2.place(x=55, y=0)
        self.button3.place(x=110, y=0)
        self.button4.place(x=0, y=55)
        self.button5.place(x=55, y=55)
        self.button6.place(x=110, y=55)
        self.button7.place(x=0, y=110)
        self.button8.place(x=55, y=110)
        self.button9.place(x=110, y=110)
        self.master = master
        self.color = color
    
    def reset_face(self):
        """Reset all buttons on the face to their default or face color."""
        self.button1.reset_button()
        self.button2.reset_button()
        self.button3.reset_button()
        self.button4.reset_button()
        self.button6.reset_button()
        self.button7.reset_button()
        self.button8.reset_button()
        self.button9.reset_button()

    def return_state(self):
        """Return the current state of the face as a string of colors."""
        return f'{self.button1.cget("fg_color")}{self.button2.cget("fg_color")}{self.button3.cget("fg_color")}{self.button4.cget("fg_color")}{self.button5.cget("fg_color")}{self.button6.cget("fg_color")}{self.button7.cget("fg_color")}{self.button8.cget("fg_color")}{self.button9.cget("fg_color")}'

    def enable_buttons(self):
        """Enable all buttons on the face."""
        self.button1.configure(state='normal')
        self.button2.configure(state='normal')
        self.button3.configure(state='normal')
        self.button4.configure(state='normal')
        self.button6.configure(state='normal')
        self.button7.configure(state='normal')
        self.button8.configure(state='normal')
        self.button9.configure(state='normal')

    def update_hover(self):
        """Update hover color for all buttons on the face."""
        self.button1.configure(hover_color=dark(selector[0]))
        self.button2.configure(hover_color=dark(selector[0]))
        self.button3.configure(hover_color=dark(selector[0]))
        self.button4.configure(hover_color=dark(selector[0]))
        self.button6.configure(hover_color=dark(selector[0]))
        self.button7.configure(hover_color=dark(selector[0]))
        self.button8.configure(hover_color=dark(selector[0]))
        self.button9.configure(hover_color=dark(selector[0]))

class big_frame(ctk.CTkFrame):
    """A frame representing the entire Rubik's cube with all six faces.
    
    Includes functionality for resetting, enabling buttons, and updating hover effects.
    
    Attributes:
        name: Name of the cube (e.g., 'Input Cube')
        altreset: Boolean indicating whether to reset to alternate colors
    """
    def __init__(self,name,altreset):
        super().__init__(master=root, height=520, width=700, fg_color=bg[0])
        self.framewhite = big_face(master=self, color=white)
        self.framegreen = big_face(master=self, color=green)
        self.frameyellow = big_face(master=self, color=yellow)
        self.frameorange = big_face(master=self, color=orange)
        self.framered = big_face(master=self, color=red)
        self.frameblue = big_face(master=self, color=blue)
        self.framewhite.place(x=180, y=180)
        self.framegreen.place(x=180, y=360)
        self.frameyellow.place(x=540, y=180)
        self.frameorange.place(x=0, y=180)
        self.framered.place(x=360, y=180)
        self.frameblue.place(x=180, y=0)
        self.reset_button = ctk.CTkButton(master=self,
                                        width=160,
                                        height=40,
                                        fg_color=theme[0],
                                        text='Reset',
                                        hover_color=dark(theme[0]),
                                        command=self.reset_frame,
                                        font=('Segoe UI',16))
        self.reset_button.place(x=0, y=480)
        self.small_frame = small_frame(name=name)
        self.altreset = altreset
        if altreset == True:
            self.reset_frame()

    def reset_frame(self):
        """Reset all faces of the cube to their default or alternate colors."""
        self.framewhite.reset_face()
        self.framegreen.reset_face()
        self.frameyellow.reset_face()
        self.frameorange.reset_face()
        self.framered.reset_face()
        self.frameblue.reset_face()
        try: solve()
        except: pass

    def enable_buttons(self):
        """Enable all buttons on all faces of the cube."""
        self.framewhite.enable_buttons()
        self.framegreen.enable_buttons()
        self.frameyellow.enable_buttons()
        self.frameorange.enable_buttons()
        self.framered.enable_buttons()
        self.frameblue.enable_buttons()

    def update_hover(self):
        """Update hover color for all buttons on all faces of the cube."""
        self.framewhite.update_hover()
        self.framegreen.update_hover()
        self.frameyellow.update_hover()
        self.frameorange.update_hover()
        self.framered.update_hover()
        self.frameblue.update_hover()


class small_label(ctk.CTkLabel):
    """A small label representing a single cell in the miniature cube preview."""
    def __init__(self,master):
        super().__init__(master=master,
                        width=15,
                        height=15,
                        fg_color=default[0],
                        corner_radius=2,
                        text='')

class small_face(ctk.CTkFrame):
    """A miniature representation of one face of the Rubik's cube.
    
    Creates a 3x3 grid of labels representing one face of the cube.
    
    Attributes:
        master: Parent widget
        color: Tuple of (hex_color, color_name) for the face's center color
    """
    def __init__(self, master, color):
        super().__init__(master=master, width=51, height=51, fg_color=bg[0])
        self.label1 = small_label(master=self)
        self.label2 = small_label(master=self)
        self.label3 = small_label(master=self)
        self.label4 = small_label(master=self)
        self.label5 = ctk.CTkFrame(master=self,
                                    width=15,
                                    height=15,
                                    fg_color=color[0],
                                    corner_radius=2)
        self.label6 = small_label(master=self)
        self.label7 = small_label(master=self)
        self.label8 = small_label(master=self)
        self.label9 = small_label(master=self)
        self.label1.place(x=0, y=0)
        self.label2.place(x=18, y=0)
        self.label3.place(x=36, y=0)
        self.label4.place(x=0, y=18)
        self.label5.place(x=18, y=18)
        self.label6.place(x=36, y=18)
        self.label7.place(x=0, y=36)
        self.label8.place(x=18, y=36)
        self.label9.place(x=36, y=36)

class small_frame(ctk.CTkFrame):
    """A miniature preview of the entire cube showing all faces.
    
    Creates a small version of the cube with all six faces arranged
    in a cross pattern for preview purposes.
    
    Attributes:
        name: Label text to show above the preview
    """
    def __init__(self,name):
        super().__init__(master=root, height=161, width=213, fg_color=bg[0])
        self.framewhite = small_face(master=self, color=white)
        self.framegreen = small_face(master=self, color=green)
        self.frameyellow = small_face(master=self, color=yellow)
        self.frameorange = small_face(master=self, color=orange)
        self.framered = small_face(master=self, color=red)
        self.frameblue = small_face(master=self, color=blue)
        self.framewhite.place(x=54, y=54)
        self.framegreen.place(x=54, y=108)
        self.frameyellow.place(x=162, y=54)
        self.frameorange.place(x=0, y=54)
        self.framered.place(x=108, y=54)
        self.frameblue.place(x=54, y=0)
        
        self.name_label = ctk.CTkLabel(master=self, width=105, height=51, fg_color=bg[0], text=name, font=('Segoe UI',16), text_color=theme[0])
        self.name_label.place(x=108, y=0)


input_frame = big_frame(name='Input Cube',altreset=False)
output_frame = big_frame(name='Output Cube',altreset=True)
output_frame.small_frame.place(x=507,y=380)
input_frame.place(x=20,y=20)


@threaded
def i_frame_trigger():
    multiprocessed(animate(outline_io_label,0,0,1))
    outline_io_label.configure(text='Input Cube')
    input_frame.place(x=20,y=20)
    output_frame.small_frame.place(x=507,y=380)
    output_frame.place_forget()
    input_frame.small_frame.place_forget()
@threaded
def o_frame_trigger():
    multiprocessed(animate(outline_io_label,170,0,1))
    outline_io_label.configure(text='Output Cube')
    output_frame.place(x=20,y=20)
    input_frame.small_frame.place(x=507,y=380)
    input_frame.place_forget()
    output_frame.small_frame.place_forget()
    input_frame.small_frame.lift()

io_frame = ctk.CTkFrame(master=root, width=340, height=40, fg_color=default[0], corner_radius=6)
i_button = ctk.CTkButton(master=io_frame, width=170, height=40,bg_color='#000001', fg_color='transparent', text='Input Cube', hover_color=dark(theme[0]), font=('Segoe UI',16), command=i_frame_trigger)
o_button = ctk.CTkButton(master=io_frame,width=170, height=40,bg_color='#000001', fg_color='transparent', text='Output Cube', hover_color=dark(theme[0]), font=('Segoe UI',16), command=o_frame_trigger)
outline_io_label = ctk.CTkLabel(master=io_frame, text='Input Cube', width=170, height=40,bg_color='#000001', fg_color=theme[0], corner_radius=6, font=('Segoe UI',16))
outline_io_label.place(x=0, y=0)
i_button.place(x=0,y=0)
o_button.place(x=170,y=0)
io_frame.place(x=380,y=20)
pywinstyles.set_opacity(i_button, color="#000001")
pywinstyles.set_opacity(o_button, color="#000001")
pywinstyles.set_opacity(outline_io_label, color="#000001")


@functools.lru_cache(maxsize=32)
def _get_next_color(current_color, direction):
    """Cache color sequence calculations for smoother scrolling"""
    colors = [white, green, yellow, orange, red, blue]
    if current_color not in colors:
        return white
    current_idx = colors.index(current_color)
    if direction < 0:
        next_idx = (current_idx + 1) % len(colors)
    else:
        next_idx = (current_idx - 1) % len(colors)
    return colors[next_idx]

@debounce(0.1)
def scroll_selector(dir):
    """Handle mouse wheel scrolling to change the current color selector."""
    global selector
    abs_coord_x = root.winfo_pointerx() - root.winfo_rootx()
    abs_coord_y = root.winfo_pointery() - root.winfo_rooty()

    if not(740 < abs_coord_x < 915 and 20 < abs_coord_y < 540):
        if selector == default:
            white_selector_button.set_selector()
        else:
            next_color = _get_next_color(selector, dir.delta)
            exec(f'{next_color[1]}_selector_button.set_selector()')


class selector_button(ctk.CTkButton):
    """A button in the color selector palette.
    
    Creates a clickable button that sets the current color for
    painting the cube faces. Includes hover effects and animation.
    
    Attributes:
        color: Tuple of (hex_color, color_name) for this selector button
    """
    def __init__(self, color):
        super().__init__(master=selector_frame,
        bg_color = bg[0],
        text = '',
        width = 40,
        height = 40,
        fg_color = color[0],
        hover_color = dark(color[0]),
        command = self.set_selector)
        self.place(x=0, y=0)
        self.color = color

    @threaded
    def set_selector(self):
        """Set the current color selector and update hover effects."""
        global selector
        if selector == default:
            input_frame.enable_buttons()
            output_frame.enable_buttons()
            outline_selector_frame.place(x=self.winfo_x()-5, y=0)
        else:
            multiprocessed(animate(outline_selector_frame, (self.winfo_x()/scale_factor)-5, 0, 1))
        selector = self.color
        input_frame.update_hover()
        output_frame.update_hover()

selector_frame = ctk.CTkFrame(master=root,width=300,height=50,fg_color=bg[0])
outline_selector_frame = ctk.CTkFrame(master=selector_frame,width=50,height=50,border_width=2,border_color=theme[0],fg_color='transparent')
white_selector_button = selector_button(white)
green_selector_button = selector_button(green)
yellow_selector_button = selector_button(yellow)
orange_selector_button = selector_button(orange)
red_selector_button = selector_button(red)
blue_selector_button = selector_button(blue)
white_selector_button.place(x=5,y=5)
green_selector_button.place(x=55,y=5)
yellow_selector_button.place(x=105,y=5)
orange_selector_button.place(x=155,y=5)
red_selector_button.place(x=205,y=5)
blue_selector_button.place(x=255,y=5)
selector_frame.place(x=405,y=95)


outputframe = ctk.CTkFrame(master=root,height=520,width=240,fg_color=bg[0])
textboxoutput = ctk.CTkTextbox(master=outputframe,fg_color='#171717',state='disabled',height=520,width=225,corner_radius=6,activate_scrollbars=False,text_color=theme[0],font=('Arial',24))
scbar = ctk.CTkScrollbar(master=outputframe,width=15, command=textboxoutput.yview)
textboxoutput.configure(yscrollcommand=scbar.set)
scbar.pack(side="right", fill="y")
textboxoutput.pack(side = 'left', fill = 'both', expand=True)
outputframe.place(x=740,y=20)


t2 = threading.Thread(target=lambda:root.bind('<MouseWheel>',scroll_selector)).start()
if __name__ == '__main__':
    root.mainloop()
