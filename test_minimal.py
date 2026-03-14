"""Minimal test to verify syntax is correct"""
from unihiker import GUI

print("Testing syntax...")

# Simple GUI test
gui = GUI()
gui.add_label(text="Syntax OK", x=160, y=120, anchor="mt", color="#2E8B57")
gui.add_button(text="Start", x=160, y=200, w=80, h=40, onclick=lambda: print("Button clicked"))

print("✅ No syntax errors!")
