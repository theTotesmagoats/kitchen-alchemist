"""
Kitchen Alchemist v1.0 — A retro cooking companion for UniHiker M10

Usage: Save as `kitchen_alchemist.py` and run on UniHiker
"""

from unihiker import GUI
import time
import os
import threading
from datetime import datetime

# ==============================
# 🎨 Colors & Constants
# ==============================
COLOR_ACCENT = "#8B4513"
MEMO_DIR = "/home/root/kitchen_memos"
CSV_GROCERY = f"{MEMO_DIR}/grocery.csv"
os.makedirs(MEMO_DIR, exist_ok=True)

# ==============================
# 🧰 Global State & Helpers
# ==============================
gui = GUI()
timers_active = [False] * 6
timer_times = [0] * 6
last_timer_total = [300, 300, 300, 300, 600, 600]
timer_labels = ["Stove1", "Stove2", "Stove3", "Stove4", "Oven1", "Oven2"]
alarm_beep_count = [0] * 6
current_category = "Pasta"

SPICE_PAIRINGS = {
    "basil": ["tomato", "garlic", "olive oil"],
    "cumin": ["chicken", "beans", "rice"],
}

MEAT_TEMPS = [
    ("Chicken breast/thigh", 165),
    ("Beef steak (medium)", 145),
]

RECIPES = {
    "Pasta": [
        {"name": "Garlic Shrimp Pasta",
         "ingredients": ["shrimp", "garlic", "olive oil", "parsley", "pasta"],
         "steps": "1. Boil pasta\n2. Sauté garlic in oil"}
    ],
}

# ==============================
# 🎚️ UI Layout Setup
# ==============================
tab_buttons = []
current_tab = 0

def create_tabs():
    tab_names = ["Timer", "Converter", "Recipes", "Meats", "Memos"]
    x_start = 20
    btn_width = (320 - 40) // len(tab_names)
    
    for i, name in enumerate(tab_names):
        btn = gui.add_button(
            text=name,
            x=x_start + i * btn_width,
            y=10,
            w=btn_width,
            h=40,
            onclick=lambda idx=i: switch_tab(idx)
        )
        tab_buttons.append(btn)

def switch_tab(tab_idx):
    global current_tab
    current_tab = tab_idx
    
    gui.clear()
    create_tabs()
    
    if tab_idx == 0:
        show_timer_tab()
    elif tab_idx == 1:
        show_converter_tab()
    elif tab_idx == 2:
        show_recipes_tab()
    elif tab_idx == 3:
        show_meats_tab()
    elif tab_idx == 4:
        show_memo_tab()

# ==============================
# ⏱️ Timer Tab
# ==============================
timer_texts = []

def format_time(seconds):
    m, s = divmod(int(seconds), 60)
    return f"{m:02d}:{s:02d}"

def update_timers():
    while True:
        for i in range(6):
            if timers_active[i] and timer_times[i] > 0:
                timer_times[i] -= 1
                try:
                    if i < len(timer_texts):
                        timer_texts[i].config(text=format_time(timer_times[i]))
                except:
                    pass
                
                if timer_times[i] == 0 and alarm_beep_count[i] < 1:
                    play_chime(i)
        time.sleep(1)

def play_chime(timer_idx):
    try:
        from unihiker import Audio
        audio = Audio()
        for freq in [523.25, 659.25, 783.99]:
            if alarm_beep_count[timer_idx] < 1:
                audio.play_tone(freq, 0.2)
        alarm_beep_count[timer_idx] = 1
    except Exception as e:
        print(f"Buzzer error: {e}")

def start_timer(i):
    if timer_times[i] == 0:
        timer_times[i] = last_timer_total[i]
    timers_active[i] = True

def pause_timer(i):
    timers_active[i] = False

def reset_timer(i):
    timers_active[i] = False
    timer_times[i] = last_timer_total[i]

