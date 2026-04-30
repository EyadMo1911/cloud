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