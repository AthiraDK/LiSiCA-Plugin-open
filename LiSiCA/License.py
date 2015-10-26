import Tkinter
from Tkinter import *
import os
import subprocess
import tkMessageBox
from LiSiCA import Plugin_GUI


HOME_DIRECTORY=os.path.expanduser('~')
lisica_Folder=os.path.join(HOME_DIRECTORY,'LiSiCA')
#sys.path.append(lisica_Folder)

icon_Folder=os.path.join(lisica_Folder,"Icons")
#exe_path=os.path.join(lisica_Folder,bin,"lisica.exe")

exe_path="D:\\LiSiCA_new_test\\LiSiCAx64.exe"

class Activation:
    def __init__(self):
        
        self.Window=Tk()
        #self.Window.config(background="white")
        self.Window.geometry('{}x{}'.format(620,250))
        self.Window.title("Product Activation")
        self.initGUI()
        self.VALID=False
        
        
    def initGUI(self):
        
        photo=PhotoImage(master=self.Window,file=os.path.join(icon_Folder,"lisica_icon.gif"))
        self.display=Label(self.Window,image=photo)
        self.display.image=photo
        self.display.grid(row=0,column=0,rowspan=2)
       
        self.activation_Status=StringVar(master=self.Window)
        self._Website=StringVar(master=self.Window)
        
        self.key_Frame=LabelFrame(self.Window,text="Enter Product Key",labelanchor="nw",font=("Times", 13),relief="ridge",borderwidth=4)
        self.key_Frame.grid(row=0,column=1,sticky=W+E,padx=(10,10),pady=(40,10))
        self.key_Entry=Entry(self.key_Frame,width=30,borderwidth=3,font=("Courier",12))
        self.activate_Button=Button(self.key_Frame,text="Activate",font=("Times", 11),command=self.activate)
        self.key_Entry.grid(row=2,padx=(5,1),pady=(20,10),sticky=E)
        self.activate_Button.grid(row=2,column=2,sticky=W,pady=(20,10),padx=(1,5))
        
        
        self.activation_Status.set(
"""*Activating LiSiCA requires a license.
    To obtain a valid license key contact us at info@insilab.com."""
                 )
        self.info_msg=Label(self.key_Frame,textvariable=self.activation_Status,font=("Times", 11))
        self.info_msg.grid(row=4,columnspan=2,padx=(2,2),pady=(20,2),sticky=W+S)
       
        self.website=Label(self.Window,text="For more information, please visit our website: http://www.insilab.com",font=("Times",11))
        self.website.grid(row=2,columnspan=2,padx=(5,5),pady=(10,1))
        #Label(self.Window,text=""" Please feel free to visit our website at http://www.insilab.com.""").grid(row=5,padx=(5,5),sticky=W+S)
                
        self.Window.mainloop()
        
    def activate(self):
        license_code=self.key_Entry.get()
        print license_code
        activate_Command=exe_path+" -activate "+license_code
        try:
            proc = subprocess.Popen(activate_Command)
            while proc.poll() is None:
                self.Window.update()
            exitCode=proc.returncode
            print exitCode
            if exitCode == 0:
                #tkMessageBox.showinfo("License", "License validation succeeded. LiSiCA plugin is activated")
                self.key_Frame.destroy()

               
                self.actiavted_Frame=LabelFrame(self.Window,relief="ridge",borderwidth=4)
                self.actiavted_Frame.grid(row=0,column=1,sticky=W+E,padx=(10,10),pady=(40,10))
                self.activated_Label=Label(self.actiavted_Frame,font=("Times",11),text="License validation succeeded. LiSiCA plugin is activated")
                self.activated_Label.grid(row=2,padx=(5,1),pady=(20,10),columnspan=2,sticky=E)
                self.run=BooleanVar(master=self.Window)
                self.run.set(True)
                self.run_plugin=Radiobutton(self.actiavted_Frame,text="Start LiSiCA plugin now", variable=self.run, command=self.finish)
                
                self.finish_Button=Button(self.actiavted_Frame,text="Run LiSiCA",font=("Times", 11),command=self.finish)
                self.finish_Button.grid(row=3,column=2,sticky=W,pady=(20,10),padx=(1,5))
                
                
                self.VALID=True
                
                
                
            elif exitCode == 200:
                #tkMessageBox.showinfo("License","There is a new version of LiSiCA plugin available. For information on this update please visit our website: http://www.insilab.com.")
                self.key_Frame.destroy()
                
         
                self.VALID=True
                
            elif exitCode == 201:
                self.key_Entry.delete(0, END)
                self.activation_Status.set(
"""*Invalid License Code.
    Please contact us at info@insilab.com to obtain a valid license key."""
                 )
                self.info_msg.configure(fg="red")
                #tkMessageBox.showerror("License Error","Invalid license code. Please contact us at info@insilab.com to obtain a valid license key.")
                
            
            elif exitCode == 202:
                self.key_Entry.delete(0, END)
                self.activation_Status.set(
"""*There is another computer activated by this license.
    Please contact us at info@insilab.com for detailed information."""
                 )
                self.info_msg.configure(fg="red")
                #tkMessageBox.showerror("License Error","There is another computer activated by this license. Please contact us at info@insilab.com for detailed information.")
                
                
            elif exitCode == 203:
                self.key_Entry.delete(0, END)
                self.activation_Status.set(
"""*Error getting info about computer.
    Please contact us at info@insilab.com for detailed information."""
                 )
                self.info_msg.configure(fg="red")
                #tkMessageBox.showerror("License Error","Error getting info about computer. Please contact us at info@insilab.com for detailed information.")
                
                
            elif exitCode == 204:
                self.key_Entry.delete(0, END)
                self.activation_Status.set(
"""*Please check your internet connection or try again later.
    Please contact us at info@insilab.com for detailed information."""
                 )
                self.info_msg.configure(fg="red")
                #tkMessageBox.showerror("License Error","Please check your internet connection or try again later. Feel free to contact us at info@insilab.com for detailed information.")
                
                
        except subprocess.CalledProcessError as licenseStatus:
            self.key_Entry.delete(0, END)
            tkMessageBox.showerror('License Error', licenseStatus.output)
 
    def finish(self):
        
            self.Window.destroy()
           
                

        
            
def activate(exe_path):
    
    a=Activation()
    if a.VALID==True:
        if a.run.get()==True:
           
            return 1
        else:
            return 2
    else:
        return 0
    
    a.Window.protocol('WM_DELETE_WINDOW',a.finish)
    

def checkLicenseStatus():
        licenseFile = os.path.join(os.path.expanduser("~"),".insilab-license.txt")
        lisica_line=()
        if os.path.isfile(licenseFile):
            with open(licenseFile) as lFile:
                for line in lFile:
                    if line[:6] == "lisica":
                        lisica_line=line.split()
                        license_details={'Key':lisica_line[1],'Version':lisica_line[2]}
                        break
                        return license_details
                    else:
                        return None
    
if __name__ == "__main__":
    #For testing
    active=activate("so") 
    
    Plugin_GUI.main()
        