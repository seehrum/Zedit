import tkinter as tk
from tkinter import (
    filedialog,
    colorchooser,
    font,
    simpledialog,
    Toplevel,
    Listbox,
    messagebox,
)
import json
import os


class ZenEdit:
    def __init__(self, root):
        self.root = root
        self.root.title("ZenEdit")
        self.config_file = "editor_config.json"
        self.auto_save_file = "autosave.txt"
        self.load_config()
        self.fullScreenState = False
        self.auto_save_enabled = tk.BooleanVar(value=True)
        self.root.bind("<F2>", lambda event: self.quit())
        self.root.bind("<F5>", lambda event: self.toggle_line_numbers())
        self.root.bind("<F6>", lambda event: self.show_word_char_count())
        self.root.bind("<F7>", self.search_text)
        self.root.bind("<F8>", self.replace_text)
        self.root.bind("<F9>", lambda event: self.new_file())
        self.root.bind("<F10>", lambda event: self.open_file())
        self.root.bind("<F11>", self.toggleFullScreen)
        self.root.bind("<F12>", lambda event: self.save_file())
        self.menu = tk.Menu(root)

        self.file_menu = tk.Menu(self.menu, tearoff=0)
        self.file_menu.add_command(label="New (F9)", command=self.new_file)
        self.file_menu.add_command(label="Open (F10)", command=self.open_file)
        self.file_menu.add_command(label="Save (F12)", command=self.save_file)
        self.file_menu.add_command(label="Save As...", command=self.save_as_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit (F2)", command=self.quit)

        self.edit_menu = tk.Menu(self.menu, tearoff=0)
        self.edit_menu.add_command(label="Search (F7)", command=self.search_text)
        self.edit_menu.add_command(label="Replace (F8)", command=self.replace_text)
        self.edit_menu.add_command(label="Go to Line...", command=self.goto_line)
        self.edit_menu.add_command(label="Toggle Line Numbers (F5)", command=self.toggle_line_numbers)

        self.view_menu = tk.Menu(self.menu, tearoff=0)
        self.view_menu.add_command(
            label="FullScreen (F11)", command=self.toggleFullScreen
        )
        self.view_menu.add_command(
            label="Word/Character Count (F6)", command=self.show_word_char_count
        )
        self.view_menu.add_command(
            label="Set Text Area Size", command=self.set_text_area_size
        )
        self.view_menu.add_command(
            label="Set Padding", command=self.set_padding
        )
        self.view_menu.add_command(label="Toggle Border", command=self.toggle_border)
        self.view_menu.add_command(
            label="Toggle Mouse Cursor Visibility", command=self.toggle_mouse_cursor_visibility
        )
        self.view_menu.add_command(
            label="Toggle Caret Cursor Visibility", command=self.toggle_caret_cursor_visibility
        )
        self.view_menu.add_command(
            label="Toggle Caret Cursor Blink", command=self.toggle_caret_cursor_blink
        )
        self.view_menu.add_command(
            label="Set Caret Cursor Blink Speed", command=self.set_caret_cursor_blink_speed
        )

        self.format_menu = tk.Menu(self.menu, tearoff=0)
        self.format_menu.add_command(label="Change Font", command=self.change_font)
        self.format_menu.add_command(label="Change Font Size", command=self.change_font_size)
        self.format_menu.add_command(label="Set Line Spacing", command=self.set_line_spacing)
        self.format_menu.add_command(label="Align Left", command=self.align_left)
        self.format_menu.add_command(label="Center", command=self.align_center)
        self.format_menu.add_command(label="Align Right", command=self.align_right)

        self.settings_menu = tk.Menu(self.menu, tearoff=0)
        self.settings_menu.add_command(
            label="Change Root Background Color", command=self.change_root_bg_color
        )
        self.settings_menu.add_command(
            label="Change Background Color", command=self.change_bg_color
        )
        self.settings_menu.add_command(
            label="Change Caret Cursor Color", command=self.change_caret_cursor_color
        )
        self.settings_menu.add_command(
            label="Change Text Color", command=self.change_fg_color
        )
        self.settings_menu.add_command(
            label="Change Selection Color", command=self.change_selection_color
        )
        self.settings_menu.add_command(
            label="Change Selection Text Color",
            command=self.change_selection_text_color,
        )
        self.settings_menu.add_command(
            label="Change Border Color", command=self.change_border_color
        )
        self.settings_menu.add_command(
            label="Set Border Thickness", command=self.set_border_thickness
        )
        self.settings_menu.add_command(
            label="Set Caret Cursor Thickness", command=self.set_caret_cursor_thickness
        )
        self.settings_menu.add_checkbutton(label="Enable Autosave", onvalue=True, offvalue=False, variable=self.auto_save_enabled, command=self.toggle_auto_save)


        self.menu.add_cascade(label="File", menu=self.file_menu)
        self.menu.add_cascade(label="Edit", menu=self.edit_menu)
        self.menu.add_cascade(label="View", menu=self.view_menu)
        self.menu.add_cascade(label="Format", menu=self.format_menu)
        self.menu.add_cascade(label="Settings", menu=self.settings_menu)
        self.menu.add_command(label="About", command=self.show_about)

        self.root.config(menu=self.menu, bg=self.config["root_bg_color"])
        self.frame = tk.Frame(root, bg=self.config["bg_color"])
        self.frame.pack(expand=True)
        self.current_font = font.Font(
            family=self.config["font_family"],
            size=self.config["font_size"],
            weight="bold" if self.config.get("font_bold", False) else "normal",
            slant="italic" if self.config.get("font_italic", False) else "roman",
        )

        self.text_area = tk.Text(
            self.frame,
            font=self.current_font,
            undo=True,
            bg=self.config["bg_color"],
            fg=self.config["fg_color"],
            insertbackground=self.config["caret_cursor_color"],
            insertwidth=4 if self.config["caret_cursor"] else 2,
            spacing3=self.config.get("line_spacing", 4),
            borderwidth=0,
            wrap=tk.WORD,
            highlightthickness=self.config.get("border_thickness", 1),
            highlightbackground=self.config["border_color"],
            highlightcolor=self.config["border_color"],
            selectbackground=self.config.get("selection_color", "#3399ff"),
            selectforeground=self.config.get("selection_text_color", "#ffffff"),
            width=self.config.get("text_width", 80),
            height=self.config.get("text_height", 25),
            padx=self.config.get("padding", 0),
            pady=self.config.get("padding", 0)
        )
        self.text_area.pack(side="top", fill="both", expand="yes")
        self.auto_save_interval = 5000
        self.auto_save()

        self.text_area.bind("<Control-s>", self.save_file)
        self.text_area.bind("<Control-S>", self.save_file)
        self.text_area.bind("<Control-z>", self.undo_text)
        self.text_area.bind("<Control-Z>", self.redo_text)
        self.text_area.bind("<Control-y>", self.redo_text)
        self.text_area.bind("<Control-Y>", self.redo_text)
        self.text_area.bind("<Control-a>", self.select_all)
        self.text_area.bind("<Control-A>", self.select_all)
        self.text_area.bind("<Control-x>", self.cut_text)
        self.text_area.bind("<Control-X>", self.cut_text)
        self.text_area.bind("<Control-c>", self.copy_text)
        self.text_area.bind("<Control-C>", self.copy_text)
        self.text_area.bind("<Control-v>", self.paste_text)
        self.text_area.bind("<Control-V>", self.paste_text)

    def load_config(self):
        if os.path.isfile(self.config_file):
            with open(self.config_file, "r") as file:
                self.config = json.load(file)
        else:
            self.config = {}
        self.config.setdefault("root_bg_color", "#1e1e1e")
        self.config.setdefault("font_family", "Arial")
        self.config.setdefault("font_size", 16)
        self.config.setdefault("font_bold", False)
        self.config.setdefault("font_italic", False)
        self.config.setdefault("bg_color", "#1e1e1e")
        self.config.setdefault("fg_color", "#ffffff")
        self.config.setdefault("caret_cursor_color", "white")
        self.config.setdefault("selection_color", "#3399ff")
        self.config.setdefault("selection_text_color", "#ffffff")
        self.config.setdefault("caret_cursor", False)
        self.config.setdefault("text_width", 80)
        self.config.setdefault("text_height", 25)
        self.config.setdefault("line_spacing", 4)
        self.config.setdefault("border_thickness", 1)
        self.config.setdefault("border_color", "#ffffff")
        self.config.setdefault("padding", 0)
        if hasattr(self, "text_area"):
            self.text_area.config(highlightbackground=self.config["border_color"])
            self.text_area.config(padx=self.config["padding"],pady=self.config["padding"])
# File
    def new_file(self):
        response = None
        if self.text_area.edit_modified():
            response = messagebox.askyesnocancel(
                "Save changes", "Do you want to save changes to the current file?"
            )
        if response is True:
            self.save_file()
            self.text_area.delete(1.0, tk.END)
        elif response is False:
            self.text_area.delete(1.0, tk.END)
            self.text_area.edit_modified(False)

    def open_file(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if not filepath:
            return
        with open(filepath, "r") as file:
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, file.read())
            self.current_file_path = filepath  # Store the current file path
        self.root.title(f"ZenEdit - {os.path.basename(filepath)}")

    def save_file(self, event=None):
        if hasattr(self, 'current_file_path') and self.current_file_path:
            filepath = self.current_file_path
        else:
            filepath = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            )
            if not filepath:
                return
            self.current_file_path = filepath  # Store the new file path
        with open(filepath, "w") as file:
            file.write(self.text_area.get(1.0, tk.END))
        self.root.title(f"ZenEdit - {os.path.basename(filepath)}")

    def save_as_file(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
        )
        if not filepath:
            return
        with open(filepath, "w") as file:
            file.write(self.text_area.get(1.0, tk.END))
        self.current_file_path = filepath  # Update current file path
        self.root.title(f"ZenEdit - {os.path.basename(filepath)}")

    def quit(self):
        response = False
        if self.text_area.edit_modified():
            response = messagebox.askyesnocancel(
                "Save on Exit", "Do you want to save the changes before exiting?"
            )
        if response is True:  # User chose to save changes
            self.save_file()
        elif response is None:  # User chose to cancel
            return  # Exit the method and do not close the application
        if response is not None:
            self.root.destroy()
