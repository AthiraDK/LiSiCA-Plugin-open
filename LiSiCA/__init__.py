import os
import urllib2
from urllib2 import urlopen,URLError,HTTPError
import zipfile
import tkMessageBox
import json

GITHUB_REPO=""
GITHUB_URL=""
url_Archive=""


class Configuration:
    def __init__(self):
        import platform
        self.system=platform.system()
        self.machine=platform.machine()
        self.architecture=platform.architecture()
        import struct
        self.python_bit=8 * struct.calcsize("P")
        self.python_version=platform.python_version_tuple()
        
    def exe_File(self):
        if self.system=='Windows':
            if self.python_bit==64:
                exe_filename="LiSiCAx64.exe"
            elif self.python_bit==32:
                exe_filename="LiSiCAx86.exe"
            else:
                exe_filename="Could not determine the python build properties"
        elif self.system=='Linux':
            exe_filename="lisica"
        else:
            print "The plugin might not be compatible with your machine"
            exe_filename="lisica"
        return exe_filename
        
        

HOME_DIRECTORY=os.path.expanduser('~')
DICTIONARY={}
class Installer:
 
    def __init__(self):
        self.zipFileName="LiSiCA_Plugin.zip"
        
    def downloadInstall(self,url):
        #url="https://codeload.github.com/gpocentek/python-gitlab/zip/master"
        try:
            urlcontent=urlopen(url)
            zipcontent=urlcontent.read()
            
            #change location to user home directory
            
            LiSiCAzipFile=open(self.zipFileName,'wb')
            LiSiCAzipFile.write(zipcontent)
            LiSiCAzipFile.close()
            urlcontent.close()
        except HTTPError, e1:
            print "HTTP Error:", e1.code, url
        except URLError, e2:
            print "URL Error:", e2.reason, url
        except:
            #Modify
            print "Exception caught"
        
            
                
                
            
            
    def extractInstall(self):
        
        with zipfile.ZipFile(self.zipFileName,"r") as LiSiCAzip:
            LiSiCAzip.extractall(HOME_DIRECTORY)
        

class Upgrader:
    def __init__(self):
        pass
    def findLatestVersion(self):
        self.latestURL="https://api.github.com/repos/libgit2/libgit2/releases/latest"
        print self.latestURL
        self.response=urllib2.urlopen(self.latestURL)
        self.data=json.load(self.response)
        print self.data['name']
        zipball_url=self.data['zipball_url']
        published_on=self.data['published_at']
        print zipball_url
        print published_on
        return self.data
        
    def upgrade(self,newVersion):
        
        self.zip_url=newVersion['zipball_url']
        i=Installer()
        i.downloadInstall(self.zip_url)
        i.extractInstall()
           
               
            
def run():
    
    
    print("LiSiCA initialiser program")
    if not os.path.isdir(os.path.join(HOME_DIRECTORY,"LiSiCA")):
        configure=Configuration()
        exe_filename=configure.exe_File()
        
        upgrader=Upgrader()
        jsonData=upgrader.findLatestVersion()
        url=jsonData['zipball_url']
        installer_Object=Installer()
        installer_Object.downloadInstall(url)
        installer_Object.extractInstall()
    else :
        
    
        lisica_Folder=os.path.join(HOME_DIRECTORY,"LiSiCA")
        import FileStructure
        file_StructureObj=FileStructure.Directory_Structure(lisica_Folder)
        if file_StructureObj.check()==True:
            pass
        else:
            tkMessageBox.showerror("Missing Files", """LiSiCA Directory is corrupted.
            Missing files or folders. Try reinstalling the plugin """)  
            
        #modify this
        exe_path="so"   
        import License
        if License.checkLicenseStatus()==None:
            License.activate(exe_path)
        else:
            import Plugin_GUI
            Plugin_GUI.main()
            
                

def main(): 
    run()
    
def __init__(self):
    self.menuBar.addmenuitem('Plugin', 'command', 'LiSiCA', label = 'LiSiCA', command=lambda s=self: main())