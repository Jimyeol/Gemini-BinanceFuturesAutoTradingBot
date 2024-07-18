import tkinter as tk

def on_button_click():
    label.config(text="버튼이 클릭되었습니다!")

window = tk.Tk()
window.title("tkinter 예제")

label = tk.Label(window, text="Hello, tkinter!")
label.pack(pady=20)

button = tk.Button(window, text="클릭", command=on_button_click)
button.pack()

window.mainloop()
