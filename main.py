import customtkinter
import sqlite3
import bcrypt
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk

# Initialize main app window
app = customtkinter.CTk()
app.title('Building Permit Management')
app.geometry('600x480')
app.config(bg='#FFFFFF')
app.resizable(FALSE, FALSE)

# Define fonts
font1 = ('Helvetica', 25, 'bold')
font2 = ('Arial', 17, 'bold')
font3 = ('Arial', 13, 'bold')
font4 = ('Arial', 13, 'bold', 'underline')
font5 = ('Arial', 10, 'bold')

# Connect to SQLite database
conn = sqlite3.connect('data.db')
cursor = conn.cursor()

# Create necessary tables if they don't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS users(username TEXT, password TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS permits(title TEXT, first TEXT, last TEXT, perm_num INT, date TEXT)''')

# itong fuction na ito ang mag papasok ng mga info na hiningi sa user sa aming database
def add_permit():
    first = First_entry.get()
    last = Last_entry.get()
    title = title_option.get()
    date = date_entry.get()
    perm_num = perm_entry.get()
    if first and last and title and date and perm_num:
        cursor.execute('SELECT perm_num FROM permits WHERE perm_num=?', (perm_num,))
        if cursor.fetchone() is not None:
            messagebox.showerror('Error', 'Permit No. already exists')
        else:
            cursor.execute('INSERT INTO permits (first, last, title, date, perm_num) VALUES (?, ?, ?, ?, ?)',
                           (first, last, title, date, perm_num))
            conn.commit()
            messagebox.showinfo('Success', 'Info Inputted in the System.')
            First_entry.delete(0, END)
            Last_entry.delete(0, END)
            date_entry.delete(0, END)
            perm_entry.delete(0, END)
            add_to_treeview()
    else:
        messagebox.showerror('Error', 'Enter all data!')
#itong function na ito ay kukunin laman ng entrybox at ilalagay sa database
def signup():
    username = username_entry.get()
    password = password_entry.get()
    if username and password:
        cursor.execute('SELECT username FROM users WHERE username=?', (username,))
        if cursor.fetchone() is not None:
            messagebox.showerror('Error', 'Username already exists')
        else:
            encoded_password = password.encode('utf-8')
            hashed_password = bcrypt.hashpw(encoded_password, bcrypt.gensalt())
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
            conn.commit()
            messagebox.showinfo('Success', 'Account has been created.')
            show_login()
    else:
        messagebox.showerror('Error', 'Enter all data!')
# itong function na to is kukunin ang mga info sa database para makapasok sa main page
def login_account():
    username = username_entry2.get()
    password = password_entry2.get()
    if username and password:
        cursor.execute('SELECT password FROM users WHERE username=?', (username,))
        result = cursor.fetchone()
        if result:
            if bcrypt.checkpw(password.encode('utf-8'), result[0]):
                messagebox.showinfo('Success', 'Logged in successfully')
                permit_page()
            else:
                messagebox.showerror('Error', 'Invalid password')
        else:
            messagebox.showerror('Error', 'Invalid Username')
    else:
        messagebox.showerror('Error', 'Enter all data!')
#itong function na to is i dedelete nya yung frame2 kung yun ang nag rurun and i rurun nya ang show_signup_frame
def show_signup():
    frame2.destroy()
    show_signup_frame()
#itong function na to is i dedelete nya yung frame1 kung yun ang nag rurun and i rurun nya ang show_login_frame
def show_login():
    frame1.destroy()
    show_login_frame()
#itong function na to is i dedelete nya yung frame2 kung yun ang nag rurun and i rurun nya ang permit_frame
def permit_page():
    frame2.destroy()
    permit_frame()
#itong function na to is i dedelete nya yung frame3 kung yun ang nag rurun and i rurun nya ang show_login_frame
def perm_out():
    frame3.destroy()
    show_login_frame()

#itong function na ito is humihingi ng confirmation user kung mga lolog out na talaga sya
def logout():
    response = messagebox.askyesno("Confirm Log out", "Are you sure you want to log out?")
    if response is NO:
        return
    elif response:
        perm_out()

#itong function na ito is kukunin nya ang laman ng table na permits sa database and i lalagay sa treeview
def add_to_treeview():
    cursor.execute('SELECT * FROM permits')
    permits = cursor.fetchall()
    tree.delete(*tree.get_children())
    for permit in permits:
        tree.insert('', END, values=permit)

