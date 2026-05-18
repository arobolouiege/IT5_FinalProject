#Purpose: The main system of this project.

#impor blocks
import tkinter as tk #tkinter - for GUI
from tkinter import ttk, messagebox, simpledialog #ttk - for better and advance looking widgets like pop up messages.
import json #for saving and loading data in JSON format
import os #for checking if the data file exists
import re #for making safe PDF filenames
import textwrap #for fitting setup details on the small PDF page
from datetime import datetime #for automatic date and time stamps

from computer_setup import ComputerSetup #computer_setup.py


class InventorySystem: #Class Definition

    FILE_NAME = "inventory_data.json" #Stores the JSON filename in one place.
    STATUS_OPTIONS = ("Available", "In Use", "Defective", "Returned") #Stores valid status options in one place.

    def __init__(self, root): #Constructor: Initializes the entire system.
       
        #main window setup
        self.root = root
        self.root.title("Computer Setup Inventory System")
        self.root.geometry("600x550")

        self.inventory = [] #List to hold all computer setups in memory. Each item will be a ComputerSetup object.

        #Tracks whether the user is editing a setup. If True, the form is in edit mode and will update an existing setup instead of adding a new one. editing_serial holds the inventory number of the setup being edited.
        self.edit_mode = False
        self.editing_serial = None

        self.load_data() #Load existing inventory data from the JSON file when the system starts.

        # GUI Setup
        title = tk.Label(
            root,
            text="Computer Setup Inventory System",
            font=("Arial", 20, "bold")
        )
        title.pack(pady=20)

        #Creates a container for form fields. This keeps the layout organized and allows for better spacing.
        form_frame = tk.Frame(root)
        form_frame.pack(pady=10)

        
        fields = [ #Stores all labels and entry variable names.
            ("Inventory Number", "serial_number_entry"),
            ("PC Name", "pc_name_entry"),
            ("System Unit Model", "system_model_entry"),
            ("Processor", "processor_entry"),
            ("RAM", "ram_entry"),
            ("Storage", "storage_entry"),
            ("Keyboard Serial", "keyboard_serial_entry"),
            ("Mouse Serial", "mouse_serial_entry"),
            ("Monitor Serial", "monitor_serial_entry"),
            ("GPU Model", "gpu_entry"),
            ("Power Supply", "power_supply_entry"),
            ("Status", "status_combobox")
        ]

        for i, (label, attr) in enumerate(fields): #Automatically creates all form labels and textboxes.

            tk.Label(
                form_frame,
                text=label
            ).grid(
                row=i,
                column=0,
                padx=10,
                pady=5,
                sticky="w"
            )

            if attr == "status_combobox":

                entry = ttk.Combobox(
                    form_frame,
                    values=self.STATUS_OPTIONS,
                    width=32,
                    state="readonly"
                ) #Creates dropdown for status field.

                entry.set("Available")

            else:

                entry = tk.Entry(form_frame, width=35) #Creates text input fields.

            entry.grid(row=i, column=1)

            setattr(self, attr, entry) #Dynamically creates object variables. For example, self.serial_number_entry, self.pc_name_entry, etc. This allows us to easily access the entry fields later using these variable names.

        #container for buttons.
        button_frame = tk.Frame(root)
        button_frame.pack(pady=20)

        # MAIN BUTTONS
        self.add_button = tk.Button(
            button_frame,
            text="Add Setup",
            width=15,
            command=self.add_setup #Runs add_setup() when button is clicked.
        )

        self.add_button.grid(row=0, column=0, padx=10)

        tk.Button(
            button_frame,
            text="View Setups",
            width=15,
            command=self.open_view_window #Opens the view window when clicked.
        ).grid(row=0, column=1, padx=10)

        tk.Button(
            button_frame,
            text="Exit",
            width=15,
            command=self.root.quit #Closes the program when clicked.
        ).grid(row=0, column=2, padx=10)

        # EDIT BUTTONS
        self.save_button = tk.Button(
            button_frame,
            text="Save",
            width=15,
            command=self.save_changes
        )
        
        self.cancel_button = tk.Button(
            button_frame,
            text="Cancel",
            width=15,
            command=self.cancel_edit
        )

    def get_current_timestamp(self):

        return datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")

    def add_setup(self):

        #Validation Block: Prevents incomplete records.
        serial_number = self.serial_number_entry.get().strip() # "Serial number" or Inventory number.

        if serial_number == "":
            messagebox.showerror(
                "Error",
                "Inventory Number is required."
            )
            return

        if self.inventory_number_exists(serial_number):

            messagebox.showerror(
                "Error",
                "Inventory Number already exists."
            )

            return

        #   Creates a new setup object from user input. related to computer_setup.py
        setup = ComputerSetup(
            serial_number,
            self.pc_name_entry.get(),
            self.system_model_entry.get(),
            self.processor_entry.get(),
            self.storage_entry.get(),
            self.ram_entry.get(),
            self.keyboard_serial_entry.get(),
            self.mouse_serial_entry.get(),
            self.monitor_serial_entry.get(),
            self.gpu_entry.get(),
            self.power_supply_entry.get(),
            self.status_combobox.get(),
            self.get_current_timestamp()
        )

        self.inventory.append(setup) #Adds the object into inventory list.

        self.save_data() #Saves the updated inventory list to the JSON file.

        messagebox.showinfo(
            "Success",
            "Setup added successfully!"
        )

        self.clear_entries() #Clear Entries Block: Clears the form fields after adding a setup.


        #View Setups
    def open_view_window(self): #Opens the table view window.

        self.root.withdraw() #Temporarily hides main window.

        self.view_window = tk.Toplevel(self.root) #Creates secondary window.

        self.view_window.protocol(
            "WM_DELETE_WINDOW",
            self.back_to_main
        )

        self.view_window.title("View Setups")
        self.view_window.geometry("1600x700")

        search_frame = tk.Frame(self.view_window)
        search_frame.pack(fill="x", padx=10, pady=10)

        tk.Label(
            search_frame,
            text="SEARCH:",
            font=("Arial", 10, "bold")
        ).pack(side="left")

        self.search_entry = tk.Entry(
            search_frame,
            width=40
        )

        #SEARCH
        self.search_entry.pack(side="left", padx=10)
        
        self.search_entry.bind( #Runs live search while typing.
            "<KeyRelease>",
            self.live_search
        )

        # TABLE STYLE
        style = ttk.Style()

        style.theme_use("default")

        style.configure(
            "Treeview",
            background="white",
            foreground="black",
            rowheight=28,
            fieldbackground="white",
            bordercolor="black",
            borderwidth=1,
            relief="solid"
        )

        style.configure(
            "Treeview.Heading",
            font=("Arial", 10, "bold"),
            borderwidth=1,
            relief="solid"
        )

        style.map(
            "Treeview",
            background=[("selected", "#347083")]
        )

        table_frame = tk.Frame(
            self.view_window,
            bd=2,
            relief="solid"
        )

        table_frame.pack(fill="both", expand=True)

        columns = (
            "serial",
            "pc",
            "model",
            "processor",
            "ram",
            "storage",
            "keyboard",
            "mouse",
            "monitor",
            "gpu",
            "psu",
            "status",
            "timestamp"
        )

        #Treeview Table Block: Displays the inventory in a tabular format with scrollbars and allows selection for editing or deletion.
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings"
        )

        headings = {
            "serial": "Inventory Number",
            "pc": "PC Name",
            "model": "System Unit Model",
            "processor": "Processor",
            "ram": "RAM",
            "storage": "Storage",
            "keyboard": "Keyboard Serial",
            "mouse": "Mouse Serial",
            "monitor": "Monitor Serial",
            "gpu": "GPU Model",
            "psu": "Power Supply",
            "status": "Status",
            "timestamp": "Date / Time Added or Modified"
        }

        for col in columns:

            self.tree.heading(
                col,
                text=headings[col]
            )

            self.tree.column(
                col,
                width=190 if col == "timestamp" else 110,
                anchor="center"
            )

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.tree.yview
        )

        self.tree.configure(
            yscrollcommand=scrollbar.set
        )

        self.tree.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        #ACTION BUTTONS
        action_frame = tk.Frame(self.view_window)
        action_frame.pack(pady=10)

        tk.Button(
            action_frame,
            text="Modify",
            width=15,
            command=self.edit_selected
        ).grid(row=0, column=0, padx=10)

        tk.Button(
            action_frame,
            text="Delete",
            width=15,
            command=self.delete_selected
        ).grid(row=0, column=1, padx=10)

        #Export
        tk.Button(
            action_frame,
            text="Export",
            width=15,
            command=self.export_selected
        ).grid(row=0, column=2, padx=10)

        tk.Button(
            action_frame,
            text="Back",
            width=15,
            command=self.back_to_main
        ).grid(row=0, column=3, padx=10)

        tk.Button(
            action_frame,
            text="Exit",
            width=15,
            command=self.root.quit
        ).grid(row=0, column=4, padx=10)

        self.refresh_table(self.inventory)

    def back_to_main(self):

        self.view_window.destroy()

        self.root.deiconify()

        #Updates table contents.
    def refresh_table(self, data):

        for item in self.tree.get_children():

            self.tree.delete(item) #Clears old rows before refreshing.

        for setup in data:

            #Displays updated inventory data.
            self.tree.insert(
                "",
                tk.END,
                values=(
                    setup.serial_number,
                    setup.pc_name,
                    setup.system_model,
                    setup.processor,
                    setup.ram,
                    setup.storage_details,
                    setup.keyboard_serial,
                    setup.mouse_serial,
                    setup.monitor_serial,
                    setup.gpu,
                    setup.power_supply,
                    setup.status,
                    setup.timestamp
                )
            )

    def live_search(self, event=None):

        keyword = self.search_entry.get().lower().strip() #Keyword Retrieval

        if keyword == "":

            self.refresh_table(self.inventory)

            return

        filtered = []

        #Search Algorithm Block
        for setup in self.inventory:

            searchable_text = " ".join([ #Combines all fields into one searchable string.
                setup.serial_number,
                setup.pc_name,
                setup.system_model,
                setup.processor,
                setup.ram,
                setup.storage_details,
                setup.keyboard_serial,
                setup.mouse_serial,
                setup.monitor_serial,
                setup.gpu,
                setup.power_supply,
                setup.status,
                setup.timestamp
            ]).lower()

            if keyword in searchable_text: #Checks if keyword exists. If yes, adds to filtered list.

                filtered.append(setup)

        self.refresh_table(filtered)

    def inventory_number_exists(self, serial_number, ignored_serial=None):

        serial_number = serial_number.strip()
        ignored_serial = ignored_serial.strip() if ignored_serial is not None else None

        for setup in self.inventory:

            existing_serial = setup.serial_number.strip()

            if ignored_serial is not None and existing_serial == ignored_serial:

                continue

            if existing_serial == serial_number:

                return True

        return False

    #Selection Block
    def edit_selected(self): #Loads selected setup into form for editing.

        selected = self.tree.selection()

        if not selected:

            messagebox.showerror(
                "Error",
                "Please select a setup."
            )

            return

        values = self.tree.item(
            selected[0],
            "values"
        )

        serial = values[0].strip()

        for setup in self.inventory:

            if setup.serial_number.strip() == serial:

                self.edit_mode = True #Enables edit mode.
                self.editing_serial = setup.serial_number

                self.add_button.grid_remove()

                self.save_button.grid(
                    row=0,
                    column=0,
                    padx=10
                )

                self.cancel_button.grid(
                    row=0,
                    column=1,
                    padx=10
                )
                #Places selected data into textboxes.
                self.serial_number_entry.delete(0, tk.END)
                self.serial_number_entry.insert(0, setup.serial_number)

                self.pc_name_entry.delete(0, tk.END)
                self.pc_name_entry.insert(0, setup.pc_name)

                self.system_model_entry.delete(0, tk.END)
                self.system_model_entry.insert(0, setup.system_model)

                self.processor_entry.delete(0, tk.END)
                self.processor_entry.insert(0, setup.processor)

                self.ram_entry.delete(0, tk.END)
                self.ram_entry.insert(0, setup.ram)

                self.storage_entry.delete(0, tk.END)
                self.storage_entry.insert(0, setup.storage_details)

                self.keyboard_serial_entry.delete(0, tk.END)
                self.keyboard_serial_entry.insert(0, setup.keyboard_serial)

                self.mouse_serial_entry.delete(0, tk.END)
                self.mouse_serial_entry.insert(0, setup.mouse_serial)

                self.monitor_serial_entry.delete(0, tk.END)
                self.monitor_serial_entry.insert(0, setup.monitor_serial)

                self.gpu_entry.delete(0, tk.END)
                self.gpu_entry.insert(0, setup.gpu)

                self.power_supply_entry.delete(0, tk.END)
                self.power_supply_entry.insert(0, setup.power_supply)

                self.status_combobox.set(setup.status)

                self.view_window.destroy()

                self.root.deiconify()

                return

    def save_changes(self):

        serial_number = self.serial_number_entry.get().strip()

        if serial_number == "":

            messagebox.showerror(
                "Error",
                "Inventory Number is required."
            )

            return

        if self.inventory_number_exists(serial_number, self.editing_serial):

            messagebox.showerror(
                "Error",
                "Inventory Number already exists."
            )

            return

        for old_setup in self.inventory:

            if old_setup.serial_number == self.editing_serial:

                self.inventory.remove(old_setup) #Deletes previous version.

                break

        #Creates updated setup object.
        updated_setup = ComputerSetup(
            serial_number,
            self.pc_name_entry.get(),
            self.system_model_entry.get(),
            self.processor_entry.get(),
            self.storage_entry.get(),
            self.ram_entry.get(),
            self.keyboard_serial_entry.get(),
            self.mouse_serial_entry.get(),
            self.monitor_serial_entry.get(),
            self.gpu_entry.get(),
            self.power_supply_entry.get(),
            self.status_combobox.get(),
            self.get_current_timestamp()
        )

        self.inventory.append(updated_setup) #Stores updated data.

        self.save_data()

        self.edit_mode = False
        self.editing_serial = None

        self.save_button.grid_remove()
        self.cancel_button.grid_remove()

        self.add_button.grid(
            row=0,
            column=0,
            padx=10
        )

        self.clear_entries()

        messagebox.showinfo(
            "Updated",
            "Setup updated successfully!"
        )

        self.root.withdraw()

        self.open_view_window()

    def cancel_edit(self):

        confirm = messagebox.askyesno(
            "Discard Changes",
            "Are you sure you want to discard all changes?"
        )

        if not confirm:
            return

        self.edit_mode = False
        self.editing_serial = None

        self.save_button.grid_remove()
        self.cancel_button.grid_remove()

        self.add_button.grid(
            row=0,
            column=0,
            padx=10
        )

        self.clear_entries()

        messagebox.showinfo(
            "Cancelled",
            "Edit cancelled successfully."
        )

        self.root.withdraw()

        self.open_view_window()

    #DELETE FUNCTION
    def delete_selected(self):

        selected = self.tree.selection()

        if not selected:

            messagebox.showerror(
                "Error",
                "Please select a setup."
            )

            return

        values = self.tree.item(
            selected[0],
            "values"
        )

        serial = values[0].strip()

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete setup {serial}?"
        )

        if not confirm:

            return

        passkey = simpledialog.askstring(
            "Passkey Required",
            "Enter passkey:",
            show="*"
        )

        if passkey != "Admin123":

            messagebox.showerror(
                "Error",
                "Incorrect passkey."
            )

            return

        for setup in self.inventory:

            if setup.serial_number.strip() == serial:

                self.inventory.remove(setup)

                self.save_data()

                self.refresh_table(self.inventory)

                messagebox.showinfo(
                    "Deleted",
                    "Setup deleted successfully!"
                )

                return

    #export function
    def get_selected_setup(self):

        selected = self.tree.selection()

        if not selected:

            messagebox.showerror(
                "Error",
                "Please select a setup."
            )

            return None

        values = self.tree.item(
            selected[0],
            "values"
        )

        serial = values[0].strip()

        for setup in self.inventory:

            if setup.serial_number.strip() == serial:

                return setup

        messagebox.showerror(
            "Error",
            "Selected setup was not found."
        )

        return None

    def export_selected(self):

        setup = self.get_selected_setup()

        if setup is None:

            return

        downloads_folder = os.path.join(
            os.path.expanduser("~"),
            "Downloads"
        )

        if not os.path.exists(downloads_folder):

            downloads_folder = os.getcwd()

        file_name = self.make_pdf_filename(setup)
        file_path = os.path.join(downloads_folder, file_name)
        file_path = self.get_unique_file_path(file_path)

        try:

            self.create_setup_pdf(setup, file_path)

            messagebox.showinfo(
                "Exported",
                f"Setup exported successfully:\n{file_path}"
            )

        except Exception as error:

            messagebox.showerror(
                "Error",
                f"Failed to export PDF.\n{error}"
            )

    def make_pdf_filename(self, setup):

        base_name = setup.pc_name.strip() or setup.serial_number.strip() or "computer_setup"
        base_name = re.sub(r'[<>:"/\\|?*]', "_", base_name)
        base_name = re.sub(r"\s+", "_", base_name).strip("._")

        if base_name == "":

            base_name = "computer_setup"

        return f"{base_name}.pdf"

    def get_unique_file_path(self, file_path):

        if not os.path.exists(file_path):

            return file_path

        folder = os.path.dirname(file_path)
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        extension = os.path.splitext(file_path)[1]
        counter = 1

        while True:

            new_path = os.path.join(
                folder,
                f"{base_name}_{counter}{extension}"
            )

            if not os.path.exists(new_path):

                return new_path

            counter += 1

    def create_setup_pdf(self, setup, file_path):

        page_width = 216 #3 inches
        page_height = 288 #4 inches
        left_margin = 14
        top_y = 266

        details = [
            ("Inventory Number", setup.serial_number),
            ("System Unit Model", setup.system_model),
            ("Processor", setup.processor),
            ("RAM", setup.ram),
            ("Storage", setup.storage_details),
            ("Keyboard Serial", setup.keyboard_serial),
            ("Mouse Serial", setup.mouse_serial),
            ("Monitor Serial", setup.monitor_serial),
            ("GPU Model", setup.gpu),
            ("Power Supply", setup.power_supply)
        ]

        lines = []

        lines.append(("bold", 13, left_margin, top_y, setup.pc_name or "Unnamed PC"))
        y_position = top_y - 20

        for label, value in details:

            text = f"{label}: {value}"
            wrapped_lines = textwrap.wrap(
                text,
                width=38,
                break_long_words=True
            ) or [text]

            for wrapped_line in wrapped_lines[:2]:

                if y_position < 18:

                    break

                lines.append(("regular", 7.5, left_margin, y_position, wrapped_line))
                y_position -= 9

            if y_position < 18:

                break

        self.write_pdf(file_path, page_width, page_height, lines)

    def write_pdf(self, file_path, page_width, page_height, lines):

        content_lines = []

        for font_style, font_size, x_position, y_position, text in lines:

            font_name = "F2" if font_style == "bold" else "F1"
            safe_text = self.escape_pdf_text(text)
            content_lines.append(
                f"BT /{font_name} {font_size} Tf {x_position} {y_position} Td ({safe_text}) Tj ET"
            )

        content = "\n".join(content_lines).encode("latin-1", "replace")

        objects = [
            b"<< /Type /Catalog /Pages 2 0 R >>",
            b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
            (
                f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {page_width} {page_height}] "
                f"/Resources << /Font << /F1 4 0 R /F2 5 0 R >> >> /Contents 6 0 R >>"
            ).encode("latin-1"),
            b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
            b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>",
            b"<< /Length " + str(len(content)).encode("latin-1") + b" >>\nstream\n" + content + b"\nendstream"
        ]

        with open(file_path, "wb") as pdf_file:

            pdf_file.write(b"%PDF-1.4\n")
            offsets = [0]

            for index, obj in enumerate(objects, start=1):

                offsets.append(pdf_file.tell())
                pdf_file.write(f"{index} 0 obj\n".encode("latin-1"))
                pdf_file.write(obj)
                pdf_file.write(b"\nendobj\n")

            xref_position = pdf_file.tell()
            pdf_file.write(f"xref\n0 {len(objects) + 1}\n".encode("latin-1"))
            pdf_file.write(b"0000000000 65535 f \n")

            for offset in offsets[1:]:

                pdf_file.write(f"{offset:010d} 00000 n \n".encode("latin-1"))

            pdf_file.write(
                (
                    f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
                    f"startxref\n{xref_position}\n%%EOF"
                ).encode("latin-1")
            )

    def escape_pdf_text(self, text):

        return str(text).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

    #SAVED  DATA
    def save_data(self):

        #Converts all objects into dictionaries.
        data = [
            setup.to_dict()
            for setup in self.inventory
        ]

        with open(self.FILE_NAME, "w") as file:

            #JSON Save Block
            json.dump(data, file, indent=4)

    #PURPOSE: Loads saved data from JSON file.
    def load_data(self):

        if os.path.exists(self.FILE_NAME): #Checks if save file exists.

            try:

                with open(self.FILE_NAME, "r") as file:

                    data = json.load(file)

                    for item in data:

                        setup = ComputerSetup(
                            item.get("serial_number", ""),
                            item.get("pc_name", ""),
                            item.get("system_model", ""),
                            item.get("processor", ""),
                            item.get("storage_details", ""),
                            item.get("ram", ""),
                            item.get("keyboard_serial", ""),
                            item.get("mouse_serial", ""),
                            item.get("monitor_serial", ""),
                            item.get("gpu", ""),
                            item.get("power_supply", ""),
                            item.get("status", "Available"),
                            item.get("timestamp", "")
                        )

                        self.inventory.append(setup)

            except:

                messagebox.showerror(
                    "Error",
                    "Failed to load inventory data."
                )

    def clear_entries(self):

        self.serial_number_entry.delete(0, tk.END)
        self.pc_name_entry.delete(0, tk.END)
        self.system_model_entry.delete(0, tk.END)
        self.processor_entry.delete(0, tk.END)
        self.ram_entry.delete(0, tk.END)
        self.storage_entry.delete(0, tk.END)
        self.keyboard_serial_entry.delete(0, tk.END)
        self.mouse_serial_entry.delete(0, tk.END)
        self.monitor_serial_entry.delete(0, tk.END)
        self.gpu_entry.delete(0, tk.END)
        self.power_supply_entry.delete(0, tk.END)
        self.status_combobox.set("Available")
