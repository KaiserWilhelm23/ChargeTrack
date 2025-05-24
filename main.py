import sys
import os
import csv
import datetime
import barcode
from barcode.writer import ImageWriter
import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk
from PIL import Image, ImageTk
from fpdf import FPDF

settings = {'pickup_hours': 24}  # Global settings dictionary

class BatteryManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Battery Charging Drop Off Manager")
        self.root.attributes('-fullscreen', True)

        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.frames = {}
        for F in (MainMenu, CheckInScreen, CheckOutScreen, ReportScreen, SettingsScreen):
            frame = F(parent=self.main_frame, controller=self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(MainMenu)

    def show_frame(self, frame_class):
        frame = self.frames[frame_class]
        frame.tkraise()

class CenteredFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.inner_frame = tk.Frame(self)
        self.inner_frame.grid(row=0, column=0)

class MainMenu(CenteredFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self.inner_frame, text="Battery Manager", font=("Arial", 24)).pack(pady=20)
        tk.Button(self.inner_frame, text="Check In", command=lambda: controller.show_frame(CheckInScreen), height=2, width=20).pack(pady=10)
        tk.Button(self.inner_frame, text="Check Out", command=lambda: controller.show_frame(CheckOutScreen), height=2, width=20).pack(pady=10)
        tk.Button(self.inner_frame, text="Generate Report", command=lambda: controller.show_frame(ReportScreen), height=2, width=20).pack(pady=10)
        tk.Button(self.inner_frame, text="Settings", command=lambda: controller.show_frame(SettingsScreen), height=2, width=20).pack(pady=10)

class CheckInScreen(CenteredFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self.inner_frame, text="Customer Name:").pack()
        self.name_input = tk.Entry(self.inner_frame)
        self.name_input.pack()

        tk.Label(self.inner_frame, text="Phone Number:").pack()
        self.phone_input = tk.Entry(self.inner_frame)
        self.phone_input.pack()

        tk.Label(self.inner_frame, text="Battery Size:").pack()
        self.batt_size_var = tk.StringVar()
        self.batt_size_dropdown = ttk.Combobox(self.inner_frame, textvariable=self.batt_size_var)
        self.batt_size_dropdown['values'] = (
    "Group 24", "Group 27", "Group 31", "Group 34", "Group 35",
    "Group 48", "Group 49", "Group 65", "Group 78", "Group 94R", "Other"
)
        self.batt_size_dropdown.set("AA")
        self.batt_size_dropdown.pack()

        self.custom_batt_input = tk.Entry(self.inner_frame)
        self.custom_batt_input.pack()
        self.custom_batt_input.insert(0, "")
        self.custom_batt_input.configure(state='disabled')

        def on_select(event):
            if self.batt_size_var.get() == "Other":
                self.custom_batt_input.configure(state='normal')
                self.custom_batt_input.delete(0, tk.END)
            else:
                self.custom_batt_input.delete(0, tk.END)
                self.custom_batt_input.insert(0, self.batt_size_var.get())
                self.custom_batt_input.configure(state='disabled')

        self.batt_size_dropdown.bind("<<ComboboxSelected>>", on_select)

        tk.Button(self.inner_frame, text="Check In", command=self.check_in).pack(pady=5)
        tk.Button(self.inner_frame, text="Back", command=lambda: controller.show_frame(MainMenu)).pack()

    def check_in(self):
        name = self.name_input.get()
        phone = self.phone_input.get()
        batt_size = self.custom_batt_input.get()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if not name or not phone or not batt_size:
            messagebox.showwarning("Input Error", "Please fill all fields.")
            return

        initials = ''.join([n[0].upper() for n in name.split()])
        unique_id = f"{batt_size}-{initials}-{str(datetime.datetime.now().microsecond)[-4:]}"

        os.makedirs("receipts", exist_ok=True)
        with open("checkin.csv", "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([name, phone, batt_size, unique_id, timestamp])

        barcode_path = f"receipts/barcode_{unique_id}.png"
        code128 = barcode.get('code128', unique_id, writer=ImageWriter())
        code128.save(barcode_path.replace('.png', ''))

        pickup_time = datetime.datetime.now() + datetime.timedelta(hours=settings['pickup_hours'])

        pdf_path = f"receipts/checkin_receipt_{unique_id}.pdf"
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="AABCMS - Check In Receipt", ln=True, align='C')
        pdf.ln(10)
        pdf.cell(200, 10, txt=f"Name: {name}", ln=True)
        pdf.cell(200, 10, txt=f"Phone: {phone}", ln=True)
        pdf.cell(200, 10, txt=f"Battery Size: {batt_size}", ln=True)
        pdf.cell(200, 10, txt=f"Unique ID: {unique_id}", ln=True)
        pdf.cell(200, 10, txt=f"Timestamp: {timestamp}", ln=True)
        pdf.cell(200, 10, txt=f"Pickup Time: {pickup_time.strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
        pdf.image(barcode_path, x=10, y=pdf.get_y(), w=100)
        pdf.output(pdf_path)

        messagebox.showinfo("Success", f"Item checked in. Receipt saved as PDF.")
        self.name_input.delete(0, tk.END)
        self.phone_input.delete(0, tk.END)
        self.batt_size_dropdown.set("AA")
        self.custom_batt_input.delete(0, tk.END)

class CheckOutScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Item ID:").pack()
        self.id_input = tk.Entry(self)
        self.id_input.pack()

        tk.Button(self, text="Check Out", command=self.check_out).pack(pady=5)
        tk.Button(self, text="Back", command=lambda: controller.show_frame(MainMenu)).pack()

    def check_out(self):
        item_id = self.id_input.get()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if not item_id:
            messagebox.showwarning("Input Error", "Please enter the item ID.")
            return

        os.makedirs("receipts", exist_ok=True)
        with open("checkout.csv", "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([item_id, timestamp])

        # Generate employee copy
        pdf_path = f"receipts/checkout_receipt_{item_id}.pdf"
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="AABCMS - Check Out Receipt", ln=True, align='C')
        pdf.ln(10)
        pdf.cell(200, 10, txt=f"Item ID: {item_id}", ln=True)
        pdf.cell(200, 10, txt=f"Timestamp: {timestamp}", ln=True)
        pdf.cell(200, 10, txt="\nCustomer Signature: ____________________________", ln=True)
        pdf.output(pdf_path)

        # Generate customer copy
        customer_pdf_path = f"receipts/checkout_customer_copy_{item_id}.pdf"
        customer_pdf = FPDF()
        customer_pdf.add_page()
        customer_pdf.set_font("Arial", size=12)
        customer_pdf.cell(200, 10, txt="AABCMS - Customer Copy", ln=True, align='C')
        customer_pdf.ln(10)
        customer_pdf.cell(200, 10, txt=f"Item ID: {item_id}", ln=True)
        customer_pdf.cell(200, 10, txt=f"Timestamp: {timestamp}", ln=True)
        customer_pdf.output(customer_pdf_path)

        messagebox.showinfo("Success", f"Item checked out. Receipts saved.")
        self.id_input.delete(0, tk.END)

class ReportScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Generate Report").pack(pady=10)
        tk.Button(self, text="Download Check-In CSV", command=self.download_checkin).pack(pady=5)
        tk.Button(self, text="Download Check-Out CSV", command=self.download_checkout).pack(pady=5)
        tk.Button(self, text="Back", command=lambda: controller.show_frame(MainMenu)).pack(pady=10)

    def download_checkin(self):
        dest = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if dest:
            with open("checkin.csv", "r") as src, open(dest, "w", newline="") as dst:
                dst.write(src.read())
            messagebox.showinfo("Success", "Check-in CSV saved.")

    def download_checkout(self):
        dest = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if dest:
            with open("checkout.csv", "r") as src, open(dest, "w", newline="") as dst:
                dst.write(src.read())
            messagebox.showinfo("Success", "Check-out CSV saved.")

class SettingsScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Settings", font=("Arial", 18)).pack(pady=10)
        tk.Label(self, text="Pickup time (hours):").pack()

        self.pickup_input = tk.Entry(self)
        self.pickup_input.insert(0, str(settings['pickup_hours']))
        self.pickup_input.pack()

        tk.Button(self, text="Save", command=self.save_settings).pack(pady=5)
        tk.Button(self, text="Back", command=lambda: controller.show_frame(MainMenu)).pack()

    def save_settings(self):
        try:
            hours = int(self.pickup_input.get())
            settings['pickup_hours'] = hours
            messagebox.showinfo("Saved", f"Pickup time set to {hours} hours.")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number.")

if __name__ == '__main__':
    root = tk.Tk()
    app = BatteryManagerApp(root)
    root.mainloop()