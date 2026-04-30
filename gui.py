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
