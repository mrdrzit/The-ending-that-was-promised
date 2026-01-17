import re

def sort_behavior_videos(file_list):
    """
    Sorts a list of file paths based on behavioral groups 
    (tra, trb, tta, ttb) and then chronologically by filename.
    """
    
    # Define the custom order priority
    priority_map = {
        'tra': 1,
        'trb': 2,
        'tta': 3,
        'ttb': 4
    }

    def _get_sort_key(path):
        # 1. Search for the group folder name inside the path
        # We look for \tra\, \trb\, etc. to ensure we match the folder
        match = re.search(r'\\(tra|trb|tta|ttb)\\', path, re.IGNORECASE)
        
        if match:
            group = match.group(1).lower()
            # Get priority from map, default to 5 if something weird happens
            priority = priority_map.get(group, 5)
        else:
            # If no group found, put it at the very end
            priority = 99
            
        # Return tuple: (Group Priority, Original Path)
        return (priority, path)

    # Return the sorted list
    return sorted(file_list, key=_get_sort_key)