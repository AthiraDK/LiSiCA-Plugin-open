import sys
import Tkinter as tk
from Tkinter import *
#Note: By default, the widgets like button, frame, radiobutton are all ttk widgets.
#To implement the widgets from Tkinter, specify tk.Button, tk.Frame etc...!
import ttk
from ttk import *
import tkMessageBox
import tkFileDialog 
import distutils
import os
import subprocess

import logging
from logging import handlers
#log file is used to debug the code when necessary

from pymol import cmd, plugins

import time
import multiprocessing
import datetime


import site
import distutils.core

from pymol.plugins import installation
from distutils.errors import DistutilsFileError
from calendar import month



startupPath=installation.get_plugdir()






try:
    filesmoved=distutils.dir_util.copy_tree(os.path.join(startupPath,'LiSiCA\LiSiCA'),os.path.join(os.path.expanduser('~'),'LiSiCA'))

except DistutilsFileError:
    print "DistutilsFileError"
except IOError:
    print "IOError"
except distutils.errors.UnknownFileError:
    print "UnknownFileError"
    
finally:
    print "In the finally block"



lisica_Folder=os.path.join(os.path.expanduser('~'),'LiSiCA')
result_Folder=os.path.join(lisica_Folder,"Results")
log_Folder=os.path.join(lisica_Folder,"Log")
icon_Folder=os.path.join(lisica_Folder,"Icons")

#process_id=os.getpid()
#process id may not be unique for the plugin instances. PyMOL uses multithreading

timestamp=datetime.datetime.fromtimestamp(time.time())
log_filename="log_"+str(timestamp.strftime('%m%d%H%M%S'))+".log"
## log file for each lisica process 

####################################################################
####                                                            ####
####      Setting up the log file for LiSiCA                    ####
####                                                            ####
####################################################################

### Configuring a logger named lisica
log=logging.getLogger("lisica")
### logger data is written to the file licisa.log in the LiSiCA folder in C:/Program files
handle=logging.FileHandler(os.path.join(log_Folder,log_filename))
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handle.setFormatter(formatter)
log.addHandler(handle)
log.setLevel(logging.DEBUG)



sys.path.append(lisica_Folder)
    

try:
    log.info("This application uses Tkinter Treectrl module")
    log.info("http://tkintertreectrl.sourceforge.net/")
    import TkTreectrl
    
except ImportError:
    #catches the exception raised if the TkTreectrl package (Tkinter wrapper of Tktreectrl tcl module) is incorrectly installed 
    #TkTreectrl package is not a standard python package and has to be installed separately
    #Installation normally done by running setup.py file
    log.critical("Error Message: '%s'" %ImportError.message)
    log.debug("TkTreectrl Import error")
    print "Import Error: Tkinter Treectrl not installed correctly"
    print("Copy and paste the TkTreectrl folder from the installation directory into the site-packages folder in Python's lib folder")
except:
    #catches all other exceptions
    #Possible exception: The tcl module tktreectrl is missing.
    #Installation of tktreectrl  normally done by running setup.py file
    log.critical("Error Message: '%s'" %Exception.message)
    log.debug("Possible: Tcl- treectrl error")
    print "Exception caught: Not Import Error"
    print "Possible: Tcl- treectrl error "
    print("Copy and paste the treectrl folder from the installation directory into the site-packages folder in Python's tcl folder")
    

####################################################################
####                                                            ####
####      Function to delete old files                          ####
####                                                            ####
####################################################################

def deleteOldFiles(folder):
    try:
        deleted=0
        if folder==log_Folder:
            days=7
        elif folder==result_Folder:
            days=30
        now=time.time()
        for f in os.listdir(folder):
            f=os.path.join(folder, f)
        
            if os.stat(f).st_mtime < now - days * 86400:
                #if the contents of the file/folder is last modified before 'days' days
                if os.stat(f).st_atime < now - 5 * 86400:
                    #if the contents of the file/folder is last accessed before 5 days
                    if os.path.isfile(f):
                        os.remove(f) 
                        deleted+=1   
                    elif os.path.isdir(f):
                        os.rmdir(f)
                        deleted+=1
    except IOError:
        log.error("IO Error")
    except OSError:
        log.error("OSError")
    except:
        log.error("Some error while deleting old log files")
    else:
        log.info("Old log files removed")
    



