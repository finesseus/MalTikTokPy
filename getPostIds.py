import re

def extract_and_print_post_ids(file_path):
    # List to store extracted post IDs
    post_ids = []

    # Open the file and read line by line
    with open(file_path, 'r') as file:
        for line in file:
            # Use regex to extract either video or photo ID from the URL
            match = re.search(r'/(video|photo)/(\d+)', line)
            if match:
                # If a match is found, add the ID to the list
                post_ids.append(match.group(2))
    
    # Format the list of IDs in a SQL-friendly format
    sql_format = "('" + "', '".join(post_ids) + "')"
    print(len(post_ids))
    print(sql_format)

# Example usage:
# Assuming '12-14Out.txt' is in the same directory as this script
file_path = '12-14Out.txt'
extract_and_print_post_ids(file_path)