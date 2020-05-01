import requests

import time
end=986
dictionary=[]
for i in range(1,end):
    url="https://dsalsrv04.uchicago.edu/cgi-bin/app/hobsonjobson_query.py?page="+str(i)
    print(i)
    x=0
    while(x<10):
        try:
            req = requests.get(url, verify=False, timeout=60).text
            break
        except:
            x=x+1
            time.sleep(2)
            print(i,x)
    entries=req.split("<span style='font-weight:700'>")
    for e in range(1,len(entries)):
        row=entries[e]
        print(row.split('</div>')[0].strip('\n'))
        dictionary.append(row.split('</div>')[0].strip('\n'))
        
import pickle
with open('parrot.pkl', 'wb') as f:
    pickle.dump(dictionary, f)
       