class GUI(Frame):
    def __init__(self,parent):
        Frame.__init__(self, parent)
        
        self.plugin = parent
        ### Configuring the parent frame (Plugin Frame) of LiSiCA
        self.plugin.geometry('{}x{}'.format(750,680))
        self.plugin.title("LiSiCA Plugin")
        
        try:
            self.plugin.iconbitmap(os.path.join(icon_Folder,"lisica_icon.ico"))
        except TclError:
            log.error(TclError.message)
            log.debug("Icon file not found in the path specified")
        except:
            log.debug("Not TclError")
            #Unix/Linux-@name.xbm
            
        self.initUI()    
        
    def close(self):
        #Command to close LiSiCA plugin
        
        if  tkMessageBox.askyesno("Exit", "Exit LiSiCA"):
            try:   
                #If the lisica.exe process is running in the background, terminates it.
                self.proc.kill()
                log.info("lisica.exe terminated")
            except:
                pass
            self.plugin.destroy()
            
    def getRefFileName(self):
        self.ref_Entry
        self.Rfilename=tkFileDialog.askopenfilename(filetypes = [('Mol2 files','*.mol2')])
        self.ref_Entry.delete(0,END)
        self.ref_Entry.insert(0,self.Rfilename)

    def getTarFileName(self):
    #get Target Ligand database file name 
        self.tar_Entry
        self.Tfilename=tkFileDialog.askopenfilename(filetypes = [('Mol2 files','*.mol2')])
        self.tar_Entry.delete(0,END)
        self.tar_Entry.insert(0,self.Tfilename)
        
    def dim(self):
    #get the product graph dimension from the radio button
        if self.dimension.get()==3:
            self.update()
            self.parameter.set("Maximum allowed Spatial Distance Difference: ")
            self.units.set("?") #Not used unicode error
            # for 3D screening, display an extra parameter "No of conformations"
            self.conf_Label.grid(row=8,sticky=W,pady=10,padx=20) #label
            self.conformations.grid(row=8,column=2,sticky=W) #Entry widget
        else:
            self.update()
            self.parameter.set("Maximum allowed Shortest Path difference: ")#initial setting req-Default 2D?
            self.units.set("bonds")#initial setting req?
            # for 2D screening, remove the parameter "No of conformations"
            self.conf_Label.grid_remove()
            self.conformations.grid_remove()
            
    def getDirPath(self):
        #allows user to change the default directory where results of LiSiCA will be stored 
            self.folder=tkFileDialog.askdirectory()
            self.result_Folder.delete(0,END)
            self.result_Folder.insert(0,self.folder)
    
    def inputValidation(self):
        msg=" "
        if os.path.isfile(self.ref_Entry.get()):
            if self.ref_Entry.get().endswith(".mol2"):
                log.info("Ref molecule file: '%s'",self.ref_Entry.get())
            else:
                log.error("Wrong file format")
                self.ref_Entry.config(highlightbackground='#B0171F')
                self.update()
        else:
            log.error("Ref molecule file path is invalid")
            msg="Invalid path for reference molecule\n"
            
            self.update()
        if os.path.isfile(self.tar_Entry.get()):
            if self.tar_Entry.get().endswith(".mol2"):
                log.info("Target molecule file: '%s'",self.tar_Entry.get())
            else:
                log.error("Wrong file format")
        else:
            log.error("Target molecule file path is invalid")
            msg=msg + "\nInvalid path for Target molecule"
            
        if os.path.isdir(self.result_Folder.get()):
            log.info("The results will be written in the folder: '%s' " %self.result_Folder.get())
        else:    
            log.debug("Folder name does not exist..!") 
            self.result_Folder.insert(0, result_Folder) 
        return msg
    
    def createCommand(self):
        self.lisica_path=os.path.join(lisica_Folder,r"bin\lisica_plugin_64x.exe")
        
        self.command=self.lisica_path\
                    +" -R "+os.path.normpath(self.ref_Entry.get())\
                    +" -T "+os.path.normpath(self.tar_Entry.get())\
                    +" -n "+str(self.CPU_Cores.get())\
                    +" -d "+str(self.dimension.get())\
                    +" -w "+self.w_Entry.get()\
                    +" -f "+self.result_Folder.get()
                    #+" -h "+str(self.hydrogen.get())
        try:
            print self.hydrogen.get()
        except:
            pass
        if self.hydrogen.get()==1:
            self.command=self.command+" -h "
        if self.dimension.get()==2:
            self.command=self.command+" -s "+str(self.max_Entry.get())
        elif self.dimension.get()==3:
            self.command=self.command\
                        +" -m "+str(self.max_Entry.get())\
                        +" -c "+str(self.conformations.get())
        else:
            log.error("Dimension is neither 2 or 3..!")
            
                 
        log.info("Command for lisica: '%s'" ,self.command)
        return self.command
                    
            
    def submitted(self):
        alert=self.inputValidation()
        if alert==" ":
            self.createCommand()
            self.go_Button.lower(self.input_Tab)
        
            self.progress=Progressbar(self.note,mode='indeterminate',length=500)
            self.progress.grid(row=17,columnspan=6,sticky=W+E,padx=(40,5),in_=self.input_Tab)
        
            print self.command
            self.startupinfo=subprocess.STARTUPINFO()
            self.startupinfo.dwFlags|=subprocess.STARTF_USESHOWWINDOW
            
            os.chdir( lisica_Folder ) 
            self.proc = subprocess.Popen(self.command.split(),shell=False,startupinfo=self.startupinfo)
           
            self.progress.start()
        
        
            while self.proc.poll() is None:
                try:
                    self.update()
                except:
                    log.info("Application has been terminated")
                
            self.progress.stop()
            self.progress.lower(self.input_Tab)
            self.go_Button.lift(self.input_Tab)
            if os.path.isfile(os.path.join(lisica_Folder,'done.txt')):
                
                #Read the result folder name from the done.txt file
                done_File=open(os.path.join(lisica_Folder,'done.txt'))
                self.timestamp_FolderName=done_File.readline()
                print self.timestamp_FolderName
                #timestamp_FolderName=self.timestamp_FolderName[:-1]
                self.timestamp_Folder=os.path.join(self.result_Folder.get(),self.timestamp_FolderName)
                done_File.close()
                print self.timestamp_Folder
                
                
                log.debug("Execution of liSiCA is complete")
                log.info("Files with common structures are available in results directory")
                self.note.select(self.output_Tab)
                self.uploadResults()
            
                try:
                    os.remove(os.path.join(lisica_Folder,'done.txt'))
                except IOError:
                        log.exception(IOError.message)
            else:
                tkMessageBox.showerror("Alert", "Abnormal termination of LiSiCA")
        
            
        else:
            tkMessageBox.showwarning("Alert", alert)


    def uploadResults(self):
        #Upload the first 100 results in lisica_result.txt to the output tab
        self.multiListBox1.delete(0,END)
        self.multiListBox2.delete(0,END)
        row=()
        compd_num=0
        try: 
            print self.w_Entry
            print self.w_Entry.get()
            print self.timestamp_Folder
            self.timestamp_Folder=self.timestamp_Folder.encode('string-escape')
            self.timestamp_Folder=self.timestamp_Folder[:-1]
            print self.timestamp_Folder
            result_File=os.path.normpath(os.path.join(self.timestamp_Folder,r'lisica_results.txt'))
            print result_File
            Textfile=open(result_File,"r") 
        #the file location -dynamically allocate..!!!!
            log.info("No IO Error. File '%s' open for reading" %Textfile.name)
        
            for block in iter(lambda: Textfile.readline(), ""):
                compd_num=compd_num+1
                row=block.split()
                rankedList=(compd_num,row[1],row[0])
                self.multiListBox1.insert(END,*rankedList)
                print compd_num
                if compd_num==int(self.w_Entry.get()):
                    print "Enters"
                    #if not self.w_Entry.get()==0:#displays only the first 100 results from the text file 
                    break
            log.info("Has finished uploading data")
            Textfile.close()
            self.multiListBox1.focus()
            self.multiListBox1.select_set(0, None)
            
        except IOError:
            log.error(IOError.errno)
            log.error(IOError.message)
            log.error(IOError.filename)
    
    def showCorr(self,ar):
        
        try:
            cmd.reinitialize()
            self.multiListBox1.focus()
            cmd.load(self.ref_Entry.get(),object="obj1")
            self.index=ar[0]
            self.selection_row=self.multiListBox1.get(self.index)
            self.selection_data=self.selection_row[0]
            self.rank=self.selection_data[0]
            self.zincId=self.selection_data[1]
            
            #Empty box2
            self.multiListBox2.delete(0,END)
            
            file_type=".mol2"
            result_Filename=self.rank+ "_" +self.zincId+file_type 
            log.info("Filename:'%s'" %result_Filename)
            i=0
            j=0
            k=0
            line=()
            #timestamp_Folder=os.path.join(result_Folder,timestamp_Done)
            file_Mol=os.path.join(self.timestamp_Folder,result_Filename)
            print file_Mol
            
            self.ref=()
            self.tar=()
            
            try:  
                fh=open(file_Mol,"r") #handle possible exceptions
                cmd.load(file_Mol,object="obj2")
            except IOError:
                tkMessageBox.showinfo("No data found", "The result molecules were not written to the output")
            for block in iter(lambda: fh.readline(), ""):
                if i==1:
                    if j==1:
                        if not block=='\n':
                        
                            k=k+1
                            line=block.split()
                            self.ref=self.ref+(line[1],)
                            self.tar=self.tar+ (line[3],)
                            
                            self.multiListBox2.insert(END,*line)
                        else:
                            i=0
                            j=0
                if "LiSiCA  RESULTS" in block:
                    i=1
                if i==1:
                    if "--------------" in block:
                        j=1
            log.info("Displayed the atom correspondence of the selected atom")
                     
            
            if self.dimension.get()==2:
                cmd.set("grid_mode",value=1)
                cmd.set("grid_slot",value=1,selection="obj1")
                cmd.set("grid_slot",value=2,selection="obj2")
                cmd.align("obj1","obj2")
            elif self.dimension.get()==3:
                self.lig1_atoms="obj1////"
                self.lig2_atoms="obj2////"
                for item in self.ref:
                    self.lig1_atoms=self.lig1_atoms+item+"+"
                for item in self.tar:
                    self.lig2_atoms=self.lig2_atoms+item+"+"   
                self.lig1_atoms=self.lig1_atoms[:-1]
                self.lig2_atoms=self.lig2_atoms[:-1]
                cmd.pair_fit(self.lig1_atoms,self.lig2_atoms)
            else:
                log.error("Dimension value is wrong")    
            
            cmd.orient()
        
        except:
            pass
        
        
    def showCorrAtoms(self,ar):
        try:
            self.multiListBox2.select_set(ar[0], None)
            self.sel_index=self.multiListBox2.get(ar[0])
            self.selected=self.sel_index[0]
            self.ref_Atom=self.selected[1]
            self.tar_Atom=self.selected[3]
            self.selected_Pair="obj1////"+self.ref_Atom+ " + obj2////"+self.tar_Atom
            cmd.select("ref",selection=self.selected_Pair)
            
        except:
            print("None selected from box2")
    def updateCommand(self,event):
        self.input_Tab.update()
        self.display_Command.delete(1.0, END)
        self.display_Command.insert(1.0, self.createCommand()) 
         
    def retag(self,tag, *args):
        for widget in args:
            widget.bindtags((tag,) + widget.bindtags())  
            
    
