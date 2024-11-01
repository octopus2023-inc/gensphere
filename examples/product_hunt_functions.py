# product_hunt_functions.py
from datetime import datetime

def read_file_as_string(file_path):
    try:
        with open(file_path, 'r') as file:
            content = file.read()
        return {'domains':content}
    except FileNotFoundError:
        return "Oops! It seems the specified file doesn't exist. Please provide a valid file path."
        
def get_current_date_function():
    return {'current_date':datetime.today().strftime('%Y-%m-%d')}
    
def get_timewindow_function():
    return {'time_window':'past month'}
        
def postprocess_search_results_functions(info):
    result=info.model_dump().get('information_list')
    return {'postprocessed_search_results':result}