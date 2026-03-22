import sys
import traceback

sys.path.insert(0, ".")

try:
    import tests.test_habit
    print("SUCCESS")
except Exception as e:
    with open("error.log", "w") as f:
        traceback.print_exc(file=f)