####################################################################
####                                                            ####
####                GUI design                                  ####
####                                                            ####
####################################################################

    
    def initUI(self):
        #Frame to display the name and icon of the software
        self.frame=Frame(self.plugin)
        self.frame.pack(fill=BOTH)
        
        
        try:
            photo=PhotoImage(master=self,file=os.path.join(icon_Folder,"lisica_icon.gif"))
            self.display=Label(self.frame,image=photo,background="#BFBFBF")
            self.display.image=photo
            self.display.pack(side=RIGHT)
        except:
            pass
        self.heading=Label(self.frame,text="LiSiCA",font=("Times",30, "bold"),
                           foreground="brown", background="#BFBFBF",anchor=CENTER)
        
        self.heading.pack(ipady=10, fill=BOTH, expand=1)
        
       
        #Notebook with 3 tabs
        self.note=Notebook(self.plugin)
        
        self.input_Tab=Frame(self.note)
        self.output_Tab=Frame(self.note)
        
        self.about_Tab=Frame(self.note)
        
        
        
        self.note.add(self.input_Tab,text="   Inputs     ")
        self.note.add(self.output_Tab, text="   Outputs   ")
        self.note.add(self.about_Tab,text="   About     ")
        self.note.pack(padx=10,pady=10, ipadx=10,ipady=10,anchor=CENTER,fill=BOTH,expand=1,after=self.frame)
        
        #Button to close LiSiCA plugin
        #self.closeButton=Button(self.plugin, text='Close', command=self.close)
        #self.closeButton.pack(pady=10,after=self.note,ipady=2)
        
        
