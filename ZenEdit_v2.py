def search_text(self, event=None):
        search_window = tk.Toplevel(self.root)
        search_window.title("Search")

        tk.Label(search_window, text="Find:").pack(side="left")
        search_entry = tk.Entry(search_window)
        search_entry.pack(side="left", fill="x", expand=True)
        search_entry.focus_set()

        case_sensitive = tk.BooleanVar(value=False)
        tk.Checkbutton(search_window, text="Case Sensitive", variable=case_sensitive).pack(side="left")

        # State to remember if the search has started
        self.search_started = False

        def do_search(next=False):
            nonlocal search_window
            search_query = search_entry.get()
            if not search_query:
                return

            start_idx = "1.0"
            if self.search_started and next:
                start_idx = self.text_area.index(tk.SEL_LAST + "+1c")
            else:
                self.search_started = True

            search_args = {'nocase': not case_sensitive.get()}
            search_idx = self.text_area.search(search_query, start_idx, **search_args)
            if not search_idx:
                messagebox.showinfo("Search", "Text not found.")
                self.search_started = False
                return

            end_idx = f"{search_idx}+{len(search_query)}c"
            self.text_area.tag_remove(tk.SEL, "1.0", tk.END)
            self.text_area.tag_add(tk.SEL, search_idx, end_idx)
            self.text_area.mark_set(tk.INSERT, end_idx)
            self.text_area.see(search_idx)

        tk.Button(search_window, text="Find", command=do_search).pack(side="left")
        tk.Button(search_window, text="Next", command=lambda: do_search(next=True)).pack(side="left")
        tk.Button(search_window, text="Close", command=search_window.destroy).pack(side="left")

        # Bind the Enter key to do a search, and Shift+Enter for the next occurrence
        search_entry.bind("<Return>", lambda event: do_search(next=self.search_started))
        search_entry.bind("<Shift-Return>", lambda event: do_search(next=True))
