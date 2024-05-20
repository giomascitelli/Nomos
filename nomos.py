import tkinter as tk
from tkinter import ttk
import json
import os
import time
import re
import math

class ProgressBarTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.progress_bars = []
        self.load_from_json()

        add_button = ttk.Button(self, text="Add", command=self.add_progress_bar)
        add_button.pack(side="bottom")

    def add_progress_bar(self, title="Progress", value=0, running=False, elapsed_time=None, level=0):
        frame = ttk.Frame(self)
        frame.pack(fill="x")

        label = ttk.Label(frame, text=title, width=20)  # Set a fixed width
        label.grid(row=0, column=0)  # Changed to grid

        # Bind double-click event to the label
        label.bind("<Double-1>", lambda e: self.edit_title(label))

        progress_bar = ttk.Progressbar(frame, length=200, mode='determinate', value=value)  # Adjusted size
        progress_bar.grid(row=0, column=1, sticky="ew")  # Changed to grid

        timer_label = ttk.Label(frame, text=self.format_time(value))
        timer_label.grid(row=0, column=2)  # Added timer label

        level_label = ttk.Label(frame, text=f"Level {level}")
        level_label.grid(row=1, column=0)  # Moved level label to the second row

        # Create a new frame for the buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=1, column=1, columnspan=3)  # Changed to grid

        start_pause_button = ttk.Button(button_frame, text="Start" if not running else "Pause", command=lambda: self.start_pause_timer(progress_bar))
        start_pause_button.pack(side="left")

        delete_button = ttk.Button(button_frame, text="Delete", command=lambda: self.delete_progress_bar(frame))
        delete_button.pack(side="left")

        pb = {"frame": frame, "label": label, "progress_bar": progress_bar, "timer_label": timer_label, "level_label": level_label, "start_pause_button": start_pause_button, "running": running, "start_time": time.time(), "elapsed_time": elapsed_time or 0, "level": level}
        self.progress_bars.append(pb)
        return pb  # Return the progress bar dictionary

    def edit_title(self, label):
        entry = tk.Entry(self)
        entry.insert(0, label["text"])
        entry.pack(side="left", fill="x", expand=True)
        entry.focus_set()

        entry.bind('<Return>', lambda e: self.update_title(label, entry))
        entry.bind('<FocusOut>', lambda e: self.update_title(label, entry))

    def update_title(self, label, entry):
        label["text"] = entry.get()
        entry.destroy()

    def delete_progress_bar(self, frame):
        self.progress_bars = [pb for pb in self.progress_bars if pb["frame"] != frame]
        frame.destroy()

    def start_pause_timer(self, progress_bar):
        for pb in self.progress_bars:
            if pb["progress_bar"] == progress_bar:
                pb["running"] = not pb["running"]
                pb["start_pause_button"]["text"] = "Pause" if pb["running"] else "Start"
                if pb["running"]:
                    pb["start_time"] = time.time() - pb["elapsed_time"]
                self.update_progress_bar(progress_bar)

    def format_time(self, seconds):
        days, remainder = divmod(seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(days)}d, {int(hours)}h, {int(minutes)}m, {int(seconds)}s"

    def update_progress_bar(self, progress_bar):
        for pb in self.progress_bars:
            if pb["progress_bar"] == progress_bar and pb["running"]:
                elapsed_time = time.time() - pb["start_time"]
                pb["progress_bar"]["value"] = (elapsed_time % 28800) * 100 / 28800  # Reset progress bar every minute
                pb["timer_label"]["text"] = self.format_time(elapsed_time)  # Update timer label
                pb["level"] = math.floor(elapsed_time / 28800)  # Calculate level based on elapsed time
                pb["level_label"]["text"] = f"Level {pb['level']}"
                pb["elapsed_time"] = elapsed_time
                self.after(1000, self.update_progress_bar, progress_bar)

    def save_to_json(self):
        data = [{"title": pb["label"]["text"], 
                "value": round(pb["progress_bar"]["value"], 2),  # Round to 2 decimal places
                "running": pb["running"], 
                "elapsed_time": round(pb.get("elapsed_time", 0), 2),  # Round to 2 decimal places
                "level": pb.get("level", 0)} 
                for pb in self.progress_bars]
        with open("progress_bars.json", "w") as f:
            json.dump(data, f, indent=4)

    def load_from_json(self):
        if os.path.exists("progress_bars.json"):
            with open("progress_bars.json", "r") as f:
                data = json.load(f)
            for pb in data:
                progress_bar = self.add_progress_bar(pb["title"], pb["value"], pb["running"], pb.get("elapsed_time"), pb.get("level"))
                progress_bar["progress_bar"]["value"] = pb["value"]
                progress_bar["timer_label"]["text"] = self.format_time(pb.get("elapsed_time", 0))

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Nomos")
        self.geometry("405x500")

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        self.tab1 = ProgressBarTab(self.notebook)
        self.tab2 = ttk.Frame(self.notebook)

        self.notebook.add(self.tab1, text="Learning")
        self.notebook.add(self.tab2, text="Jobs")

        self.on_top_image = tk.PhotoImage(file="static/alwaysontop.png")
        self.on_top_button = None

        self.create_table()

        self.timers = {}  # Store timers for each row

        self.load_from_json()

        self.protocol("WM_DELETE_WINDOW", self.on_close)



    def create_table(self):
        style = ttk.Style(self)
        style.configure("Treeview", rowheight=25)
        style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))
        style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])
        style.configure("Treeview", font=("Helvetica", 10), background="white", foreground="black")
        style.configure("Treeview.Heading", background="#404040", foreground="white", relief="flat")
        style.map("Treeview.Heading", relief=[('active', 'groove'), ('pressed', 'sunken')])

        # Centered columns
        style.configure("mystyle.Treeview", highlightthickness=0, bd=0, font=('Sans Serif', 10))
        style.configure("mystyle.Treeview.Heading", font=('Sans Serif', 11, 'bold'))
        style.layout("mystyle.Treeview", [('mystyle.Treeview.treearea', {'sticky': 'nswe'})])
        style.configure("mystyle.Treeview", background="white", foreground="black")
        style.configure("mystyle.Treeview.Heading", background="#404040", foreground="black", relief="flat")
        style.map("mystyle.Treeview.Heading", relief=[('active', 'groove'), ('pressed', 'sunken')])

        self.tree = ttk.Treeview(self.tab2, columns=("Title", "Time", "Value", "Earnings p/h", "Action"), show="headings", style="mystyle.Treeview")
        self.tree.heading("Title", text="Title", anchor='center')
        self.tree.heading("Time", text="Time", anchor='center')
        self.tree.heading("Value", text="Value", anchor='center')
        self.tree.heading("Earnings p/h", text="Earnings p/h", anchor='center')
        self.tree.heading("Action", text="Action", anchor='center')

        # Set column width
        self.tree.column("Title", width=80, anchor='center')
        self.tree.column("Time", width=100, anchor='center')
        self.tree.column("Value", width=60, anchor='center')
        self.tree.column("Earnings p/h", width=100, anchor='center')
        self.tree.column("Action", width=50, anchor='center')

        self.tree.bind("<Double-1>", self.on_double_click)
        self.tree.bind("<Button-3>", self.delete_row)  # Right click to delete row

        self.tree.pack(fill="both", expand=True)  # Make the table adjust to window size
        self.create_on_top_button()

        add_button = ttk.Button(self.tab2, text="Add", command=self.add_row)
        add_button.pack(side="bottom")

    def toggle_on_top(self):
        self.on_top = not getattr(self, 'on_top', False)
        self.attributes("-topmost", self.on_top)

    def create_on_top_button(self):
        self.on_top_button = tk.Button(self, image=self.on_top_image, command=self.toggle_on_top, borderwidth=0, highlightthickness=0)
        self.on_top_button.image = self.on_top_image
        self.on_top_button.place(x=365, y=0)

    def on_close(self):
        self.tab1.save_to_json()
        self.update_all_timers()
        self.save_to_json()
        self.destroy()

    def update_all_timers(self):
        for item in self.timers:
            if self.timers[item]["running"]:
                self.timers[item]["elapsed"] = time.time() - self.timers[item]["start"]

    def on_double_click(self, event):
        item = self.tree.identify('item', event.x, event.y)
        column = self.tree.identify('column', event.x, event.y)

        if column == "#5":
            self.start_pause_timer(item)
        elif column in ["#1", "#4"]:
            text = self.tree.item(item, "values")[int(column[1]) - 1]
            self.entry = tk.Entry(self.tree, text=text)
            self.entry.place(x=event.x, y=event.y, anchor='w')

            self.entry.focus_set()

            self.entry.bind('<Return>', lambda e: self.update_item(item, column))
            self.entry.bind('<FocusOut>', lambda e: self.update_item(item, column))

    def start_pause_timer(self, item):
        if item in self.timers:
            if self.timers[item]["running"]:
                self.timers[item]["running"] = False
                self.tree.set(item, "#5", "Start")
            else:
                self.timers[item]["start"] = time.time() - self.timers[item]["elapsed"]
                self.timers[item]["running"] = True
                self.tree.set(item, "#5", "Pause")
        else:
            self.timers[item] = {"start": time.time(), "elapsed": 0, "running": True}
            self.tree.set(item, "#5", "Pause")

        # Apply the tag to the action column
        self.tree.item(item, tags=("action",))

        self.update_timer(item)

    def time_to_seconds(self, time_str):
        d, h, m, s = map(int, re.findall(r'\d+', time_str))
        return d * 86400 + h * 3600 + m * 60 + s

    def format_time(self, seconds):
        days, seconds = divmod(seconds, 86400)
        hours, seconds = divmod(seconds, 3600)
        minutes, seconds = divmod(seconds, 60)
        return f"{int(days)}d {int(hours)}h {int(minutes)}m {int(seconds)}s"

    def update_timer(self, item):
        if item in self.timers and self.timers[item]["running"]:
            self.timers[item]["elapsed"] = time.time() - self.timers[item]["start"]
            formatted_time = self.format_time(self.timers[item]["elapsed"])
            self.tree.set(item, "#2", formatted_time)

            # Update the value in column 3
            value_per_hour_str = self.tree.set(item, "#4")
            value_per_hour = float(value_per_hour_str.replace('$ ', '') or 0)
            value = value_per_hour * self.timers[item]["elapsed"] / 3600
            self.tree.set(item, "#3", f"$ {value:.2f}")

            # Update every 1 second
            self.after(1000, self.update_timer, item)

    def add_row(self):
        item = self.tree.insert("", "end", values=("Job", self.format_time(0), "$ 0.00", "$ 0.00", "Start"))
        self.timers[item] = {"start": time.time(), "elapsed": 0, "running": False}
        self.save_to_json()

        # Apply the tag to the action column
        self.tree.item(item, tags=("action",))

    def update_item(self, item, column):
        if column == "#4":
            # Check if the input is a valid monetary value
            if not re.match(r'^\d+(\.\d{2})?$', self.entry.get()):
                self.entry.destroy()
                return
            else:
                # Format the value as "$ {value}"
                value = f"$ {float(self.entry.get()):.2f}"
                self.tree.set(item, column, value)
                self.entry.destroy()
                self.save_to_json()
                return

        self.tree.set(item, column, self.entry.get())
        self.entry.destroy()
        self.save_to_json()

    def delete_row(self, event):
        item = self.tree.identify('item', event.x, event.y)
        self.tree.delete(item)
        if item in self.timers:
            del self.timers[item]
        self.save_to_json()

    def save_to_json(self):
        items = self.tree.get_children()
        data = []
        for item in items:
            row = list(self.tree.item(item)["values"])
            if item in self.timers:
                row[1] = self.format_time(self.timers[item]["elapsed"])
                row[3] = self.tree.set(item, "#4")
            data.append(row)

        with open("jobs.json", "w") as f:
            json.dump(data, f)

    def load_from_json(self):
        if os.path.exists("jobs.json"):
            with open("jobs.json", "r") as f:
                data = json.load(f)

            for row in data:
                item = self.tree.insert("", "end", values=row)
                self.timers[item] = {"start": time.time(), "elapsed": self.time_to_seconds(row[1]), "running": False}
                self.tree.set(item, "#4", row[3])

if __name__ == "__main__":
    app = App()
    app.mainloop()

