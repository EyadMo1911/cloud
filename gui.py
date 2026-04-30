import tkinter as tk
from tkinter import messagebox, filedialog
from tkcalendar import DateEntry
from PIL import Image, ImageTk
import requests
import threading
from db import *

setup_db()

PRIMARY = "#2563eb"
CARD = "#1f2937"
BG = "#0b1220"
TEXT = "white"
ACCENT = "#10b981"

current_user = None
current_page = "login"
page_stack = []
last_section = None

root = tk.Tk()
root.title("AI Medical System PRO")
root.geometry("1200x800")
root.configure(bg=BG)

container = tk.Frame(root, bg=BG)
container.pack(fill="both", expand=True)

pages = {}

for p in ["login","home","chat","xray","skin","doctor","pharmacy"]:
    pages[p] = tk.Frame(container, bg=BG)

def show_page(name):
    global current_page, page_stack

    if not current_user and name != "login":
        messagebox.showwarning("Login", "Please login first")
        return

    if current_page != name:
        page_stack.append(current_page)

    for p in pages.values():
        p.pack_forget()

    pages[name].pack(fill="both", expand=True)
    current_page = name

def go_back():
    global last_section

    if last_section == "doctor":
        show_page("doctor")
        load_doctors_grid()
        last_section = None
        return

    if last_section == "pharmacy":
        show_page("pharmacy")
        load_drugs()
        last_section = None
        return

    if page_stack:
        show_page(page_stack.pop())
    else:
        show_page("home")

def nav(frame):
    bar = tk.Frame(frame, bg="#111827")
    bar.pack(fill="x")

    for t in ["home","chat","xray","skin","doctor","pharmacy"]:
        tk.Button(bar, text=t.capitalize(),
                  command=lambda x=t: show_page(x),
                  bg=CARD, fg="white").pack(side="left", padx=5, pady=5)

def back_button(frame):
    tk.Button(frame, text="⬅ Back", command=go_back,
              bg="#374151", fg="white").pack(anchor="nw", padx=10, pady=10)

login = pages["login"]

card = tk.Frame(login, bg=CARD, padx=40, pady=40)
card.place(relx=0.5, rely=0.5, anchor="center")

tk.Label(card, text="Login", bg=CARD, fg=TEXT, font=("Arial", 16, "bold")).pack(pady=10)

username_entry = tk.Entry(card)
username_entry.pack(pady=5)

password_entry = tk.Entry(card, show="*")
password_entry.pack(pady=5)

def login_ui():
    global current_user
    user = login_user(username_entry.get(), password_entry.get())
    if user:
        current_user = user
        show_page("home")
    else:
        messagebox.showerror("Error", "Wrong credentials")

def signup_ui():
    register_user(username_entry.get(), password_entry.get())
    messagebox.showinfo("OK", "Account created")

tk.Button(card, text="Login", command=login_ui, bg=PRIMARY, fg="white").pack(pady=5)
tk.Button(card, text="Signup", command=signup_ui, bg=ACCENT, fg="white").pack(pady=5)

home = pages["home"]
nav(home)

home_canvas = tk.Canvas(home, bg=BG, highlightthickness=0)
home_scrollbar = tk.Scrollbar(home, orient="vertical", command=home_canvas.yview)
home_scrollable_frame = tk.Frame(home_canvas, bg=BG)

home_scrollable_frame.bind("<Configure>", lambda e: home_canvas.configure(scrollregion=home_canvas.bbox("all")))
home_canvas.create_window((0, 0), window=home_scrollable_frame, anchor="nw")
home_canvas.configure(yscrollcommand=home_scrollbar.set)

home_canvas.pack(side="left", fill="both", expand=True)
home_scrollbar.pack(side="right", fill="y")

center = tk.Frame(home_scrollable_frame, bg=BG)
center.pack(expand=True, pady=50)

buttons = [
    ("Chat","chat"),
    ("X-Ray","xray"),
    ("Skin","skin"),
    ("Doctors","doctor"),
    ("Pharmacy","pharmacy")
]

