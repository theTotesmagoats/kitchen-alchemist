# 🍳 Kitchen Alchemist

A **retro cooking companion** for UniHiker M10 — built with love, mustard yellow, and real-time timers.

## ✨ Features That Actually Help in the Kitchen

### ⏱️ 6 Timers (Stove + Oven)
- Stove 1–4 + Oven 1–2 — each with start/pause/reset
- Gentle buzzer chime when done (not an alarm!)
- **Pause All** and **Repeat Last** buttons for busy cooks
- Visual progress bars in retro digital style

### ⚖️ Measurement Converter
- Drag-style conversion: cups ↔ grams ↔ ml
- Tap icons for common foods: flour, sugar, butter, milk
- Instant visual feedback — no math required

### 🍝 Recipe Explorer
- 5 categories: Pasta, Eggs, Rice Bowl, Salad, Oatmeal
- Tap recipe → see ingredients + steps
- **Spice Pairings**: tap basil, cumin, thyme, etc. → see what mixes well
- One-tap “Add to Grocery List” (saves to `grocery.csv`)

### 🥩 Meat Temps Guide
- Scrollable list of common meats + safe internal temps (°F)
- Tap any temp → convert °F ↔ °C instantly
- Includes: chicken, beef, pork, fish, eggs

### 🎤 Voice Memos (Text-Based)
- Tap mic icon → speak for up to 10 seconds
- Opens text box where you type what you said
- Saves to `YYYY-MM-DD_mealname.txt` under `/kitchen_memos/`
- Review notes later — your cooking journal, auto-saved

### 🎨 Retro UI Design
- Mustard yellow (#D4A017), leather brown (#8B4513), olive green (#2E8B57)
- Monospace fonts for that 70s digital timer feel
- Big touch zones — works with sticky fingers!

## 📦 What’s Included
- Single file: `kitchen_alchemist.py`
- Pre-loaded recipes, spice pairings, meat temps (all offline)
- Grocery list auto-saves to CSV
- Voice memos saved as plain text files

## 🔧 Setup on UniHiker M10

### Step 1: Save the Code
Copy `kitchen_alchemist.py` to your UniHiker’s home directory:
```bash
cp kitchen_alchemist.py /home/root/
```

### Step 2: Create Memo Directory (optional but recommended)
```bash
mkdir -p /home/root/kitchen_memos
```

### Step 3: Run It!
In Jupyter Notebook or terminal:
```python
%run kitchen_alchemist.py
```
Or just:
```bash
python3 kitchen_alchemist.py
```

## 📝 Notes & Limitations
- **Voice memos**: The UniHiker mic is analog-only, so we use *text-based transcription* (type what you said). This keeps it lightweight and truly offline.
- **No internet required** — everything works during power outages or in the dark.
- Buzzer alerts are gentle chimes, not loud alarms — perfect for kitchens!

## 🎁 Bonus: Nourishment Note
After cooking, tap ❤️ to pick your mood + get a tiny self-help quote (e.g., *“You showed up for yourself today.”*)

---

### Made with love for real humans who cook. 🌿

**Version**: 1.0 | **Date**: March 2026 | **For your 43-year-old self and your favorite kitchen**
