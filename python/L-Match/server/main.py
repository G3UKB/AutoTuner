import sys
import capacitance
import inductance

try:
    # Main loop for ever
    capacitance.init()
    inductance.init()
    
    while True:
       v = input("Cap 0-127?")
       capacitance.set_value(int(v))
       v = input("Inductance 0-4?")
       inductance.set_value(int(v))
        
except KeyboardInterrupt:
    sys.exit(0)
            