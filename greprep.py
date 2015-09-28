import re
import urllib
import HTMLParser
import os.path
import random

html_parser = HTMLParser.HTMLParser()
meanings = {}

def getWordDescAndMeaning(word):
    desc = ""
    meaning = ""
    page = urllib.urlopen(baseurl + word)
    pagestring = ""
    for lines in page.readlines():
        pagestring = pagestring + " " + lines
    pagestring = re.sub(r'\s+', ' ', pagestring)
    extracted = re.findall('og:description"\scontent=".*?"', pagestring)
    if not len(extracted) == 0:
        desc = html_parser.unescape ( extracted[0][25:-1].decode('utf-8') )
    meaningsstring = re.findall('class="definition".*?h3', pagestring)
    if len ( meaningsstring ) == 0:
        return ["",""]
    for mstring in meaningsstring:
        meanings = re.findall('a>.*?/h3', mstring)
        for m in meanings:
            toadd = m[2:-4].strip()
            toadd = toadd[0].upper() + toadd[1:]
            toadd = html_parser.unescape ( toadd.decode('utf-8') )
            if meaning == "":
                meaning = toadd
            else:
                meaning = meaning + "; " + toadd
    return [desc,meaning]


def getDescAndMeanings(wordlist):
    toreturn = []
    count = 0
    for word in wordlist:
        count += 1
        dandm = getWordDescAndMeaning(word)
        toreturn.append([word, dandm[0]])
        meanings [ word ] = dandm[1]
        print "Done with " + word + " (" + str(count) + "/" + str(len(wordlist)) + ")"
    print ( "" )
    return toreturn


baseurl = "http://www.vocabulary.com/dictionary/"
wordlist = []

if not os.path.isfile ( "worddata.dat" ):
    inpf = open('wordlist.txt')
    for line in inpf:
        line = line.strip().lower()
        wordlist.append(line)
    
    f = open("worddata.dat", "w")
    fm = open("wordmeanings.dat", "w")
    print ( "Downloading word data from vocabulary.com..." )
    wordlist = getDescAndMeanings ( wordlist )
    for [word,desc] in wordlist:
        fm.write ( word + "$$$$" + meanings[word].encode('utf-8') + "\n" )
        word = word[0].upper() + word[1:]
        f.write( word + "$$$$" + desc.encode('utf-8') + "\n")
    f.close()
    fm.close()
else:
    fetchedwords = {}
    f = open("worddata.dat")
    for line in f:
        line = line.strip().split("$$$$")
        wordlist.append([line[0], line[1]])
        fetchedwords[line[0].lower()] = True
    f.close()
    fm = open("wordmeanings.dat")
    for line in fm:
        line = line.strip().split("$$$$")
        meanings[line[0]] = line[1]
    fm.close()
    
    print "Has the wordlist been modified since the last run? [yes/no] ",
    a = raw_input().strip().lower()
    if a == "yes":
        inpf = open("wordlist.txt")
        outf = open("worddata.dat", "a")
        meaf = open("wordmeanings.dat", "a")
        tofetch = []
        for line in inpf:
            line = line.strip().lower()
            if not line in fetchedwords:
                tofetch . append ( line )
        
        count = 0
        for line in tofetch:
            desc = getWordDescAndMeaning ( line )
            count += 1
            meanings[line] = desc[1]
            desc = desc[0]
            wordlist.append([line, desc])
            meanf.write( line + "$$$$" + meanings[line].encode('utf-8') + "\n" )
            line = line[0].upper() + line[1:]
            outf.write( line + "$$$$" + desc.encode('utf-8') + "\n" )
            print "Done with " + line + " (" + str(count) + "/" + str(len(tofetch)) + ")"
        inpf.close()
        outf.close()
        meanf.close()

def playFlashCards ():
    random.shuffle(wordlist)
    print ( "\nPressing enter reveals the next word/description. Type mark to mark the word for review and exit to exit at any time." )
    print ( "Press enter to continue.." )
    raw_input()
    count = 0
    marked = []
    for [word, desc] in wordlist:
        count += 1
        print str(count) + ". " + word + " : ",
        inp = raw_input().strip().lower()
        if inp == "exit":
            break
        elif inp == "mark":
            marked.append(word)
        print ( meanings[word.lower()] + "\n" )


    while len(marked) > 0:
        newmark = []
        print "\n" + str(len(marked)) + " words marked. Type exit at any time to exit."
        print "Press any key to continue..."
        raw_input()
        count = 0
        random.shuffle(marked)
        for word in marked:
            count += 1
            print str(count) + ". " + word + " : ",
            inp = raw_input().strip().lower()
            if inp == "exit":
                return
            elif inp == "mark":
                newmark . append ( word )
            print ( meanings[word.lower()] + "\n" )
        marked = newmark


