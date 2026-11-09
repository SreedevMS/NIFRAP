import tkinter as tk
from tkinter import messagebox
import requests
import xlsxwriter
import os
import re
from bs4 import BeautifulSoup
from docx import Document
from tkinter import ttk, filedialog, messagebox
import psutil
import scapy.all as scapy
from scapy.layers.inet import IP
from tkinter import scrolledtext
from queue import Queue
import threading

def button1_click():


    def scrape_data():
        url = url_entry.get()

        choice = choice_var.get()

        if choice == 1:  # HTML
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            html = soup.prettify()
            htmls = []

            # Save data in Word
            word = filedialog.asksaveasfilename(defaultextension=".docx", filetypes=[("Word Document", "*.docx")], title="Save Word File")
            if word:
                doc = Document()
                doc.add_heading("Web Scraping", level=1)
                doc.add_paragraph(html)
                doc.save(word)
                messagebox.showinfo("Success", "Data saved successfully.")
            else:
                messagebox.showwarning("Warning", "No Word file selected.")

        elif choice == 2:  # TABLE
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            table = soup.find('table')

            if table is None:
                messagebox.showinfo("Info", "No table found on the website.")
                data = []
            else:
                table_data = []
                rows = table.find_all('tr')
                for row in rows:
                    row_data = []
                    columns = row.find_all('td')
                    for column in columns:
                        cell_value = column.text.strip()
                        row_data.append(cell_value)
                    table_data.append(row_data)

                for row in table_data:
                    print(row)
                data = table_data

                # Save data in Excel
                excel = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Workbook", "*.xlsx")], title="Save Excel File")
                if excel:
                    workbook = xlsxwriter.Workbook(excel)
                    worksheet = workbook.add_worksheet()
                    for row_num, row_data in enumerate(data):
                        for col_num, cell_value in enumerate(row_data):
                            worksheet.write(row_num, col_num, cell_value)
                    workbook.close()
                    messagebox.showinfo("Success", "Data saved successfully.")
                else:
                    messagebox.showwarning("Warning", "No Excel file selected.")

        elif choice == 3:  # IMAGES
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            image_tags = soup.find_all('img')

            if len(image_tags) == 0:
                messagebox.showinfo("Info", "No images found on the website.")
            else:
                folder_name = filedialog.askdirectory(title="Select Folder to Save Images")

                if folder_name:
                    if not os.path.exists(folder_name):
                        os.makedirs(folder_name)

                    for img in image_tags:
                        img_url = img.get('src')
                        img_name = re.sub(r'[^a-zA-Z0-9_.-]', '', os.path.basename(img_url))
                        img_data = requests.get(img_url).content
                        with open(os.path.join(folder_name, img_name), 'wb') as handler:
                            handler.write(img_data)

                    messagebox.showinfo("Success", "The images were successfully saved in the selected folder.")
                else:
                    messagebox.showwarning("Warning", "No folder selected.")

        elif choice == 4:  # LINKS
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            links = []
            for link in soup.find_all('a'):
                href = link.get('href')
                if href is not None and href.startswith('http'):
                    links.append(href)

            for link in links:
                print(link)

            # Save links in Excel or Word
            save_choice = save_choice_var.get()

            if save_choice == 1:  # Excel
                excel = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Workbook", "*.xlsx")], title="Save Excel File")
                if excel:
                    workbook = xlsxwriter.Workbook(excel)
                    worksheet = workbook.add_worksheet()
                    for n, link in enumerate(links):
                        worksheet.write(n, 0, link)
                    workbook.close()
                    messagebox.showinfo("Success", "Data saved successfully.")
                else:
                    messagebox.showwarning("Warning", "No Excel file selected.")

            elif save_choice == 2:  # Word
                word = filedialog.asksaveasfilename(defaultextension=".docx", filetypes=[("Word Document", "*.docx")], title="Save Word File")
                if word:
                    doc = Document()
                    doc.add_heading("Web Scraping", level=1)
                    for link in links:
                        doc.add_paragraph(link)
                    doc.save(word)
                    messagebox.showinfo("Success", "Data saved successfully.")
                else:
                    messagebox.showwarning("Warning", "No Word file selected.")

        elif choice == 5:  # TEXTS
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            paragraphs = soup.find_all('p')

            doc = Document()
            doc.add_heading("Web Scraping", level=1)

            for heading in headings:
                doc.add_paragraph(str(heading))
                print(heading.text)
                print('---')
            for paragraph in paragraphs:
                doc.add_paragraph(str(paragraph))
                print(paragraph.text)
                print('\n')

            # Save data in Word
            word = filedialog.asksaveasfilename(defaultextension=".docx", filetypes=[("Word Document", "*.docx")], title="Save Word File")
            if word:
                doc.save(word)
                messagebox.showinfo("Success", "Data saved successfully.")
            else:
                messagebox.showwarning("Warning", "No Word file selected.")

        elif choice == 6:  # EXIT
            root.destroy()

        else:
            messagebox.showwarning("Warning", "Invalid choice. Please enter a number between 1 and 6.")


    # Create the main GUI window
    root = tk.Tk()
    root.title("Web Scraper")
    root.geometry("800x600")

    # Styling the GUI
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("TLabel", background="#f0f0f0")
    style.configure("TFrame", background="#f0f0f0")
    style.configure("TButton", background="#e0e0e0", padding=10, font=("Arial", 12))
    style.configure("TRadiobutton", background="#f0f0f0", font=("Arial", 12))

    heading_label = tk.Label(root, text="WEB SCRAPER", font=("Arial", 20, "bold"))
    # Pack the Label widget to display it
    heading_label.pack(pady=20)
    # URL Entry
    url_frame = ttk.Frame(root)
    url_frame.pack(pady=20)

    url_label = ttk.Label(url_frame, text="Enter the URL:")
    url_label.pack(side="left", padx=10)

    url_entry = ttk.Entry(url_frame, width=40)
    url_entry.pack(side="left")

    # Scrape Data Type
    choice_frame = ttk.LabelFrame(root, text="Choose Data Type")
    choice_frame.pack(pady=20)

    choice_var = tk.IntVar()
    choice_var.set(1)

    choices = [
        ("HTML", 1),
        ("TABLE", 2),
        ("IMAGES", 3),
        ("LINKS", 4),
        ("TEXTS", 5),
        ("EXIT", 6)
    ]

    for text, value in choices:
        choice_radio = ttk.Radiobutton(choice_frame, text=text, variable=choice_var, value=value)
        choice_radio.pack(anchor="w", padx=10, pady=5)

    # Save Option
    save_choice_frame = ttk.LabelFrame(root, text="Choose Save Option")
    save_choice_frame.pack(pady=10)

    save_choice_var = tk.IntVar()
    save_choice_var.set(1)

    save_choices = [
        ("Excel", 1),
        ("Word", 2)
    ]

    for text, value in save_choices:
        save_choice_radio = ttk.Radiobutton(save_choice_frame, text=text, variable=save_choice_var, value=value)
        save_choice_radio.pack(anchor="w", padx=10, pady=5)

    # Scrape Data Button
    scrape_button = ttk.Button(root, text="Scrape Data", command=scrape_data)
    scrape_button.pack(pady=20)

    root.mainloop()
