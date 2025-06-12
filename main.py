import tkinter as tk
from tkinter import colorchooser, ttk

class DrawingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sketchpad Web")

        self.mode = tk.StringVar(value="Titik")
        self.color = "#000000"
        self.start_x = self.start_y = None
        self.current_preview = None

        self.shapes = []      # Stack: (item_id, shape_data)
        self.undo_stack = []  # Stack: shape_data

        self.build_ui()

    def build_ui(self):
        toolbar = tk.Frame(self.root, padx=10, pady=10)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        tk.Label(toolbar, text="Mode:").pack(side=tk.LEFT)
        mode_menu = ttk.Combobox(toolbar, textvariable=self.mode,
            values=["Titik", "Titik Bersambung", "Garis", "Persegi", "Lingkaran", "Elips", "Hapus"],
            state="readonly")
        mode_menu.pack(side=tk.LEFT, padx=5)

        tk.Label(toolbar, text="Warna:").pack(side=tk.LEFT, padx=(10, 0))
        self.color_preview = tk.Button(toolbar, bg=self.color, width=3, command=self.choose_color)
        self.color_preview.pack(side=tk.LEFT)

        action_frame = tk.Frame(toolbar)
        action_frame.pack(side=tk.RIGHT)
        tk.Button(action_frame, text="Undo", command=self.undo).pack(side=tk.LEFT, padx=5)
        tk.Button(action_frame, text="Redo", command=self.redo).pack(side=tk.LEFT)
        tk.Button(action_frame, text="Clear All", command=self.clear_canvas).pack(side=tk.LEFT, padx=5)

        self.canvas = tk.Canvas(self.root, bg="white", width=800, height=500)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

    def choose_color(self):
        color_code = colorchooser.askcolor(title="Pilih Warna")
        if color_code[1]:
            self.color = color_code[1]
            self.color_preview.configure(bg=self.color)

    def on_click(self, event):
        self.start_x, self.start_y = event.x, event.y
        if self.mode.get() == "Titik":
            shape = self.canvas.create_oval(event.x-2, event.y-2, event.x+2, event.y+2, fill=self.color, outline="")
            shape_data = ("Titik", event.x, event.y, event.x, event.y, self.color)
            self.shapes.append((shape, shape_data))
            self.undo_stack.clear()
        elif self.mode.get() == "Hapus":
            closest = self.canvas.find_closest(event.x, event.y)
            if closest:
                shape_id = closest[0]
                shape_tuple = next(((sid, data) for sid, data in self.shapes if sid == shape_id), None)
                if shape_tuple:
                    self.canvas.delete(shape_id)
                    self.shapes.remove(shape_tuple)
                    self.undo_stack.append(shape_tuple)

    def on_drag(self, event):
        if self.mode.get() == "Titik Bersambung":
            shape = self.canvas.create_oval(event.x - 2, event.y - 2, event.x + 2, event.y + 2,
                                            fill=self.color, outline="")
            shape_data = ("Titik", event.x, event.y, event.x, event.y, self.color)
            self.shapes.append((shape, shape_data))
            self.undo_stack.clear()
            return

        if self.mode.get() not in ["Garis", "Persegi", "Lingkaran", "Elips"]:
            return

        if self.current_preview:
            self.canvas.delete(self.current_preview)

        x1, y1 = self.start_x, self.start_y
        x2, y2 = event.x, event.y

        if self.mode.get() == "Garis":
            self.current_preview = self.canvas.create_line(x1, y1, x2, y2, fill=self.color, width=2)
        elif self.mode.get() == "Persegi":
            self.current_preview = self.canvas.create_rectangle(x1, y1, x2, y2, outline=self.color, width=2)
        elif self.mode.get() == "Lingkaran":
            r = ((x2 - x1)**2 + (y2 - y1)**2)**0.5
            self.current_preview = self.canvas.create_oval(x1 - r, y1 - r, x1 + r, y1 + r, outline=self.color, width=2)
        elif self.mode.get() == "Elips":
            self.current_preview = self.canvas.create_oval(x1, y1, x2, y2, outline=self.color, width=2)

    def on_release(self, event):
        if self.mode.get() in ["Titik", "Titik Bersambung", "Hapus"]:
            return

        x1, y1 = self.start_x, self.start_y
        x2, y2 = event.x, event.y
        shape_type = self.mode.get()
        shape_id = None

        if self.current_preview:
            self.canvas.delete(self.current_preview)
            self.current_preview = None

        if shape_type == "Garis":
            shape_id = self.canvas.create_line(x1, y1, x2, y2, fill=self.color, width=2)
        elif shape_type == "Persegi":
            shape_id = self.canvas.create_rectangle(x1, y1, x2, y2, outline=self.color, width=2)
        elif shape_type == "Lingkaran":
            r = ((x2 - x1)**2 + (y2 - y1)**2)**0.5
            shape_id = self.canvas.create_oval(x1 - r, y1 - r, x1 + r, y1 + r, outline=self.color, width=2)
            x2, y2 = x1 + r, y1 + r
        elif shape_type == "Elips":
            shape_id = self.canvas.create_oval(x1, y1, x2, y2, outline=self.color, width=2)

        if shape_id:
            shape_data = (shape_type, x1, y1, x2, y2, self.color)
            self.shapes.append((shape_id, shape_data))
            self.undo_stack.clear()

    def undo(self):
        if self.shapes:
            shape_id, data = self.shapes.pop()
            self.canvas.delete(shape_id)
            self.undo_stack.append((shape_id, data))

    def redo(self):
        if self.undo_stack:
            _, data = self.undo_stack.pop()
            shape_type, x1, y1, x2, y2, color = data
            new_id = None

            if shape_type == "Titik":
                new_id = self.canvas.create_oval(x1-2, y1-2, x1+2, y1+2, fill=color, outline="")
            elif shape_type == "Garis":
                new_id = self.canvas.create_line(x1, y1, x2, y2, fill=color, width=2)
            elif shape_type == "Persegi":
                new_id = self.canvas.create_rectangle(x1, y1, x2, y2, outline=color, width=2)
            elif shape_type == "Lingkaran":
                new_id = self.canvas.create_oval(x1, y1, x2, y2, outline=color, width=2)
            elif shape_type == "Elips":
                new_id = self.canvas.create_oval(x1, y1, x2, y2, outline=color, width=2)

            if new_id:
                self.shapes.append((new_id, data))

    def clear_canvas(self):
        for sid, _ in self.shapes:
            self.canvas.delete(sid)
        self.shapes.clear()
        self.undo_stack.clear()

if __name__ == "__main__":
    root = tk.Tk()
    app = DrawingApp(root)
    root.mainloop()
