import sys
import os

def remove_duplicate_emails(filename):
    if not filename:
        print("Error: No filename provided. Please specify a file containing email addresses.")
        return
    
    data_dir = "Data"
    filepath = os.path.join(data_dir, filename)

    if not os.path.exists(filepath):
        print(f"Error: File '{filepath}' not found.")
        return

    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            emails = {line.strip().lower() for line in file if '@' in line}
        
        output_file = os.path.join(data_dir, f"cleaned_{filename}")
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write('\n'.join(sorted(emails)))
        
        print(f"Cleaning completed! Results saved in: {output_file}")
    except Exception as e:
        print(f"An error occurred while processing '{filename}': {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = input("Enter the filename (must be in 'Data/' directory): ").strip()

    remove_duplicate_emails(filename)