#Edit 
    def search_text(self, event=None):
        search_query = simpledialog.askstring("Search", "Find:")
        if not search_query:
            return
        start_idx = self.text_area.index(tk.INSERT)
        search_idx = self.text_area.search(search_query, start_idx, nocase=1)
        if not search_idx:
            search_idx = self.text_area.search(
                search_query, "1.0", nocase=1, stopindex=start_idx
            )
        if search_idx:
            end_idx = f"{search_idx}+{len(search_query)}c"
            self.text_area.tag_remove(tk.SEL, "1.0", tk.END)  # Clear existing selection
            self.text_area.tag_add(tk.SEL, search_idx, end_idx)  # Select found text
            self.text_area.mark_set(
                tk.INSERT, end_idx
            )
            self.text_area.see(search_idx)  # Scroll to the found text
        else:
            messagebox.showinfo("Search", "Text not found.")
    
    def replace_text(self, event=None):
        search_query = simpledialog.askstring("Replace", "Find what:")
        if not search_query:
            return

        replacement = simpledialog.askstring("Replace", "Replace with:")
        if replacement is None:
            return

        all_text = self.text_area.get("1.0", tk.END)
        count = all_text.count(search_query)
        updated_text = all_text.replace(search_query, replacement)
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert("1.0", updated_text)

        messagebox.showinfo(
            "Replace",
            f"Replaced {count} occurrences of '{search_query}' with '{replacement}'.",
        )
    
    def goto_line(self):
        line_number = simpledialog.askinteger("Go to Line", "Enter line number:")
        if line_number is not None and line_number > 0:
            index = f"{line_number}.0"
            if self.text_area.compare(index, "<=", "end"):
                self.text_area.see(index)
                self.text_area.mark_set("insert", index)
                self.text_area.tag_remove(tk.SEL, "1.0", tk.END)
                self.text_area.tag_add(tk.SEL, index, f"{index} lineend")