#itong fuction na to is i dedelete nya yung selected permit and i dedelete nya sa database and sa treeview
def delete():
    selected_item = tree.focus()
    if not selected_item:
        messagebox.showerror('ERROR', 'Choose an employee to delete.')
    else:
        perm_num = tree.item(selected_item)['values'][3]
        try:
            cursor.execute('DELETE FROM permits WHERE perm_num = ?', (perm_num,))
            conn.commit()
            add_to_treeview()
            messagebox.showinfo('Success', 'Data has been deleted')
        except Exception as e:
            messagebox.showerror('ERROR', f'Failed to delete data: {e}')

#itong  function na ito is i uupdate nya yung selected permit sa database and sa treeview
def update():
    selected_item = tree.focus()
    if not selected_item:
        messagebox.showerror('Error', 'Select an employee to update')
    else:
        first = First_entry.get()
        last = Last_entry.get()
        title = title_option.get()
        date = date_entry.get()
        perm_num = perm_entry.get()

        if not (first and last and title and date and perm_num):
            messagebox.showerror('Error', 'Enter all data!')
            return

        original_permit_num = tree.item(selected_item)['values'][3]

        cursor.execute('''
            UPDATE permits
            SET first = ?, last = ?, title = ?, date = ?, perm_num = ?
            WHERE perm_num = ?
        ''', (first, last, title, date, perm_num, original_permit_num))
        
        conn.commit()

        add_to_treeview()
        messagebox.showinfo('Success', 'Data has been updated')

        First_entry.delete(0, END)
        Last_entry.delete(0, END)
        date_entry.delete(0, END)
        perm_entry.delete(0, END)


