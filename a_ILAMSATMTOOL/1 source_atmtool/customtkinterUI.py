from customtkinter import *

# https://customtkinter.tomschimansky.com/
# https://www.pythonguis.com/tutorials/use-tkinter-to-design-gui-layout/

app = CTk()
app.geometry("960x1080")


tabview = CTkTabview(master=app)
tabview.pack(pady=20, padx=20)

tabview.add("Tab 1")
tabview.add("Tab 2")
tabview.add("Tab 3")

set_appearance_mode("dark")

label_1 = CTkLabel(master=tabview.tab("Tab 1"), text="This is Tab 1")
label_1.pack(pady=12, padx=10)
btn_1 = CTkButton(master=tabview.tab("Tab 1"), text="Click Me ", corner_radius=32, fg_color="#C850C0",hover_color="#FF5733", width=200, height=50)
btn_1.pack(pady=12, padx=10)

app.mainloop()