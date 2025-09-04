import time
from lib.display.touch import Touch

def main():
    """Main application loop."""
    print("Starting Touch example...")
    
    # Create an instance of the Touch class.
    # The initialization and interrupt setup is handled internally.
    touch = Touch()
    
    while True:
        if touch.read():
            print("Touch detected!")
        
        time.sleep_ms(50)

if __name__ == "__main__":
    main()
