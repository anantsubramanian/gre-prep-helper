import re
import urllib
import HTMLParser
import os.path
import os
import random

html_parser = HTMLParser.HTMLParser()
meanings = {}
data = {}

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
wordgroups = []

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
        data [ word ] = desc
    f.close()
    fm.close()
else:
    fetchedwords = {}
    f = open("worddata.dat")
    for line in f:
        line = line.strip().split("$$$$")
        wordlist.append([line[0], line[1]])
        data [ line[0] ] = line[1]
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
            data [ line ] = desc
            print "Done with " + line + " (" + str(count) + "/" + str(len(tofetch)) + ")"
        inpf.close()
        outf.close()
        meanf.close()

if os.path.isfile("wordgroups.dat"):
    f = open("wordgroups.dat")
    for line in f:
        wordgroups.append(line.strip().split())
    f.close()
 

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

def deleteword ( todelete ):
    listfile = open ( "wordlist.txt" )
    descfile = open ( "worddata.dat" )
    meanfile = open ( "wordmeanings.dat" )
    lofile = open ( "wordlist.txt.out", "w" )
    dofile = open ( "worddata.dat.out", "w" )
    mofile = open ( "wordmeanings.dat.out", "w" )
    
    for line in listfile:
        if line.strip().lower() == todelete:
            continue
        lofile.write(line)
    
    for line in descfile:
        if line.strip().split("$$$$")[0].lower() == todelete:
            continue
        dofile.write(line)

    for line in meanfile:
        if line.strip().split("$$$$")[0].lower() == todelete:
            continue
        mofile.write(line)

    listfile.close()
    descfile.close()
    meanfile.close()
    lofile.close()
    dofile.close()
    mofile.close()

    os.remove("wordlist.txt")
    os.remove("worddata.dat")
    os.remove("wordmeanings.dat")

    os.rename("wordlist.txt.out", "wordlist.txt")
    os.rename("worddata.dat.out", "worddata.dat")
    os.rename("wordmeanings.dat.out", "wordmeanings.dat")


def playWordGroups(numq):
    random.shuffle(wordgroups)
    score = 0
    count = 0
    print ( "\nFor each question, choose the options which fall in the same word group as the blank / have the same meaning given." )
    print ( "Press enter to continue" )
    raw_input()
    print ( "\n\n" )
    curword = 0
    for worddesclist in wordgroups:
        if count == numq:
            break
        count += 1
        print str ( count ) + ". ",
        word = worddesclist [ random.randint(0, len(worddesclist)-1) ] . strip()
        desc = data [ word ]
        #newdesc = re.sub(r'(' + word + r')', '______', desc)
        #newdesc = re.sub(r'(' + word.lower() + r')', '______', newdesc)
        #newdesc = newdesc[0].upper() + newdesc[1:]
        #print ( newdesc.decode('utf-8') + "\n\n" )
        print ( word + "\n\n" )

        options = []
        picked = { word.lower() : True }
        true = {}
        i = 0
        for w in worddesclist:
            true [ w.lower() ] = True

        while i < 2:
            choice = worddesclist [ random.randint(0, len(worddesclist)-1) ]
            if not choice.lower() in picked:
                i += 1
                picked [ choice.lower() ] = True
                options.append(choice)
        
        i = 0
        while i < 3:
            choice = wordlist [ random.randint(0, len(wordlist)-1) ] [0]
            if not choice.lower() in picked:
                if not choice.lower() in true:
                    i += 1
                    picked [ choice.lower() ] = True
                    options.append(choice)

        i = 1
        random.shuffle(options)
        for option in options:
            print str(i) + ") " + option + "  ",
            i += 1
        print str(i) + ") Exit",
        
        print "\n\nEnter your choices: ",
        choices = [ int(a) for a in raw_input().strip().split() if len(a) > 0 ]

        allcorrect = True
        if len(choices) == 0:
           allcorrect = False
        elif len(choices) == 1 and choices[0] == len(options) + 1:
            return
        else:
            for choice in choices:
                if options[choice-1].lower() not in true:
                    allcorrect = False
                    break

        if not allcorrect:
            print "Incorrect!\n"
            print "The correct choices were: ",
            for c in options:
                if c.lower() in true:
                    print str(c) + " ",
            print "\nPress any key to continue...\n"
        else:
            print "Correct!\n\n"
        
        curword += 1
        


def addGroup():
    mfile = open ( "wordmeanings.dat", "a" )
    dfile = open ( "worddata.dat", "a" )
    gfile = open ( "wordgroups.dat", "a" )
    print "\nEnter the words you want to add to this group separated by spaces:\n"
    groupl = [ w.strip() for w in raw_input().strip().split() if len(w.strip()) > 0 ]
    count = 0
    groupstruct = []
    for word in groupl:
        if not word in meanings:
            dandm = getWordDescAndMeaning ( word )
            mfile.write ( word + "$$$$" + dandm[1].encode('utf-8') + "\n" )
            word = word[0].upper() + word[1:]
            dfile.write ( word + "$$$$" + dandm[0].encode('utf-8') + "\n" )
            data [ word ] = dandm[0]
            gfile.write( word + " " )
        word = word[0].upper() + word[1:]
        groupstruct.append(word)
        count += 1
        print "Done fetching " + word + " (" + str(count) + "/" + str(len(groupl)) + ")"

    gfile.write("\n")
    mfile.close()
    gfile.close()
    dfile.close()

    wordgroups.append(groupstruct)

while True:
    
    print ( "\n\n" + ("-" * 14) + " Choose Game Mode " + ("-" * 14) + "\n" )
    print ( "1. Flash cards" )
    print ( "2. Quiz mode" )
    print ( "3. Word groups" )
    print ( "4. Display meaning" )
    print ( "5. Display meaning and add word" )
    print ( "6. List words" )
    print ( "7. Delete word from list" )
    print ( "8. Add word group" )
    print ( "9. Exit" )
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
        print "\nEnter the number of questions (or press enter for all " + str(len(wordgroups)) + " questions): ",
        numq = raw_input().strip()
        if len ( numq ) > 0:
            numq = int ( numq )
        else:
            numq = -1
        playWordGroups(numq)
    elif choice == "4":
        print "\nEnter your word: ",
        displayMeaning( raw_input().strip().lower(), False )
    elif choice == "5":
        print "\nEnter your word: ",
        displayMeaning( raw_input().strip().lower(), True )
    elif choice == "6":
        count = 0
        for [word,tp] in wordlist:
            count += 1
            print str(count) + ". " + word
    elif choice == "7":
        print "\nEnter the word to be deleted: ",
        todelete = raw_input().strip()
        deleteword ( todelete )
    elif choice == "8":
        addGroup()
    else:
        exit()

