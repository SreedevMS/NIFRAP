import tkinter as tk
import subprocess

def button1_click():
    subprocess.run("C:/Users/acer/OneDrive/Desktop/Final Review/Application/Web_Scraper.exe", check=True)

def button2_click():
    subprocess.run("C:/Users/acer/OneDrive/Desktop/Final Review/Application/Network_Sniffing.exe", check=True)

root = tk.Tk()
root.title("NIFRAP")
root.iconbitmap("C:/Users/acer/Downloads/hacker.ico")

# Set window size to full screen
window_width = root.winfo_screenwidth()
window_height = root.winfo_screenheight()
root.geometry(f"{window_width}x{window_height}")

# Add a heading label
heading_label = tk.Label(root, text="NIFRAP", font=("Arial", 24, "bold"))
heading_label.pack(pady=20)

image = tk.PhotoImage(file="C:/Users/acer/Downloads/data-mining.png")
image1 = tk.PhotoImage(file="C:/Users/acer/Downloads/remote-control.png")

button1 = tk.Button(root, text="Web Scraping", font=("Arial", 18, "bold"), command=button1_click, image=image, compound=tk.TOP)
button1.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

button2 = tk.Button(root, text="Network Sniffing", font=("Arial", 18, "bold"), command=button2_click, image=image1, compound=tk.TOP)
button2.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

root.mainloop()

