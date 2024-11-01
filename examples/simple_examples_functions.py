# simple_examples_functions.py
from datetime import datetime
        
def get_current_date_function():
    return {'current_date':datetime.today().strftime('%Y-%m-%d')}
