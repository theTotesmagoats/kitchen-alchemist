"""
Kitchen Alchemist v1.0 — A retro cooking companion for UniHiker M10
- 6 timers (4 stove + 2 oven)
- Measurement converter (cups ↔ grams ↔ ml)
- Recipe explorer with spice pairings
- Meat temps guide (°F/°C)
- Voice memos (text-based, timestamped)
- Retro UI: mustard yellow, leather brown, olive green

Usage: Save as `kitchen_alchemist.py` and run on UniHiker
"""

from unihiker import GUI
import time
import os
import threading
from datetime import datetime

# ==============================
# 🎨 Retro Color Palette & Constants
# ==============================
COLOR_BG = "#F5E6C8"      # Cream paper
COLOR_PRIMARY = "#D4A017" # Mustard yellow (buttons, accents)
COLOR_ACCENT = "#8B4513"  # Leather brown (text headers)
COLOR_SUCCESS = "#2E8B57" # Olive green (timers done)
COLOR_WARN = "#CD5C5C"    # Indian red (errors/alerts)

FONT_MAIN = ("DejaVuSansMono", 16, "bold")  # Retro digital feel
FONT_SMALL = ("DejaVuSansMono", 12)
FONT_LARGE = ("DejaVuSansMono", 20, "bold")

# Paths
MEMO_DIR = "/home/root/kitchen_memos"
CSV_GROCERY = f"{MEMO_DIR}/grocery.csv"

# Ensure directories exist
os.makedirs(MEMO_DIR, exist_ok=True)

# ==============================
# 🧰 Global State & Helpers
# ==============================
gui = GUI()
timers_active = [False] * 6  # Stove 1–4, Oven 1–2
timer_times = [0] * 6        # Seconds remaining
timer_totals = [0] * 6       # Original duration (for repeat)
last_timer_total = [300, 300, 300, 300, 600, 600]  # Default: 5min stove, 10min oven
timer_labels = ["Stove 1", "Stove 2", "Stove 3", "Stove 4", "Oven 1", "Oven 2"]
alarm_beep_count = [0] * 6

# Spice pairings database (simplified)
SPICE_PAIRINGS = {
    "basil": ["tomato", "garlic", "olive oil", "mozzarella"],
    "cumin": ["chicken", "beans", "rice", "tomatoes"],
    "thyme": ["mushrooms", "potatoes", "lemon", "chicken"],
    "oregano": ["tomato sauce", "lamb", "feta", "olives"],
    "rosemary": ["potatoes", "chicken", "garlic", "lemon"],
    "paprika": ["pork", "eggs", "potatoes", "rice"],
    "cinnamon": ["apples", "bananas", "oats", "yogurt"],
    "ginger": ["garlic", "soy sauce", "sesame oil", "tofu"]
}

# Meat temps (°F)
MEAT_TEMPS = [
    ("Chicken breast/thigh", 165),
    ("Ground turkey/chicken", 165),
    ("Beef steak (medium)", 145),
    ("Beef roast (medium)", 145),
    ("Pork chop/loin", 145),
    ("Pork ground", 160),
    ("Fish", 145),
    ("Eggs (dishes)", 160)
]