#ito na ang main frame which hihingin sa user ang mga information nya and mapiprint sila sa treeview
def permit_frame():
    global frame3, First_entry, Last_entry, title_option, date_entry, perm_entry, tree

    frame3 = customtkinter.CTkFrame(app, bg_color='#FFFFFF', fg_color='#FFFFFF', width=600, height=480)
    frame3.pack(fill='both', expand=True)

    frameT = customtkinter.CTkFrame(frame3, bg_color='#FFFFFF', fg_color='#FFFFFF', width=600, height=180)
    frameT.grid(row=0, column=0, sticky='n')

    options = ['Mr.', 'Ms.', 'Mrs.']
    variable1 = StringVar()

    title_label = customtkinter.CTkLabel(frameT, font=font2, text='Title:', text_color='#4B0076', bg_color='#FFFFFF')
    title_label.grid(row=0, column=0, padx=10)

    title_option = customtkinter.CTkComboBox(frameT, font=font2, text_color='#33113D', fg_color='#fff',
                                             dropdown_hover_color='#3C005E', button_color='#4B0076',
                                             button_hover_color='#3C005E', border_color='#4B0076', dropdown_fg_color='#4B0076',
                                             width=165, variable=variable1, values=options, state='readonly')
    title_option.set('Mr.')
    title_option.grid(row=1, column=0, padx=10)

    First_label = customtkinter.CTkLabel(frameT, font=font2, text='First Name:', text_color='#4B0076', bg_color='#FFFFFF')
    First_label.grid(row=0, column=1, padx=10)

    First_entry = customtkinter.CTkEntry(frameT, font=font2, text_color='#33113D', fg_color='#fff', placeholder_text='Name',
                                         border_color='#4B0076', border_width=2, width=165)
    First_entry.grid(row=1, column=1, padx=10)

    Last_label = customtkinter.CTkLabel(frameT, font=font2, text='Last Name:', text_color='#4B0076', bg_color='#FFFFFF')
    Last_label.grid(row=0, column=2, padx=10)

    Last_entry = customtkinter.CTkEntry(frameT, font=font2, text_color='#33113D', fg_color='#fff', placeholder_text='Name',
                                        border_color='#4B0076', border_width=2, width=165)
    Last_entry.grid(row=1, column=2, padx=10)

    date_label = customtkinter.CTkLabel(frameT, font=font2, text='Date:', text_color='#4B0076', bg_color='#FFFFFF')
    date_label.grid(row=2, column=0, padx=10)

    date_entry = customtkinter.CTkEntry(frameT, font=font2, text_color='#33113D', fg_color='#fff', placeholder_text='Date (YYYY-MM-DD)',
                                        border_color='#4B0076', border_width=2, width=165)
    date_entry.grid(row=3, column=0, padx=10)

    perm_label = customtkinter.CTkLabel(frameT, font=font2, text='Perm No.:', text_color='#4B0076', bg_color='#FFFFFF')
    perm_label.grid(row=2, column=1, padx=10)

    perm_entry = customtkinter.CTkEntry(frameT, font=font2, text_color='#33113D', fg_color='#fff', placeholder_text='Perm No.: (XXXX)',
                                        border_color='#4B0076', border_width=2, width=165)
    perm_entry.grid(row=3, column=1, padx=10)

    insert_button = customtkinter.CTkButton(frameT, command=add_permit, font=font2, text_color='#fff', text='Insert Info',
                                            fg_color='#4B0076', hover_color='#3C005E', bg_color='#fff', cursor='hand2',
                                            corner_radius=5, width=165)
    insert_button.grid(row=4, column=1, padx=10, pady=5)

    frameM = customtkinter.CTkFrame(frame3, bg_color='#FFFFFF', fg_color='#FFFFFF', width=600, height=250)
    frameM.grid(row=1, column=0, sticky='nsew', padx=50, pady=10)

    style = ttk.Style(frameM)
    style.theme_use('clam')
    style.configure('Treeview', font=font3, foreground='#FFFFFF', background='#4B0076', fieldbackground='#FFFFFF')
    style.configure('Treeview.Heading', font=font3, foreground='#fff', background='#350053', relief='flat')
    style.map('Treeview', background=[('selected', '#3C005E')])
    style.map('Treeview.Heading', background=[('active', '#3C005E')])

    tree = ttk.Treeview(frameM, height=6)
    tree['columns'] = ('Title', 'First Name', 'Last Name', 'Permit no.', 'Date Issued')

    tree.column('#0', width=0, stretch=tk.NO)
    tree.column('Title', anchor=tk.CENTER, width=50)
    tree.column('First Name', anchor=tk.CENTER, width=100)
    tree.column('Last Name', anchor=tk.CENTER, width=100)
    tree.column('Permit no.', anchor=tk.CENTER, width=90)
    tree.column('Date Issued', anchor=tk.CENTER, width=105)

    tree.heading('Title', text='Title')
    tree.heading('First Name', text='First Name')
    tree.heading('Last Name', text='Last Name')
    tree.heading('Permit no.', text='Permit no.')
    tree.heading('Date Issued', text='Date Issued')

    tree.grid(row=0, column=0, padx=20, pady=20, sticky='nsew')

    frameB = customtkinter.CTkFrame(frame3, bg_color='#FFFFFF', fg_color='#FFFFFF', width=600, height=100)
    frameB.grid(row=2, column=0, sticky='n')

    edit_button = customtkinter.CTkButton(frameB, command=update, font=font2, text_color='#fff', text='Edit Info',
                                            fg_color='#4B0076', hover_color='#3C005E', bg_color='#fff', cursor='hand2',
                                            corner_radius=5, width=165)
    edit_button.grid(row=0, column=0, padx=10, pady=5)

    delete_button = customtkinter.CTkButton(frameB, command=delete, font=font2, text_color='#fff', text='Delete Info',
                                            fg_color='#4B0076', hover_color='#3C005E', bg_color='#fff', cursor='hand2',
                                            corner_radius=5, width=165)
    delete_button.grid(row=0, column=1, padx=10, pady=5)

    logout_button = customtkinter.CTkButton(frameB, command=logout, font=font2, text_color='#fff', text='Log Out',
                                            fg_color='#4B0076', hover_color='#3C005E', bg_color='#fff', cursor='hand2',
                                            corner_radius=5, width=165)
    logout_button.grid(row=0, column=2, padx=10, pady=5)

    add_to_treeview()