#About Tab Design
        #Read License Code from .insilab-text file
        
        #label_About_style=ttk.Style()
        #label_About_style.configure('AboutTabLabel.TLabel', font=('Helvetica', 12, 'Bold'),foreground="black", background="white")
        
        self.license_Frame=tk.LabelFrame(self.about_Tab,text="Product License Information",labelanchor="nw",font=("Times", 12),relief="ridge",borderwidth=4)
        self.version_Frame=tk.LabelFrame(self.about_Tab,text="Product Version Information",labelanchor="nw",font=("Times", 12),relief="ridge",borderwidth=4)
        
        #self.license_Frame.grid(row=0,sticky=W+E,padx=(10,10),pady=(40,10))
        #self.version_Frame.grid(row=1,sticky=W+E,padx=(10,10),pady=(40,10))
        self.license_Frame.pack(fill=X,padx=(10,10),pady=(20,20))
        self.version_Frame.pack(fill=X,padx=(10,10),pady=(20,20))
        
        license_details=self.checkLicenseStatus()
        self.License_Code=StringVar(master=self)
        self.License_Code.set(license_details['Key'])
        self.Version=StringVar(master=self)
        self.Version.set(license_details['Version'])
        Label(self.license_Frame,text="LiSiCA Product Key :",font=("Times",11)).grid(row=2,columnspan=2,padx=(10,10),pady=(10,10),sticky=W)
        Label(self.license_Frame,textvariable=self.License_Code,font=("Times",11)).grid(row=2,column=2,columnspan=2,padx=(10,10),pady=(10,10),sticky=W)
        
       
        self.deactivate_Button=Button(self.license_Frame,text="Deactivate License Key",command=self.deactivate)
        self.deactivate_Button.grid(row=4,column=1,sticky=E,pady=(5,5),padx=(5,5))
        
        Label(self.version_Frame,text="LiSiCA Product Version :",font=("Times",11)).grid(row=7,columnspan=2,padx=(10,10),pady=(10,10),sticky=W)
        Label(self.version_Frame,textvariable=self.Version,font=("Times",11)).grid(row=7,column=2,columnspan=2,padx=(10,10),pady=(10,10),sticky=W)
        
        #Checking for latest upgrades
        try:
            from pmg_tk.startup import Lisica__init__ as x
            upgraderObj=x.Upgrader()
            latest=upgraderObj.findLatestVersion()
            tag_name=latest['tag_name']
            tag_name=tag_name[1:]
            from distutils.version import StrictVersion
            if StrictVersion(self.Version.get())>StrictVersion(tag_name):
                Label(self.version_Frame,text="New Update available !",font=("Times",11,'bold')).grid(row=8,column=0,columnspan=2,padx=(10,10),pady=(10,10),sticky=W)
                Label(self.version_Frame,text="For More information : ",font=("Times",11)).grid(row=9,columnspan=2,padx=(10,5),pady=(10,10),sticky=W)
        
        
                self.release_url=Label(self.version_Frame,text=latest['html_url'],font=("Times",11),foreground="blue",underline=True)
                self.release_url.grid(row=9,column=2,columnspan=2,padx=(10,5),pady=(10,10),sticky=W)
                
                self.upgrade_Button=Button(self.version_Frame,text="Upgrade to "+ tag_name,command=lambda: upgraderObj.upgrade(latest))
                self.upgrade_Button.grid(row=10,column=3,sticky=E,pady=(5,5),padx=(5,5))
                
                
            '''
            published_DateTime=latest['published_at']
            year=int(published_DateTime[0:4])
            month=int(published_DateTime[5:7])
            #date=published_DateTime[8:10]
            print year
            print month
            
            if year<2015:
                pass
            elif year ==2015:
                #check month
                if month<9:
                    pass
                elif month==9:
                    #check date
                    pass
                else:
                    #upgrade
                    Label(self.version_Frame,text="New Update available",font=("Times",11)).grid(row=8,column=2,columnspan=2,padx=(10,10),pady=(10,10),sticky=W)
                    print "here"
            else:
                #upgrade
                pass
         '''           
                
        except:
            print "Could not use the upgrader function"
        
        
        self.contact_Frame=tk.LabelFrame(self.about_Tab,text="Contact Us",labelanchor="nw",font=("Times", 12),relief="ridge",borderwidth=4)
        self.contact_Frame.pack(fill=X,padx=(10,10),pady=(20,20))
        Label(self.contact_Frame,text="Contact Us at info@insilab.com",font=("Times",11)).grid(columnspan=2,padx=(10,10),pady=(10,10),sticky=W)
        Label(self.contact_Frame,text="Please feel free to visit our website : ",font=("Times",11)).grid(row=2,columnspan=2,padx=(10,5),pady=(10,10),sticky=W)
        
        
        self.website=Label(self.contact_Frame,text=r"http://www.insilab.com.",font=("Times",11),foreground="blue",underline=True)
        import tkFont
        hyperlink_font=tkFont.Font(self.website,self.website.cget("font"))
        hyperlink_font.configure(underline=True)
        self.website.configure(font=hyperlink_font)
        
        self.website.grid(row=2,column=2,columnspan=2,padx=(0,10),pady=(10,10),sticky=W)
        self.website.bind("<Button-1>", self.openWebsite)
