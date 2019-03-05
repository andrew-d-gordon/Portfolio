'''
Created on Feb 8, 2019

@author: Gordon
'''
from spellchecker import SpellChecker

if __name__ == '__main__':
    pass

spell = SpellChecker(distance=1)

# analyze the cipher text to break the substitution cipher
# return (plain text, cipher text alphabet)
# where cipher text alphabet(CA) is of the form {c1, c2, c3, c4, _, c6, _, ...}
# replace c3 with whatever character in the CA corresponds to c in the PA
# _ is used to denote any letter for which you are uncertain about
def decode(ciphertext):
    '''initializing average frequencies for letters in English alphabet
    based on graph in assignment document, first index left for spaces (most freq. char)'''
    avg_frequencies = [' ', 'e', 't', 'a', 'o', 'i', 'n', 's', 'h', 'r', 'd', 'l', 'c', 'u', 'm', 'w', 'f', 'g', 'y', 'p', 'b', 'v', 'k', 'j', 'x', 'q', 'z']
    #print(avg_frequencies)
    
    '''initializing array to mark frequencies of each letter, then initializing cipher text alphabet to have length of 27'''
    frequency_check = [[0 for x in range(2)] for y in range(27)]
    frequency_check[0][0] = ' '
    for i in range(26):
        frequency_check[i+1][0] = chr((i)+97)
        frequency_check[i+1][1] = 0
    
    ciphertext_alphabet = []
    for i in range(1, 28):
        ciphertext_alphabet.append(' ')
    ciphertext_alphabet[0] = ' '
    
    '''in section below I will count frequencies of spaces and letters, I will also check for
    where I have one letter words (which I know to be either a or i) and repeated letters which I 
    have to be (in plain text) ee, ss, ll, pp, or oo (zz possible but very unlikely)'''
    achar = ' '
    ichar = ' '
    schar = ' '
    lchar = ' '
    echar = ' '
    pchar = ' '
    ochar = ' '
    for x in range(len(ciphertext)):
        #find character spot in alphabet, go to frequency array and add one, if char is a space put it in last slot of freq array
        if(ord(ciphertext[x])!=32):
            #print(ord(i[1])-97)
            frequency_check[ord(ciphertext[x])-96][1]+=1
            #print(x[1], frequency_check[ord(ciphertext[x])-96][1])
        if ord(ciphertext[x])<97 or ord(ciphertext[x])>122:
            frequency_check[0][1]+=1
        #checking for one letter words to store to be recognized as either a or i
        if ciphertext[x-1] == ' ' and ciphertext[x+1] == ' ':
            if ichar == ' ' or achar == ' ':
                if ichar==' ':
                    ichar=ciphertext[x]
                    #print("ichar", ichar)
                if achar==' ' and ciphertext[x]!=ichar:
                    achar=ciphertext[x]
                    #print("achar", achar)
        #checking for repeated letters which could be either ee, ss, or ll
        elif x<len(ciphertext)-1:
            if ciphertext[x]==ciphertext[x+1]:
                if  (echar==' ' or schar == ' ' or lchar== ' ' or pchar==' ' or ochar== ' '):
                    if echar==' ':
                        echar=ciphertext[x]
                        #print("echar", echar)
                    elif schar==' ' and ciphertext[x]!=echar:
                        schar=ciphertext[x]
                        #print("schar", schar)
                    elif lchar==' ' and ciphertext[x]!=schar and ciphertext[x]!=echar:
                        lchar=ciphertext[x]
                        #print("lchar", lchar)
                    elif pchar==' ' and ciphertext[x]!=schar and ciphertext[x]!=echar and ciphertext[x]!=lchar:
                        pchar=ciphertext[x]
                        #print("pchar", pchar)
                    elif ochar==' ' and ciphertext[x]!=schar and ciphertext[x]!=echar and ciphertext[x]!=lchar and ciphertext[x]!=pchar:
                        ochar=ciphertext[x]
                        #print("ochar", ochar)
    
    '''sorting my frequency counter array in decreasing order'''         
    frequency_check.sort(key=lambda x: x[1])
    frequency_check.reverse()
    #print(frequency_check)
    
    '''next I will set the cipher text alphabet to resemble my
    avg_frequencies array in relation to my frequency counter array.
    Here I will also keep track of where I want to have a and i or e,s,l,p, or o
    to end up, and promptly swap them after.'''
    aswap = 0
    iswap = 0
    eswap = 0
    sswap = 0
    lswap = 0
    pswap = 0
    oswap = 0
    apos = 0
    ipos = 0
    epos = 0
    spos = 0
    lpos = 0
    ppos = 0
    opos = 0
    #fill in ciphertext_alphabet based on frequencies then after swap positioning to put a,i,l,s,e chars in right spot
    for i in range(1, len(ciphertext_alphabet)):
        #print(ciphertext_alphabet[ord(avg_frequencies[i])])
        ciphertext_alphabet[ord(avg_frequencies[i])-96]=frequency_check[i][0]
        #store indices of where to end up swapping a,i,e,s,l later on
        if i==ord(achar)-96:
            aswap=i
        if i==ord(ichar)-96:
            iswap=i
        if i==ord(echar)-96:
            eswap=i
        if i==ord(schar)-96:
            sswap=i
        if i==ord(lchar)-96:
            lswap=i
        if i==ord(pchar)-96:
            pswap = i
        if i==ord(ochar)-96:
            oswap = i
        #finding where a ended up after filling based on frequencies then, storing position to swap    
        if ciphertext_alphabet[ord(avg_frequencies[i])-96] == 'a':
            apos = ord(avg_frequencies[i])-96
        #finding where i ended up after filling based on frequencies then storing position to swap     
        if ciphertext_alphabet[ord(avg_frequencies[i])-96] == 'i':
            ipos = ord(avg_frequencies[i])-96
        #finding where e ended up after filling based on frequencies then, storing position to swap
        if ciphertext_alphabet[ord(avg_frequencies[i])-96] == 'e':
            epos = ord(avg_frequencies[i])-96
        #finding where s ended up after filling based on frequencies then, storing position to swap
        if ciphertext_alphabet[ord(avg_frequencies[i])-96] == 's':
            spos = ord(avg_frequencies[i])-96
        #finding where l ended up after filling based on frequencies then, storing position to swap
        if ciphertext_alphabet[ord(avg_frequencies[i])-96] == 'l':
            lpos = ord(avg_frequencies[i])-96
        #finding where p ended up after filling based on frequencies then, storing position to swap
        if ciphertext_alphabet[ord(avg_frequencies[i])-96] == 'p':
            ppos = ord(avg_frequencies[i])-96
        #finding where o ended up after filling based on frequencies then, storing position to swap
        if ciphertext_alphabet[ord(avg_frequencies[i])-96] == 'o':
            opos = ord(avg_frequencies[i])-96
    
    '''swapping all the actual positions of a,i,e,s,l, p or o with
    their more likely spots which were recorded in above loop '''       
    ciphertext_alphabet[apos] = ciphertext_alphabet[aswap]
    ciphertext_alphabet[aswap] = 'a'
    ciphertext_alphabet[ipos] = ciphertext_alphabet[iswap]
    ciphertext_alphabet[iswap] = 'i'
    ciphertext_alphabet[epos] = ciphertext_alphabet[eswap]
    ciphertext_alphabet[eswap] = 'e'
    ciphertext_alphabet[spos] = ciphertext_alphabet[sswap]
    ciphertext_alphabet[sswap] = 's'
    ciphertext_alphabet[lpos] = ciphertext_alphabet[lswap]
    ciphertext_alphabet[lswap] = 'l'
    ciphertext_alphabet[ppos] = ciphertext_alphabet[pswap]
    ciphertext_alphabet[pswap] = 'p'
    ciphertext_alphabet[opos] = ciphertext_alphabet[oswap]
    ciphertext_alphabet[oswap] = 'o'
    #print(ciphertext_alphabet)
    
    '''computing plain text with generated cipher text alphabet,
    then collecting misspelled words in my word string (resetting after each space'''
    plaintext = ""
    misspelled = []
    word=""
    for i in enumerate(ciphertext):
        if(ord(i[1])<97 or ord(i[1])>122):
            plaintext=plaintext+' '
            misspelled.append(word)
            word=""
        else:
            #print(ord(i[1])-96)
            plaintext=plaintext+ciphertext_alphabet[ord(i[1])-96]
            word=word+ciphertext_alphabet[ord(i[1])-96]
    misspelled = spell.unknown(misspelled)
    spell.distance=1
    '''for i in enumerate(misspelled):
        print(i, ":", spell.candidates(i[1]))
    print(misspelled)
    print(plaintext)
    #print(spell.candidates(plaintext))'''
    
    '''tuple to store plain text, and cipher text alphabet '''
    #plainAndCipher = (plaintext, ciphertext_alphabet)
    return(plaintext, ciphertext_alphabet)
    