#itong function na ito is kung saan mag reregister ang user and yung ininput nyang informations papasok sa database
def show_signup_frame():
    global frame1, username_entry, password_entry
    frame1 = customtkinter.CTkFrame(app, fg_color='#FFFFFF', width=600, height=480)
    frame1.place(x=0, y=0)
    frameR = customtkinter.CTkFrame(frame1, fg_color='#FFFFFF', width=300, height=480)
    frameR.pack(expand=True, side=RIGHT)

    image1 = Image.open("1.png")
    side_img = customtkinter.CTkImage(dark_image=image1, light_image=image1, size=(300, 480))
    customtkinter.CTkLabel(master=frame1, text="", image=side_img).pack(expand=True, side=LEFT)

    signup_label = customtkinter.CTkLabel(frameR, font=font1, text='Sign Up', text_color='#4B0076', bg_color='#FFFFFF')
    signup_label.place(x=30, y=20)

    user_label = customtkinter.CTkLabel(frameR, font=font3, text='Username:', text_color='#4B0076', bg_color='#FFFFFF')
    user_label.place(x=30, y=105)

    username_entry = customtkinter.CTkEntry(frameR, font=font2, text_color='#33113D', fg_color='#F3F3F3',
                                            bg_color='#FFFFFF', border_color='#4B0076', border_width=3,
                                            width=245, height=50)
    username_entry.place(x=30, y=130)

    pass_label = customtkinter.CTkLabel(frameR, font=font3, text='Password:', text_color='#4B0076', bg_color='#FFFFFF')
    pass_label.place(x=30, y=195)

    password_entry = customtkinter.CTkEntry(frameR, font=font2, show='*', text_color='#33113D',
                                            fg_color='#F3F3F3', bg_color='#FFFFFF', border_color='#4B0076',
                                            border_width=3, width=245, height=50)
    password_entry.place(x=30, y=220)

    signup_button = customtkinter.CTkButton(frameR, command=signup, font=font2, text_color='#fff',
                                            text='Sign up', fg_color='#4B0076', hover_color='#3C005E',
                                            bg_color='#FFFFFF', cursor='hand2', corner_radius=5, width=245)
    signup_button.place(x=30, y=320)

    login_button = customtkinter.CTkButton(frameR, command=show_login, font=font2, text_color='#4B0076',
                                           text='Log in', fg_color='#FFFFFF', hover_color='#EAEAEA',
                                           bg_color='#FFFFFF', border_color='#4B0076', border_width=2,
                                           cursor='hand2', corner_radius=5, width=245)
    login_button.place(x=30, y=370)

#itong function na to is kukunin nya ang data sa user table ng database and i cocompare kung pareho sila if pareho i rurun nya na ang main page
def show_login_frame():
    global frame2, username_entry2, password_entry2
    frame2 = customtkinter.CTkFrame(app, width=600, height=480)
    frame2.place(x=0, y=0)
    frameR = customtkinter.CTkFrame(frame2, fg_color='#FFFFFF', width=300, height=480)
    frameR.pack(expand=True, side=RIGHT)

    image1 = Image.open("1.png")
    side_img = customtkinter.CTkImage(dark_image=image1, light_image=image1, size=(300, 480))
    customtkinter.CTkLabel(master=frame2, text="", image=side_img).pack(expand=True, side=LEFT)

    login_label2 = customtkinter.CTkLabel(frameR, font=font1, text='Log in', text_color='#4B0076', bg_color='#FFFFFF')
    login_label2.place(x=30, y=20)

    user_label = customtkinter.CTkLabel(frameR, font=font3, text='Username:', text_color='#4B0076', bg_color='#FFFFFF')
    user_label.place(x=30, y=105)

    username_entry2 = customtkinter.CTkEntry(frameR, font=font2, text_color='#33113D', fg_color='#F3F3F3',
                                             bg_color='#FFFFFF', border_color='#4B0076', border_width=3,
                                             width=245, height=50)
    username_entry2.place(x=30, y=130)

    pass_label = customtkinter.CTkLabel(frameR, font=font3, text='Password:', text_color='#4B0076', bg_color='#FFFFFF')
    pass_label.place(x=30, y=195)

    password_entry2 = customtkinter.CTkEntry(frameR, font=font2, show='*', text_color='#33113D',
                                             fg_color='#F3F3F3', bg_color='#FFFFFF', border_color='#4B0076',
                                             border_width=3, width=245, height=50)
    password_entry2.place(x=30, y=220)

    login_button2 = customtkinter.CTkButton(frameR, command=login_account, font=font2, text_color='#fff',
                                            text='Log in', fg_color='#4B0076', hover_color='#3C005E',
                                            bg_color='#FFFFFF', cursor='hand2', corner_radius=5, width=245)
    login_button2.place(x=30, y=320)

    signup_button2 = customtkinter.CTkButton(frameR, command=show_signup, font=font2, text_color='#4B0076',
                                             text='Sign up', fg_color='#FFFFFF', hover_color='#EAEAEA',
                                             bg_color='#FFFFFF', border_color='#4B0076', border_width=2,
                                             cursor='hand2', corner_radius=5, width=245)
    signup_button2.place(x=30, y=370)

#cinall namen dto ang show_login_frame para makapag log in na ang user
show_login_frame()

#itong function na ito is pag cinlose ang frame is i cucut nya yung connection ng database sa cinlose na frame
def on_closing():
    conn.close()
    app.destroy()

app.protocol("WM_DELETE_WINDOW", on_closing)
app.mainloop()
