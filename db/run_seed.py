from db.seed import seed
from db.connection import db

try:
    seed()
except Exception as e:
    print(e)
finally:
    db.close()
    
