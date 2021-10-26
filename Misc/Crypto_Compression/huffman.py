'''
Created on Feb 24, 2019

@author: Gordon
'''
import sys

class Node:
    rc,lc,key = None,None,None
    def __init__(self,key):
        self.rc = None
        self.lc = None
        self.key = key
   
'''To encode: Make list of most frequent nodes, build huffman tree by
taking two smallest and making them leaves of a root node that is null.
Next make a new root node where you add the tree you just made as the right
child, and the next most likely char as the left child. Do this until
tree is complete. Then go through tree encoding your actual message with
moves to the left as 0s, and moves through the tree to the right as 1s. Next
encode your sequence of 1s and 0s as bits, convert every 8 into an ascii
char which helps to compress, add postorder traversal and leftover 1s and 0s, to the end.'''
                    
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
    #print(charlist, "<--charlist")
    
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
    '''add 1s and 0s to bitstring until it is of length 8 (i.e. bitcount is 8),
     then add chr(int(string, base=2)) to encoded'''
    encodedmessage = ""
    bitstring = ''
    bitcount=0
    asciicharcount = 0
    for i in enumerate(message):
        found = False
        findernode = realroot
        #print("bitcount at top:", bitcount)
        #print("bitstring at top:", bitstring)
        if bitcount == 8:
            #print("adding bitstring")
            encodedmessage+=chr(int(bitstring, base=2))
            bitcount = 0
            bitstring = ''
            asciicharcount+=1
        while(found!=True):
            if findernode.lc.key == i[1]:
                bitstring+='0'
                bitcount+=1
                #print("bitcount:", bitcount)
                #print("bitstring in left child:", bitstring)
                found = True
                if bitcount == 8:
                    #print("adding bitstring:", bitstring)
                    encodedmessage+=chr(int(bitstring, base=2))
                    bitcount = 0
                    bitstring = ''
                    asciicharcount+=1
            elif findernode.rc.key == i[1]:
                bitstring+='1'
                bitcount+=1
                #print("bitcount:", bitcount)
                #print("bitstring in right child:", bitstring)
                found = True
                if bitcount == 8:
                    #print("adding bitstring:", bitstring)
                    encodedmessage+=chr(int(bitstring, base=2))
                    bitcount = 0
                    bitstring = ''
                    asciicharcount+=1 
            else:
                bitstring+='1'
                findernode = findernode.rc
                bitcount+=1
                #print("bitcount:", bitcount)
                #print("bitstring so far:", bitstring)
                if bitcount == 8:
                    #print("adding bitstring:", bitstring)
                    encodedmessage+=chr(int(bitstring, base=2))
                    bitcount = 0
                    bitstring = ''
                    asciicharcount+=1
    #print(encodedmessage, "this is encodedmessage with charlist")  
    #print("done adding ascii characters to message, there are:", asciicharcount, "characters")
    #print(encodedmessage, "this is encodedmessage with charlist")          
    if bitcount!=0:
        #left over bitstring added to the end
        encodedmessage+=bitstring
    #add space between message and  charlist (post order trav.)          
    encodedmessage+=' '
    encodedmessage+=charlist
    return(encodedmessage)

    
'''To decode: take in ascii encoded message, make it binary (with postorder
 traversal at end, rebuild tree from postorder, then rebuild message and
 return it.'''
def decode(encodedmessage):  
    encoded = ""
    messageend = 0
    done = False
    '''recovering message from mostly masked representation'''
    for x in range(len(encodedmessage)):
        if encodedmessage[x]==' ':
            break
        elif encodedmessage[x] == '1':
            encoded+='1'
            messageend+=1
        elif encodedmessage[x] == '0':
            encoded+='0'
            messageend+=1
        else:
            #print("ord(x[1])):", ord(encodedmessage[x]))
            oldtxt = bin(ord(encodedmessage[x]))
            for i in range(0,8-len(oldtxt[2:])):
                encoded+='0'
            encoded+=oldtxt[2:]
            messageend+=1
                
    encoded+=encodedmessage[messageend:]
    #print(encoded)

    '''pull out postorder traversal from encoded'''
    postordertraversal = ""
    postorderstartfound = False
    i=0
    endofencoded=0
    while postorderstartfound==False:
        #looks for last entry of encodedmessage (postorder stored at end of passedmessage)
        endofencoded+=1
        if encoded[i] == ' ':
            #print("found space")
            postorderstartfound=True
        #print(encodedmessage[i])
        i=i+1
    postordertraversal = encoded[endofencoded:]
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
        if encoded[i] == ("1"):
            findernode = findernode.rc
            if findernode.key != None:
                decodedmessage+=findernode.key
                findernode = realroot
        elif encoded[i] == '0':
            findernode=findernode.lc
            decodedmessage+=findernode.key
            findernode=realroot
    #print(decodedmessage, "<--decodedmessage")
    return(decodedmessage)

if __name__ == '__main__':
    #globals()[sys.argv[1]]
    script_name = sys.argv[0]
    fi = open(sys.argv[2], "r")
    fidata = fi.read().replace('\n', '')
    fo = open(sys.argv[3], "w")
    fo.write(globals()[sys.argv[1]](fidata))
    pass

#test input   
'''testmessage="a b c d e f g h i j k l m n o p... :;][\.,o129385089uoiquwet$^&*&^%$#@!"
encodedmessage = encode(testmessage)
#("encoded message:", encodedmessage)
print("decoded message:", decode(encodedmessage))'''