#Input Tab Design
        
        #Choose Mol2 file for Reference Ligand 
        Label(self.input_Tab,text="Reference Ligand: ").grid(row=1,sticky=W,pady=(20,10),padx=20)
        self.ref_Entry=Entry(self.input_Tab,width=50)
        
        self.ref_Entry.grid(row=1,column=2,pady=(20,10))
        
        self.button_BrowseRef=Button(self.input_Tab,text="Browse",command=self.getRefFileName)
        self.button_BrowseRef.grid(row=1,column=4,pady=(20,10))
        
        
        #Choose Mol2 file for Target Ligand(s)
        Label(self.input_Tab, text="Target Ligand(s):").grid(row=2,sticky=W,padx=20)
        self.tar_Entry=Entry(self.input_Tab,width=50)
        self.tar_Entry.grid(row=2,column=2)
        Button(self.input_Tab,text="Browse",command=self.getTarFileName).grid(row=2,column=4)
        
        #set variables for dimension parameters
        self.parameter=StringVar(master=self)
        self.units=StringVar(master=self)
        #set default for parameters
        self.parameter.set("Maximum allowed Shortest Path difference: ")
        self.units.set("bonds")
        
        global Conf_Label,conformations 
        #declaring these widget variables outside the function dim()
        #prevents repeated creation of widgets.

        self.conf_Label=Label(self.input_Tab, text="No of conformations: ")
        self.conformations=Entry(self.input_Tab, width=10)
        self.conformations.insert(0, "1")

        #2D or 3D Screening? Default is 2D- RadioButtons
        self.dimension=IntVar(master=self)
        self.dimension.set(2)
       
        self.d2=Radiobutton(self.input_Tab,text="2 Dimensional Screening", variable=self.dimension, value=2, command=self.dim)
        self.d3=Radiobutton(self.input_Tab,text="3 Dimensional Screening", variable=self.dimension, value=3, command=self.dim)
        Label(self.input_Tab,text="Product Graph Dimension:").grid(row=5,columnspan=2,sticky=W,pady=10,padx=20)
        self.d2.grid(row=5,column=2,columnspan=2,sticky=W+E)
        self.d3.grid(row=6,column=2,columnspan=2,sticky=W+E)
        
        #Depending on the dimension chosen 
        self.maxLabel=Label(self.input_Tab, textvariable=self.parameter)
        self.maxLabel.grid(row=7,sticky=W,pady=10,padx=20)
        self.maxLabel.update()
        self.max_Entry=Entry(self.input_Tab, width=10)
        self.max_Entry.grid(row=7,column=2,sticky=W)
        self.max_Entry.insert(0,"1")
       
        #Value to be acquired and passed
            #To display the unit, uncomment the following line
        #Label(self.input_Tab, textvariable=self.units).grid(row=7,column=2)
           
        
        self.w_Label=Label(self.input_Tab, text="No of highest ranked molecules to write to the output: ")
        self.w_Entry=Entry(self.input_Tab, width=10)
        
        
        self.w_Label.grid(row=9,sticky=W,pady=10,padx=20)
        self.w_Entry.grid(row=9,column=2,sticky=W)
        self.w_Entry.insert(0, "100")
        
        
        self.hydrogen=IntVar(master=self)
        
        
        Label(self.input_Tab, text="Consider Hydrogens :").grid(row=11,sticky=W,pady=10,padx=20)
        self.checkBox=Checkbutton(self.input_Tab,variable=self.hydrogen)
       
        self.checkBox.grid(row=11,column=2,sticky=W)
        
        #Get the no of CPU cores available in the system
        self.CPU_Cores=IntVar(master=self)
        self.CPU_Cores.set(multiprocessing.cpu_count())#Deafult=all CPU cores
        #Widget to set the CPU count manually- Slider
        Label(self.input_Tab, text="Number of CPU cores to be used: ").grid(row=12,sticky=W,pady=10,padx=20)
            #Defualt = All available CPU cores 
        self.slider=tk.Scale(self.input_Tab,
                          variable=self.CPU_Cores,
                          from_=1,
                          to=multiprocessing.cpu_count(),
                          length=100,
                          resolution=1,
                          orient=HORIZONTAL)
        self.slider.grid(row=12,column=2,pady=10,sticky=W)

        #Option to choose the directory for Results of LiSiCA
        Label(self.input_Tab, text="Save results in:").grid(row=13,sticky=W,padx=20)
        self.result_Folder=Entry(self.input_Tab,width=50)
        self.result_Folder.grid(row=13,column=2,pady=10)
        self.result_Folder.insert(0, result_Folder) 
        
        Button(self.input_Tab,text="Browse",command=self.getDirPath).grid(row=13,column=4)

        

        
        self.display_Command=Text(self.input_Tab,height=3)
        
        self.display_Command.grid(row=14,columnspan=6,sticky=W+E)
        
        self.input_Tab.bind("<Key>", self.updateCommand)
        
        self.retag("Parameters", self.ref_Entry, self.tar_Entry, self.d2, self.d3, self.conformations,self.w_Entry,self.max_Entry,self.slider,self.result_Folder,self.checkBox,self.input_Tab)
        self.input_Tab.bind_class("Parameters", "<Button-1>", self.updateCommand)
        
        self.go_Button=Button(self.note,text="GO",command=self.submitted)
        self.go_Button.grid(row=17,column=4,pady=(5,5),in_=self.input_Tab)
        

        

    # Output Tab Design
        #Frame on the left half of Output Tab for displaying the Results
        self.frame_Result=Frame(self.output_Tab)
        self.frame_Result.pack(side=LEFT,fill=BOTH,expand=1)
        #Frame on the right half Output Tab for displaying the Atom correspondence
        self.frame_Corr=Frame(self.output_Tab)
        self.frame_Corr.pack(side=RIGHT,fill=BOTH,expand=1)

        #Design of the Result frame
        self.ref=()
        self.tar=()
        
            #Add a scroll bar named scrollbar1
        self.scrollbar1=Scrollbar(self.frame_Result)
        self.scrollbar1.pack(side=RIGHT,fill=Y)
            #Add a multi-column list box to the frame
            #The MultiListBox class belongs to TkTreectrl module
            #TkTreectrl package is an external package and is to be downloaded and installed  
        self.multiListBox1=TkTreectrl.MultiListbox(self.frame_Result,yscrollcommand=self.scrollbar1.set,
                                                   expandcolumns=(1,2),selectcmd=self.showCorr)
        self.multiListBox1.pack(side=LEFT,fill=BOTH,expand=1)
        self.multiListBox1.config(columns=('Rank','ZINC ID', "Tanimoto score"))
            #The scrollbar2 is linked to the multiListBox2
        self.scrollbar1.config(command=self.multiListBox1.yview)

        #Design of the Atoms' Correspondence displaying frame
            #Add a scroll bar named scrollbar2
        self.scrollbar2=Scrollbar(self.frame_Corr)
        self.scrollbar2.pack(side=RIGHT,fill=Y)
            #Add a multi-column list box to the frame
            #The MultiListBox class belongs to TkTreectrl module
            #TkTreectrl package is an external package and is to be downloaded and installed  
        self.multiListBox2=TkTreectrl.MultiListbox(self.frame_Corr,yscrollcommand=self.scrollbar2.set,expandcolumns=(0,1,2,3,4),selectcmd=self.showCorrAtoms)
        self.multiListBox2.pack(side=LEFT,fill=BOTH,expand=1)
        self.multiListBox2.config(columns=('Ref. Num','Ref. Atom','Tar. Num','Tar. Atom','Atom Type'))
            #The scrollbar2 is linked to the multiListBox2
        self.scrollbar2.config(command=self.multiListBox2.yview)
        
        
        self.pack()
        
    def checkLicenseStatus(self):
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
    def deactivate(self):
        self.deactivate_command="D:\\LiSiCA_new_test\\LiSiCAx64.exe" +" -deactivate"
    
        exitCode=1
        try:
            exitCode = subprocess.call(self.deactivate_command)
            if exitCode == 0:
                tkMessageBox.showinfo("License", "License deactivation succeded.")
                self.plugin.destroy()
                
            elif exitCode == 205:
                
                tkMessageBox.showerror("License Error","Something went wrong. Please contact us at info@insilab.com for detailed information.")
            elif exitCode == 206:
                
                tkMessageBox.showerror("License Error","You don't have permission to deactivate this license. Please contact us at info@insilab.com for detailed information.")
            elif exitCode == 207:
                
                tkMessageBox.showerror("License Error","Error getting info about computer. Please contact us at info@insilab.com for detailed information.")
            elif exitCode == 208:
                
                tkMessageBox.showerror("License Error","Failed connecting to server. Please check your internet connection or try again later. Feel free to contact us at info@insilab.com for detailed information.")
        except subprocess.CalledProcessError as licenseStatus:
            tkMessageBox.showerror('License Error', licenseStatus.output)  
        
    def openWebsite(self,event):
        import webbrowser
        try:
            webbrowser.open_new(r"http://www.insilab.com")
        except:
            print "Error. Could not open the Website"
#######################################################################################################################


def main():
    
    #For each 
    if os.path.isfile(os.path.join(lisica_Folder,'lisica.log')):
        open(os.path.join(lisica_Folder,'lisica.log'),"w").close()
    
    
            
    log.info("*******************")
    log.info("LiSiCA: version 1.0") 
    log.info("Plugin_timestamp: '%s'" %timestamp.strftime("%Y-%m-%d %H: %M :%S"))
    root = Tk()
    treectrl=os.path.join(lisica_Folder,'treectrl2.4.1')
    root.tk.eval('lappend auto_path {'+treectrl+'}')
    lisica=GUI(root)
    root.protocol('WM_DELETE_WINDOW', lisica.close)
    root.mainloop()
#if __name__ == "__main__":
    
    #main()
    #deleteOldFiles(log_Folder)

#def __init__(self):
    #self.menuBar.addmenuitem('Plugin', 'command', 'LiSiCA', label = 'LiSiCA', command=lambda s=self: main())

