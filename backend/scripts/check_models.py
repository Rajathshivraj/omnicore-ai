import sys
import traceback

sys.path.insert(0, r"d:\Projects\omnicore-ai\omnicore-ai\backend")

try:
    import app.db.models
    print('OK: app.db.models imported')
except Exception as e:
    print('IMPORT ERROR:', type(e).__name__, e)
    traceback.print_exc()
