import sys
import traceback

sys.path.insert(0, ".")

try:
    import tests.test_habit  # noqa: F401
    print("SUCCESS")
except Exception:
    with open("error.log", "w") as f:
        traceback.print_exc(file=f)
