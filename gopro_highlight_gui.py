#!/usr/bin/env python3
"""Simple Tkinter GUI for selecting source directory and destination and starting highlight extraction."""
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os
import sys

# import processing function
from gopro_highlight import process_directory


class App:
    def __init__(self, root):
        self.root = root
        root.title('GoPro Highlight Extractor')

        frm = tk.Frame(root, padx=10, pady=10)
        frm.pack(fill='both', expand=True)

        # Source dir
        tk.Label(frm, text='Source directory:').grid(row=0, column=0, sticky='w')
        self.src_var = tk.StringVar()
        tk.Entry(frm, textvariable=self.src_var, width=50).grid(row=0, column=1, sticky='we')
        tk.Button(frm, text='Browse', command=self.browse_src).grid(row=0, column=2, padx=6)

        # Dest dir
        tk.Label(frm, text='Destination directory:').grid(row=1, column=0, sticky='w')
        self.dst_var = tk.StringVar()
        tk.Entry(frm, textvariable=self.dst_var, width=50).grid(row=1, column=1, sticky='we')
        tk.Button(frm, text='Browse', command=self.browse_dst).grid(row=1, column=2, padx=6)

        # Options
        tk.Label(frm, text='Pre (s):').grid(row=2, column=0, sticky='w')
        self.pre_var = tk.DoubleVar(value=1.0)
        tk.Entry(frm, textvariable=self.pre_var, width=8).grid(row=2, column=1, sticky='w')

        tk.Label(frm, text='Post (s):').grid(row=2, column=1, sticky='e')
        self.post_var = tk.DoubleVar(value=1.0)
        tk.Entry(frm, textvariable=self.post_var, width=8).grid(row=2, column=1, sticky='e', padx=(0,80))

        self.recursive_var = tk.BooleanVar(value=True)
        tk.Checkbutton(frm, text='Recursive', variable=self.recursive_var).grid(row=3, column=0, sticky='w')
        self.name_ts_var = tk.BooleanVar(value=True)
        tk.Checkbutton(frm, text='Name with timestamp', variable=self.name_ts_var).grid(row=3, column=1, sticky='w')
        self.reencode_var = tk.BooleanVar(value=False)
        tk.Checkbutton(frm, text='Re-encode (frame-accurate)', variable=self.reencode_var).grid(row=3, column=2, sticky='w')

        # Start button
        self.start_btn = tk.Button(frm, text='Start', command=self.start)
        self.start_btn.grid(row=4, column=0, pady=10)

        self.clear_btn = tk.Button(frm, text='Clear Log', command=self.clear_log)
        self.clear_btn.grid(row=4, column=1, pady=10, sticky='w')

        # Progress bar
        from tkinter import ttk
        self.progress = ttk.Progressbar(frm, orient='horizontal', length=400, mode='determinate')
        self.progress.grid(row=4, column=2, padx=8, sticky='we')

        # Log
        self.log = scrolledtext.ScrolledText(frm, height=12, state='disabled')
        self.log.grid(row=5, column=0, columnspan=3, sticky='nsew')

        # Configure grid expansion
        frm.columnconfigure(1, weight=1)
        frm.rowconfigure(5, weight=1)

    def browse_src(self):
        d = filedialog.askdirectory()
        if d:
            self.src_var.set(d)

    def browse_dst(self):
        d = filedialog.askdirectory()
        if d:
            self.dst_var.set(d)

    def log_msg(self, msg: str):
        self.log['state'] = 'normal'
        self.log.insert('end', msg + '\n')
        self.log.see('end')
        self.log['state'] = 'disabled'

    def clear_log(self):
        self.log['state'] = 'normal'
        self.log.delete('1.0', 'end')
        self.log['state'] = 'disabled'

    def start(self):
        src = self.src_var.get()
        dst = self.dst_var.get()
        if not src or not os.path.isdir(src):
            messagebox.showerror('Error', 'Please select a valid source directory')
            return
        if not dst:
            messagebox.showerror('Error', 'Please select a destination directory')
            return
        self.start_btn.config(state='disabled')
        self.clear_btn.config(state='disabled')
        t = threading.Thread(target=self._run_process, args=(src, dst), daemon=True)
        t.start()

    def _run_process(self, src, dst):
        def cb(msg, percent=None):
            # schedule UI update on main thread
            self.root.after(0, self.log_msg, msg)
            if percent is not None:
                # Progressbar doesn't have a 'set' method; update its 'value'
                self.root.after(0, lambda p=percent: self.progress.config(value=p))

        try:
            # reset progress UI
            self.root.after(0, lambda: self.progress.config(value=0))
            results = process_directory(src, dst, float(self.pre_var.get()), float(self.post_var.get()), mode='anchor', recursive=self.recursive_var.get(), name_with_ts=self.name_ts_var.get(), reencode=self.reencode_var.get(), csv_path=os.path.join(dst, 'summary.csv'), progress_callback=cb)
            self.root.after(0, self.log_msg, f'Processing complete. {len(results)} clips created')
            self.root.after(0, lambda: self.progress.config(value=100))
            messagebox.showinfo('Done', f'Processing complete. {len(results)} clips created')
        except Exception as e:
            self.root.after(0, self.log_msg, f'Error: {e}')
            messagebox.showerror('Error', str(e))
        finally:
            self.root.after(0, lambda: self.start_btn.config(state='normal'))
            self.root.after(0, lambda: self.clear_btn.config(state='normal'))


def main():
    # ensure ffmpeg exists
    import shutil
    if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):
        messagebox.showerror('Missing binaries', 'ffmpeg and ffprobe are required. Install them (e.g. sudo apt install ffmpeg)')
        sys.exit(1)

    root = tk.Tk()
    app = App(root)
    root.geometry('800x450')
    root.mainloop()


if __name__ == '__main__':
    main()
