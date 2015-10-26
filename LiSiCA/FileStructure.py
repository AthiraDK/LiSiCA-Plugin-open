import os


HOME_DIRECTORY=os.path.expanduser('~')
class Directory_Structure:
   
    def __init__(self,lisica_folder):
        self.lisica_Folder=lisica_folder
        #self.conf_FileName=os.path.join(lisica_folder,"configuration.txt")
        self.conf_FileName=os.path.join(HOME_DIRECTORY,"foldertree.txt")
        self.missing_Files=0
     
    def check(self):
        
        try:
            if os.path.isdir(self.lisica_Folder):
                print "Yes"
            self.conf_File=open(self.conf_FileName)
            self.installation_Status=self.conf_File.readline()
            
            if self.installation_Status=="INSTALLED CORRECTLY":
            #if False:
                print "INSTALLED CORRECTLY"
                return True
                
            else:
                
                #check here
                #confirm directory structure
                for line in iter(lambda: self.conf_File.readline(), ""):
                    line=os.path.normpath(os.path.join(self.lisica_Folder,line))
                    line=str(line)
                    line=line.encode('string-escape')
                    line=line[:-2]
                    #print line
                    if os.path.isfile(line):
                        print "OK"
                    elif os.path.isdir(line):
                        print "OK"
                    else:
                        print "Not found in LiSiCA folder : '%s'" %line
                        self.missing_Files+=1
                    
                self.conf_File.close()
                if self.missing_Files==0:
                    modify_conf_File=open(self.conf_FileName,"w")
                    modify_conf_File.write("INSTALLED CORRECTLY")
                    modify_conf_File.close()
                    return True
                else:
                    return False 
                
                
        except IOError as e:
            print e.messageInfo
            return False
            
def main():
    a=Directory_Structure(os.path.join(HOME_DIRECTORY,"LiSiCA"))
    has_allFiles=a.check()
    return has_allFiles
if __name__ == "__main__":
    #For testing
    value=main()      
    print value     