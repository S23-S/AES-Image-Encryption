import tkinter as tk
from tkinter import filedialog, messagebox
from encryptor import encrypt_ecb, encrypt_cbc, encrypt_ctr
from image_utils import load_image, save_image
from Crypto.Random import get_random_bytes
from PIL import Image, ImageTk, ImageDraw
import os

# Modern color palette
BG = "#0a0e27"          # deep dark blue
CARD = "#1a1f3a"        # card background
ACCENT = "#00d9ff"      # cyan accent
ACCENT_HOVER = "#00b8d4"
SUCCESS = "#00e676"     # green
DANGER = "#ff1744"      # red
WARNING = "#ffc107"     # amber
TEXT = "#e8eaf6"        # light text
TEXT_DIM = "#9fa8da"    # dimmed text

class ModernButton(tk.Canvas):
    def __init__(self, parent, text, command, bg_color=ACCENT, width=200, height=50):
        super().__init__(parent, width=width, height=height, bg=CARD, 
                        highlightthickness=0, cursor="hand2")
        
        self.command = command
        self.bg_color = bg_color
        self.hover_color = self._adjust_color(bg_color, 1.2)
        self.pressed_color = self._adjust_color(bg_color, 0.8)
        self.text = text
        self.is_hovered = False
        self.is_pressed = False
        
        self.draw_button()
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_press)
        self.bind("<ButtonRelease-1>", self.on_release)
    
    def _adjust_color(self, color, factor):
        """Lighten or darken a hex color"""
        color = color.lstrip('#')
        r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        r = min(255, int(r * factor))
        g = min(255, int(g * factor))
        b = min(255, int(b * factor))
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def draw_button(self):
        self.delete("all")
        color = self.pressed_color if self.is_pressed else (
                self.hover_color if self.is_hovered else self.bg_color)
        
        # Rounded rectangle
        self.create_rounded_rect(5, 5, self.winfo_reqwidth()-5, 
                                self.winfo_reqheight()-5, 10, fill=color, outline="")
        
        # Shadow effect
        if not self.is_pressed:
            self.create_rounded_rect(7, 7, self.winfo_reqwidth()-3, 
                                    self.winfo_reqheight()-3, 10, fill="", 
                                    outline=self._adjust_color(color, 0.5), width=1)
        
        # Text
        self.create_text(self.winfo_reqwidth()//2, self.winfo_reqheight()//2,
                        text=self.text, fill="white", 
                        font=("Segoe UI", 11, "bold"))
    
    def create_rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = [x1+r, y1, x1+r, y1, x2-r, y1, x2-r, y1, x2, y1,
                 x2, y1+r, x2, y1+r, x2, y2-r, x2, y2-r, x2, y2,
                 x2-r, y2, x2-r, y2, x1+r, y2, x1+r, y2, x1, y2,
                 x1, y2-r, x1, y2-r, x1, y1+r, x1, y1+r, x1, y1]
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def on_enter(self, e):
        self.is_hovered = True
        self.draw_button()
    
    def on_leave(self, e):
        self.is_hovered = False
        self.draw_button()
    
    def on_press(self, e):
        self.is_pressed = True
        self.draw_button()
    
    def on_release(self, e):
        self.is_pressed = False
        self.draw_button()
        if self.is_hovered:
            self.command()


class AESImageGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AES Image Encryption Demo")
        self.root.geometry("900x700")
        self.root.minsize(700, 600)  # Minimum window size
        self.root.configure(bg=BG)
        self.root.resizable(True, True)  # Enable resizing

        self.image_path = None
        self.key = get_random_bytes(32)

        self.build_ui()
        
        # Bind resize event for responsive layout
        self.root.bind('<Configure>', self.on_resize)

    def build_ui(self):
        # Main container with scrollbar support
        main_container = tk.Frame(self.root, bg=BG)
        main_container.pack(fill="both", expand=True)
        
        # Header
        header = tk.Frame(main_container, bg=BG)
        header.pack(fill="x", pady=(20, 10))
        
        title_label = tk.Label(header, text="🔐 AES IMAGE ENCRYPTION",
                              fg=ACCENT, bg=BG, 
                              font=("Segoe UI", 24, "bold"))
        title_label.pack()
        
        subtitle = tk.Label(header, 
                           text="Visual Demonstration of Encryption Modes",
                           fg=TEXT_DIM, bg=BG, 
                           font=("Segoe UI", 11))
        subtitle.pack(pady=(5, 10))
        
        # Warning banner
        warning_frame = tk.Frame(main_container, bg=DANGER, height=50)
        warning_frame.pack(fill="x", padx=40, pady=(0, 20))
        warning_frame.pack_propagate(False)
        
        tk.Label(warning_frame, 
                text="⚠ WARNING: ECB mode is cryptographically weak and reveals patterns!",
                fg="white", bg=DANGER, 
                font=("Segoe UI", 10, "bold")).pack(expand=True)
        
        # Main content area with responsive layout
        self.content = tk.Frame(main_container, bg=BG)
        self.content.pack(fill="both", expand=True, padx=40, pady=(0, 20))
        
        # Store column references for responsive layout
        self.left_col = tk.Frame(self.content, bg=BG)
        self.right_col = tk.Frame(self.content, bg=BG)
        
        # Initial layout
        self.update_layout()
        
        self.build_key_card(self.left_col)
        self.build_image_card(self.left_col)
        self.build_encryption_card(self.right_col)
    
    def on_resize(self, event):
        """Handle window resize to adjust layout"""
        if event.widget == self.root:
            self.update_layout()
    
    def update_layout(self):
        """Switch between side-by-side and stacked layout based on width"""
        width = self.root.winfo_width()
        
        # Forget current packing
        self.left_col.pack_forget()
        self.right_col.pack_forget()
        
        if width < 800:  # Stack vertically on narrow windows
            self.left_col.pack(fill="both", expand=True)
            self.right_col.pack(fill="both", expand=True, pady=(20, 0))
        else:  # Side by side on wider windows
            self.left_col.pack(side="left", fill="both", expand=True, padx=(0, 10))
            self.right_col.pack(side="right", fill="both", expand=True, padx=(10, 0))

    def create_card(self, parent, title, icon=""):
        card = tk.Frame(parent, bg=CARD, padx=20, pady=20)
        card.pack(fill="both", expand=True, pady=(0, 20))
        
        header = tk.Frame(card, bg=CARD)
        header.pack(fill="x", pady=(0, 15))
        
        tk.Label(header, text=f"{icon} {title}", 
                fg=TEXT, bg=CARD,
                font=("Segoe UI", 13, "bold")).pack(anchor="w")
        
        # Decorative line
        line = tk.Frame(card, bg=ACCENT, height=2)
        line.pack(fill="x", pady=(5, 15))
        
        return card

    def build_key_card(self, parent):
        card = self.create_card(parent, "ENCRYPTION KEY", "🔑")
        
        # Key display
        key_frame = tk.Frame(card, bg=CARD)
        key_frame.pack(fill="x", pady=(0, 15))
        
        self.key_display = tk.Text(key_frame, height=3, bg=BG, fg=ACCENT,
                                   insertbackground=ACCENT, relief="flat",
                                   font=("Consolas", 9), wrap="word",
                                   selectbackground=ACCENT_HOVER)
        self.key_display.pack(fill="x", padx=2, pady=2)
        self.update_key_display()
        
        # Buttons
        btn_frame = tk.Frame(card, bg=CARD)
        btn_frame.pack(fill="x")
        
        ModernButton(btn_frame, "🔄 Generate New", self.generate_key, 
                    ACCENT, 180, 45).pack(side="left", padx=(0, 10))
        ModernButton(btn_frame, "📋 Copy Key", self.copy_key, 
                    SUCCESS, 140, 45).pack(side="left")

    def build_image_card(self, parent):
        card = self.create_card(parent, "IMAGE SOURCE", "🖼️")
        
        # Image preview frame with border
        preview_frame = tk.Frame(card, bg="#0d1224", relief="flat", padx=10, pady=10)
        preview_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        # Image preview label
        self.image_preview = tk.Label(preview_frame, 
                                      text="No image selected\n\n📷\n\nClick 'Load Image' to begin",
                                      fg=TEXT_DIM, bg="#0d1224",
                                      font=("Segoe UI", 10),
                                      width=30, height=12,
                                      relief="flat")
        self.image_preview.pack(expand=True, fill="both")
        
        # Status display below preview
        self.image_status = tk.Label(card, 
                                     text="",
                                     fg=TEXT_DIM, bg=CARD,
                                     font=("Segoe UI", 9, "italic"))
        self.image_status.pack(pady=(0, 15))
        
        # Buttons
        btn_frame = tk.Frame(card, bg=CARD)
        btn_frame.pack(fill="x")
        
        ModernButton(btn_frame, "📁 Load Image", self.select_image, 
                    SUCCESS, 180, 45).pack(side="left", padx=(0, 10))
        ModernButton(btn_frame, "✨ Test Pattern", self.create_pattern, 
                    WARNING, 140, 45).pack(side="left")

    def build_encryption_card(self, parent):
        card = self.create_card(parent, "ENCRYPTION MODES", "⚡")
        
        # ECB Mode
        self.create_mode_section(card, 
            "ECB Mode", 
            "Electronic Codebook - INSECURE",
            "Identical blocks produce identical ciphertext",
            DANGER,
            lambda: self.encrypt('ECB'))
        
        # CBC Mode
        self.create_mode_section(card,
            "CBC Mode",
            "Cipher Block Chaining - SECURE",
            "Each block depends on previous blocks",
            SUCCESS,
            lambda: self.encrypt('CBC'))
        
        # CTR Mode
        self.create_mode_section(card,
            "CTR Mode",
            "Counter Mode - SECURE",
            "Stream cipher using block counter",
            ACCENT,
            lambda: self.encrypt('CTR'))

    def create_mode_section(self, parent, title, subtitle, desc, color, command):
        section = tk.Frame(parent, bg="#0d1224", padx=15, pady=15)
        section.pack(fill="x", pady=(0, 15))
        
        tk.Label(section, text=title, fg=TEXT, bg="#0d1224",
                font=("Segoe UI", 12, "bold")).pack(anchor="w")
        
        tk.Label(section, text=subtitle, fg=color, bg="#0d1224",
                font=("Segoe UI", 9, "italic")).pack(anchor="w", pady=(2, 5))
        
        tk.Label(section, text=desc, fg=TEXT_DIM, bg="#0d1224",
                font=("Segoe UI", 9), wraplength=300).pack(anchor="w", pady=(0, 10))
        
        ModernButton(section, f"Encrypt with {title.split()[0]}", 
                    command, color, 280, 45).pack()

    def update_key_display(self):
        self.key_display.delete("1.0", tk.END)
        self.key_display.insert(tk.END, self.key.hex())

    def generate_key(self):
        self.key = get_random_bytes(32)
        self.update_key_display()
        messagebox.showinfo("Success", "New encryption key generated!")

    def copy_key(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.key.hex())
        messagebox.showinfo("Copied", "Encryption key copied to clipboard!")

    def select_image(self):
        self.image_path = filedialog.askopenfilename(
            title="Select an image",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")])
        if self.image_path:
            filename = os.path.basename(self.image_path)
            self.image_status.config(text=f"✓ {filename}", fg=SUCCESS)
            self.display_image(self.image_path)

    def create_pattern(self):
        img = Image.new('RGB', (256, 256), 'white')
        d = ImageDraw.Draw(img)
        for i in range(0, 256, 32):
            d.rectangle([i, i, i+64, i+64], fill='black')
        os.makedirs('input', exist_ok=True)
        self.image_path = 'input/test_pattern.png'
        img.save(self.image_path)
        self.image_status.config(text="✓ test_pattern.png", fg=SUCCESS)
        self.display_image(self.image_path)
    
    def display_image(self, image_path):
        """Display the selected image in the preview area"""
        try:
            # Open and resize image to fit preview
            img = Image.open(image_path)
            
            # Get the preview area size (approximate)
            max_width = 280
            max_height = 200
            
            # Calculate scaling to fit within preview while maintaining aspect ratio
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(img)
            
            # Update the preview label
            self.image_preview.config(image=photo, text="")
            self.image_preview.image = photo  # Keep a reference!
            
        except Exception as e:
            self.image_preview.config(text=f"Error loading image:\n{str(e)}", 
                                     fg=DANGER)
            messagebox.showerror("Error", f"Could not load image:\n{str(e)}")

    def encrypt(self, mode):
        if not self.image_path:
            messagebox.showerror("Error", "Please select an image first!")
            return

        try:
            img, data, size = load_image(self.image_path)

            if mode == 'ECB':
                encrypted = encrypt_ecb(data)
                out = 'output/ecb.png'
            elif mode == 'CBC':
                encrypted = encrypt_cbc(data)
                out = 'output/cbc.png'
            else:
                encrypted = encrypt_ctr(data)
                out = 'output/ctr.png'

            save_image(encrypted[:len(data)], size, out)
            messagebox.showinfo("Success!", 
                              f"{mode} encryption complete!\n\nSaved to: {out}")
        except Exception as e:
            messagebox.showerror("Error", f"Encryption failed:\n{str(e)}")


if __name__ == '__main__':
    os.makedirs('output', exist_ok=True)
    root = tk.Tk()
    app = AESImageGUI(root)
    root.mainloop()