#View
    def toggleFullScreen(self, event=None):
        self.fullScreenState = not self.fullScreenState
        self.root.attributes("-fullscreen", self.fullScreenState)
        if self.fullScreenState:
            self.root.config(menu="")
        else:
            self.root.config(menu=self.menu)
    
    def toggle_line_numbers(self):
        lines = self.text_area.get('1.0', 'end-1c').split('\n')
        if lines[0].split(".")[0].isdigit():
            # Assume line numbers are present, so remove them
            stripped_lines = [line.split('. ', 1)[-1] if '. ' in line else line for line in lines]
        else:
            # Add line numbers
            stripped_lines = [f"{i+1}. {line}" for i, line in enumerate(lines)]

        self.text_area.delete('1.0', 'end')
        self.text_area.insert('1.0', '\n'.join(stripped_lines))

    def show_word_char_count(self):
        text_content = self.text_area.get(1.0, "end-1c")  # Get content of text_area
        words = len(text_content.split())
        characters = len(text_content)
        messagebox.showinfo(
            "Word/Character Count", f"Words: {words}\nCharacters: {characters}"
        )

    def set_text_area_size(self):
        width = simpledialog.askinteger(
            "Text Area Width",
            "Enter width:",
            initialvalue=self.config.get("text_width", 80),
        )
        height = simpledialog.askinteger(
            "Text Area Height",
            "Enter height:",
            initialvalue=self.config.get("text_height", 25),
        )
        if width and height:
            self.config["text_width"] = width
            self.config["text_height"] = height
            self.text_area.config(width=width, height=height)
            self.save_config()
    
    def set_padding(self):
        padding = simpledialog.askinteger("Padding", "Enter padding size:", minvalue=0)
        if padding is not None:
            self.text_area.config(padx=padding, pady=padding)
            self.config["padding"] = padding
            self.save_config()
    
    def toggle_border(self):
        current_thickness = self.text_area.cget("highlightthickness")
        new_thickness = 0 if current_thickness > 0 else 1
        self.text_area.config(highlightthickness=new_thickness)
    
    def toggle_mouse_cursor_visibility(self):
        if self.text_area["cursor"] in ["", "xterm"]:
            self.text_area.config(cursor="none")
        else:
            self.text_area.config(cursor="xterm")
    
    def toggle_caret_cursor_visibility(self):
        if self.text_area['insertwidth'] > 1:
            self.text_area.config(insertwidth=0)
        else:
            self.text_area.config(insertwidth=1)
    
    def toggle_caret_cursor_blink(self):
        if self.text_area['insertofftime'] == 0:
            self.text_area.config(insertofftime=300, insertontime=600)
        else:
            self.text_area.config(insertofftime=0, insertontime=0)
    
    def set_caret_cursor_blink_speed(self):
        blink_time = simpledialog.askinteger(
            "Cursor Blink Speed",
            "Enter blink speed in milliseconds (0 for no blink):",
            minvalue=0
        )
        if blink_time is not None:
            self.text_area.config(insertofftime=blink_time, insertontime=blink_time)
