#You can use the regular expression /(?<!\n)\n(?!\n)/,
import requests
import re
import copy
import math
import operator
'''
Download hobson jobson
'''
def downloadDictionary():
    url='https://archive.org/stream/in.ernet.dli.2015.210564/2015.210564.Hobson-jobson_djvu.txt'
    req = requests.get(url).text
    return(req)
'''
Save Dictionary to Local
'''
def saveDictionary(html,name):
    file=open(name,'w',encoding='utf-8')
    file.write(html)
    file.close()
    
'''
Load Dictionary from Local
'''
def loadDictionary(name):
    html=open(name,'r',encoding='utf-8').read().replace('- \n','').replace('-\n','')
    return(html)

    
'''
Extract text from HTML
'''

def extractDictionary(html):
    dictionary=html.split('<pre>')[1].split('</pre>')[0]
    return(dictionary)

'''
Clean Text from HTML

'''
'''
Generates Candidate Terms
'''
def generateCandidates(text):
    candidateList=re.findall(r'\n[A-Z]+,',text)     #starts at word boundary all caps uptil ,
    start=0
    end=0
    for i in range(0,len(candidateList)-1):
        if candidateList[i][:2]=='\nA' and candidateList[i+1][:2]=='\nA':
            start=i
            break
    candidateList2=candidateList[::-1]        
    for i in range(0,len(candidateList2)-1):
        if candidateList2[i][:2]=='\nZ' and candidateList2[i+1][:2]=='\nZ':
            end=len(candidateList)-i+1        #Z exclusive
            break
    return(start,end,candidateList)
    
    
'''
extracts Definitions
'''    
def extractItems(start,end,candidateList,text):
    newCandidates=candidateList[start:end]
    rawDictionary={}
    for i in range(0,len(newCandidates)-1):
       
        if newCandidates[i] not in rawDictionary:
            rawDictionary[newCandidates[i]]= text.split(newCandidates[i])[1].split(newCandidates[i+1])[0]
        else:
            if len(text.split(newCandidates[i])[1].split(newCandidates[i+1])[0])>len(rawDictionary[newCandidates[i]]):
                rawDictionary[newCandidates[i]]= text.split(newCandidates[i])[1].split(newCandidates[i+1])[0]
        text=newCandidates[i].join(text.split(newCandidates[i])[1:])
    return(rawDictionary)
'''
Cleaning Dictionary
Separates Examples, Otherwords, definition
'''
def cleanItems(dic):
    cleanDic={}
    for k in dic:
        cleanEntry=re.sub('\n+',' ',re.sub(' +',' ',dic[k])).strip(' ')
        if len(cleanEntry.split(' '))>6:
            try:
                entryStart=cleanEntry.find(re.findall(r'[a-z]',cleanEntry)[0][0])
                circa=cleanEntry[entryStart:].split(' c. ')
                if len(circa)>1:
                    cleanDic[k.replace('\n','')[:-1].lower()]=[re.sub(' +',' ',circa[0]),cleanEntry[:entryStart],' c. '+circa[1]]
                else:   #if there is no circa
                    cleanDic[k.replace('\n','')[:-1].lower()]=[re.sub(' +',' ',circa[0]),cleanEntry[:entryStart],'']
            except:
                #print(k)
                pass
    return(cleanDic)            
'''
Removes Punctuations from definitions
'''    
def removePunctuations(dic):
    newDic={}
    for k in dic:
        newDic[k]=[re.sub(r'[^\w\s]','',dic[k][0].lower()),dic[k][1].lower(),dic[k][2].lower()]
        
    return(newDic)
    
'''
TFIDF

'''

def TFIDF(dic):
    vocab=[]
    for k in dic:
        vocab.extend(dic[k][0].split(' '))
        
    vocab=list(set(vocab))


    df={}
    for v in vocab:
        df[v]=0
    for k in dic:
        wordList=list(set(dic[k][0].split(' ')))
        for d in wordList:
            df[d]=df[d]+1 
    idf=copy.deepcopy(df)        
    for d in df:
        idf[d]=math.log(len(dic)/float(df[d]))
        
    tf={}
    for k in dic:
        tf[k]={}
        wordList=list(set(dic[k][0].split(' ')))
        for w in wordList:
            tf[k][w]=0
        wordList=list(set(dic[k][0].split(' ')))
        for w in wordList:
            tf[k][w]=tf[k][w]+1
    tfidf={}        
    for k in dic:
        tfidf[k]={}
        wordList=list(set(dic[k][0].split(' ')))
        wordLen=len(list(dic[k][0].split(' ')))
        for w in wordList:
            tfidf[k][w]=idf[w]*tf[k][w]/wordLen
    return(tfidf)
'''
retreives relevant ranked
'''
def retrieval(k,tfidf):
    scores={}
    for t in tfidf:
        if t!=k:
            candidateKey=list(tfidf[t].keys())
            zebKeys=list(tfidf[k].keys())
            keys=list(set(zebKeys).intersection(set(candidateKey)))
            num=0
            for c in keys:
                num=num+tfidf[t][c]*tfidf[k][c]
            ssq1 = np.linalg.norm(np.array(list(tfidf[t].values())))
            ssq2 = np.linalg.norm(np.array(list(tfidf[k].values())))
            
            denom=ssq1*ssq2
            scores[t]=num/denom
    relevance=sorted(scores.items(),key=operator.itemgetter(1),reverse=True)       
    return(relevance)
    
'''
spellcheck
'''
#'\b[A-Z]+,'

import numpy as np
#html=downloadDictionary()
#saveDictionary(html,'hobsonRaw')
text=loadDictionary('hobson2.txt')
#hobson=extractDictionary(html)
jobson=generateCandidates(text)
newCandidates=jobson[2][jobson[0]:jobson[1]]
items=extractItems(jobson[0],jobson[1],jobson[2],text)
processed=cleanItems(items)
preTfIdf=removePunctuations(processed)
tfidf=TFIDF(preTfIdf)
k='zebu'
R=retrieval(k,tfidf)     
