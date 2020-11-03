import subprocess
import requests
import json
from time import sleep
from os import listdir, system, geteuid

if geteuid() != 0:
  print("This script must be run as root!")
  exit(1)

PATH =   r"/data/misc/wifi/WifiConfigStore.xml"
file = "lbss"
cmd = 'iw dev wlan0 scan'

if file not in listdir():
    open(file, "w").close()

with open(file,"r") as f:
   data1 = f.read()
    
def insert(ess,password):
   return '<Network>\n<WifiConfiguration>\n<string name="ConfigKey">&quot;'+ess+'&quot;-WPA_PSK</string>\n<string name="SSID">&quot;'+ess+';</string>\n<null name="BSSID" />\n<string name="PreSharedKey">&quot;'+password+'&quot;</string>\n<null name="WEPKeys" />\n<int name="WEPTxKeyIndex" value="0" />v<boolean name="HiddenSSID" value="true" />\n<boolean name="RequirePMF" value="false" />\n<byte-array name="AllowedKeyMgmt" num="1">02</byte-array>\n<byte-array name="AllowedProtocols" num="1">03</byte-array>\n<byte-array name="AllowedAuthAlgos" num="1">01</byte-array>\n<byte-array name="AllowedGroupCiphers" num="1">0f</byte-array>\n<byte-array name="AllowedPairwiseCiphers" num="1">06</byte-array>\n<boolean name="Shared" value="true" />\n<int name="WapiCertSelMode" value="-1" />\n<null name="WapiCertSel" />\n<int name="WapiPskType" value="-1" />\n<null name="WapiPsk" />\n<int name="Status" value="2" />\n<null name="FQDN" />\n<null name="ProviderFriendlyName" />\n<null name="LinkedNetworksList" />\n<null name="DefaultGwMacAddress" />\n<boolean name="ValidatedInternetAccess" value="false" />\n<boolean name="NoInternetAccessExpected" value="false" />\n<int name="UserApproved" value="0" />\n<boolean name="MeteredHint" value="false" />\n<int name="MeteredOverride" value="0" />\n<boolean name="UseExternalScores" value="false" />\n<int name="NumAssociation" value="0" />\n<int name="CreatorUid" value="1000" />\n<string name="CreatorName">android.uid.system:1000</string>\n<string name="CreationTime">time=10-17 23:44:31.845</string>\n<int name="LastUpdateUid" value="1000" />\n<string name="LastUpdateName">android.uid.system:1000</string>\n<int name="LastConnectUid" value="1000" />\n<boolean name="IsLegacyPasspointConfig" value="false" />\n<long-array name="RoamingConsortiumOIs" num="0" />\n<string name="RandomizedMacAddress">02:00:00:00:00:00</string>\n</WifiConfiguration>\n<NetworkStatus>\n<string name="SelectionStatus">NETWORK_SELECTION_ENABLED</string>\n<string name="DisableReason">NETWORK_SELECTION_ENABLE</string>\n<null name="ConnectChoice" />\n<long name="ConnectChoiceTimeStamp" value="-1" />\n<boolean name="HasEverConnected" value="false" />\n</NetworkStatus>\n<IpConfiguration>\n<string name="IpAssignment">DHCP</string>\n<string name="ProxySettings">NONE</string>\n</IpConfiguration>\n</Network>\n'

def main():
   
   ans=input("\n[+] What do we do?\n\n\t[1]  Scan access points.\n\t[2]  Search in 3wifi.\n\n[+] Your choise: ")
   
   if ans == '1':
      scan()
 
   elif ans == '2':
      
      check(api())
   
   else:
      print('\n[!] Wrong choise!')
      main()


def scan():
   
   global data1
   
   while 1:
      
      count=0
      counter2=0
      counter1=0
      bssid=[]
      
      lines = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf').stdout.splitlines()
      
      for line in lines:

         if "(on wlan0)" in line:
            bssid.append(line[4:21])
            
      for i in bssid:
         if i not in data1:
            with open(file,"a") as f:
               f.write(i+'\n')
            counter1+=1
         counter2+=1
         open(file,"a").close()
      
      with open(file,"r") as f:
         data1 = f.read()
      for i in data1:
         if i=='\n':
            count+=1
      system('clear') 
      print('Scanning...\n\nAll points: '+str(count)+'\nPoints nearby: ' + str(counter2)+'\nWrote new points: '+str(counter1)+'\n_________________________\n\nPress Ctrl + Z to finish')

      sleep(7)
      
      
      
      

def check(API):
    
   if "WifiConfigStore.xml" not in listdir("/data/misc/wifi/"):
    raise Exception ('File WifiConfigStore not found!')
     
   global data1
   counter3=0
   
   lastlines=('</NetworkList>\n<PasspointConfigData>\n<long name="ProviderIndex" value="0" />\n</PasspointConfigData>\n</WifiConfigStoreData>')

   with open(PATH,"r") as wifi:
      lines=wifi.readlines()

   
   with open(PATH,"w") as wifi:
      wifi.writelines(lines[:-118])
   
   a=0
   b=99

   bssid=data1.split('\n')
   del bssid[-1]

   while b<len(bssid):
      bssiD = bssid[a:b]
      
      result=request(API,bssiD)

      a+=100
      b+=100
      
      if json.loads(result)["data"]!=[]:
           
         for mac in json.loads(result)["data"].values():
             for i in mac:
                 if i["essid"] in open(PATH,"r").read():
                    continue                 
                 counter3+=1                
                 with open(PATH,"a") as wifi:
                    wifi.write(insert(i["essid"],i["key"]))
          
   if len(bssid)%100!=0:
      
      b=len(bssid)
      bssiD = bssid[a:b]
           
      result=request(API,bssiD)
      
      if json.loads(result)["data"]!=[]:         
         for mac in json.loads(result)["data"].values():             
             for i in mac:                
                 if i["essid"] in open(PATH,"r").read():
                    continue
                 counter3+=1                 
                 with open(PATH,"a") as wifi:
                    wifi.write(insert(i["essid"],i["key"]))
                  
   with open(PATH,"a") as wifi:
      wifi.write(lastlines)
   
   open(file,"w").close()
   
   print("\nSearch in 3wifi is over\n\nNumber of wrote points: "+str(counter3)+"\n")  
   

def request(API,bssiD):
         data={"key": API,"bssid":bssiD}
         return requests.post("http://3wifi.stascorp.com/api/apiquery", 
         json=data).text
         

                  
def api():
         
   def inp():
      
      return input("\n[+] Input your API: ") 
                    
   def testAPI(API):
      if json.loads(request(API,"test"))["result"] ==  False:               
         if json.loads(request(API,"test"))["error"] ==  "loginfail":
            print("\n[!] Your API is incorrect!")
            testAPI(inp())                               
         else:
            print("\n[!] Something wrong, please try again.")
            testAPI(inp())
      else:
         with open("API","w") as f:
            f.write(API)
         return API

   if "API" not in listdir():
      return testAPI(inp())
   else:
         with open("API","r") as f:
            return testAPI(f.read())       
   
   input("Press Enter to quit")
      
main()