# Mini recipe database
RECIPES = {
    "Pasta": [
        {"name": "Garlic Shrimp Pasta",
         "ingredients": ["shrimp", "garlic", "olive oil", "parsley", "pasta"],
         "steps": "1. Boil pasta 8-10 min\n2. Sauté garlic in oil\n3. Add shrimp, cook 2-3 min\n4. Toss with pasta & parsley"},
        {"name": "Simple Tomato Pasta",
         "ingredients": ["tomatoes", "garlic", "olive oil", "basil", "pasta"],
         "steps": "1. Boil pasta\n2. Sauté garlic in oil\n3. Add chopped tomatoes, cook 5 min\n4. Toss with pasta & basil"}
    ],
    "Eggs": [
        {"name": "Perfect Scrambled Eggs",
         "ingredients": ["eggs", "butter", "salt", "chives"],
         "steps": "1. Whisk eggs with salt\n2. Melt butter in pan\n3. Cook low & slow, stir gently\n4. Garnish with chives"},
        {"name": "Over-Easy Eggs",
         "ingredients": ["eggs", "butter", "salt", "pepper"],
         "steps": "1. Melt butter in pan\n2. Crack eggs, cook 3 min\n3. Flip, cook 1 min more"}
    ],
    "Rice Bowl": [
        {"name": "Sesame Rice Bowl",
         "ingredients": ["rice", "soy sauce", "sesame oil", "green onion"],
         "steps": "1. Cook rice\n2. Mix soy + sesame oil\n3. Top rice, drizzle & garnish"},
        {"name": "Rice & Beans",
         "ingredients": ["rice", "black beans", "cilantro", "lime"],
         "steps": "1. Cook rice\n2. Heat beans with rice\n3. Top with cilantro + lime"}
    ],
    "Salad": [
        {"name": "Classic Garden Salad",
         "ingredients": ["lettuce", "tomato", "cucumber", "olive oil", "lemon"],
         "steps": "1. Chop veggies\n2. Toss with olive oil & lemon\n3. Season to taste"},
        {"name": "Caprese Salad",
         "ingredients": ["tomato", "mozzarella", "basil", "olive oil"],
         "steps": "1. Slice tomato & mozzarella\n2. Layer with basil\n3. Drizzle oil"}
    ],
    "Oatmeal": [
        {"name": "Classic Oatmeal",
         "ingredients": ["oats", "milk", "cinnamon", "banana"],
         "steps": "1. Boil oats in milk\n2. Cook 5 min, stir\n3. Top with banana & cinnamon"},
        {"name": "Apple Cinnamon Oats",
         "ingredients": ["oats", "apple", "cinnamon", "honey"],
         "steps": "1. Cook oats\n2. Add diced apple & cinnamon\n3. Sweeten with honey"}
    ]
}

# ==============================
# 🎚️ UI Layout Setup
# ==============================
tab_buttons = []
current_tab = 0

def create_tabs():
    """Create top navigation tabs"""
    tab_names = ["⏱️ Timer", "⚖️ Converter", "🍳 Recipes", "🥩 Meats", "🎤 Memos"]
    x_start = 20
    btn_width = (320 - 40) // len(tab_names)
    
    for i, name in enumerate(tab_names):
        btn = gui.add_button(
            text=name,
            x=x_start + i * btn_width,
            y=10,
            w=btn_width,
            h=40,
            color=COLOR_PRIMARY if i == 0 else "#E8D5B2",
            text_color="#FFF",
            font=("DejaVuSansMono", 14),
            onclick=lambda idx=i: switch_tab(idx)
        )
        tab_buttons.append(btn)

def switch_tab(tab_idx):
    """Switch between main tabs"""
    global current_tab
    current_tab = tab_idx
    
    # Update button colors
    for i, btn in enumerate(tab_buttons):
        color = COLOR_PRIMARY if i == tab_idx else "#E8D5B2"
        btn.config(bg=color)
    
    # Clear screen (except tabs)
    gui.clear()
    create_tabs()  # Redraw tabs
    
    # Show tab content
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
timer_buttons = []
timer_texts = []

def format_time(seconds):
    """Format seconds as MM:SS"""
    m, s = divmod(int(seconds), 60)
    return f"{m:02d}:{s:02d}"

def update_timers():
    """Background thread to update timers every second"""
    while True:
        for i in range(6):
            if timers_active[i] and timer_times[i] > 0:
                timer_times[i] -= 1
                if timer_texts[i]:
                    timer_texts[i].config(text=format_time(timer_times[i]))
                
                # Play chime when done
                if timer_times[i] == 0 and not alarm_beep_count[i]:
                    play_chime(i)
        
        time.sleep(1)

def play_chime(timer_idx):
    """Play gentle chime on buzzer"""
    global alarm_beep_count
    
    try:
        from unihiker import Audio
        audio = Audio()
        
        # Play 3-note ascending chime
        for freq in [523.25, 659.25, 783.99]:  # C5, E5, G5
            if alarm_beep_count[timer_idx] < 1:  # Only play once per completion
                audio.play_tone(freq, 0.2)
        
        alarm_beep_count[timer_idx] = 1
        
    except Exception as e:
        print(f"Buzzer error: {e}")

def start_timer(i):
    """Start/Resume timer i"""
    if timer_times[i] == 0:
        timer_times[i] = last_timer_total[i]
    
    timers_active[i] = True
    timer_buttons[i * 3].config(text="⏸️ Pause")

def pause_timer(i):
    """Pause timer i"""
    timers_active[i] = False
    timer_buttons[i * 3].config(text="▶️ Start")

def reset_timer(i):
    """Reset timer i to original duration"""
    timers_active[i] = False
    timer_times[i] = last_timer_total[i]
    if timer_texts[i]:
        timer_texts[i].config(text=format_time(timer_times[i]))
    alarm_beep_count[i] = 0
    timer_buttons[i * 3].config(text="▶️ Start")

