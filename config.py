# Auto Check-in Configuration File
# Modify the following configuration to suit your environment
#
# Third-party notice: the check-in implementation scripts referenced below come from
# upstream projects. See THIRD_PARTY_NOTICES.md for sources, authors and licenses.
#   - trae-daily-checkin       : https://github.com/BlueChonk/trae-daily-checkin
#   - workbuddy-checkin        : https://github.com/GitOfUser/workbuddy-checkin

# ============================================================
# Application Path Configuration
# ============================================================

# Trae SOLO CN path
# Default: C:\Users\Administrator\AppData\Local\Programs\TRAE SOLO CN\TRAE SOLO CN.exe
TRAE_EXE = r"C:\Users\Administrator\AppData\Local\Programs\TRAE SOLO CN\TRAE SOLO CN.exe"

# WorkBuddy path
# Default: C:\Users\Administrator\AppData\Local\Programs\WorkBuddy\WorkBuddy.exe
WORKBUDDY_EXE = r"C:\Users\Administrator\AppData\Local\Programs\WorkBuddy\WorkBuddy.exe"

# ============================================================
# Check-in Script Path Configuration
# ============================================================

# Trae check-in script path (usually no need to modify)
# Vendored from https://github.com/BlueChonk/trae-daily-checkin (MIT)
TRAE_CHECKIN_SCRIPT = r"D:\agents_project\auto_sign\trae-daily-checkin\src\auto-checkin.mjs"

# WorkBuddy check-in script path (usually no need to modify)
# Vendored from https://github.com/GitOfUser/workbuddy-checkin
WORKBUDDY_CHECKIN_SCRIPT = r"D:\agents_project\auto_sign\workbuddy-checkin\scripts\checkin_py.py"

# ============================================================
# Check-in Coordinate Configuration (WorkBuddy only)
# ============================================================

# WorkBuddy user menu coordinates (1920x1080 resolution)
WORKBUDDY_MENU_X = 207
WORKBUDDY_MENU_Y = 983

# WorkBuddy check-in button coordinates (1920x1080 resolution)
WORKBUDDY_CHECKIN_X = 93
WORKBUDDY_CHECKIN_Y = 566

# ============================================================
# Timeout Configuration (seconds)
# ============================================================

# Trae check-in timeout
TRAE_TIMEOUT = 120

# WorkBuddy check-in timeout
WORKBUDDY_TIMEOUT = 60

# Wait time between check-in tasks
WAIT_BETWEEN_TASKS = 5
