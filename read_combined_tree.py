import json

def read_combined_tree_json(file_path):
    """
    Reads the JSON file containing the combined tree.

    Args:
        file_path (str): The file path of the JSON file.

    Returns:
        dict: A dictionary containing the combined tree data.
    """
    with open(file_path, 'r') as f:
        combined_tree = json.load(f)
    return combined_tree

def main():
    file_path = 'combined_tree.json'  # Replace with your JSON file path if different
    combined_tree = read_combined_tree_json(file_path)
    
    # Print the combined tree dictionary
    print(json.dumps(combined_tree, indent=4))

if __name__ == "__main__":
    main()