def show_timer_tab():
    """Display the Timer tab UI"""
    gui.add_label(text="Kitchen Alchemist", x=160, y=60, anchor="mt", color=COLOR_ACCENT)
    
    # Grid layout for 6 timers (2 columns × 3 rows)
    grid_x = [40, 180]
    grid_y = [90, 150, 210]
    
    global timer_buttons, timer_texts
    timer_buttons = []
    timer_texts = []
    
    for i in range(6):
        row = i // 2
        col = i % 2
        
        x_base = grid_x[col]
        y_base = grid_y[row]
        
        # Timer label
        gui.add_label(text=timer_labels[i], x=x_base + 40, y=y_base - 15, anchor="mt", color=COLOR_ACCENT)
        
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
        start_btn = gui.add_button(
            text="▶️ Start",
            x=x_base,
            y=y_base + 40,
            w=60,
            h=30,
            font=("DejaVuSansMono", 12),
            onclick=lambda idx=i: (
                pause_timer(idx) if timers_active[idx] else start_timer(idx)
            )
        )
        
        # Reset button
        reset_btn = gui.add_button(
            text="🔄",
            x=x_base + 80,
            y=y_base + 40,
            w=30,
            h=30,
            font=("DejaVuSansMono", 12),
            onclick=lambda idx=i: reset_timer(idx)
        )
        
        timer_buttons.extend([start_btn, reset_btn])
    
    # Bottom controls
    gui.add_button(
        text="⏸️ Pause All",
        x=40,
        y=280,
        w=130,
        h=35,
        color="#CD5C5C",
        text_color="#FFF",
        onclick=lambda: [pause_timer(i) for i in range(6)]
    )
    
    gui.add_button(
        text="🔁 Repeat Last",
        x=170,
        y=280,
        w=130,
        h=35,
        color="#D4A017",
        text_color="#FFF",
        onclick=lambda: [
            reset_timer(i) or timer_times.__setitem__(i, last_timer_total[i]) 
            for i in range(6)
        ]
    )

