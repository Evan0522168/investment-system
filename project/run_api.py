import uvicorn
import os
import sys
import traceback

try:
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting API on port {port}", flush=True)
    uvicorn.run("api.main:app", host="0.0.0.0", port=port)
except Exception as e:
    print(f"STARTUP ERROR: {e}", flush=True)
    traceback.print_exc()
    sys.exit(1)
