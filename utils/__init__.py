from datetime import datetime as dt

def get_now(tab=True):
    if tab:
        return dt.now().strftime("%Y-%m-%d %H:%M:%S") + "\t"
    else:
        return dt.now().strftime("%Y-%m-%d %H:%M:%S")