# import machine

# AXS5106L_I2C_ADDR = 0x63

# # Register definitions (based on common touch controllers like FT6x36)
# # Note: You may need to adjust these based on the actual AXS5106L datasheet
# AXS5106L_REG_MODE = 0x00
# AXS5106L_REG_GEST_ID = 0x01
# AXS5106L_REG_TD_STATUS = 0x02
# AXS5106L_REG_P1_XH = 0x03
# AXS5106L_REG_P1_XL = 0x04
# AXS5106L_REG_P1_YH = 0x05
# AXS5106L_REG_P1_YL = 0x06

# class AXS5106L:
#     def __init__(self, i2c):
#         self.i2c = i2c
#         self.addr = AXS5106L_I2C_ADDR
#         self.init_controller()

#     def init_controller(self):
#         try:
#             # Perform a basic check for device presence
#             self.i2c.writeto(self.addr, b'\x00')
#             print("AXS5106L detected. Initializing...")
            
#             # Write a command to set the device to normal operation mode
#             # This register and value is an example based on similar controllers.
#             # Refer to the AXS5106L datasheet for the correct command.
#             # self.i2c.writeto_mem(self.addr, AXS5106L_REG_MODE, b'\x00')
            
#             print("AXS5106L initialized.")

#         except OSError as e:
#             print("I2C communication error during initialization:", e)
#             raise

#     def read_touch(self):
#         try:
#             print("Reading touch data...")
#             # Read touch data
#             data = self.i2c.readfrom_mem(self.addr, AXS5106L_REG_TD_STATUS, 6)
#             print("Raw touch data:", list(data))

#             num_touches = data[0] & 0x0F # The number of touches is often in the low nibble of the status register
            
#             if num_touches > 0:
#                 x_msb = data[1]
#                 x_lsb = data[2]
#                 y_msb = data[3]
#                 y_lsb = data[4]
                
#                 # Reconstruct the 12-bit coordinate from the two bytes
#                 x = ((x_msb & 0x0F) << 8) | x_lsb
#                 y = ((y_msb & 0x0F) << 8) | y_lsb
                
#                 return (num_touches, x, y)
#             else:
#                 return (0, 0, 0)
#         except OSError as e:
#             print("I2C communication error during touch read:", e)
#             return (0, 0, 0)

import machine
import time

# Use the I2C address that works for your board.
AXS5106L_I2C_ADDR = 0x63

# Assuming TD_STATUS is correct.
AXS5106L_REG_TD_STATUS = 0x02

class AXS5106L:
    def __init__(self, i2c, reset_pin):
        self.i2c = i2c
        self.addr = AXS5106L_I2C_ADDR
        self.reset_pin = reset_pin
        self.init_controller()

    def init_controller(self):
        # Configure and toggle the reset pin
        print("Resetting AXS5106L...")
        reset = machine.Pin(self.reset_pin, machine.Pin.OUT)
        reset.value(0)
        time.sleep_ms(10)
        reset.value(1)
        time.sleep_ms(100)
        
        try:
            # Check for device presence at the new address
            self.i2c.writeto(self.addr, b'')
            print("AXS5106L detected at address 0x63. Initializing...")
        except OSError as e:
            print("I2C communication error during initialization:", e)
            raise

    def read_touch(self):
        try:
            # **Wake up the controller before reading**
            # A zero-byte write is a common wake-up sequence for I2C devices.
            self.i2c.writeto(self.addr, b'')
            time.sleep_ms(5)
            
            # Read touch data
            data = self.i2c.readfrom_mem(self.addr, AXS5106L_REG_TD_STATUS, 6)
            
            # # The coordinate reconstruction is an example based on common controllers.
            # # Refer to the datasheet for the exact layout.
            # num_touches = (data[0] & 0x0F)
            
            # if num_touches > 0:
            #     x = ((data[1] & 0x0F) << 8) | data[2]
            #     y = ((data[3] & 0x0F) << 8) | data[4]
            #     return (num_touches, x, y)
            # else:
            #     return (0, 0, 0)

            return (0, 0, 0)  # Placeholder until actual read is implemented
        except OSError as e:
            print("I2C communication error during touch read:", e)
            return (0, 0, 0)
