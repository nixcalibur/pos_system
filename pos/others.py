import datetime

def open_main_page(self):
    self.login_frame.pack_forget()
    self.main_frame.pack(expand=True, fill="both")

def tick(self): # Update the time label with the current time
    self.time_label.config(text=str(datetime.datetime.now()).rpartition('.')[0])
    self.parent.after(1000, self.tick)

# Close the database connection when the application is closed
def __del__(self):
    self.conn.close()