#Format
    def change_font(self):
        font_window = tk.Toplevel(self.root)
        font_window.title("Choose Font")

        # Font list
        font_listbox = tk.Listbox(font_window, width=30, height=10)
        font_listbox.pack(side="left", fill="y")
        scrollbar = tk.Scrollbar(font_window, command=font_listbox.yview)
        scrollbar.pack(side="left", fill="y")
        font_listbox.config(yscrollcommand=scrollbar.set)

        # Font preview
        preview_text = "The quick brown fox jumps over the lazy dog"
        preview_label = tk.Label(font_window, text=preview_text)
        preview_label.pack(pady=10)

        # Font options
        is_bold = tk.BooleanVar(value=self.config.get("font_bold", False))
        is_italic = tk.BooleanVar(value=self.config.get("font_italic", False))
        font_size = tk.IntVar(value=self.config.get("font_size", 12))

        tk.Checkbutton(font_window, text="Bold", variable=is_bold).pack()
        tk.Checkbutton(font_window, text="Italic", variable=is_italic).pack()
        size_entry = tk.Spinbox(font_window, from_=8, to=72, textvariable=font_size)
        size_entry.pack()

        def update_preview():
            font_name = font_listbox.get(tk.ANCHOR)
            bold = 'bold' if is_bold.get() else 'normal'
            italic = 'italic' if is_italic.get() else 'roman'
            size = font_size.get()
            preview_font = font.Font(family=font_name, size=size, weight=bold, slant=italic)
            preview_label.config(font=preview_font)

        def apply_font():
            self.config["font_family"] = font_listbox.get(tk.ANCHOR)
            self.config["font_size"] = font_size.get()
            self.config["font_bold"] = is_bold.get()
            self.config["font_italic"] = is_italic.get()
            self.current_font = font.Font(
                family=self.config["font_family"],
                size=self.config["font_size"],
                weight='bold' if self.config["font_bold"] else 'normal',
                slant='italic' if self.config["font_italic"] else 'roman',
            )
            self.text_area.config(font=self.current_font)
            self.save_config()
            font_window.destroy()

        font_listbox.bind("<<ListboxSelect>>", lambda e: update_preview())
        is_bold.trace('w', lambda *_: update_preview())
        is_italic.trace('w', lambda *_: update_preview())
        font_size.trace('w', lambda *_: update_preview())

        for fnt in font.families():
            font_listbox.insert(tk.END, fnt)

        apply_button = tk.Button(font_window, text="Apply", command=apply_font)
        apply_button.pack(pady=10)

        update_preview()  # Initial update to set default preview

    def change_font_size(self):
        font_size = simpledialog.askinteger(
            "Font Size", "Enter font size:", initialvalue=self.config["font_size"]
        )
        if font_size:
            self.config["font_size"] = font_size
            self.current_font = font.Font(
                family=self.config["font_family"],
                size=font_size,
                weight="bold" if self.config.get("font_bold", False) else "normal",
                slant="italic" if self.config.get("font_italic", False) else "roman",
            )
            self.text_area.config(font=self.current_font)
            self.save_config()
    
    def set_line_spacing(self):
        spacing = simpledialog.askfloat(
            "Line Spacing",
            "Enter line spacing:",
            initialvalue=self.config.get("line_spacing", 4),
        )
        if spacing:
            self.config["line_spacing"] = spacing
            self.text_area.config(spacing3=spacing)
            self.save_config()

    def align_left(self):
        self.text_area.tag_configure("left", justify="left")
        self.apply_tag_to_selection("left")

    def align_center(self):
        self.text_area.tag_configure("center", justify="center")
        self.apply_tag_to_selection("center")

    def align_right(self):
        self.text_area.tag_configure("right", justify="right")
        self.apply_tag_to_selection("right")

    def apply_tag_to_selection(self, tag):
        self.clear_alignment_tags()
        start_index = (
            self.text_area.index("sel.first")
            if self.text_area.tag_ranges("sel")
            else "1.0"
        )
        end_index = (
            self.text_area.index("sel.last")
            if self.text_area.tag_ranges("sel")
            else "end"
        )
        self.text_area.tag_add(tag, start_index, end_index)

    def clear_alignment_tags(self):
        self.text_area.tag_remove("left", "1.0", "end")
        self.text_area.tag_remove("center", "1.0", "end")
        self.text_area.tag_remove("right", "1.0", "end")
    
    def auto_save(self):
        if self.auto_save_enabled.get():  # Check if autosave is enabled
            # Determine the file path: use the current file path if available, otherwise fallback to a default
            filepath = self.current_file_path if hasattr(self, 'current_file_path') and self.current_file_path else self.auto_save_file
            with open(filepath, "w") as file:
                file.write(self.text_area.get(1.0, tk.END))
        self.root.after(self.auto_save_interval, self.auto_save) 