# ==============================
# ⚖️ Converter Tab
# ==============================
def show_converter_tab():
    gui.add_label(text="Measurement Converter", x=160, y=60, anchor="mt", color=COLOR_ACCENT)
    
    selected_unit = [0]
    
    def set_unit(unit_idx):
        selected_unit[0] = unit_idx
    
    for i, unit in enumerate(["cups", "grams", "ml"]):
        gui.add_button(
            text=unit,
            x=60 + i * 80,
            y=90,
            w=70,
            h=30,
            onclick=lambda idx=i: set_unit(idx)
        )
    
    value_label = gui.add_label(text="1 cup", x=160, y=130, anchor="mt", color="#333")
    
    def adjust_value(delta):
        current = float(value_label.config("text").split()[0])
        new_val = max(0.25, min(current + delta, 8))
        value_label.config(text=f"{new_val} {['cups', 'grams', 'ml'][selected_unit[0]]}")
    
    gui.add_button(text="+", x=130, y=150, w=25, h=30, onclick=lambda: adjust_value(0.25))
    gui.add_button(text="-", x=165, y=150, w=25, h=30, onclick=lambda: adjust_value(-0.25))
    
    conv_label = gui.add_label(
        text="≈ 120g (flour)",
        x=160,
        y=190,
        anchor="mt",
        color="#D4A017"
    )

