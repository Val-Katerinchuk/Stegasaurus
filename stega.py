from matplotlib.image import imread
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import numpy as np

DELIMITER = '£££'
LENGTH_END = '£'  # Marks end of length header

def steg_write(image_path, message, output_path='edited_image.png'):
    if not image_path.lower().endswith('.png'):
        raise ValueError('The input image must be a PNG file.')

    message += DELIMITER
    binary_message = ''.join(f'{byte:08b}' for byte in message.encode('utf-8'))
    img = Image.open(image_path)
    pixels = np.array(img)
    flat = pixels.flatten()

    # Calculate available space in the image
    total_bits_available = len(flat) * 3  # Each pixel has 3 bits available
    if len(binary_message) > total_bits_available:
        raise ValueError('Message is too large for the given image!')

    # Encode the length of the message as a 32-bit integer
    message_length = len(binary_message)
    message_length_bits = f'{message_length:032b}'  # 32-bit binary length

    # Write the message length in the first 12 pixels (36 bits)
    for i in range(12):  # First 12 pixels for message length (36 bits)
        pos = i * 3  # Each pixel has 3 channels (R, G, B)
        for j in range(3):  # Each channel (R, G, B)
            bit_index = i * 3 + j
            if bit_index < len(message_length_bits):
                flat[pos + j] = (flat[pos + j] & 0xFE) | int(message_length_bits[bit_index])  # Set LSB

    # Write the message binary data across the image
    for i, bit in enumerate(binary_message):
        pixel_index = (i + 12 * 3)  # Start after the first 12 pixels (3 channels each)
        flat[pixel_index] = (flat[pixel_index] & 0xFE) | int(bit)

    # Reshape the image back to the original shape
    new_pixels = flat.reshape(pixels.shape).astype(np.uint8)
    Image.fromarray(new_pixels).save(output_path)
    messagebox.showinfo("Success", f"Message hidden in {output_path}!")


def steg_read(image_path):
    img = Image.open(image_path)
    flat = np.array(img).flatten()

    # Read the length of the message from the first 12 pixels (36 bits)
    message_length_bits = ''
    for i in range(12):  # First 12 pixels for message length (36 bits)
        pos = i * 3
        for j in range(3):  # Each channel (R, G, B)
            message_length_bits += str(flat[pos + j] & 1)  # Read LSB from each channel

    # Convert the length bits to an integer
    message_length = int(message_length_bits[:32], 2)  # Only take the first 32 bits

    # Now that we know the message length, we can read the message
    bits = []
    for i in range(12 * 3, 12 * 3 + message_length):  # Start after the length (12 pixels)
        bits.append(str(flat[i] & 1))  # Read LSB

    # Reconstruct the message from the bits as bytes
    byte_array = bytearray(int(''.join(bits[i:i+8]), 2) for i in range(0, len(bits), 8))
    message = byte_array.decode('utf-8', errors='replace')
    
    # Remove the delimiter if it exists at the end
    if message.endswith(DELIMITER):
        message = message[:-len(DELIMITER)]
    
    return message

#steg_write('mandervilles.png','hpwdy', 'edited_mander.png', 10)
#print(steg_read('edited_mander.png',5,10))

class SteganographyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Steganography Tool")
        
        # Image Selection
        tk.Label(root, text="Image Path:").grid(row=0, column=0, padx=5, pady=5)
        self.image_path_entry = tk.Entry(root, width=40)
        self.image_path_entry.grid(row=0, column=1, padx=5, pady=5)
        tk.Button(root, text="Browse", command=self.browse_image).grid(row=0, column=2, padx=5, pady=5)
        
        # Message (for writing)
        tk.Label(root, text="Message to Hide:").grid(row=1, column=0, padx=5, pady=5)
        self.message_entry = tk.Entry(root, width=40)
        self.message_entry.grid(row=1, column=1, padx=5, pady=5)
        
        
        
        
        
        # Buttons
        tk.Button(root, text="Write Message", command=self.write_message).grid(row=4, column=0, padx=5, pady=5)
        tk.Button(root, text="Read Message", command=self.read_message).grid(row=4, column=1, padx=5, pady=5)
    
    def browse_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("PNG Files", "*.png")])
        if file_path:
            self.image_path_entry.delete(0, tk.END)
            self.image_path_entry.insert(0, file_path)
    
    def write_message(self):
        try:
            image_path = self.image_path_entry.get()
            message = self.message_entry.get()
            #spacing = int(self.spacing_entry.get())
            steg_write(image_path, message)
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def read_message(self):
        try:
            image_path = self.image_path_entry.get()
            #spacing = int(self.spacing_entry.get())
            hidden_message = steg_read(image_path)
            messagebox.showinfo("Hidden Message", f"Extracted Message: {hidden_message}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

# Run the GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = SteganographyApp(root)
    root.mainloop()