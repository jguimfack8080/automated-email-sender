import sys

def remove_duplicate_emails(filename):
    if not filename:
        print("Error: No filename provided. Please specify a file containing email addresses.")
        return
    
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            emails = {line.strip().lower() for line in file if '@' in line}
        
        output_file = f"cleaned_{filename}"
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write('\n'.join(sorted(emails)))
        
        print(f"Cleaning completed! Results saved in: {output_file}")
    except FileNotFoundError:
        print("Error: File not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    filename = sys.argv[1] if len(sys.argv) > 1 else None
    remove_duplicate_emails(filename)