# ==============================
# 🍳 Recipes Tab
# ==============================
def show_recipes_tab():
    global current_category
    
    gui.add_label(text="Recipe Explorer", x=160, y=60, anchor="mt", color=COLOR_ACCENT)
    
    categories = ["Pasta", "Eggs", "Rice Bowl", "Salad", "Oatmeal"]
    for i, cat in enumerate(categories):
        gui.add_button(
            text=cat,
            x=20 + i * 58,
            y=90,
            w=55,
            h=30,
            onclick=lambda c=cat: set_category(c)
        )
    
    recipe_label = gui.add_label(
        text="Loading...",
        x=160,
        y=130,
        anchor="mt",
        color="#333"
    )
    
    def show_recipe():
        recipes = RECIPES.get(current_category, [])
        if recipes:
            recipe = recipes[0]
            text = f"{recipe['name']}\n\nIngredients:\n" + ", ".join(recipe["ingredients"])[:80]
            recipe_label.config(text=text)
    
    # Spice section
    gui.add_label(text="Spice Pairings:", x=40, y=210, anchor="w", color="#8B4513")
    
    spices = ["basil", "cumin"]
    for i, spice in enumerate(spices):
        def show_spice(s=spice):
            pairings = SPICE_PAIRINGS.get(s, [])
            pairing_text = f"{s.capitalize()} pairs with:\n" + ", ".join(pairings)
            gui.add_label(text=pairing_text, x=160, y=270, anchor="mt", color="#D4A017")
        
        gui.add_button(
            text=spice.capitalize(),
            x=40 + (i % 3) * 95,
            y=235 + (i // 3) * 35,
            w=85,
            h=30,
            onclick=show_spice
        )
    
    def save_to_grocery():
        recipes = RECIPES.get(current_category, [])
        if not recipes:
            return
        
        ingredients = recipes[0]["ingredients"]
        
        try:
            with open(CSV_GROCERY, "r") as f:
                lines = f.readlines()
        except FileNotFoundError:
            lines = []
        
        current_items = [line.strip().split(",")[0] for line in lines[1:]] if len(lines) > 1 else []
        new_lines = lines[:1] if lines else ["item,quantity,date\n"]
        
        for ing in ingredients:
            if ing not in current_items:
                new_lines.append(f"{ing},1,{datetime.now().strftime('%Y-%m-%d')}\n")
        
        with open(CSV_GROCERY, "w") as f:
            f.writelines(new_lines)
        
        gui.add_label(
            text="Added to Grocery List!",
            x=160,
            y=290,
            anchor="mt",
            color="#D4A017"
        )
    
    gui.add_button(
        text="Add to Grocery List",
        x=40,
        y=290,
        w=250,
        h=35,
        onclick=save_to_grocery
    )

def set_category(cat):
    global current_category
    current_category = cat
    show_recipes_tab()

# ==============================
# 🥩 Meats Tab
# ==============================
def show_meats_tab():
    gui.add_label(text="Meat Temps Guide", x=160, y=60, anchor="mt", color=COLOR_ACCENT)
    
    y_base = 90
    for i, (meat, temp_f) in enumerate(MEAT_TEMPS):
        y_pos = y_base + i * 35
        
        gui.add_label(
            text=f"{meat}: {temp_f}F",
            x=20,
            y=y_pos,
            anchor="w",
            font=("DejaVuSansMono", 14)
        )
        
        temp_c = int((temp_f - 32) * 5 / 9)
        def make_convert(temp_c=temp_c):
            return lambda: gui.add_label(
                text=f"≈ {temp_c}C",
                x=280,
                y=y_pos + 5,
                anchor="w",
                color="#D4A017"
            )
        
        gui.add_button(
            text=f"{temp_c}C",
            x=250,
            y=y_pos,
            w=60,
            h=25,
            onclick=make_convert()
        )

# ==============================
# 🎤 Voice Memos Tab
# ==============================
def show_memo_tab():
    gui.add_label(text="Voice Memos", x=160, y=60, anchor="mt", color=COLOR_ACCENT)
    
    today = datetime.now().strftime("%Y-%m-%d")
    date_label = gui.add_label(
        text=f"Date: {today}",
        x=40,
        y=90,
        anchor="w",
        color="#8B4513"
    )
    
    meal_name = ["Dinner"]
    def set_meal(m):
        meal_name[0] = m
    
    gui.add_button(text="Breakfast", x=40, y=120, w=80, h=30, onclick=lambda: set_meal("Breakfast"))
    gui.add_button(text="Lunch", x=130, y=120, w=60, h=30, onclick=lambda: set_meal("Lunch"))
    gui.add_button(text="Dinner", x=200, y=120, w=80, h=30, onclick=lambda: set_meal("Dinner"))
    
    recording = [False]
    record_btn = gui.add_button(
        text="Record",
        x=40,
        y=160,
        w=250,
        h=50,
        onclick=lambda: toggle_recording()
    )
    
    def toggle_recording():
        recording[0] = not recording[0]
        
        if recording[0]:
            record_btn.config(text="Stop")
            threading.Thread(target=record_timer, args=(record_btn,), daemon=True).start()
        else:
            record_btn.config(text="Record")
    
    def record_timer(btn):
        import time
        for i in range(10, 0, -1):
            btn.config(text=f"Recording... {i}s")
            time.sleep(1)
        
        btn.config(text="Record")
        recording[0] = False
    
    text_entry = gui.add_textbox(
        x=40,
        y=220,
        w=250,
        h=60,
        placeholder="Type what you said..."
    )
    
    def save_memo():
        text = text_entry.config("text").strip()
        if not text:
            return
        
        filename = f"{MEMO_DIR}/{today}_{meal_name[0].lower()}.txt"
        
        with open(filename, "a") as f:
            timestamp = datetime.now().strftime("%H:%M")
            f.write(f"[{timestamp}] {text}\n\n")
        
        gui.add_label(
            text="Memo saved!",
            x=160,
            y=300,
            anchor="mt",
            color="#2E8B57"
        )
    
    gui.add_button(
        text="Save Memo",
        x=40,
        y=290,
        w=250,
        h=40,
        onclick=save_memo
    )

# ==============================
# 🏁 Main Entry Point
# ==============================
def show_timer_tab():
    """Display the Timer tab UI"""
    gui.add_label(text="Kitchen Alchemist", x=160, y=60, anchor="mt", color="#8B4513")
    
    # Grid layout for 6 timers (2 columns × 3 rows)
    grid_x = [40, 180]
    grid_y = [90, 150, 210]
    
    global timer_texts
    timer_texts = []
    
    for i in range(6):
        row = i // 2
        col = i % 2
        
        x_base = grid_x[col]
        y_base = grid_y[row]
        
        # Timer label
        gui.add_label(text=timer_labels[i], x=x_base + 40, y=y_base - 15, anchor="mt", color="#8B4513")
        
        # Time display
        time_text = gui.add_label(
            text=format_time(last_timer_total[i]),
            x=x_base + 40, 
            y=y_base,
            anchor="mt",
            color="#333",
            font=("DejaVuSansMono", 22, "bold")
        )
        timer_texts.append(time_text)
        
        # Start/Pause button
        gui.add_button(
            text="Start",
            x=x_base,
            y=y_base + 40,
            w=60,
            h=30,
            onclick=lambda idx=i: (
                pause_timer(idx) if timers_active[idx] else start_timer(idx)
            )
        )
        
        # Reset button
        gui.add_button(
            text="Reset",
            x=x_base + 80,
            y=y_base + 40,
            w=60,
            h=30,
            onclick=lambda idx=i: reset_timer(idx)
        )

if __name__ == "__main__":
    threading.Thread(target=update_timers, daemon=True).start()
    
    create_tabs()
    show_timer_tab()
