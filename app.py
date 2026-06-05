import subprocess
import sys
import time


SITES = [
    ("ShopMart", "sites/shopmart.py", 8101),
    ("TripNest", "sites/tripnest.py", 8102),
    ("InkPress", "sites/inkpress.py", 8103),
    ("FrameShare", "sites/frameshare.py", 8104),
    ("GadgetHub", "sites/gadgethub.py", 8105),
    ("CloudDesk", "sites/clouddesk.py", 8106),
    ("FitTrack", "sites/fittrack.py", 8107),
    ("LearnBoard", "sites/learnboard.py", 8108),
    ("BookBarn", "sites/bookbarn.py", 8109),
    ("NewsNest", "sites/newsnest.py", 8110),
    ("CouponBee", "sites/couponbee.py", 8111),
]


def main():
    processes = []
    print("Starting TargetWeb independent sites:")
    for name, script, port in SITES:
        proc = subprocess.Popen([sys.executable, script])
        processes.append((name, port, proc))
        print(f"- {name}: http://127.0.0.1:{port}")
    print("\nPress Ctrl+C to stop all sites.")
    try:
        while True:
            time.sleep(1)
            for name, port, proc in processes:
                if proc.poll() is not None:
                    raise RuntimeError(f"{name} on port {port} exited with code {proc.returncode}")
    except KeyboardInterrupt:
        print("\nStopping sites...")
    finally:
        for _name, _port, proc in processes:
            if proc.poll() is None:
                proc.terminate()
        for _name, _port, proc in processes:
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()


if __name__ == "__main__":
    main()
