import customtkinter as ctk
from tkinter import simpledialog, messagebox, ttk, IntVar, Scale
from PIL import Image, ImageTk, ImageGrab
from PIL import Image as PILImage
import networkx as nx
import numpy as np
import pandas as pd
from tkinter.colorchooser import askcolor
import os


class FlowsheetApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1200x800")
        self.root.title("Easy PFD Draw v1.0")

        # Initialize arrow properties
        self.arrow_color = "blue"  # Default arrow color
        self.arrow_size = 2  # Default arrow size
        self.eraser_size = 10  # Default eraser size (can be adjusted)
        self.text_color = "black"  # Default text color
        self.text_size_var = IntVar(value=12)

        # To hold image references
        self.images = {}

        # Initialize canvas items dictionary
        self.canvas_items = {}

        # Initialize canvas and machinery selection menu
        self.initialize_ui()
        self.graph = nx.DiGraph()
        self.drawing_mode = False
        self.current_line_points = []

    def initialize_ui(self):
        # Create a frame for the machinery selection menu
        self.menu_frame = ctk.CTkFrame(self.root)
        self.menu_frame.pack(side=ctk.LEFT, fill=ctk.Y, padx=10, pady=10)

        # Add machinery selection dropdowns
        self.add_machinery_dropdowns()

        # Arrow size and color options
        self.add_arrow_options()

        # Text size and color options
        self.add_text_options()

        # Create Draw Arrow buttons
        self.create_action_buttons()

        # Create a canvas for placing machinery and drawing streams
        self.canvas_frame = ctk.CTkFrame(self.root)
        self.canvas_frame.pack(side=ctk.RIGHT, fill=ctk.BOTH, expand=True, padx=10, pady=10)
        self.canvas = ctk.CTkCanvas(self.canvas_frame, width=800, height=600, bg="white")
        #self.draw_grid_lines()
        self.canvas.pack(fill=ctk.BOTH, expand=True)

        # Add user guide text box
        self.add_user_guide_box()

        # Bind mouse events for drawing streams
        self.canvas.bind("<Button-1>", self.canvas_click)

        # Add copyright notice
        self.add_copyright_notice()

        self.start_x, self.start_y = None, None
        self.lines = []
        self.machines = {}
        self.canvas_items = {}






    def add_user_guide_box(self):
        guide_frame = ctk.CTkFrame(self.menu_frame)
        guide_frame.pack(fill=ctk.X, padx=10, pady=10)

        guide_text = (
            "User Guide:\n"
            "1. Use 'Start Draw' to insert stream Arrows.\n"
            "2. You can insert arrow by selecting 2 points on the Canvas frame.\n"
            "3. Dont forget to click on stop drawing after finishing draw\n"
            "4. Do the same for Erasing objects within the Canvas frame\n"
            "5. Use 'Add Text' to insert text box'.\n"
            "6. Use 'Add Sticky note' to add sticky note text box in yellow box.\n"
            "7. Go fullscreen when saving as PNG file.\n"

        )

        guide_label = ctk.CTkLabel(guide_frame, text=guide_text, justify=ctk.LEFT)
        guide_label.pack(fill=ctk.X, padx=5, pady=5)


    def add_copyright_notice(self):
        copyright_frame = ctk.CTkFrame(self.menu_frame)
        copyright_frame.pack(side=ctk.BOTTOM, fill=ctk.X, padx=10, pady=5)

        copyright_label = ctk.CTkLabel(copyright_frame, text="© 2024 'AmirFaramarzpour'. All rights reserved.", justify=ctk.LEFT)
        copyright_label.pack(fill=ctk.X, padx=5, pady=5)


    def add_machinery_dropdowns(self):
        machinery = {
            "Crushing": ["Jaw Crusher", "Cone Crusher", "Screen", "Vibrating Sieve", "Belt Feeder"],
            "Grinding": ["Ball Mill Layout 1", "Ball Mill Layout 2","Rod Mill Layout 1","Rod Mill Layout 2","AG Mill","SAG Mill", "Tower Mill"],
            "Hydrocyclone": ["Hydrocyclone Layout 1", "Hydrocyclone Layout 2","Desliming"],
            "Physical Separation": ["SLon WHIMS", "Drum Magnetic Separator","RER Magnetic Separator", "Spiral","Wilfley Concentrating table"],
            "Flotation Unit": ["Flotation Cell", "Bank Cell 4","Bank Cell 2","Tank Cell","Conditioner","Column cell","Conditioner 2"],
            "Thickener": ["Clarifier","Conventional Thickener","Drum Filter"],
            "General": ["Mine pit", "Dry Stacking", "Stockpile", "dumptruck", "Tailings Dam", "Bin", "Sump and Pump","Sump"]
            # Add more machinery as needed
        }
        for machine, layouts in machinery.items():
            frame = ctk.CTkFrame(self.menu_frame)
            frame.pack(fill=ctk.X, padx=10, pady=5)

            label = ctk.CTkLabel(frame, text=machine)
            label.pack(side=ctk.LEFT)

            dropdown = ttk.Combobox(frame, values=layouts)
            dropdown.pack(side=ctk.RIGHT)
            dropdown.bind("<<ComboboxSelected>>", lambda e, m=machine, d=dropdown: self.place_machine(m, d.get()))

    #def draw_grid_lines(self):
        #canvas_width = self.canvas.winfo_reqwidth()
        #canvas_height = self.canvas.winfo_reqheight()
        #self.canvas.create_rectangle(0, 0, canvas_width, canvas_height, fill='white', outline='white')  # Ensure canvas is white
        # Draw grid lines on the canvas
        #for i in range(0, canvas_width, 20):  # Vertical lines
            #self.canvas.create_line(i, 0, i, canvas_height, fill="lightgray", tags="grid")
        #for i in range(0, canvas_height, 20):  # Horizontal lines
            #self.canvas.create_line(0, i, canvas_width, i, fill="lightgray", tags="grid")

    def add_arrow_options(self):
        arrow_frame = ctk.CTkFrame(self.menu_frame)
        arrow_frame.pack(fill=ctk.X, padx=10, pady=5)

        color_button = ctk.CTkButton(arrow_frame, text="Arrow Color", command=self.choose_color)
        color_button.pack(side=ctk.LEFT, padx=5, pady=5)

        size_label = ctk.CTkLabel(arrow_frame, text="Arrow Size:")
        size_label.pack(side=ctk.LEFT, padx=5)

        self.size_var = ctk.DoubleVar(value=self.arrow_size)
        size_slider = ctk.CTkSlider(arrow_frame, from_=1, to=10, variable=self.size_var)
        size_slider.pack(side=ctk.LEFT, padx=5)


    def choose_color(self):
        color = askcolor()[1]
        if color:
            self.arrow_color = color

    def add_text_options(self):
        text_frame = ctk.CTkFrame(self.menu_frame)
        text_frame.pack(fill=ctk.X, padx=10, pady=5)

        color_button = ctk.CTkButton(text_frame, text="Text Color", command=self.choose_text_color)
        color_button.pack(side=ctk.LEFT, padx=5, pady=5)

        size_label = ctk.CTkLabel(text_frame, text="Font Size:")
        size_label.pack(side=ctk.LEFT, padx=5)

        self.text_size_var = ctk.DoubleVar(value=12)
        size_slider = ctk.CTkSlider(text_frame, from_=8, to=72, variable=self.text_size_var)
        size_slider.pack(side=ctk.LEFT, padx=5)


    def choose_text_color(self):
        color = askcolor()[1]
        if color:
            self.text_color = color

    def add_text(self):
        text = simpledialog.askstring("Input", "Enter the text:")
        if text:
            # Default position
            x, y = 150, 150
            
            try:
                text_id = self.canvas.create_text(x, y, text=text, font=("Comic Sans MS", int(self.text_size_var.get())), fill=self.text_color, tags=("movable", "text"))

                # Make the text movable by binding motion events
                self.canvas.tag_bind(text_id, "<Button1-Motion>", self.move_text)
                self.canvas.tag_bind(text_id, "<ButtonRelease-1>", self.stop_move_text)

            except Exception as e:
                print(f"Error creating text: {e}")
                messagebox.showerror("Error", f"Failed to create text. {e}")

    def move_text(self, event):
        item = self.canvas.find_withtag("current")[0]
        x, y = event.x, event.y
        self.canvas.coords(item, x, y)

    def stop_move_text(self, event):
        item = self.canvas.find_withtag("current")[0]
        self.canvas.itemconfig(item, tags=("movable", "text"))

    def add_sticky_note_text(self):
        text = simpledialog.askstring("Input", "Enter the sticky note text:")
        if text:
            # Default position
            x, y = 150, 150
            
            try:
                # Create the text item first
                text_id = self.canvas.create_text(x, y, text=text, font=("Arial", int(self.text_size_var.get())), fill=self.text_color, tags=("movable", "sticky_note_text"))

                # Get the bounding box of the text
                bbox = self.canvas.bbox(text_id)
                x0, y0, x1, y1 = bbox

                # Create the sticky note rectangle based on the text size
                padding = 10  # Padding around the text
                sticky_note_id = self.canvas.create_rectangle(x0-padding, y0-padding, x1+padding, y1+padding, fill="yellow", outline="black", tags=("movable", "sticky_note"))

                # Ensure text is on top of the rectangle
                self.canvas.tag_raise(text_id, sticky_note_id)
                
                # Link sticky note background and text together
                self.canvas_items[sticky_note_id] = text_id
                self.canvas_items[text_id] = sticky_note_id
                
                # Bind motion events to both elements
                self.canvas.tag_bind(sticky_note_id, "<Button1-Motion>", self.move_sticky_note)
                self.canvas.tag_bind(sticky_note_id, "<ButtonRelease-1>", self.stop_move_sticky_note)
                self.canvas.tag_bind(text_id, "<Button1-Motion>", self.move_sticky_note)
                self.canvas.tag_bind(text_id, "<ButtonRelease-1>", self.stop_move_sticky_note)
            except Exception as e:
                print(f"Error creating sticky note: {e}")
                messagebox.showerror("Error", f"Failed to create sticky note. {e}")

    def move_sticky_note(self, event):
        item = self.canvas.find_withtag("current")[0]
        x, y = event.x, event.y
        linked_item = self.canvas_items.get(item)
        if linked_item:
            if self.canvas.type(item) == "rectangle":
                bbox = self.canvas.bbox(linked_item)
                x0, y0, x1, y1 = bbox
                width = x1 - x0
                height = y1 - y0
                
                # Move the rectangle to the new position
                self.canvas.coords(item, x - width//2 - 10, y - height//2 - 10, x + width//2 + 10, y + height//2 + 10)
                # Move the text to the center of the rectangle
                self.canvas.coords(linked_item, x, y)
            elif self.canvas.type(item) == "text":
                bbox = self.canvas.bbox(item)
                x0, y0, x1, y1 = bbox
                width = x1 - x0
                height = y1 - y0

                # Move the text to the new position
                self.canvas.coords(item, x, y)
                # Move the rectangle to center the text
                self.canvas.coords(linked_item, x - width//2 - 10, y - height//2 - 10, x + width//2 + 10, y + height//2 + 10)

    def stop_move_sticky_note(self, event):
        item = self.canvas.find_withtag("current")[0]
        self.canvas.itemconfig(item, tags=("movable", "sticky_note"))

    def create_action_buttons(self):
        button_frame = ctk.CTkFrame(self.menu_frame)
        button_frame.pack(padx=10, pady=5)

        self.start_draw_button = ctk.CTkButton(button_frame, text="Start Draw", command=self.start_drawing, fg_color="blue", hover_color="lightblue")
        self.start_draw_button.grid(row=0, column=0, padx=5, pady=5)

        self.stop_draw_button = ctk.CTkButton(button_frame, text="Stop Draw", command=self.stop_drawing, fg_color="blue", hover_color="lightblue")
        self.stop_draw_button.grid(row=0, column=1, padx=5, pady=5)

        self.start_erase_button = ctk.CTkButton(button_frame, text="Start Erase", command=self.start_erasing, fg_color="red", hover_color="lightcoral")
        self.start_erase_button.grid(row=1, column=0, padx=5, pady=5)

        self.stop_erase_button = ctk.CTkButton(button_frame, text="Stop Erase", command=self.stop_erasing, fg_color="red", hover_color="lightcoral")
        self.stop_erase_button.grid(row=1, column=1, padx=5, pady=5)

        self.add_text_button = ctk.CTkButton(button_frame, text="Add Text", command=self.add_text)
        self.add_text_button.grid(row=2, column=0, padx=5, pady=5, columnspan=2)

        self.save_button = ctk.CTkButton(button_frame, text="Save as PNG", command=self.save_as_png)
        self.save_button.grid(row=3, column=0, padx=5, pady=5, columnspan=2)

        self.add_sticky_note_button = ctk.CTkButton(button_frame, text="Add Sticky Note", command=self.add_sticky_note_text)
        self.add_sticky_note_button.grid(row=4, column=0, padx=5, pady=5, columnspan=2)

    def save_as_png(self):
        # Update the canvas to make sure everything is drawn
        self.canvas.update_idletasks()

        # Get the coordinates of the canvas relative to the window
        x = self.canvas.winfo_rootx() + self.canvas.winfo_x()
        y = self.canvas.winfo_rooty() + self.canvas.winfo_y()
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        # Capture the canvas content as an image
        bbox = (x, y, x + width, y + height)
        image = ImageGrab.grab(bbox)

        # Save the image as a PNG file
        image.save("canvas_output.png")

        print("PFD saved successfully as canvas_output.png")

    def place_machine(self, machine, layout):
        x, y = 50, 50  # Default position, can be adjusted to be dynamic

        # Define the folder path for the images
        img_folder = "Layouts"

        # Generate the image path based on the machine and layout selected
        img_path = os.path.join(img_folder, f"{layout.lower().replace(' ', '_')}.jpg")  # Ensure your images are named correctly

        # Load and place the image only if it exists
        try:
            img = Image.open(img_path)
            img_tk = ImageTk.PhotoImage(img)

            image_id = self.canvas.create_image(x, y, anchor=ctk.NW, image=img_tk, tags=("movable", "image"))
            self.images[image_id] = img_tk  # Keep a reference to prevent garbage collection

            text_id = self.canvas.create_text(x + 50, y + 110, text=f"{layout}", font=("Arial", 11, "bold"), tags=("movable", "text"))

            self.canvas_items[image_id] = text_id  # Track images and text together
            self.canvas_items[text_id] = image_id  # Track text and images together

            self.canvas.tag_bind(image_id, "<Button1-Motion>", self.move_machine)
            self.canvas.tag_bind(image_id, "<ButtonRelease-1>", self.stop_move_machine)
            self.canvas.tag_bind(text_id, "<Button1-Motion>", self.move_machine)
            self.canvas.tag_bind(text_id, "<ButtonRelease-1>", self.stop_move_machine)

            # Example of scaling the image manually
            #self.scale_image(image_id, 0.75, 0.75)  # Scale the image by 1.5 times

        except FileNotFoundError:
            messagebox.showerror("Error", f"Image file '{img_path}' not found.")


    def move_machine(self, event):
        item = self.canvas.find_withtag("current")[0]
        x, y = event.x, event.y
        linked_item = self.canvas_items.get(item)
        if linked_item:
            self.canvas.coords(item, x, y)
            self.canvas.coords(linked_item, x + 50, y + 110)
        else:
            self.canvas.coords(item, x, y)

    def stop_move_machine(self, event):
        item = self.canvas.find_withtag("current")[0]
        self.canvas.itemconfig(item, tags=("movable",))

    def erase_mode(self, enable):
        self.drawing_mode = False
        self.current_line_points = []
        self.canvas.unbind("<Button-1>")
        if enable:
            self.canvas.bind("<Button-1>", self.erase_click)
        else:
            self.canvas.bind("<Button-1>", self.canvas_click)

    def erase_click(self, event):
        eraser_radius = self.eraser_size
        items = self.canvas.find_overlapping(event.x - eraser_radius, event.y - eraser_radius, 
                                             event.x + eraser_radius, event.y + eraser_radius)
        for item in items:
            if "grid" not in self.canvas.gettags(item):
                linked_item = self.canvas_items.pop(item, None)
                if linked_item:
                    self.canvas.delete(linked_item)
                    del self.canvas_items[linked_item]
                self.canvas.delete(item)
                if item in self.images:
                    del self.images[item]

    def start_drawing(self):
        self.drawing_mode = True
        self.current_line_points = []
        self.canvas.unbind("<Button-1>")
        self.canvas.bind("<Button-1>", self.start_line)

    def stop_drawing(self):
        self.drawing_mode = False
        self.current_line_points = []
        self.canvas.unbind("<Button-1>")
        self.canvas.bind("<Button-1>", self.canvas_click)

    def start_erasing(self):
        self.erase_mode(True)

    def stop_erasing(self):
        self.erase_mode(False)

    def start_line(self, event):
        self.current_line_points.append((event.x, event.y))
        if len(self.current_line_points) > 1:
            self.draw_current_line()

    def draw_current_line(self):
        for i in range(len(self.current_line_points) - 1):
            line = self.canvas.create_line(
                self.current_line_points[i][0], self.current_line_points[i][1],
                self.current_line_points[i + 1][0], self.current_line_points[i + 1][1],
                arrow=ctk.LAST, fill=self.arrow_color, width=self.size_var.get(), tags="line"
            )
            self.lines.append(line)

    def canvas_click(self, event):
        if self.drawing_mode:
            self.start_line(event)

if __name__ == "__main__":
    root = ctk.CTk()
    app = FlowsheetApp(root)
    root.mainloop()