for i, (t, p) in enumerate(buttons):
    c = tk.Frame(center, bg=CARD, padx=20, pady=20)
    c.grid(row=i//3, column=i%3, padx=20, pady=20)

    tk.Label(c, text=t, fg=TEXT, bg=CARD, font=("Arial", 14, "bold")).pack(pady=10)
    tk.Button(c, text="Open", command=lambda x=p: show_page(x), bg=PRIMARY, fg="white").pack()

chat = pages["chat"]
nav(chat)
back_button(chat)

chat_container = tk.Frame(chat, bg=BG)
chat_container.pack(fill="both", expand=True, padx=10, pady=10)

chat_canvas = tk.Canvas(chat_container, bg=BG, highlightthickness=0)
chat_scrollbar = tk.Scrollbar(chat_container, orient="vertical", command=chat_canvas.yview)
chat_scrollable_frame = tk.Frame(chat_canvas, bg=BG)

chat_scrollable_frame.bind("<Configure>", lambda e: chat_canvas.configure(scrollregion=chat_canvas.bbox("all")))
chat_canvas.create_window((0, 0), window=chat_scrollable_frame, anchor="nw")
chat_canvas.configure(yscrollcommand=chat_scrollbar.set)

chat_canvas.pack(side="left", fill="both", expand=True)
chat_scrollbar.pack(side="right", fill="y")

bottom = tk.Frame(chat, bg=BG)
bottom.pack(fill="x")

entry = tk.Entry(bottom, font=("Arial", 14))
entry.pack(side="left", fill="x", expand=True, padx=10, pady=10)

def add_message(text, is_user):
    frame = tk.Frame(chat_scrollable_frame, bg=BG)
    frame.pack(fill="x", pady=5)
    
    if is_user:
        msg_frame = tk.Frame(frame, bg=PRIMARY, padx=12, pady=8)
        msg_frame.pack(side="right", padx=10)
        tk.Label(msg_frame, text=text, fg="white", bg=PRIMARY, wraplength=400, justify="right").pack()
    else:
        msg_frame = tk.Frame(frame, bg=CARD, padx=12, pady=8)
        msg_frame.pack(side="left", padx=10)
        tk.Label(msg_frame, text=text, fg=TEXT, bg=CARD, wraplength=400, justify="left").pack()
    
    chat_canvas.yview_moveto(1)

def send():
    msg = entry.get()
    if not msg:
        return

    entry.delete(0, tk.END)
    add_message(msg, True)

    def run():
        try:
            r = requests.post("http://127.0.0.1:5000/chat", json={"message": msg})
            res = r.json()["response"]
        except:
            res = "Server Error"

        add_message(res, False)

    threading.Thread(target=run).start()

tk.Button(bottom, text="Send", command=send, bg=PRIMARY, fg="white").pack(side="right")
entry.bind("<Return>", lambda e: send())

xray = pages["xray"]
nav(xray)
back_button(xray)

xray_container = tk.Frame(xray, bg=BG)
xray_container.pack(fill="both", expand=True, padx=10, pady=10)

xray_canvas = tk.Canvas(xray_container, bg=BG, highlightthickness=0)
xray_scrollbar = tk.Scrollbar(xray_container, orient="vertical", command=xray_canvas.yview)
xray_scrollable_frame = tk.Frame(xray_canvas, bg=BG)

xray_scrollable_frame.bind("<Configure>", lambda e: xray_canvas.configure(scrollregion=xray_canvas.bbox("all")))
xray_canvas.create_window((0, 0), window=xray_scrollable_frame, anchor="nw")
xray_canvas.configure(yscrollcommand=xray_scrollbar.set)

xray_canvas.pack(side="left", fill="both", expand=True)
xray_scrollbar.pack(side="right", fill="y")

xray_cards_frame = tk.Frame(xray_scrollable_frame, bg=BG)
xray_cards_frame.pack(fill="both", expand=True, padx=20, pady=20)

def suggest_doc_xray(d):
    d = d.lower()
    if "bone" in d or "fracture" in d:
        return "Orthopedic"
    elif "lung" in d or "chest" in d:
        return "Pulmonologist"
    return "General Doctor"

def add_xray_card(disease, diagnosis, treatment, doc, img_path):
    card = tk.Frame(xray_cards_frame, bg=CARD, padx=15, pady=15, relief="raised", bd=1)
    card.pack(pady=10, fill="x")
    
    try:
        img = Image.open(img_path).resize((100, 100))
        img = ImageTk.PhotoImage(img)
        img_label = tk.Label(card, image=img, bg=CARD)
        img_label.image = img
        img_label.pack(side="left", padx=10)
    except:
        pass
    
    info_frame = tk.Frame(card, bg=CARD)
    info_frame.pack(side="left", fill="x", expand=True)
    
    tk.Label(info_frame, text=f"🩻 Disease: {disease}", fg=ACCENT, bg=CARD, font=("Arial", 12, "bold")).pack(anchor="w")
    tk.Label(info_frame, text=f"📋 Diagnosis: {diagnosis}", fg=TEXT, bg=CARD).pack(anchor="w")
    tk.Label(info_frame, text=f"💊 Treatment: {treatment}", fg=TEXT, bg=CARD).pack(anchor="w")
    tk.Label(info_frame, text=f"👨‍⚕️ Suggested Doctor: {doc}", fg=TEXT, bg=CARD).pack(anchor="w")

def upload_xray():
    file = filedialog.askopenfilename()
    if not file:
        return

    def run():
        try:
            with open(file, "rb") as f:
                r = requests.post("http://127.0.0.1:5000/predict_xray", files={"file": f})
            d = r.json()
        except:
            messagebox.showerror("Error", "Server not working")
            return

        doc = suggest_doc_xray(d["disease"])
        add_xray_card(d["disease"], d["diagnosis"], d["treatment"], doc, file)

    threading.Thread(target=run).start()

tk.Button(xray, text="📤 Upload X-Ray", command=upload_xray, bg=PRIMARY, fg="white").pack(pady=10)

skin = pages["skin"]
nav(skin)
back_button(skin)

skin_container = tk.Frame(skin, bg=BG)
skin_container.pack(fill="both", expand=True, padx=10, pady=10)

skin_canvas = tk.Canvas(skin_container, bg=BG, highlightthickness=0)
skin_scrollbar = tk.Scrollbar(skin_container, orient="vertical", command=skin_canvas.yview)
skin_scrollable_frame = tk.Frame(skin_canvas, bg=BG)

skin_scrollable_frame.bind("<Configure>", lambda e: skin_canvas.configure(scrollregion=skin_canvas.bbox("all")))
skin_canvas.create_window((0, 0), window=skin_scrollable_frame, anchor="nw")
skin_canvas.configure(yscrollcommand=skin_scrollbar.set)

skin_canvas.pack(side="left", fill="both", expand=True)
skin_scrollbar.pack(side="right", fill="y")

skin_cards_frame = tk.Frame(skin_scrollable_frame, bg=BG)
skin_cards_frame.pack(fill="both", expand=True, padx=20, pady=20)

def suggest_doc_skin(disease):
    disease_lower = disease.lower()
    if "acne" in disease_lower:
        return "Dermatologist (Acne Specialist)"
    elif "eczema" in disease_lower:
        return "Dermatologist (Eczema Specialist)"
    elif "psoriasis" in disease_lower:
        return "Dermatologist (Psoriasis Specialist)"
    elif "rash" in disease_lower:
        return "Dermatologist"
    elif "skin" in disease_lower:
        return "Dermatologist"
    return "General Doctor"

def add_skin_card(disease, diagnosis, treatment, doc, img_path):
    card = tk.Frame(skin_cards_frame, bg=CARD, padx=15, pady=15, relief="raised", bd=1)
    card.pack(pady=10, fill="x")
    
    try:
        img = Image.open(img_path).resize((100, 100))
        img = ImageTk.PhotoImage(img)
        img_label = tk.Label(card, image=img, bg=CARD)
        img_label.image = img
        img_label.pack(side="left", padx=10)
    except:
        pass
    
    info_frame = tk.Frame(card, bg=CARD)
    info_frame.pack(side="left", fill="x", expand=True)
    
    tk.Label(info_frame, text=f"🧴 Disease: {disease}", fg=ACCENT, bg=CARD, font=("Arial", 12, "bold")).pack(anchor="w")
    tk.Label(info_frame, text=f"📋 Diagnosis: {diagnosis}", fg=TEXT, bg=CARD).pack(anchor="w")
    tk.Label(info_frame, text=f"💊 Treatment: {treatment}", fg=TEXT, bg=CARD).pack(anchor="w")
    tk.Label(info_frame, text=f"👨‍⚕️ Suggested Doctor: {doc}", fg=TEXT, bg=CARD).pack(anchor="w")

def upload_skin():
    file = filedialog.askopenfilename()
    if not file:
        return

    def run():
        try:
            with open(file, "rb") as f:
                r = requests.post("http://127.0.0.1:5000/predict_face", files={"file": f})
            d = r.json()
        except:
            messagebox.showerror("Error", "Server not working")
            return

        doc = suggest_doc_skin(d["disease"])
        add_skin_card(d["disease"], d["diagnosis"], d["treatment"], doc, file)

    threading.Thread(target=run).start()

tk.Button(skin, text="📤 Upload Skin Image", command=upload_skin, bg=PRIMARY, fg="white").pack(pady=10)

doctor = pages["doctor"]
nav(doctor)
back_button(doctor)

doctor_container = tk.Frame(doctor, bg=BG)
doctor_container.pack(fill="both", expand=True, padx=10, pady=10)

doctor_canvas = tk.Canvas(doctor_container, bg=BG, highlightthickness=0)
doctor_scrollbar = tk.Scrollbar(doctor_container, orient="vertical", command=doctor_canvas.yview)
doctor_scrollable_frame = tk.Frame(doctor_canvas, bg=BG)

doctor_scrollable_frame.bind("<Configure>", lambda e: doctor_canvas.configure(scrollregion=doctor_canvas.bbox("all")))
doctor_canvas.create_window((0, 0), window=doctor_scrollable_frame, anchor="nw")
doctor_canvas.configure(yscrollcommand=doctor_scrollbar.set)

doctor_canvas.pack(side="left", fill="both", expand=True)
doctor_scrollbar.pack(side="right", fill="y")

doctor_buttons_frame = tk.Frame(doctor_scrollable_frame, bg=BG)
doctor_buttons_frame.pack(pady=10)

tk.Button(doctor_buttons_frame, text="📋 My Appointments", command=lambda: show_appointments(), bg=PRIMARY, fg="white").pack(side="left", padx=10)

doctors_grid_frame = tk.Frame(doctor_scrollable_frame, bg=BG)
doctors_grid_frame.pack(fill="both", expand=True, padx=20, pady=20)

def load_doctors_grid():
    for w in doctors_grid_frame.winfo_children():
        w.destroy()
    
    center_container = tk.Frame(doctors_grid_frame, bg=BG)
    center_container.pack(expand=True)
    
    doctors = get_doctors_by_specialty("Bone")
    
    if not doctors:
        tk.Label(center_container, text="No doctors available", fg=TEXT, bg=BG).pack()
        return
    
    for i, (d, _, _) in enumerate(doctors):
        card = tk.Frame(center_container, bg=CARD, padx=20, pady=20, relief="raised", bd=1)
        card.grid(row=i//2, column=i%2, padx=20, pady=20)
        
        tk.Label(card, text="👨‍⚕️", font=("Arial", 30), bg=CARD).pack()
        tk.Label(card, text=d, fg=TEXT, bg=CARD, font=("Arial", 12, "bold")).pack(pady=5)
        tk.Label(card, text="Specialist", fg="lightgray", bg=CARD).pack()
        tk.Button(card, text="📅 Book Appointment", command=lambda x=d: book(x), bg=PRIMARY, fg="white").pack(pady=10)

def book(doc):
    global last_section
    last_section = "doctor"

    for w in doctors_grid_frame.winfo_children():
        w.destroy()

    card = tk.Frame(doctors_grid_frame, bg=CARD, padx=30, pady=30)
    card.pack(expand=True)

    tk.Label(card, text=f"👨‍⚕️ Dr. {doc}", fg=TEXT, bg=CARD, font=("Arial", 16, "bold")).pack(pady=10)
    tk.Label(card, text="Your Name", fg=TEXT, bg=CARD).pack()
    name = tk.Entry(card)
    name.pack(pady=5)
    tk.Label(card, text="Date", fg=TEXT, bg=CARD).pack()
    cal = DateEntry(card)
    cal.pack(pady=5)
    tk.Label(card, text="Time", fg=TEXT, bg=CARD).pack()
    time = tk.StringVar(value="10:00")
    tk.OptionMenu(card, time, "10:00","11:00","12:00","14:00","15:00","16:00").pack(pady=5)

    def confirm():
        if not name.get():
            messagebox.showerror("Error", "Please enter your name")
            return

        success = book_appointment(current_user[0], doc, cal.get(), time.get())

        if not success:
            messagebox.showerror("Booking Failed", "This time slot is already booked!")
            return

        messagebox.showinfo("Success", "Appointment booked successfully")
        load_doctors_grid()

    tk.Button(card, text="✅ Confirm Booking", command=confirm, bg=ACCENT, fg="white").pack(pady=10)
    tk.Button(card, text="⬅ Back", command=load_doctors_grid, bg="#374151", fg="white").pack()

def show_appointments():
    global last_section
    last_section = "doctor"

    for w in doctors_grid_frame.winfo_children():
        w.destroy()
    
    appointments = get_my_appointments(current_user[0])
    
    if not appointments:
        card = tk.Frame(doctors_grid_frame, bg=CARD, padx=40, pady=40)
        card.pack(expand=True)
        tk.Label(card, text="📅 No appointments found", fg=TEXT, bg=CARD, font=("Arial", 14)).pack()
    else:
        title_frame = tk.Frame(doctors_grid_frame, bg=BG)
        title_frame.pack(pady=10)
        tk.Label(title_frame, text="📋 My Appointments", fg=ACCENT, bg=BG, font=("Arial", 16, "bold")).pack()
        
        for d, date, time_slot in appointments:
            card = tk.Frame(doctors_grid_frame, bg=CARD, padx=20, pady=15, relief="raised", bd=1)
            card.pack(pady=10, padx=20, fill="x")
            
            tk.Label(card, text=f"👨‍⚕️ Dr. {d}", fg=ACCENT, bg=CARD, font=("Arial", 12, "bold")).pack(anchor="w")
            tk.Label(card, text=f"📅 Date: {date}  |  🕐 Time: {time_slot}", fg=TEXT, bg=CARD).pack(anchor="w")
    
    tk.Button(doctors_grid_frame, text="⬅ Back to Doctors", command=load_doctors_grid, bg="#374151", fg="white").pack(pady=10)

load_doctors_grid()

pharmacy = pages["pharmacy"]
nav(pharmacy)
back_button(pharmacy)

pharmacy_container = tk.Frame(pharmacy, bg=BG)
pharmacy_container.pack(fill="both", expand=True, padx=10, pady=10)

pharmacy_canvas = tk.Canvas(pharmacy_container, bg=BG, highlightthickness=0)
pharmacy_scrollbar = tk.Scrollbar(pharmacy_container, orient="vertical", command=pharmacy_canvas.yview)
pharmacy_scrollable_frame = tk.Frame(pharmacy_canvas, bg=BG)

pharmacy_scrollable_frame.bind("<Configure>", lambda e: pharmacy_canvas.configure(scrollregion=pharmacy_canvas.bbox("all")))
pharmacy_canvas.create_window((0, 0), window=pharmacy_scrollable_frame, anchor="nw")
pharmacy_canvas.configure(yscrollcommand=pharmacy_scrollbar.set)

pharmacy_canvas.pack(side="left", fill="both", expand=True)
pharmacy_scrollbar.pack(side="right", fill="y")

pharmacy_buttons_frame = tk.Frame(pharmacy_scrollable_frame, bg=BG)
pharmacy_buttons_frame.pack(pady=10)


tk.Button(pharmacy_buttons_frame, text="📦 My Drug Orders",
          command=lambda: show_drug_orders(),
          bg=PRIMARY, fg="white").pack(side="left", padx=10)
drugs_grid_frame = tk.Frame(pharmacy_scrollable_frame, bg=BG)
drugs_grid_frame.pack(fill="both", expand=True, padx=20, pady=20)

def load_drugs():
    for w in drugs_grid_frame.winfo_children():
        w.destroy()
    
    center_container = tk.Frame(drugs_grid_frame, bg=BG)
    center_container.pack(expand=True)
    
    drugs = get_all_drugs()
    
    if not drugs:
        tk.Label(center_container, text="No drugs available", fg=TEXT, bg=BG).pack()
        return
    
    for i, (id_, name, drug, qty) in enumerate(drugs):
        card = tk.Frame(center_container, bg=CARD, padx=20, pady=20, relief="raised", bd=1)
        card.grid(row=i//2, column=i%2, padx=20, pady=20)
        
        tk.Label(card, text="💊", font=("Arial", 30), bg=CARD).pack()
        tk.Label(card, text=drug, fg=TEXT, bg=CARD, font=("Arial", 12, "bold")).pack(pady=5)
        tk.Label(card, text=f"Stock: {qty}", fg="lightgray", bg=CARD).pack()

        def book_drug(drug_name=drug, quantity=qty):
            global last_section
            last_section = "pharmacy"

            win = tk.Toplevel()
            win.title("Order Drug")
            win.configure(bg=BG)
            win.geometry("400x500")

            tk.Label(win, text="💊 Order Drug", fg=ACCENT, bg=BG, font=("Arial", 16, "bold")).pack(pady=10)
            tk.Label(win, text=f"Drug: {drug_name}", fg=TEXT, bg=BG).pack()
            tk.Label(win, text="Full Name", bg=BG, fg=TEXT).pack(pady=5)
            name_entry = tk.Entry(win)
            name_entry.pack()
            tk.Label(win, text="Quantity", bg=BG, fg=TEXT).pack(pady=5)
            q_entry = tk.Entry(win)
            q_entry.pack()
            tk.Label(win, text="Delivery Type", bg=BG, fg=TEXT).pack(pady=5)
            delivery_type = tk.StringVar(value="pharmacy")

            tk.Radiobutton(win, text="🏪 Pickup from Pharmacy", variable=delivery_type, value="pharmacy", bg=BG, fg=TEXT).pack()
            tk.Radiobutton(win, text="🚚 Home Delivery", variable=delivery_type, value="delivery", bg=BG, fg=TEXT).pack()

            addr_label = tk.Label(win, text="Delivery Address", bg=BG, fg=TEXT)
            addr_entry = tk.Entry(win)

            def toggle_delivery(*args):
                if delivery_type.get() == "delivery":
                    addr_label.pack(pady=5)
                    addr_entry.pack(pady=5)
                else:
                    addr_label.pack_forget()
                    addr_entry.pack_forget()

            delivery_type.trace("w", toggle_delivery)

            def confirm_order():
                if not name_entry.get():
                    messagebox.showerror("Error", "Please enter your name")
                    return
                if not q_entry.get().isdigit():
                    messagebox.showerror("Error", "Please enter valid quantity")
                    return

                qv = int(q_entry.get())

                if qv > quantity:
                    messagebox.showerror("Error", f"Not enough stock! Available: {quantity}")
                    return

                address = addr_entry.get() if delivery_type.get() == "delivery" else ""

                order_drug(current_user[0], drug_name, qv, delivery_type.get(), address)
                messagebox.showinfo("Success", "Order placed successfully!")
                load_drugs()
                win.destroy()

            tk.Button(win, text="✅ Confirm Order", command=confirm_order, bg=ACCENT, fg="white").pack(pady=20)

        tk.Button(card, text="🛒 Order Now", command=book_drug, bg=ACCENT, fg="white").pack(pady=10)

def show_drug_orders():
    global last_section
    last_section = "pharmacy"

    for w in drugs_grid_frame.winfo_children():
        w.destroy()
    
    orders = get_my_drug_orders(current_user[0])
    
    if not orders:
        card = tk.Frame(drugs_grid_frame, bg=CARD, padx=40, pady=40)
        card.pack(expand=True)
        tk.Label(card, text="📦 No orders found", fg=TEXT, bg=CARD, font=("Arial", 14)).pack()
    else:
        title_frame = tk.Frame(drugs_grid_frame, bg=BG)
        title_frame.pack(pady=10)
        tk.Label(title_frame, text="📋 My Drug Orders", fg=ACCENT, bg=BG, font=("Arial", 16, "bold")).pack()
        
        for drug, qty, typ, addr, status, created_at in orders:
            card = tk.Frame(drugs_grid_frame, bg=CARD, padx=20, pady=15, relief="raised", bd=1)
            card.pack(pady=10, padx=20, fill="x")
            
            status_color = "#10b981" if status == "completed" else "#f59e0b"
            
            tk.Label(card, text=f"💊 {drug}", fg=ACCENT, bg=CARD, font=("Arial", 12, "bold")).pack(anchor="w")
            tk.Label(card, text=f"Quantity: {qty}  |  Type: {typ}", fg=TEXT, bg=CARD).pack(anchor="w")
            if addr:
                tk.Label(card, text=f"Address: {addr}", fg="lightgray", bg=CARD).pack(anchor="w")
            tk.Label(card, text=f"📅 {created_at}", fg="gray", bg=CARD).pack(anchor="w")
            tk.Label(card, text=f"Status: {status}", fg=status_color, bg=CARD).pack(anchor="w")
    
    tk.Button(drugs_grid_frame, text="⬅ Back to Drugs", command=load_drugs, bg="#374151", fg="white").pack(pady=10)

load_drugs()

show_page("login")
root.mainloop()