packet_count = 0

def button2_click():

    packet_queue = Queue()
    
    sniffing_active = False

    def get_network_interfaces():
        interfaces = psutil.net_if_addrs()
        return interfaces

    def packet_handler(packet):
        global packet_count

        packet_count += 1

        if packet.haslayer(IP):
            src_ip = packet[IP].src
            dst_ip = packet[IP].dst
            proto = packet[IP].proto
            proto_name = get_protocol_name(proto)
            packet_info = f"Packet {packet_count}: Source IP: {src_ip} | Destination IP: {dst_ip} | Protocol: {proto_name}"
            packet_queue.put(packet_info)  # Add packet info to the queue
            print(packet_info)  # Print packet info

            # Update packet count label and refresh GUI
            packet_count_label.config(text=f"Total packets captured: {packet_count}")
            window.update_idletasks()

    def get_protocol_name(proto):
        protocol_map = {6: "TCP", 17: "UDP", 1: "ICMP", 2: "IGMP", 41: "IPv6", 58: "ICMPv6", 80: "HTTP"}
        return protocol_map.get(proto, "Unknown")

    def start_sniffing(interface, filter):
        global sniffing_active

        sniffing_active = True
        print(f"Sniffing on interface {interface} with filter: {filter}")

        def sniff_packets():
            scapy.sniff(iface=interface, filter=filter, prn=packet_handler)

        # Run the packet capturing process in a separate thread
        sniffing_thread = threading.Thread(target=sniff_packets)
        sniffing_thread.start()

        output_textarea.insert(tk.END, "Sniffing started on interface: " + interface + "\n")
        process_output_queue()

    def stop_sniffing():
        global sniffing_active
        sniffing_active = False
        output_textarea.insert(tk.END, "Sniffing stopped.\n")

    def start_button_click():
        global selected_interface
        selected_interface = interface_listbox.get(tk.ACTIVE)
        start_sniffing(selected_interface, "ip")

    def process_output_queue():
        while not packet_queue.empty():
            packet_info = packet_queue.get()
            output_textarea.insert(tk.END, packet_info + "\n")
        if sniffing_active:
            window.after(100, process_output_queue)

    # Get network interfaces
    interfaces = get_network_interfaces()

    # Create GUI
    window = tk.Tk()
    window.title("Network Packet Sniffer")
    window.geometry("800x600")
    window.iconbitmap("C:/Users/acer/Downloads/remote-control.ico")

    # Interface selection label
    interface_label = tk.Label(window, text="Select Network Interface:")
    interface_label.pack()

    # Interface listbox
    interface_listbox = tk.Listbox(window, width=40)
    for interface_name in interfaces.keys():
        interface_listbox.insert(tk.END, interface_name)
    interface_listbox.pack()

    # Start button
    start_button = tk.Button(window, text="Start Sniffing", command=start_button_click)
    start_button.pack()

    # Stop button
    stop_button = tk.Button(window, text="Stop Sniffing", command=stop_sniffing)
    stop_button.pack()

    # Packet count label
    packet_count_label = tk.Label(window, text="Total packets captured: 0")
    packet_count_label.pack()

    output_textarea = scrolledtext.ScrolledText(window, width=100, height=80)
    output_textarea.pack()

    # Start GUI main loop
    window.mainloop()

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
