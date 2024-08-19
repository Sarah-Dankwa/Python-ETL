from db.seed import seed
from db.connection import connect_to_db

db = None
try:
    db = connect_to_db()
    seed()
except Exception as e:
    print(e)
finally:
    if db:
        db.close()
    
