import requests
import asyncio
import os
import json
import time
import multiprocessing
import sys
import subprocess
import urllib3

global inputFile
global outputFile
global status
global statusflag
global phrase
global phraseflag
global suffix
global suffixflag
global redirectsflag
global errorsflag
global proxyflag
global proxy
global jsonflag

def main():
    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
    inPool = 20
    f = open (inputFile,'r')
    revisar0 = f.readlines()
    f.close()
    revisar = {}
    result = {}
    manager = multiprocessing.Manager()
    po = multiprocessing.Pool(inPool)
    
    if(suffixflag):
        suffixlist = suffix.split(",")
    for c in revisar0:
        c = c.strip()
        if(suffixflag):
            for s in suffixlist:
                cs=c+s
                revisar[cs] = ""
        else:
            revisar[c] = ""
    result = {}
    #print(revisar)
    a = 0
    totalSitios = len(revisar)
    print("total de sitios a revisar:" + str(totalSitios))
    for i in revisar:
        a = a+1
        result[i] = (po.apply_async(execmd, (i, a)))
    po.close()
    po.join()
    cleanResults = {}
    a = 0
    for k,v in result.items():
      a=a+1
      buffer = v.get()
      #print(a, "_/_", totalSitios, end='\r')
      if(buffer > 0):
         cleanResults[k]=v.get()
    g = open(outputFile,'w+')
    if(not jsonflag):
        for k in cleanResults:
            g.write(k + "," + str(cleanResults[k]) +"\n")
    else:
        for k in cleanResults:
            d={"url":k,"status":cleanResults[k]}
            j=json.dumps(d)
            
            g.write(str(j) +"\n")
    g.close()


def execmd(site, a ):
    try:
        #clean site
        filt = site.find(" ")
        if (filt>0):
            site = site[0:filt]
        if(filt > 0 ):
            site = site[0:filt]
        filt = site.find("http")
        if(filt == -1):
            site = "https://" + site
        #agregar path
        #revisar sitio
        #print("site:" + site)
        if(a%100==0):
           print("revisando sitio n" + str(a))
        proxies = {
          "http": proxy,
          "https": proxy
	}
        if(not proxyflag):
           r = requests.get(site , timeout=(10,20), verify=False, allow_redirects=redirectsflag)
        else:
           r = requests.get(site , timeout=(10,20), verify=False, allow_redirects=redirectsflag,proxies=proxies)
        #print("code: " + str(r.status_code) + "text: \n" + r.text)
        textMatch = False
        if( phraseflag ):
           if( phrase in r.text):
              textMatch = True
           else:
              TextMatch = False
        else:
           textMatch = True
           

        if (str(r.status_code) in status):
           statusMatch=True
        else:
           statusMatch = False
        
        if( statusMatch and textMatch):
            # and "javascript:alert('test')" in r.text
            sc = r.status_code
            print("detectado sitio: " + site + " n:" + str(a))
            return sc
        else:
            return 0
    except Exception as e:
        if (errorsflag):
           print (e)
        return 0




if __name__ == "__main__":
#   asyncio.run(main())
   s = time.perf_counter()
   statusflag = False
   phraseflag = False
   inputFile = 'sites.txt'
   outputFile= 'results.txt'
   suffixflag = False
   redirectsflag = False
   errorsflag = False
   proxyflag=False
   for i in range(1,len(sys.argv)):
      if sys.argv[i] == '-rc' or sys.argv[i] == '--responsecode' :
         status = sys.argv[i+1].split(",")
         statusflag=True
      elif sys.argv[i] == '-p' or sys.argv[i] == '--phrase':
         phrase = sys.argv[i+1]
         phraseflag = True
      elif sys.argv[i] == '-s' or sys.argv[i] == '--suffix':
         suffix = sys.argv[i+1]
         suffixflag = True
      elif sys.argv[i] == '-i' or sys.argv[i] == '--input':
         inputFile = sys.argv[i+1]
      elif sys.argv[i] == '-o' or sys.argv[i] == '--output':
         outputFile = sys.argv[i+1]
      elif sys.argv[i] == '-ar' or sys.argv[i] == '--allowredirect':
         redirectsflag = True
      elif sys.argv[i] == '-proxy' or sys.argv[i] == '--proxy':
         proxy = sys.argv[i+1]
         proxyflag = True
      elif sys.argv[i] == '--json':
         jsonflag = True
      elif sys.argv[i] == '-e' or sys.argv[i] == '--errors':
         errorsflag = True   
   if(not phraseflag and not suffixflag):
      print('Se debe buscar por al menos un parametro: -p, -s')
      exit()
   if(not statusflag):
      statusflag = True
      status = '200'
   main()
   elapsed = time.perf_counter() - s
   print(f"{__file__} executed in {elapsed:0.2f} seconds.")