def playQuiz (numq):
    random.shuffle(wordlist)
    score = 0
    count = 0
    print ( "\nFor each question, choose the word from the options that would best fit the blank / has the meaning given." )
    print ( "Press enter to continue" )
    raw_input()
    print ( "\n\n" )
    for [word, desc] in wordlist:
        if count == numq:
            break
        print str ( count + 1 ) + ". ",
        newdesc = re.sub(r'(' + word + r')', '______', desc)
        newdesc = re.sub(r'(' + word.lower() + r')', '______', newdesc)
        newdesc = newdesc[0].upper() + newdesc[1:]
        print ( newdesc.decode('utf-8') + "\n\n" )
        
        options = []
        options.append ( word )
        picked = { word : "True" }
        i = 0
        while i < 3:
            pick = wordlist[random.randint(0, len(wordlist) - 1)][0]
            if not pick in picked :
                options.append ( pick )
                picked [ pick ] = True
                i += 1
        random.shuffle ( options )
        
        ans = ""
        while ans == "" or int(ans) > 4:
             
            i = 1
            for choice in options:
                print str(i) + ") " + choice + "  ",
                i += 1
            for choice in options:
                print str(i) + ") Meaning of " + choice + "  ",
                i += 1
            print "9)  Exit to menu"
            
            print "\n\nYour choice: ",
            ans = raw_input().strip()
            if ans == "9":
                print ( "You scored " + str ( score ) + " out of " + str(count) + "\n" )
                return
            
            if len(ans) > 0 and int(ans) > 4:
                print options [ int(ans) - 5 ] + ": ",
                print meanings [ options [ int(ans) - 5 ] . lower() ] + "\n"
                continue
            
            if len(ans) > 0 and options [ int(ans) - 1 ] == word:
                print ( "Correct!" )
                score += 1
            else:
                print ( "Incorrect! The correct answer was " + word )
                for optindx in range(4):
                    print options[optindx] + ": " + meanings[options[optindx].lower()]

                print ( "Press enter to continue..." )
                raw_input ()
            
            print ( "\n\n" )
        
        count += 1
    
    print ( "You scored " + str ( score ) + " out of " + str(count) + "\n" )


def displayMeaning ( word, shouldAdd ):
    if word in meanings:
        print meanings[word].decode('utf-8') + "\n"
        return
    
    descandmeaning = getWordDescAndMeaning ( word )
    if len ( descandmeaning [0] ) == 0 :
        print "Word not found!\n"
    else:
        print "\nMeaning: " + descandmeaning [1] . decode('utf-8')
        print "\nSentence:\n" + descandmeaning [0] . encode('utf-8')
        
        if shouldAdd :
            meanings [ word ] = descandmeaning [1]
            f = open ("wordmeanings.dat", "a")
            fdesc = open ("worddata.dat", "a")
            fword = open ( "wordlist.txt", "a" )
            fword.write ( word.lower() + "\n" )
            f.write ( word + "$$$$" + descandmeaning [1] . encode('utf-8') + "\n" )
            word = word[0].upper() + word[1:]
            fdesc.write ( word + "$$$$" + descandmeaning [0] . encode('utf-8') + "\n" )
            f.close()
            fdesc.close()
            fword.close()

while True:
    
    print ( "\n\n" + ("-" * 14) + " Choose Game Mode " + ("-" * 14) + "\n" )
    print ( "1. Flash cards" )
    print ( "2. Quiz mode" )
    print ( "3. Display meaning" )
    print ( "4. Display meaning and add word" )
    print ( "5. Exit" )
    print "\n\nYour choice: ",
    
    choice = raw_input().strip()
    if choice == "1":
        playFlashCards()
    elif choice == "2":
        print "\nEnter the number of questions (or press enter for all " + str(len(wordlist)) + " questions): ",
        numq = raw_input().strip()
        if len ( numq ) > 0:
            numq = int ( numq )
        else:
            numq = -1
        playQuiz(numq)
    elif choice == "3":
        print "\nEnter your word: ",
        displayMeaning( raw_input().strip().lower(), False )
    elif choice == "4":
        print "\nEnter your word: ",
        displayMeaning( raw_input().strip().lower(), True )
    else:
        exit()

