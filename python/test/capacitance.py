"""
Capacitance is formed fron double sided PCB.
There are two PCB slabs that sandwich the components between them.
Thus the PCB is both a structure to hold the components (relays and coils)
and is itself the capacitance.

Each slab is approx 1000pf, so maximum capacitance is around 2000p.
One slab is carved into 6 segments in a divide by 2 manner. Thus the
segments are, if they were accurately made and ignoring discounted parts:

Rounding up to power of 2 is the idealised progression. 
    1024pf
    512pf
    256pf
    128pf
    64pf
    32pf
    16pf

Measured values are:

    1010pf
    504pf
    281pf
    139pf
    79pf
    43pf
    24pf

These will be trimmed down to closer to the idealised values.

This gives capacitance values from (idealised) 16pf to 2024pf in 16pf steps (VERY APPROXIMATELY).
This means there are 128 capacitance steps.

"""

from time import sleep

# Maps relay to GPIO pins in BCM numbering scheme.
# Corresponding to relays 0 - 6 where 0 == 16pf and 6 == 1024pf
pinArray = [4,17,27,22,5,6,13]

# Cap value of each division
# Relay 0 = 16pf to relay 6 = 1024pf
capArray = [16,32,64,128,256,512,1024]

# calculated map of capacitance to relay activations
# This map should be 128 elements long.
# i.e. {cap-value : [rel, rel, ..], cap-value ...}
actMap = {}

def makeActMap():
    
    # Iterate every capacitance size
    for c in range(16,2048,16):
        if c in capArray:
            # Exact value
            rly = capArray.index(c)
            actMap[c] = [rly,]
        else:
            # Find combination to give correct capacitance
            acc = []
            remC = c
            while True:
                
                # Find the highest capacitance value which is an integral
                nextC = highCap(remC)
                if nextC == 0:
                    break
                else:
                    acc.append(nextC)
                    remC = remC-nextC
            rlys = []
            for v in acc:
                rlys.append(capArray.index(v))
            actMap[c] = rlys
        
        #print(actMap)
        # checkit
        acc = 0
        for v in actMap[c]:
           acc = acc + capArray[v]
        if acc != c:
            print("Error, expected %d, got %d" % (c, acc))
            return
    
def highCap(c):
    if c == 0: return 0
    # Find highest value cap for this C
    last = 0
    for v in reversed(capArray):
        if v/c <= 1.0:
            return v
    return 0
    
# Entry point
if __name__ == '__main__':
    makeActMap()