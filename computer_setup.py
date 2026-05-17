class ComputerSetup: #Purpose: Creates a blueprint for storing computer setup information.

    def __init__( #constructor 
        self,   
        #Purpose: To hold  user input and assigned it
        serial_number,
        pc_name,
        system_model,
        processor,
        storage_details,
        ram,
        keyboard_serial,
        mouse_serial,
        monitor_serial,
        gpu,
        power_supply,
        status="Available"
    ):
        #Purpose: Saved the received values inside the object permanently
        self.serial_number = serial_number
        self.pc_name = pc_name 
        self.system_model = system_model
        self.processor = processor
        self.storage_details = storage_details
        self.ram = ram
        self.keyboard_serial = keyboard_serial
        self.mouse_serial = mouse_serial
        self.monitor_serial = monitor_serial
        self.gpu = gpu
        self.power_supply = power_supply
        self.status = status


   
    def to_dict(self): #Method Block (Purpose: To convert the computer setup data into a dictionary format for easy storage and retrieval {This is needed because JSON files cannot save custom Python objects directly.}) 
        # Act as translator (json.dump() would fail and Python objects cannot be directly saved to JSON)

        return { #Creates a dictionary containing all object data. Inshort formatted siya sa JSON format file.

            "serial_number": self.serial_number,
            "pc_name": self.pc_name,
            "system_model": self.system_model,
            "processor": self.processor,
            "storage_details": self.storage_details,
            "ram": self.ram,
            "keyboard_serial": self.keyboard_serial,
            "mouse_serial": self.mouse_serial,
            "monitor_serial": self.monitor_serial,
            "gpu": self.gpu, 
            "power_supply": self.power_supply,
            "status": self.status
        }