'''ciphertext_alphabet = ['a','z','e','r','t','y','u','i','o','p','q','s','d','f','g','h','j','k','l','m','w','x','c','v','b','n']
ciphertext = "lgdtmodtl o ytts miam o ligwsr stm bgw ass qfgc miam mitkt ol a dgflmtk cioei iortl ztiofr mit zsaeqzgakr of esall zwm mitf om sggql rtth ofmg db tbtl citf o eafm ktdtdztk ciam dami o ad lwhhgltr mg zt masqofu azgwm afr o qfgc miam o ad fgm alltkmoxt tfgwui mg mtss bgw aslg om cgwsr zt uggr mg mtss bgw miam ciost ct al a mtaeiofu lmayy eakt azgwm bgw gwk lmwrtfml a uktam rtas ct aslg hkogkomont gwk laytmb yaoksb iouisb lg oy miol dgflmtk txtk rgtl zktaq gwm ykgd ztiofr mit zsaeqzgakr o coss zt kwffofu al yalm al o eaf gwm gy mit rggk maqofu arxafmaut gy mit yaem miam om coss utm gft gy bgw afr mitf zt mgg zwlb mg eialt dt"
plaintext = "sometimes i feel that i should let you all know that there is a monster which hides behind the blackboard in class but then it looks deep into my eyes when i cant remember what math i am supposed to be talking about and i know that i am not assertive enough to tell you also it would be good to tell you that while we as a teaching staff care about you our students a great deal we also prioritize our safety fairly highly so if this monster ever does break out from behind the blackboard i will be running as fast as i can out of the door taking advantage of the fact that it will get one of you and then be too busy to chase me"

print(decode(ciphertext))
print(plaintext)'''