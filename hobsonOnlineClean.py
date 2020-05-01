import pickle
import requests
import re
import copy
import math
import operator
import json
import re
import numpy as np
import json

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
hobson=pickle.load(open("parrot.pkl","rb"))
stop_words = set(stopwords.words('english')) 
total=0
missing=0
jobson={}
jobson2={}
for h in hobson:
    row=h.split('</span>')
    if len(row[0])<2:
        missing=missing+1
    else:
        entry=row[0].replace(',','.').split('.')[0].strip(' ')
        T=row[1].strip('\t').replace('&nbsp;&nbsp;','').strip('\n').strip('\t').strip(' ').strip('\n').strip(',').strip(' ').replace('</i>','<i>').replace('</b>','<b>').replace('<i>','').replace('</b>','<b>').replace('<b>','').replace('<p>','').split('</p>')[0]
        T=re.sub("[\<].*?[\>]", "", T)
        jobson[entry.lower()]=[row[0],T.lower()]
        T=row[1].strip('\t').replace('&nbsp;&nbsp;','').strip('\n').strip('\t').strip(' ').strip('\n').strip(',').strip(' ').replace('</i>','<i>').replace('</b>','<b>').replace('<i>','').replace('</b>','<b>').replace('<b>','').replace('<p>','').replace('</p>','\n')
        T=re.sub("[\<].*?[\>]", "", T)
        jobson2[entry.lower()]=T
    total=total+1
    
'''
Removes Punctuations from definitions
'''    
def removePunctuations(dic):
    newDic={}
    for k in dic:
        temp=re.sub(r'[^\w\s]','',dic[k][1])
        word_tokens = word_tokenize(temp) 
  
        filtered_sentence = [w for w in word_tokens if not w in stop_words and len(w)>1]
        if len(filtered_sentence)>20:
            newDic[k]=' '.join(filtered_sentence)
    return(newDic)
    
'''
TFIDF

'''

def TFIDF(dic):
    vocab=[]
    for k in dic:
        try:
            vocab.extend(dic[k].split(' '))
        except:
            print(k)
            print(L)
    vocab=list(set(vocab))


    df={}
    for v in vocab:
        if v.isnumeric()==False:
            df[v]=0
    for k in dic:
        wordList=list(set(dic[k].split(' ')))
        for d in wordList:
            if d in df:
                df[d]=df[d]+1 
    idf=copy.deepcopy(df)        
    for d in df:
        idf[d]=math.log(len(dic)/float(df[d]))
        
    tf={}
    for k in dic:
        tf[k]={}
        wordList=list(set(dic[k].split(' ')))
        for w in wordList:
            if w in df:
                tf[k][w]=0
        wordList=list(set(dic[k].split(' ')))
        for w in wordList:
            if w in df:
                tf[k][w]=tf[k][w]+1
    tfidf={}        
    for k in dic:
        tfidf[k]={}
        wordList=list(set(dic[k].split(' ')))
        wordLen=len(list(dic[k].split(' ')))
        for w in wordList:
            if w in df:
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
    
preTfIdf=removePunctuations(jobson)
tfidf=TFIDF(preTfIdf)
K=['zebu','zobo','yak','buffalo','banana','lumberdar']
for k in K:
    retr=[]
    R=retrieval(k,tfidf)     
    for r in R:
        #if r[1]>0.06:
        retr.append(r)
    print(k,retr[:10])
    
with open('tfidf.json', 'w') as json_file:
    json.dump(tfidf, json_file)    
        
with open('hobsonJobson.json', 'w') as json_file:
    json.dump(jobson2, json_file)         