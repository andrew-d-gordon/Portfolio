'''
Created on Feb 24, 2019
Work in Progress, can successfully encode and decode files.
Needs encoded to be transferred to bit representation of encoding and traversal in order to compress.
@author: Gordon
'''
import sys

class Node:
    rc,lc,key = None,None,None
    def __init__(self,key):
        self.rc = None
        self.lc = None
        self.key = key
   
'''To encode: Make a small tree first with root node.
     Make a new root node and then set that to 
     be the head of the smaller bst, and add 
     left child to be next biggest probability. Continue
     this process til all characters have been accounted for.'''
                    
def encode(message):
    '''if all characters are possible, rework array to be in range of all possible ascii characters'''
    '''make a frequency array which keeps track of all the characters frequencies'''
    frequencyarray = [[0 for x in range(2)] for y in range(255)]
    charactertotal = 0
    for i in enumerate(message):
        frequencyarray[ord(i[1])][1]+=1
        if frequencyarray[ord(i[1])][0] == 0:
            frequencyarray[ord(i[1])][0] = i[1]
    #print(charactertotal)   
        
    '''sort the array in increasing order, then create charlist
    to hold character frequencies from smallest to biggest'''
    frequencyarray.sort(key=lambda x: x[1])
    charlist = ""
    j=0
    for i in range(len(frequencyarray)):
        if frequencyarray[i][0] != 0:
            charlist+=frequencyarray[i][0]
    print(charlist, "<--charlist")
    
    '''now we will build tree adding smaller trees of probability,
     starting from leftmost end in charlist'''
    rootofsmalltree = None
    realroot = None
    for i in range(len(charlist)):
        if len(charlist)==1:
            #print("1 character case in encode")
            n=Node(None)
            n.lc=Node(charlist[i][0])
            realroot = n
        elif i == 0:
            #print("first run")
            n = Node(None)
            n.rc = Node(charlist[i][0])
            n.lc = Node(charlist[i+1][0])
            rootofsmalltree = n
            if len(charlist)==2:
                realroot = n
        elif i<len(charlist)-1:
            n = Node(None)
            n.rc = rootofsmalltree
            n.lc = Node(charlist[i+1][0])
            rootofsmalltree = n
            #print(charlist[i+1][0], "<--")
            if i == len(charlist)-2:
                realroot = n
    #print(realroot.lc.key)
    #print(realroot.key, "<-- bst root key,", realroot.rc.key, "<-- should be none", realroot.lc.key, "<-- should not be none")
    #print(realroot.rc.lc.key, "<-- should not be none")
    '''Now that we have our tree, we have to construct encoded message'''
    encodedmessage = ""
    
    for i in enumerate(message):
        found = False
        findernode = realroot
        while(found!=True):
            if findernode.lc.key == i[1]:
                encodedmessage+=str(0)
                found = True
            elif findernode.rc.key == i[1]:
                encodedmessage+=str(1)
                found = True
            else:
                encodedmessage+=str(1)
                findernode = findernode.rc
    encodedmessage+=' '
    encodedmessage+=charlist
    #print(' '.join(format(ord(x), 'b') for x in charlist))
    #map(bin, bytearray(encodedmessage))
    #st = "hello world"
    #' '.join(format(x, 'b') for x in bytearray(st))
    #print(st)
    #print(encodedmessage)
    #print(encodedmessage)
    #print("{0:b}".format(10))
    #print(encodedmessage)
    return(encodedmessage)

    
'''To decode: take in binary message, if 0, move to left child,
if 1, move to right child, once you have found a character, reset
finder node to be the root of your bst again, then continue process
until message has been completely decoded.'''
def decode(encodedmessage):
    '''want to pull postorder from encodedmessage then build tree, then move 
    through our tree from tree root, by going to the left child when we see 
    a 0, and going to a right child when we see a 1 until we find a letter,
    then we start back from the top repeat until we have found all of the letters'''
    
    '''pull out postorder traversal from encodedmessage'''
    postordertraversal = ""
    postorderstartfound = False
    i=0
    endofencoded=0
    while postorderstartfound==False:
        #looks for last entry of encodedmessage (postorder stored at end of passedmessage)
        endofencoded+=1
        if encodedmessage[i] == ' ':
            #print("found space")
            postorderstartfound=True
        #print(encodedmessage[i])
        i=i+1
    postordertraversal = encodedmessage[endofencoded:]
    #print(postordertraversal, "<--postordertraversal in decode")
    #print(encodedmessage[endofencoded])
    #print(len(postordertraversal)+2)
    
    '''now we will build tree adding smaller trees of probability,
     starting from leftmost end in postordertraversal message'''
    rootofsmalltree = None
    realroot = None
    for i in range(len(postordertraversal)):
        #print(i, "<-- i in building tree")
        if len(postordertraversal)==1:
            #print("1 character case in decode")
            n=Node(None)
            n.lc=Node(postordertraversal[i][0])
            realroot = n
        elif i == 0:
            #print(i, "<-- i in building tree")
            n = Node(None)
            n.rc = Node(postordertraversal[i][0])
            #print(postordertraversal[i][0], "<--tree bottom leftmost right node")
            n.lc = Node(postordertraversal[i+1][0])
            #print(postordertraversal[i+1][0], "<--tree bottom rightmost left node")
            rootofsmalltree = n
            if len(postordertraversal)==2:
                realroot = n
        elif i<len(postordertraversal)-1:
            n = Node(None)
            n.rc = rootofsmalltree
            n.lc = Node(postordertraversal[i+1][0])
            #print(postordertraversal[i+1][0], "<--added to tree on the left")
            rootofsmalltree = n
            #print(postordertraversal[i+1][0], "<--")
            if i == len(postordertraversal)-2:
                realroot = n
    #print(realroot.key, "<-- head root of tree")
                
    findernode = realroot
    decodedmessage = ""
    #print(findernode.rc.lc.key, findernode.rc.rc.lc.key)
    for i in range(0, endofencoded):
        #print(i[1])
        #print(findernode.lc.key)
        #print(encodedmessage[i])
        if encodedmessage[i] == ("1"):
            findernode = findernode.rc
            if findernode.key != None:
                decodedmessage+=findernode.key
                findernode = realroot
        elif encodedmessage[i] == '0':
            findernode=findernode.lc
            decodedmessage+=findernode.key
            findernode=realroot
    #print(decodedmessage, "<--decodedmessage")
    return(decodedmessage)

if __name__ == '__main__':
    '''#globals()[sys.argv[1]]
    script_name = sys.argv[0]
    fi = open(sys.argv[2], "r")
    fidata = fi.read().replace('\n', '')
    sys.argv[3].write(globals()[sys.argv[1]](fidata))'''
    pass
    
#message = "heyo let us get this bread brethren 9%#wE6t"
testmessage="a b c d e f g h i j k l m n o p... :;][\.,o129385089uoiquwet$^&*&^%$#@!"
encodedmessage = encode(testmessage)
print("encoded message:", encodedmessage)
print("decoded message:", decode(encodedmessage))
