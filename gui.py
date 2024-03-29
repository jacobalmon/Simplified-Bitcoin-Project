from tkinter import *

#Extra Credit if we wanted to.
class GUI:
    def __init__(self, root):
        self.master = root
        self.master.geometry("750x500")
        whitespace = " "
        self.master.title(30 * whitespace + "Simplified Bitcoin")

        self.client = Label(self.master, text="Client")
        self.client.place(x=30, y=0)

        self.server = Label(self.master, text="Server")
        self.server.place(x=345, y=0)

        self.clientoutput = Text(self.master, height=16, width=40)
        self.clientoutput.place(x=30, y=50)

        self.serveroutput = Text()
if __name__ == "__main__":
    myTkRoot = Tk()
    myGui = GUI(myTkRoot)
    myTkRoot.mainloop()
