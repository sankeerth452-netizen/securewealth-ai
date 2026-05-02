import time

USER_HISTORY = {
    "avg_transaction": 20000.0,
    "last_transactions": [],
    "login_time": None,
    "trusted_device": True
}

def init_login_time():
    if USER_HISTORY["login_time"] is None:
        USER_HISTORY["login_time"] = time.time()
        print(f"[DEBUG] USER_HISTORY login_time initialized: {USER_HISTORY['login_time']}")

def add_transaction(amount: float):
    USER_HISTORY["last_transactions"].append(amount)
    
    # Keep only last 10
    if len(USER_HISTORY["last_transactions"]) > 10:
        USER_HISTORY["last_transactions"].pop(0)
    
    # Update avg as mean
    if USER_HISTORY["last_transactions"]:
        USER_HISTORY["avg_transaction"] = sum(USER_HISTORY["last_transactions"]) / len(USER_HISTORY["last_transactions"])
    
    print(f"[DEBUG] Updated USER_HISTORY. avg_transaction: {USER_HISTORY['avg_transaction']:.2f}, last_transactions: {USER_HISTORY['last_transactions']}")
