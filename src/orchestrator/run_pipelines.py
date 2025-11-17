import sys
from run_phase1 import run_phase1
from run_phase2 import run_phase2

def main():
    print("\n==============================")
    print(" ALPHASIGNAL FULL PIPELINE")
    print("==============================\n")

    run_phase1()
    run_phase2()

    print("\n FULL PIPELINE SUCCESSFULLY COMPLETED!\n")

if __name__ == "__main__":
    main()
