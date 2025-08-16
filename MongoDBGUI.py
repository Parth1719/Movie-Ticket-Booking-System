import tkinter as tk
from tkinter import ttk, messagebox
from pymongo import MongoClient
from bson import ObjectId

# MongoDB Connection
client = MongoClient("mongodb://localhost:27017/")
db = client["movie_ticket_system413"]
collection = db["bookings413"]

# GUI Application
class MovieTicketApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎬 Movie Ticket Booking System")
        self.root.geometry("1000x600")
        self.root.configure(bg="#f0f8ff")  # Light pastel background
        self.root.state("zoomed")  # Open in fullscreen mode

        # Title
        title = tk.Label(
            root,
            text="🎬 Movie Ticket Booking System",
            font=("Arial", 24, "bold"),
            bg="#4a90e2",
            fg="white",
            pady=12
        )
        title.pack(fill="x")

        # Frame for Form
        form_frame = tk.Frame(root, bg="#e6f7ff", bd=3, relief="ridge")
        form_frame.pack(side=tk.LEFT, fill="y", padx=20, pady=15)

        tk.Label(form_frame, text="Customer Name:", bg="#e6f7ff", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        tk.Label(form_frame, text="Movie Name:", bg="#e6f7ff", font=("Arial", 12, "bold")).grid(row=1, column=0, padx=10, pady=10, sticky="w")
        tk.Label(form_frame, text="Tickets:", bg="#e6f7ff", font=("Arial", 12, "bold")).grid(row=2, column=0, padx=10, pady=10, sticky="w")

        self.name_var = tk.StringVar()
        self.movie_var = tk.StringVar()
        self.tickets_var = tk.StringVar()

        tk.Entry(form_frame, textvariable=self.name_var, font=("Arial", 12), width=25, bd=2, relief="solid").grid(row=0, column=1, padx=10, pady=10)
        tk.Entry(form_frame, textvariable=self.movie_var, font=("Arial", 12), width=25, bd=2, relief="solid").grid(row=1, column=1, padx=10, pady=10)
        tk.Entry(form_frame, textvariable=self.tickets_var, font=("Arial", 12), width=25, bd=2, relief="solid").grid(row=2, column=1, padx=10, pady=10)

        # Buttons Frame
        btn_frame = tk.Frame(form_frame, bg="#e6f7ff")
        btn_frame.grid(row=3, column=0, columnspan=2, pady=20)

        def make_button(text, color, cmd, col):
            btn = tk.Button(btn_frame, text=text, command=cmd, bg=color, fg="white",
                            font=("Arial", 11, "bold"), width=14, bd=0, relief="flat", activebackground="#333")
            btn.grid(row=0, column=col, padx=7)
            return btn

        self.btn_add = make_button("Add Booking", "#4caf50", self.add_booking, 0)
        self.btn_update = make_button("Update", "#ff9800", self.update_booking, 1)
        self.btn_delete = make_button("Delete", "#f44336", self.delete_booking, 2)
        self.btn_clear = make_button("Clear", "#2196f3", self.clear_fields, 3)

        # Table Frame
        table_frame = tk.Frame(root, bg="#f0f8ff")
        table_frame.pack(side=tk.RIGHT, fill="both", expand=True, padx=20, pady=15)

        columns = ("id", "name", "movie", "tickets")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        # Styling
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview",
                        font=("Arial", 11),
                        rowheight=28,
                        background="#ffffff",
                        fieldbackground="#ffffff")
        style.configure("Treeview.Heading",
                        font=("Arial", 12, "bold"),
                        background="#4a90e2",
                        foreground="white")
        style.map("Treeview", background=[("selected", "#90caf9")])

        for col in columns:
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, anchor="center", width=180)

        # Alternate row colors
        self.tree.tag_configure("oddrow", background="#e6f2ff")
        self.tree.tag_configure("evenrow", background="#ffffff")

        self.tree.pack(fill="both", expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<ButtonRelease-1>", self.load_selected_row)

        self.load_data()

    def add_booking(self):
        name = self.name_var.get()
        movie = self.movie_var.get()
        tickets = self.tickets_var.get()

        if name and movie and tickets:
            booking = {"name": name, "movie": movie, "tickets": tickets}
            collection.insert_one(booking)
            self.load_data()
            self.clear_fields()
            messagebox.showinfo("Success", "Booking Added Successfully!")
        else:
            messagebox.showwarning("Error", "All fields are required!")

    def load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        bookings = list(collection.find())
        for index, booking in enumerate(bookings):
            tag = "evenrow" if index % 2 == 0 else "oddrow"
            self.tree.insert("", "end",
                             values=(str(booking["_id"]), booking["name"], booking["movie"], booking["tickets"]),
                             tags=(tag,))

    def load_selected_row(self, event):
        selected = self.tree.focus()
        if selected:
            values = self.tree.item(selected, "values")
            self.name_var.set(values[1])
            self.movie_var.set(values[2])
            self.tickets_var.set(values[3])

    def update_booking(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Error", "No booking selected")
            return

        values = self.tree.item(selected, "values")
        booking_id = values[0]

        collection.update_one(
            {"_id": ObjectId(booking_id)},
            {"$set": {"name": self.name_var.get(),
                      "movie": self.movie_var.get(),
                      "tickets": self.tickets_var.get()}}
        )
        self.load_data()
        messagebox.showinfo("Success", "Booking Updated Successfully!")

    def delete_booking(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Error", "No booking selected")
            return

        values = self.tree.item(selected, "values")
        booking_id = values[0]

        collection.delete_one({"_id": ObjectId(booking_id)})
        self.load_data()
        self.clear_fields()
        messagebox.showinfo("Success", "Booking Deleted Successfully!")

    def clear_fields(self):
        self.name_var.set("")
        self.movie_var.set("")
        self.tickets_var.set("")


# Run Application
if __name__ == "__main__":
    root = tk.Tk()
    app = MovieTicketApp(root)
    root.mainloop()