# ==============================
# ⚖️ Converter Tab
# ==============================
def show_converter_tab():
    """Display the Measurement Converter tab UI"""
    gui.add_label(text="Measurement Converter", x=160, y=60, anchor="mt", color=COLOR_ACCENT)
    
    # Unit selector (simple buttons)
    unit_vars = ["cups", "grams", "ml"]
    selected_unit = [0]  # Use list for mutable reference
    
    def set_unit(unit_idx):
        selected_unit[0] = unit_idx
        update_converter_display()
    
    # Create unit toggle buttons
    x_positions = [60, 140, 220]
    for i, unit in enumerate(["cups", "grams", "ml"]):
        gui.add_button(
            text=unit,
            x=x_positions[i],
            y=90,
            w=70,
            h=30,
            color=COLOR_PRIMARY if selected_unit[0] == i else "#E8D5B2",
            onclick=lambda idx=i: set_unit(idx)
        )
    
    # Value slider (visual only, no real slider support in unihiker GUI)
    value_label = gui.add_label(
        text="1 cup",
        x=160,
        y=130,
        anchor="mt",
        color="#333"
    )
    
    def adjust_value(delta):
        current = float(value_label.config("text").split()[0])
        new_val = max(0.25, min(current + delta, 8))
        value_label.config(text=f"{new_val} {['cups', 'grams', 'ml'][selected_unit[0]]}")
    
    # Up/Down buttons
    gui.add_button(
        text="+",
        x=130,
        y=150,
        w=25,
        h=30,
        onclick=lambda: adjust_value(0.25)
    )
    gui.add_button(
        text="−",
        x=165,
        y=150,
        w=25,
        h=30,
        onclick=lambda: adjust_value(-0.25)
    )
    
    # Conversion display
    conv_label = gui.add_label(
        text="≈ 120g",
        x=160,
        y=190,
        anchor="mt",
        color="#D4A017",
        font=("DejaVuSansMono", 18, "bold")
    )
    
    def update_converter_display():
        unit = ["cups", "grams", "ml"][selected_unit[0]]
        try:
            val = float(value_label.config("text").split()[0])
            
            if unit == "cups":
                conv_val = int(val * 120)  # Flour approximation
                conv_text = f"≈ {conv_val}g (flour)"
            elif unit == "grams":
                conv_val = round(val / 120, 2)
                conv_text = f"≈ {conv_val} cups"
            else:  # ml
                conv_val = int(val * 0.42)  # Approx to cups
                conv_text = f"≈ {conv_val} cups"
            
            conv_label.config(text=conv_text)
        except:
            pass
    
    # Food icons with conversions
    foods = [
        ("🌾 Flour", "1 cup = ~120g"),
        ("🍬 Sugar", "1 cup = ~200g"),
        ("🧈 Butter", "1 cup = ~227g"),
        ("🥛 Milk", "1 cup = ~240ml")
    ]
    
    y_base = 230
    for i, (icon, info) in enumerate(foods):
        x_pos = 40 + (i % 2) * 160
        y_pos = y_base + (i // 2) * 50
        
        gui.add_label(text=icon, x=x_pos, y=y_pos - 10, anchor="w", color="#333")
        gui.add_label(text=info, x=x_pos, y=y_pos, anchor="w", font=("DejaVuSansMono", 12))

# ==============================
# 🍳 Recipes Tab
==============================
current_category = "Pasta"

def show_recipes_tab():
    """Display the Recipe Explorer tab UI"""
    global current_category
    
    gui.add_label(text="Recipe Explorer", x=160, y=60, anchor="mt", color=COLOR_ACCENT)
    
    # Category buttons
    categories = ["Pasta", "Eggs", "Rice Bowl", "Salad", "Oatmeal"]
    cat_btns = []
    
    for i, cat in enumerate(categories):
        btn = gui.add_button(
            text=cat,
            x=20 + i * 58,
            y=90,
            w=55,
            h=30,
            color=COLOR_PRIMARY if cat == current_category else "#E8D5B2",
            onclick=lambda c=cat: set_category(c)
        )
        cat_btns.append(btn)
    
    # Recipe display
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
            recipe = recipes[0]  # Show first recipe (cycle later)
            text = f"{recipe['name']}\n\nIngredients:\n" + ", ".join(recipe["ingredients"])[:80]
            recipe_label.config(text=text)
    
    def cycle_recipe():
        nonlocal current_category
        recipes = RECIPES.get(current_category, [])
        if len(recipes) > 1:
            # Simple rotation - in real app would track index
            pass
    
    show_recipe()
    
    # Next/Prev buttons
    gui.add_button(
        text="→",
        x=250,
        y=130,
        w=40,
        h=30,
        onclick=lambda: [show_recipe(), cycle_recipe()]
    )
    
    # Spice section
    gui.add_label(text="Spice Pairings:", x=40, y=210, anchor="w", color="#8B4513")
    
    spices = ["basil", "cumin", "thyme", "oregano", "rosemary"]
    for i, spice in enumerate(spices):
        btn = gui.add_button(
            text=spice.capitalize(),
            x=40 + (i % 3) * 95,
            y=235 + (i // 3) * 35,
            w=85,
            h=30,
            onclick=lambda s=spice: show_spice_pairings(s)
        )
    
    # Add to grocery list button
    gui.add_button(
        text="🛒 Add to Grocery List",
        x=40,
        y=290,
        w=250,
        h=35,
        color="#D4A017",
        text_color="#FFF",
        onclick=lambda: save_to_grocery()
    )

def set_category(cat):
    global current_category
    current_category = cat
    show_recipes_tab()

def show_spice_pairings(spice):
    pairings = SPICE_PAIRINGS.get(spice, ["Check your pantry!"])
    pairing_text = f"{spice.capitalize()} pairs with:\n" + ", ".join(pairings)
    
    # Clear previous text area (simplified for demo)
    gui.add_label(
        text=pairing_text,
        x=160,
        y=270,
        anchor="mt",
        color="#D4A017"
    )

def save_to_grocery():
    """Save current recipe ingredients to grocery list"""
    recipes = RECIPES.get(current_category, [])
    if not recipes:
        return
    
    ingredients = recipes[0]["ingredients"]
    
    # Read existing groceries
    try:
        with open(CSV_GROCERY, "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        lines = []
    
    # Add new items (avoid duplicates)
    current_items = [line.strip().split(",")[0] for line in lines[1:]] if len(lines) > 1 else []
    new_lines = lines[:1] if lines else ["item,quantity,date\n"]
    
    for ing in ingredients:
        if ing not in current_items:
            new_lines.append(f"{ing},1,{datetime.now().strftime('%Y-%m-%d')}\n")
    
    with open(CSV_GROCERY, "w") as f:
        f.writelines(new_lines)
    
    gui.add_label(
        text="✅ Added to Grocery List!",
        x=160,
        y=290,
        anchor="mt",
        color="#D4A017"
    )

# ==============================
# 🥩 Meats Tab
==============================
def show_meats_tab():
    """Display the Meat Temps Guide tab UI"""
    gui.add_label(text="Meat Temps Guide", x=160, y=60, anchor="mt", color=COLOR_ACCENT)
    
    # Scrollable list (simplified for UniHiker screen)
    y_base = 90
    for i, (meat, temp_f) in enumerate(MEAT_TEMPS):
        y_pos = y_base + i * 35
        
        # Meat name and temp in °F
        gui.add_label(
            text=f"{meat}: {temp_f}°F",
            x=20,
            y=y_pos,
            anchor="w",
            font=("DejaVuSansMono", 14)
        )
        
        # Convert button
        def make_convert(temp_c):
            return lambda: gui.add_label(
                text=f"≈ {temp_c}°C",
                x=280,
                y=y_pos + 5,
                anchor="w",
                color="#D4A017"
            )
        
        temp_c = int((temp_f - 32) * 5 / 9)
        gui.add_button(
            text=f"{temp_c}°C",
            x=250,
            y=y_pos,
            w=60,
            h=25,
            onclick=make_convert(temp_c)
        )

# ==============================
# 🎤 Voice Memos Tab
==============================
def show_memo_tab():
    """Display the Voice Memos tab UI"""
    gui.add_label(text="Voice Memos", x=160, y=60, anchor="mt", color=COLOR_ACCENT)
    
    # Date selector (simplified to today for now)
    today = datetime.now().strftime("%Y-%m-%d")
    date_label = gui.add_label(
        text=f"Date: {today}",
        x=40,
        y=90,
        anchor="w",
        color="#8B4513"
    )
    
    # Meal name input (simplified)
    meal_name = ["Dinner"]
    def set_meal(m):
        meal_name[0] = m
    
    gui.add_button(
        text="Breakfast",
        x=40,
        y=120,
        w=80,
        h=30,
        onclick=lambda: set_meal("Breakfast")
    )
    gui.add_button(
        text="Lunch",
        x=130,
        y=120,
        w=60,
        h=30,
        onclick=lambda: set_meal("Lunch")
    )
    gui.add_button(
        text="Dinner",
        x=200,
        y=120,
        w=80,
        h=30,
        onclick=lambda: set_meal("Dinner")
    )
    
    # Recording control
    recording = [False]
    record_btn = gui.add_button(
        text="🎤 Record",
        x=40,
        y=160,
        w=250,
        h=50,
        color="#CD5C5C" if not recording[0] else "#2E8B57",
        onclick=lambda: toggle_recording()
    )
    
    # Text entry area (simplified)
    text_entry = gui.add_textbox(
        x=40,
        y=220,
        w=250,
        h=60,
        placeholder="Type what you said..."
    )
    
    def toggle_recording():
        recording[0] = not recording[0]
        
        if recording[0]:
            record_btn.config(text="⏹️ Stop")
            
            # Simulate 10-sec recording
            threading.Thread(target=record_timer, args=(record_btn,)).start()
        else:
            record_btn.config(text="🎤 Record")
    
    def record_timer(btn):
        import time
        for i in range(10, 0, -1):
            btn.config(text=f"Recording... {i}s")
            time.sleep(1)
        
        btn.config(text="🎤 Record")
        recording[0] = False
    
    # Save memo button
    def save_memo():
        text = text_entry.config("text").strip()
        if not text:
            return
        
        filename = f"{MEMO_DIR}/{today}_{meal_name[0].lower()}.txt"
        
        with open(filename, "a") as f:
            timestamp = datetime.now().strftime("%H:%M")
            f.write(f"[{timestamp}] {text}\n\n")
        
        gui.add_label(
            text="✅ Memo saved!",
            x=160,
            y=300,
            anchor="mt",
            color="#2E8B57"
        )
    
    gui.add_button(
        text="💾 Save Memo",
        x=40,
        y=290,
        w=250,
        h=40,
        color="#D4A017",
        text_color="#FFF",
        onclick=save_memo
    )

# ==============================
# 🏁 Main Entry Point
# ==============================
if __name__ == "__main__":
    # Start timer update thread
    threading.Thread(target=update_timers, daemon=True).start()
    
    # Create UI
    create_tabs()
    
    # Show initial tab (Timer)
    show_timer_tab()
