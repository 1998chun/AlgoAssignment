import time
import os
from RabinKarp import RabinKarp
import json

class article:
    #read file and store each words in a list named text


    def __init__(self, filename, cityName, text):
        text_file=open(filename,"r")
        self.__words = text_file.read().lower().split()
        text_file.close()
        self.__noStopWords = self.__words[:]
        self.__freqN = 0
        self.__freqP = 0
        self.data = None
        self.cityName = cityName
        self.text = text
        self.getNoStopWords()
        try:
            with open(os.path.dirname(os.path.abspath(__file__))+"/Webpage_txt/"+self.text+'.json') as json_file:  
                self.data = json.load(json_file)
                json_file.close()
            self.__freqN = self.data['N']
            self.__freqP = self.data['P']
        except:
            pass

    #count number of words
    def getTotal(self, list):
        return len(list)

    #return dictionary
    def getWords(self, list):
        words= {}
        for x in list:
            words[x] = words.get(x,0) + 1
        return words

     #Total num of words in file b4 removing stop words
    def getOriTotal(self):
        return self.getTotal(self.__words)

    #dictionary of all words b4 removing stop Words
    def getOriWords(self):
        return self.getWords(self.__words)

     #Total num of words in file b4 removing stop words
    def getNoStopTotal(self):
        self.__noStopWords = self.__removeStop(self.__noStopWords)
        #print(self.__noStopWords)
        return self.getTotal(self.__noStopWords)

    #dictionary of all words b4 removing stop Words
    def getNoStopWords(self):
        self.__noStopWords = self.__removeStop(self.__noStopWords)
        return self.getWords(self.__noStopWords)

    def getPolarity(self):
        polarity = (self.__freqP - self.__freqN)/self.getOriTotal()
        return polarity

    def getPosCount(self):
        return self.__freqP

    def getNegCount(self):
        return self.__freqN

    def __removeStop(self,list):
        # q = self.primeNum()
        # store a list of stop words
        stopWords = []
        ROOT = os.path.dirname(os.path.abspath(__file__))
        text_file=open(ROOT+"/Webpage_txt/stop_words.txt","r")
        stopWords = text_file.read().lower().split()
        text_file.close()
        #remove stop words 1 by 1
        for x in stopWords:
            self.search(x,list)
        return list

    #search using Rabin-Karp Algorithm
    def search(self, pattern, list):
        for j in list:
            text_hash = RabinKarp(j, len(j))
            pattern_hash = RabinKarp(pattern, len(pattern))

            for i in range(len(j) - len(pattern) + 1):
                if text_hash.hash == pattern_hash.hash:
                    if text_hash.window_text() == pattern:
                        list.remove(j)

    def tempSearch(self, pattern, list):
        for j in list:
            text_hash = RabinKarp(j, len(j))
            pattern_hash = RabinKarp(pattern, len(pattern))

            for i in range(len(j) - len(pattern) + 1):
                if text_hash.hash == pattern_hash.hash:
                    if text_hash.window_text() == pattern:
                        return True
        return False


    def calculateWords(self):
        print('\tCalculating word...')
        self.data = {}
        ROOT = os.path.dirname(os.path.abspath(__file__))
        #Negative words
        text_file=open(ROOT+"/Webpage_txt/Negative Words Reference.txt","r")
        neg_words = text_file.read().lower().split()
        text_file.close()

        #positive words
        text_file=open(ROOT+"/Webpage_txt/Positive Words Reference.txt","r")
        pos_words = text_file.read().lower().split()
        text_file.close()
        #check all the words in the articles
        for i in self.__noStopWords:
            if(self.tempSearch(i,pos_words) == True):
                print('\t ++ '+str(i))
                self.__freqP += 1
            elif(self.tempSearch(i,neg_words) == True) :
                print('\t -- '+str(i))
                self.__freqN += 1
        self.data['N'] = self.__freqN
        self.data['P'] = self.__freqP
        with open(os.path.dirname(os.path.abspath(__file__))+"/Webpage_txt/"+self.text+'.json', 'w') as outfile:  
            json.dump(self.data, outfile)
            outfile.close()
