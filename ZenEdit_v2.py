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

class Zedit:
    def __init__(self, root):
        self.root = root
        self.root.title("Zedit")
        self.config_file = "editor_config.json"
        self.auto_save_file = "autosave.txt"
        self.load_config()
        self.fullScreenState = False
        self.root.bind("<F9>", lambda event: self.new_file())
        self.root.bind("<F11>", self.toggleFullScreen)
        self.root.bind("<F6>", lambda event: self.show_word_char_count())
        self.root.bind("<F2>", lambda event: self.quit())
        self.root.bind("<F10>", lambda event: self.open_file())
        self.root.bind("<F12>", lambda event: self.save_file())
        self.menu = tk.Menu(root)
        self.file_menu = tk.Menu(self.menu, tearoff=0)
        self.file_menu.add_command(label="New (F9)", command=self.new_file)
        self.file_menu.add_command(label="Open (F10)", command=self.open_file)
        self.file_menu.add_command(label="Save (F12)", command=self.save_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit (F2)", command=self.quit)
        self.edit_menu = tk.Menu(self.menu, tearoff=0)
        self.edit_menu.add_command(
            label="Change Root Background Color", command=self.change_root_bg_color
        )
        self.edit_menu.add_command(
            label="Change Background Color", command=self.change_bg_color
        )
        self.edit_menu.add_command(
            label="Change Text Color", command=self.change_fg_color
        )
        self.edit_menu.add_command(
            label="Change Cursor Color", command=self.change_cursor_color
        )
        self.edit_menu.add_command(
            label="Change Selection Color", command=self.change_selection_color
        )
        self.edit_menu.add_command(
            label="Change Selection Text Color",
            command=self.change_selection_text_color,
        )
        self.edit_menu.add_command(
            label="Change Border Color", command=self.change_border_color
        )
        self.edit_menu.add_command(
            label="Toggle Block Cursor", command=self.toggle_block_cursor
        )
        self.edit_menu.add_command(label="Change Font", command=self.change_font)
        self.edit_menu.add_command(
            label="Change Font Size", command=self.change_font_size
        )
        self.edit_menu.add_command(
            label="Set Line Spacing", command=self.set_line_spacing
        )

        self.format_menu = tk.Menu(self.menu, tearoff=0)
        self.format_menu.add_command(label="Align Left", command=self.align_left)
        self.format_menu.add_command(label="Center", command=self.align_center)
        self.format_menu.add_command(label="Align Right", command=self.align_right)
        
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
        self.view_menu.add_command(label="Toggle Border", command=self.toggle_border)
        self.view_menu.add_command(
            label="Toggle Cursor Visibility", command=self.toggle_cursor_visibility
        )
        self.menu.add_cascade(label="File", menu=self.file_menu)
        self.menu.add_cascade(label="Edit", menu=self.edit_menu)
        self.menu.add_cascade(label="View", menu=self.view_menu)
        self.menu.add_cascade(label="Format", menu=self.format_menu)
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
            insertbackground=self.config["cursor_color"],
            insertwidth=4 if self.config["block_cursor"] else 2,
            spacing3=self.config.get("line_spacing", 4),
            borderwidth=0,
            wrap=tk.WORD,
            highlightthickness=0,
            highlightbackground=self.config["border_color"],
            highlightcolor=self.config["border_color"],
            selectbackground=self.config.get("selection_color", "#3399ff"),
            selectforeground=self.config.get("selection_text_color", "#ffffff"),
            width=self.config.get("text_width", 80),
            height=self.config.get("text_height", 25),
        )
        self.text_area.pack(side="top", fill="both", expand="yes")
        self.auto_save_interval = 5000
        self.auto_save()

        self.text_area.bind('<Control-z>', self.undo_text)
        self.text_area.bind('<Control-Z>', self.redo_text)
        self.text_area.bind('<Control-y>', self.redo_text)
        self.text_area.bind('<Control-Y>', self.redo_text)
        self.text_area.bind('<Control-a>', self.select_all)
        self.text_area.bind('<Control-A>', self.select_all)
        self.text_area.bind('<Control-x>', self.cut_text)
        self.text_area.bind('<Control-X>', self.cut_text)
        self.text_area.bind('<Control-c>', self.copy_text)
        self.text_area.bind('<Control-C>', self.copy_text)
        self.text_area.bind('<Control-v>', self.paste_text)
        self.text_area.bind('<Control-V>', self.paste_text)
        
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
        self.config.setdefault("cursor_color", "white")
        self.config.setdefault("selection_color", "#3399ff")
        self.config.setdefault("selection_text_color", "#ffffff")
        self.config.setdefault("block_cursor", False)
        self.config.setdefault("text_width", 80)
        self.config.setdefault("text_height", 25)
        self.config.setdefault("line_spacing", 4)
        self.config.setdefault("border_color", "#ffffff")  # Default border color
        if hasattr(self, 'text_area'):
            self.text_area.config(highlightbackground=self.config["border_color"])

    def change_border_color(self):
        color = colorchooser.askcolor(title="Choose border color")[1]
        if color:
            self.config["border_color"] = color
            self.text_area.config(highlightbackground=color, highlightcolor=color)
            self.save_config()
    
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
        self.text_area.tag_add('sel', '1.0', 'end')
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

    def auto_save(self):
        with open(self.auto_save_file, "w") as file:
            file.write(self.text_area.get(1.0, tk.END))
        self.root.after(self.auto_save_interval, self.auto_save)

    def toggleFullScreen(self, event=None):
        self.fullScreenState = not self.fullScreenState
        self.root.attributes("-fullscreen", self.fullScreenState)
        if self.fullScreenState:
            self.root.config(menu="")
        else:
            self.root.config(menu=self.menu)
    def show_word_char_count(self):
        text_content = self.text_area.get(1.0, "end-1c")  # Get content of text_area
        words = len(text_content.split())
        characters = len(text_content)

    # Show the counts in a message box
        messagebox.showinfo("Word/Character Count", f'Words: {words}\nCharacters: {characters}')
            
    def align_left(self):
        self.text_area.tag_configure("left", justify='left')
        self.apply_tag_to_selection("left")

    def align_center(self):
        self.text_area.tag_configure("center", justify='center')
        self.apply_tag_to_selection("center")

    def align_right(self):
        self.text_area.tag_configure("right", justify='right')
        self.apply_tag_to_selection("right")

    def apply_tag_to_selection(self, tag):
        # Clear existing alignment tags before applying the new one
        self.clear_alignment_tags()

        # Apply the given tag to the selected text. If no text is selected, apply to all text.
        start_index = self.text_area.index("sel.first") if self.text_area.tag_ranges("sel") else "1.0"
        end_index = self.text_area.index("sel.last") if self.text_area.tag_ranges("sel") else "end"
        self.text_area.tag_add(tag, start_index, end_index)

    def clear_alignment_tags(self):
        # Remove existing alignment tags from the entire text
        self.text_area.tag_remove("left", "1.0", "end")
        self.text_area.tag_remove("center", "1.0", "end")
        self.text_area.tag_remove("right", "1.0", "end")
    
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

    def quit(self):
        response = None
        if self.text_area.edit_modified():
            response = messagebox.askyesnocancel(
                "Save on Exit", "Do you want to save the changes before exiting?"
            )
            if response is True:
                self.save_file()

        if response is not True:
            self.root.destroy()

    def open_file(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if not filepath:
            return
        self.text_area.delete(1.0, tk.END)
        with open(filepath, "r") as file:
            self.text_area.insert(tk.END, file.read())

    def save_file(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
        )
        if not filepath:
            return
        with open(filepath, "w") as file:
            file.write(self.text_area.get(1.0, tk.END))

    def toggle_block_cursor(self):
        self.config["block_cursor"] = not self.config["block_cursor"]
        insert_width = 4 if self.config["block_cursor"] else 2
        self.text_area.config(insertwidth=insert_width)
        self.save_config()

    def change_bg_color(self):
        color = colorchooser.askcolor(title="Choose background color")[1]
        if color:
            self.config["bg_color"] = color
            self.text_area.config(bg=color)
            self.frame.config(bg=color)
            self.save_config()

    def change_fg_color(self):
        color = colorchooser.askcolor(title="Choose text color")[1]
        if color:
            self.config["fg_color"] = color
            self.text_area.config(fg=color)
            self.save_config()

    def change_cursor_color(self):
        color = colorchooser.askcolor(title="Choose cursor color")[1]
        if color:
            self.config["cursor_color"] = color
            self.text_area.config(insertbackground=color)
            self.save_config()

    def change_selection_color(self):
        color = colorchooser.askcolor(title="Choose selection color")[1]
        if color:
            self.config["selection_color"] = color
            self.text_area.config(selectbackground=color)
            self.save_config()

    def change_selection_text_color(self):
        color = colorchooser.askcolor(title="Choose selection text color")[1]
        if color:
            self.config["selection_text_color"] = color
            self.text_area.config(selectforeground=color)
            self.save_config()

    def change_root_bg_color(self):
        color = colorchooser.askcolor(title="Choose root background color")[1]
        if color:
            self.config["root_bg_color"] = color
            self.root.config(bg=color)
            self.save_config()
            
    def change_font(self):
        font_window = Toplevel(self.root)
        font_window.title("Choose Font")
        font_listbox = Listbox(font_window)
        font_listbox.pack(side="left", fill="y")
        scrollbar = tk.Scrollbar(
            font_window, orient="vertical", command=font_listbox.yview
        )
        scrollbar.pack(side="right", fill="y")
        font_listbox.config(yscrollcommand=scrollbar.set)
        for fnt in font.families():
            font_listbox.insert(tk.END, fnt)

        is_bold = tk.BooleanVar(value=self.config.get("font_bold", False))
        is_italic = tk.BooleanVar(value=self.config.get("font_italic", False))
        bold_check = tk.Checkbutton(font_window, text="Bold", variable=is_bold)
        italic_check = tk.Checkbutton(font_window, text="Italic", variable=is_italic)
        bold_check.pack(side="top", fill="x")
        italic_check.pack(side="top", fill="x")

        def on_font_select(event):
            selection = font_listbox.curselection()
            if selection:
                font_name = font_listbox.get(selection[0])
                font_size = simpledialog.askinteger(
                    "Font Size",
                    "Enter font size:",
                    initialvalue=self.config["font_size"],
                )
                if font_size:
                    self.config["font_family"] = font_name
                    self.config["font_size"] = font_size
                    self.config["font_bold"] = is_bold.get()
                    self.config["font_italic"] = is_italic.get()
                    self.current_font = font.Font(
                        family=font_name,
                        size=font_size,
                        weight="bold" if is_bold.get() else "normal",
                        slant="italic" if is_italic.get() else "roman",
                    )
                    self.text_area.config(font=self.current_font)
                    self.save_config()
                    font_window.destroy()

        font_listbox.bind("<<ListboxSelect>>", on_font_select)

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

    def toggle_border(self):
        current_thickness = self.text_area.cget("highlightthickness")
        new_thickness = 0 if current_thickness > 0 else 1
        self.text_area.config(highlightthickness=new_thickness)

    def toggle_cursor_visibility(self):
        if self.text_area["cursor"] in ["", "xterm"]:
            self.text_area.config(cursor="none")
        else:
            self.text_area.config(cursor="xterm")


if __name__ == "__main__":
    root = tk.Tk()
    editor = Zedit(root)  # Create an instance of Zedit
    root.protocol("WM_DELETE_WINDOW", editor.quit)  # Bind the close event to the quit method of the editor instance
    root.mainloop()