#Settings
    def change_root_bg_color(self):
        color = colorchooser.askcolor(title="Choose root background color")[1]
        if color:
            self.config["root_bg_color"] = color
            self.root.config(bg=color)
            self.save_config()
    
    def change_bg_color(self):
        color = colorchooser.askcolor(title="Choose background color")[1]
        if color:
            self.config["bg_color"] = color
            self.text_area.config(bg=color)
            self.frame.config(bg=color)
            self.save_config()
    
    def change_caret_cursor_color(self):
        color = colorchooser.askcolor(title="Choose cursor color")[1]
        if color:
            self.config["caret_cursor_color"] = color
            self.text_area.config(insertbackground=color)
            self.save_config()
    
    def change_selection_color(self):
        color = colorchooser.askcolor(title="Choose selection color")[1]
        if color:
            self.config["selection_color"] = color
            self.text_area.config(selectbackground=color)
            self.save_config()
    
    def change_fg_color(self):
        color = colorchooser.askcolor(title="Choose text color")[1]
        if color:
            self.config["fg_color"] = color
            self.text_area.config(fg=color)
            self.save_config()

    def change_selection_text_color(self):
        color = colorchooser.askcolor(title="Choose selection text color")[1]
        if color:
            self.config["selection_text_color"] = color
            self.text_area.config(selectforeground=color)
            self.save_config()

    def change_border_color(self):
        color = colorchooser.askcolor(title="Choose border color")[1]
        if color:
            self.config["border_color"] = color
            self.text_area.config(highlightbackground=color, highlightcolor=color)
            self.save_config()
    
    def set_border_thickness(self):
        thickness = simpledialog.askinteger(
            "Set Border Thickness",
            "Enter border thickness:",
            initialvalue=self.config.get(
                "border_thickness", 1
            ),  # Default thickness is 1
        )
        if thickness is not None:  # Check if the user entered a value
            self.config["border_thickness"] = thickness
            self.text_area.config(highlightthickness=thickness)
            self.save_config()

    
    def set_caret_cursor_thickness(self):
        thickness = simpledialog.askinteger("Caret Cursor Thickness", "Enter caret cursor thickness:", initialvalue=self.config.get("insertwidth", 2))
        if thickness is not None:
            self.config["insertwidth"] = thickness
            self.text_area.config(insertwidth=thickness)
            self.save_config()

    def toggle_auto_save(self):
        # This method will be called whenever the autosave menu item is toggled
        if self.auto_save_enabled.get():
            messagebox.showinfo("Autosave Enabled", "Autosave feature has been enabled.")
        else:
            messagebox.showinfo("Autosave Disabled", "Autosave feature has been disabled.")
#About
    def show_about(self):
        about_text = "ZenEdit v2.0\nA simple text editor built with Tkinter."
        messagebox.showinfo("About ZenEdit", about_text)
#shortcuts
    def undo_text(self, event=None):
        try:
            self.text_area.edit_undo()
        except tk.TclError:
            pass
        return "break"

    def redo_text(self, event=None):
        try:
            self.text_area.edit_redo()
        except tk.TclError:
            pass
        return "break"

    def select_all(self, event=None):
        self.text_area.tag_add("sel", "1.0", "end")
        return "break"

    def cut_text(self, event=None):
        self.text_area.event_generate("<<Cut>>")
        return "break"

    def copy_text(self, event=None):
        self.text_area.event_generate("<<Copy>>")
        return "break"

    def paste_text(self, event=None):
        self.text_area.event_generate("<<Paste>>")
        return "break"
    
    def save_config(self):
        with open(self.config_file, "w") as file:
            json.dump(self.config, file, indent=4)
            
if __name__ == "__main__":
    root = tk.Tk()
    editor = ZenEdit(root)
    root.protocol("WM_DELETE_WINDOW", editor.quit)
    root.mainloop()
