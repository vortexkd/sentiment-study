#!/usr/bin/python

import re
import sys
import csv

word_db = {}      #stores encountered words and their probability in "word" : [pos,neg,neut] format.
tweet_spread = [] # count of positive, negative, and neutral/irrelevant tweets. 
positive = "positive"
negative = "negative"
neutral = "neutral"

def word_presence(text):
  #Need to split the string into words and punctuation.
  result = []
  words = re.findall("[A-z\-]+",text.lower())
  if words:
    for word in words:
      if word not in result:
        result.append(word)
  emoji = re.findall("(\(;|\(:|:\)|:P|:D|;\)|:-\)|=\)|\(=|T\.T|D:|:\(|\):)",text)
  if emoji:
    for emo in emoji:
      if emo not in result:
        result.append(emo)
  return result    #this returns the list of words that appear in a single tweet.


#for each line in file, call a function that checks the words in the line, and updates the dict from 
#{ word : [pos_val, neg_val, neut_val]} to have the incremented values. this is part of the learning.

#steps - read n tweets, create a data file.
#read a data file, create bayes list.

#these two just for convenience.
def get_type(word):
  if word == "positive":
    return 0
  elif word == "negative":
    return 1
  else:
    return 2
  return

def get_feel(num):
  if num == 0:
    return positive
  elif num == 1:
    return negative
  else:
    return "neutral or irrelevant"
  return

#misc.
def sort_key(key):
  return sum(word_db.get(key))

def learn(file_name):
  #use only for learning *new* tweets (else the weightage of the words would be a bit odd.
  #commented lines here can be used to reset data for learning.
  #global word_db
  #global tweet_spread
  #tweet_spread = [0,0,0]
  #word_db = {}
  file = open(file_name, "r")
  next(file)
  tweet_count = 0
  for line in file:
    data = line.split(",")
    if data[0] == "twitter":
      break;
    else:
      tweet_count += 1
      tweet_spread[get_type(data[1])] += 1
      for each in word_presence(' '.join(data[4:])):
        if each in word_db:
          word_db[each][get_type(data[1])] += 1
        else:
          word_db[each] = [0,0,0]
          word_db[each][get_type(data[1])] += 1
  print "Log : Tweets read: "+str(tweet_count)
  file.close()
  #record stuff here.
  record = open("word_data.txt","w")
  for key in sorted(word_db,key=sort_key,reverse=True):
    record.write(key+","+str(word_db.get(key)[0])+","+str(word_db.get(key)[1])+","+str(word_db.get(key)[2])+"\n")
  record.close()
  spread = open("tweet_spread.txt","w")
  spread.write(str(tweet_spread[0])+","+str(tweet_spread[1])+","+str(tweet_spread[2]))
  spread.close()
  return

def remember(db):
  #called when the program is run - reads the word_data and stores in word_db
  global tweet_spread
  file = open(db,"r")
  for line in file:
    data = line.strip().split(",")
    word_db[data[0]] = map(int,data[1:])
  file.close()
  spread = open("tweet_spread.txt","r")
  for line in spread:
    tweet_spread = map(int, line.strip().split(","))
  spread.close()
  return


def check_pos(word,check):
  #checks using naive bayes how much a word influences a tweet toward pos, neg, or neutral (based on value sent in by check)
  if word in word_db:
    p_type = tweet_spread[get_type(check)] / float(sum(tweet_spread)) #p(positive_tweet) | p(neg_tweet) | p(neut_tweet)
    p_word = sum(word_db.get(word)) / float(sum(tweet_spread))
    likelihood = float(word_db.get(word)[get_type(check)]) / tweet_spread[get_type(check)]
    posterior = likelihood * p_type / p_word
    return posterior
  else: #failsafe
    return 1
  return

def speculate(probs):
  #multiplies a list of probabilities given by check_pos. these values are generated for pos, neg and neut and then compared.
  if not probs: #failsafe if all words in the tweet have never been encountered.
    return 0
  confidence = probs.pop()
  while probs:
    new = probs.pop()
    confidence = confidence * new
  return confidence
    


def decide(tweet):
  words = word_presence(tweet) #returns list of the unique words and emojis in the tweet. (emoji list is non-exhaustive)
  pos_prob = []
  neg_prob = []
  neut_prob = []
  for word in words:
    #creates a list of posterior probabilities using naive bayes.
    pos_prob.append(check_pos(word,positive))
    neg_prob.append(check_pos(word,negative))
    neut_prob.append(check_pos(word,neutral))
  #multiplies those probabilities together.
  pos = speculate(pos_prob)
  neg = speculate(neg_prob)
  neut = speculate(neut_prob)
  #compares the end result and returns a category, pos, neg, or neut.
  if pos == 0 and neg == 0:
    return 2
  elif pos > neg:
    return 0
  else:
    return 1
  return


def test(filename):
  report = open("report.txt","w")
  file = open(filename)
  next(file)
  tweets = 0
  correct = 0
  for line in file:
    data = line.strip().split(",")
    if data[0] == "twitter": #test data is only "twitter" other tags have been used for learning and hence return unreasonably high accuracy values.
      tweets += 1
      if get_type(data[1]) == decide(' '.join(data[4:])):
        correct += 1
      else: #debugging:
        report.write("WRONG: \n")
        report.write(" ".join(data[4:]))
        report.write("\nDiagnosed as : "+get_feel(decide(' '.join(data[4:])))+"\nActually : "+data[1]+"\n-----------------------------------\n")
  print "ACCURACY : "+str(float(correct) / float(tweets))
  file.close()
  report.close()
  return

def main():
  args = sys.argv[1:]
  remember("word_data.txt")
  if not args:
    test("full-corpus-1.csv")
  else:
    if args[0] == "--learn":
      learn("full-corpus-1.csv")
    elif args[0] == "--test":
      #will test the tweet here and give breakdown.
      decide("*singing*! everytime  I  try  to leave something keeps  pulling me  back  (me  back) telling me  I  need  #Twitter & all that. lol  (:") 
    else:
      #well.
      test("full-corpus-1.csv") 
    
if __name__ == "__main__":
  main()