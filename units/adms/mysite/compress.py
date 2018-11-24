import os

def compress_static():
    current_path=os.getcwd()
    for root,dirs,files in os.walk(current_path):
        if files:
            for vfileName in files:
                fileName = os.path.join(root,vfileName)
                if fileName[-3:]==".js" or fileName[-4:]==".css":
                    os.popen("java -jar yuicompressor-2.4.6.jar -o "+fileName+" "+fileName)
                
if __name__=="__main__":
    compress_static()