import winsound
import time

def play_beep():
    # Speed breaker alert - Long urgent beep pattern
    print("SPEED BREAKER AHEAD!")
    # Pattern 1: Long urgent warning beep
    winsound.Beep(800, 1800)  # Low frequency, long duration (1.5 seconds)

if __name__ == "__main__":
    play_beep()



