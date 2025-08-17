import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4, legal, A3
from PIL import Image, ImageTk
import os
import sys
from threading import Thread
TABLOID = (11 * 72, 17 * 72) 
class ImageToPDFConverter:
    def __init__(self, root):
        self.root = root
        self.image_paths = []
        self.output_pdf_name = tk.StringVar(value="output")
        self.selected_images_listbox = tk.Listbox(root, selectmode=tk.MULTIPLE)
        self.progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
        self.page_size = tk.StringVar(value="A4")
        self.image_position = tk.StringVar(value="Center")
        self.thumbnail_images = []  
        
        self.initialize_ui()

    def initialize_ui(self):
        
        self.root.title("Image to PDF Converter")
        self.root.geometry("500x700")
        
        
        title_label = tk.Label(self.root, text="Image to PDF Converter", font=("Helvetica", 16, "bold"))
        title_label.pack(pady=10)
        
        
        select_frame = tk.Frame(self.root)
        select_frame.pack(pady=5, fill=tk.X)
        
        select_images_button = tk.Button(select_frame, text="Select Images", command=self.select_images)
        select_images_button.pack(side=tk.LEFT, padx=5)
        
        remove_button = tk.Button(select_frame, text="Remove Selected", command=self.remove_selected_images)
        remove_button.pack(side=tk.LEFT, padx=5)
        
      
        list_frame = tk.Frame(self.root)
        list_frame.pack(pady=5, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.selected_images_listbox = tk.Listbox(
            list_frame, 
            selectmode=tk.MULTIPLE,
            yscrollcommand=scrollbar.set,
            height=10
        )
        self.selected_images_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.selected_images_listbox.yview)
        
        
        self.selected_images_listbox.bind("<Double-Button-1>", self.show_image_preview)
        
        
        settings_frame = tk.LabelFrame(self.root, text="PDF Settings", padx=5, pady=5)
        settings_frame.pack(pady=5, fill=tk.X)
        
       
        name_frame = tk.Frame(settings_frame)
        name_frame.pack(fill=tk.X, pady=2)
        tk.Label(name_frame, text="PDF Name:").pack(side=tk.LEFT)
        pdf_name_entry = tk.Entry(name_frame, textvariable=self.output_pdf_name, width=30)
        pdf_name_entry.pack(side=tk.LEFT, padx=5)
        
        
        

        size_frame = tk.Frame(settings_frame)
        size_frame.pack(fill=tk.X, pady=2)
        tk.Label(size_frame, text="Page Size:").pack(side=tk.LEFT)
        sizes = [("Letter (8.5x11 in)", "letter"), ("A4 (210x297 mm)", "A4"), 
        ("Legal (8.5x14 in)", "legal"), ("Tabloid (11x17 in)", "tabloid"),
        ("A3 (297x420 mm)", "A3")]
        for text, size in sizes:
            rb = tk.Radiobutton(size_frame, text=text, variable=self.page_size, value=size)
            rb.pack(side=tk.LEFT, padx=5)
        
        
        pos_frame = tk.Frame(settings_frame)
        pos_frame.pack(fill=tk.X, pady=2)
        tk.Label(pos_frame, text="Image Position:").pack(side=tk.LEFT)
        positions = ["Center", "Top-Left", "Top-Right", "Bottom-Left", "Bottom-Right", "Stretch"]
        for pos in positions:
            rb = tk.Radiobutton(pos_frame, text=pos, variable=self.image_position, value=pos)
            rb.pack(side=tk.LEFT, padx=2)
        
        
        self.progress.pack(pady=10)
        
        
        convert_button = tk.Button(self.root, text="Convert to PDF", command=self.start_conversion_thread)
        convert_button.pack(pady=10)
        
        
        self.status_var = tk.StringVar()
        self.status_bar = tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.update_status("Ready")

    def update_status(self, message):
        self.status_var.set(message)
        self.root.update_idletasks()

    def select_images(self):
        try:
            files = filedialog.askopenfilenames(
                title="Select Images",
                filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.tiff")]
            )
            
            if files:
                
                valid_files = []
                for file in files:
                    try:
                        with Image.open(file) as img:
                            img.verify()  
                        valid_files.append(file)
                    except (IOError, SyntaxError) as e:
                        messagebox.showwarning(
                            "Invalid Image",
                            f"Skipping {os.path.basename(file)}: Not a valid image file"
                        )
                
                if valid_files:
                    self.image_paths.extend(valid_files)
                    self.update_selected_images_listbox()
                    self.update_status(f"{len(self.image_paths)} images selected")
                else:
                    self.update_status("No valid images selected")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while selecting images: {str(e)}")
            self.update_status("Error selecting images")

    def remove_selected_images(self):
        try:
            selected_indices = list(self.selected_images_listbox.curselection())
            if not selected_indices:
                messagebox.showinfo("Info", "No images selected for removal")
                return
                
            
            for index in sorted(selected_indices, reverse=True):
                del self.image_paths[index]
                
            self.update_selected_images_listbox()
            self.update_status(f"{len(selected_indices)} images removed")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while removing images: {str(e)}")
            self.update_status("Error removing images")

    def update_selected_images_listbox(self):
        self.selected_images_listbox.delete(0, tk.END)
        for image_path in self.image_paths:
            self.selected_images_listbox.insert(tk.END, os.path.basename(image_path))

    def show_image_preview(self, event):
        try:
            selection = self.selected_images_listbox.curselection()
            if not selection:
                return
                
            index = selection[0]
            image_path = self.image_paths[index]
            
            preview_window = tk.Toplevel(self.root)
            preview_window.title("Image Preview")
            
            img = Image.open(image_path)
            img.thumbnail((400, 400))  # Resize for preview
            
            
            photo = ImageTk.PhotoImage(img)
            self.thumbnail_images.append(photo)  # Keep reference
            
            label = tk.Label(preview_window, image=photo)
            label.pack(padx=10, pady=10)
            
            info_label = tk.Label(
                preview_window, 
                text=f"{os.path.basename(image_path)}\nSize: {img.width}x{img.height} px"
            )
            info_label.pack(pady=5)
            
            close_button = tk.Button(preview_window, text="Close", command=preview_window.destroy)
            close_button.pack(pady=5)
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not display preview: {str(e)}")

    def start_conversion_thread(self):
        if not self.image_paths:
            messagebox.showwarning("Warning", "No images selected for conversion")
            return
            
        
        self.root.children["!button"]["state"] = tk.DISABLED
        self.progress["value"] = 0
        self.update_status("Starting conversion...")
        
        
        thread = Thread(target=self.convert_images_to_pdf)
        thread.start()
        
        
        self.check_thread_status(thread)

    def check_thread_status(self, thread):
        if thread.is_alive():
            self.root.after(100, lambda: self.check_thread_status(thread))
        else:
            self.root.children["!button"]["state"] = tk.NORMAL
            self.update_status("Ready")

    def convert_images_to_pdf(self):
        try:
            output_pdf_path = self.output_pdf_name.get() + ".pdf" if self.output_pdf_name.get() else "output.pdf"
            
            
            page_sizes = {
                "letter": letter,
                "A4": A4,
                "legal": legal,
                "tabloid": TABLOID,
                "A3": A3
            }
            selected_size = page_sizes.get(self.page_size.get(), A4)
            
            pdf = canvas.Canvas(output_pdf_path, pagesize=selected_size)
            page_width, page_height = selected_size
            
            total_images = len(self.image_paths)
            processed_images = 0
            
            for image_path in self.image_paths:
                try:
                    with Image.open(image_path) as img:
                        
                        if self.image_position.get() == "Stretch":
                            img_width = page_width
                            img_height = page_height
                            x_pos = 0
                            y_pos = 0
                        else:
                           
                            scale_factor = min(
                                (page_width - 40) / img.width,  
                                (page_height - 40) / img.height
                            )
                            img_width = img.width * scale_factor
                            img_height = img.height * scale_factor
                            
                            
                            if self.image_position.get() == "Center":
                                x_pos = (page_width - img_width) / 2
                                y_pos = (page_height - img_height) / 2
                            elif self.image_position.get() == "Top-Left":
                                x_pos = 20
                                y_pos = page_height - img_height - 20
                            elif self.image_position.get() == "Top-Right":
                                x_pos = page_width - img_width - 20
                                y_pos = page_height - img_height - 20
                            elif self.image_position.get() == "Bottom-Left":
                                x_pos = 20
                                y_pos = 20
                            elif self.image_position.get() == "Bottom-Right":
                                x_pos = page_width - img_width - 20
                                y_pos = 20
                            else:  
                                x_pos = (page_width - img_width) / 2
                                y_pos = (page_height - img_height) / 2
                        
                        
                        pdf.setFillColor(255, 255, 255)
                        pdf.rect(0, 0, page_width, page_height, fill=True)
                        pdf.drawInlineImage(img, x_pos, y_pos, width=img_width, height=img_height)
                        pdf.showPage()
                        
                        processed_images += 1
                        progress = (processed_images / total_images) * 100
                        self.progress["value"] = progress
                        self.update_status(f"Processing {processed_images}/{total_images}: {os.path.basename(image_path)}")
                        
                except Exception as img_error:
                    messagebox.showwarning(
                        "Image Error",
                        f"Could not process {os.path.basename(image_path)}: {str(img_error)}"
                    )
                    continue
            
            pdf.save()
            self.progress["value"] = 100
            self.update_status(f"Successfully created {output_pdf_path} with {processed_images} pages")
            messagebox.showinfo("Success", f"PDF created successfully: {output_pdf_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create PDF: {str(e)}")
            self.update_status("Conversion failed")
        finally:
            self.progress["value"] = 0

def main():
    root = tk.Tk()
    converter = ImageToPDFConverter(root)
    root.mainloop()

if __name__ == "__main__":
    main()