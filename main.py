import tkinter as tk
import subprocess

def mainclassic():
    subprocess.Popen(["python", "mainclassic.py"])

def mainclassicPremium():
    subprocess.Popen(["python", "mainclassic-premium.py"])

def mainorigin():
    subprocess.Popen(["python", "mainorigin.py"])

def mainoriginPremium():
    subprocess.Popen(["python", "mainorigin-premium.py"])

root = tk.Tk()
root.title("AUTOPLAY")
root.geometry("300x240")

btn_mainclassic = tk.Button(root, text="Axie Classic", font=("Helvetica", 14), command=mainclassic)
btn_mainclassic.pack(pady=10)

btn_mainclassic = tk.Button(root, text="Axie Classic - Premium", font=("Helvetica", 14), command=mainclassicPremium)
btn_mainclassic.pack(pady=10)

btn_mainorigin = tk.Button(root, text="Axie Origin", font=("Helvetica", 14), command=mainorigin)
btn_mainorigin.pack(pady=10)

btn_mainorigin = tk.Button(root, text="Axie Origin - Premium", font=("Helvetica", 14), command=mainoriginPremium)
btn_mainorigin.pack(pady=10)

root.mainloop()
