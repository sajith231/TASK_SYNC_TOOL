import threading
import tkinter as tk
from tkinter import ttk, messagebox

from sync import SyncTool


class TaskPrimeGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TASK PRIME")
        self.root.geometry("800x500")   # wider window
        self.root.resizable(False, False)

        self.sync_thread = None
        self.running = False

        self.build_ui()

        # 👇 AUTO START SYNC WHEN UI LOADS
        self.root.after(500, self.start_sync)

    def build_ui(self):
        title = tk.Label(
            self.root,
            text="TASK PRIME",
            font=("Segoe UI", 22, "bold")
        )
        title.pack(pady=10)

        subtitle = tk.Label(
            self.root,
            text="SYNC Tool",
            font=("Segoe UI", 11)
        )
        subtitle.pack()

        # Table Frame
        frame = ttk.Frame(self.root)
        frame.pack(padx=20, pady=20, fill="both", expand=True)

        columns = ("table", "rows")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings", height=12)

        self.tree.heading("table", text="Table Name")
        self.tree.heading("rows", text="Message / Fetched Rows")

        # Wider second column
        self.tree.column("table", width=200, anchor="w")
        self.tree.column("rows", width=550, anchor="w")

        self.tree.pack(fill="both", expand=True)

        # Horizontal Scrollbar (for long errors)
        x_scroll = ttk.Scrollbar(frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(xscrollcommand=x_scroll.set)
        x_scroll.pack(side="bottom", fill="x")

        # Status
        self.status_label = tk.Label(
            self.root,
            text="Status: Idle",
            font=("Segoe UI", 10),
            fg="blue"
        )
        self.status_label.pack(pady=10)

        # Buttons
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=10)

        self.start_btn = ttk.Button(
            btn_frame,
            text="Start Sync",
            command=self.start_sync
        )
        self.start_btn.grid(row=0, column=0, padx=20)

        self.stop_btn = ttk.Button(
            btn_frame,
            text="Stop",
            command=self.stop_sync,
            state="disabled"
        )
        self.stop_btn.grid(row=0, column=1, padx=20)

    # ------------------------------
    # Sync Control
    # ------------------------------

    def start_sync(self):
        if self.running:
            return

        self.running = True
        self.tree.delete(*self.tree.get_children())
        self.status_label.config(text="Status: Running...", fg="green")
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")

        self.sync_thread = threading.Thread(target=self.run_sync)
        self.sync_thread.start()

    def stop_sync(self):
        self.running = False
        self.status_label.config(text="Status: Stopped", fg="red")
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")

    # ------------------------------
    # Main Sync Runner
    # ------------------------------

    def run_sync(self):
        try:
            tool = SyncTool(gui_callback=self.update_table)

            success = tool.run()

            if success:
                self.start_countdown()
            else:
                self.status_label.config(text="Status: Failed", fg="red")

        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.status_label.config(text="Status: Error", fg="red")

        self.running = False
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")

    # ------------------------------
    # Auto Close Countdown
    # ------------------------------

    def start_countdown(self, seconds=10):
        self.countdown_seconds = seconds
        self.update_countdown()

    def update_countdown(self):
        if self.countdown_seconds > 0:
            self.status_label.config(
                text=f"Status: Completed - Closing in {self.countdown_seconds} seconds...",
                fg="green"
            )
            self.countdown_seconds -= 1
            self.root.after(1000, self.update_countdown)
        else:
            self.root.destroy()

    # ------------------------------
    # Update GUI from Sync
    # ------------------------------

    def update_table(self, table_name, row_count):
        if table_name == "ERROR":
            # Clear table
            self.tree.delete(*self.tree.get_children())

            # Insert full error message
            self.tree.insert("", "end", values=("ERROR", row_count))

            # Update status
            self.status_label.config(
                text=f"Status: {row_count}",
                fg="red"
            )
        else:
            self.tree.insert("", "end", values=(table_name, row_count))
            self.root.update_idletasks()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = TaskPrimeGUI()
    app.run()
