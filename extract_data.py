import os
import csv
import email.utils


def concatenate_lines(file_path):
    # Create a temporary list to store processed lines
    prefixes = ['AB -', 'IS  -', 'MH  -', 'PMC -', 'AU  -', 'TT  -', 'AID -', 'PT  -', 'PST -', 'CI  -', 'AB  -', 'FIR -', 'RN  -', 'PHST-', 'EIN -', 'EFR -', 'SI  -', 'LID -', 'LR  -', 'JT  -', 'MHDA-', 'OT  -', 'PMCR-', 'VI  -', 'IR  -', 'DEP -', 'SB  -', 'DCOM-', 'AUID-', 'COIS-', 'MID -', 'CN  -', 'PL  -', 'TI  -', 'PG  -', 'STAT-', 'IP  -', 'AD  -', 'CRDT-', 'OTO -', 'LA  -', 'OAB -', 'IRAD-', 'PMID-', 'JID -', 'GR  -', 'SPIN-', 'OABL-', 'FAU -', 'OWN -', 'EDAT-', 'TA  -', 'SO  -', 'DP  -', 'CON -', 'CIN -']

    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    processed_lines = []
    current_line = ""

    for line in lines:
        line = line.strip()

        if any(line.startswith(prefix) for prefix in prefixes):
            # If the line starts with one of the prefixes, append it to the processed lines
            processed_lines.append(line)
            current_line = line
        elif current_line:
            # If the line doesn't start with a prefix, add it to the last line that did
            processed_lines[-1] += " " + line

    # Write the processed lines back to the file
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write('\n'.join(processed_lines))


def extract_info_from_text(file_path):
    data_list = []
    current_entry = {}

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            if line.startswith("FAU"):
                # New author entry starts
                if current_entry:
                    data_list.append(current_entry.copy())  # Add the previous entry to the list
                current_entry = {'First Name': None, 'Last name': None, 'Institution': None, 'Email': None}

                # Extracting first name or initial and last name from "FAU" line
                names = line.strip().split(" - ")[1].split(", ")
                current_entry['First Name'] = names[1] if len(names) > 1 else None
                current_entry['Last name'] = names[0]


            elif line.startswith("AD"):
                # Extracting institution and email from "AD" line
                parts = line.strip().split(",")
                if len(parts) > 1:
                    current_entry['Institution'] = parts[0].strip() + " " + parts[1].strip()  # Extracting institution from the second comma

                # Check the line for an email address
                line = line.strip().split()
                for word in line:
                    if "@" in word:
                        current_entry['Email'] = word.strip()  # Extracting email
                        break

    # Add the last entry to the list
    if current_entry:
        data_list.append(current_entry)

    return data_list


def write_to_csv(data_list, csv_file_path):
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['First Name', 'Last name', 'Institution', 'Email'])  # Write header

        for entry in data_list:
            email = entry.get('Email', None)  # Get the email entry, defaulting to None if not present
            if email is not None:  # Check if email is not null
                csv_writer.writerow([entry['First Name'], entry['Last name'], entry['Institution'], email])

if __name__ == "__main__":
    try:
        # Prompt user for input file path
        input_file_path = input("\nDrag and drop the file here and press Enter: ")

        # Replace '/c/' with 'C:\' in the input file path if present
        if input_file_path.startswith('/c/'):
            input_file_path = input_file_path.replace('/c/', 'C:\\')
        input_file_path = input_file_path.replace('"', '')

        # Use user's download folder as default for output CSV file
        default_output_folder = os.path.join(os.path.expanduser("~"), "Downloads")
        default_output_path = os.path.join(default_output_folder, "output_data.csv")

        # Prompt user for output CSV file path with default value
        output_csv_path = input(f"\nEnter the path for the output CSV file (default: {default_output_path}): ") or default_output_path

        # Check if the user is using the default output path
        if output_csv_path == default_output_path:
            print(f"\nUsing default output path: {output_csv_path} \n")

        # Validate and extract data
        if os.path.exists(input_file_path):
            concatenate_lines(input_file_path)
            extracted_data = extract_info_from_text(input_file_path)
            write_to_csv(extracted_data, output_csv_path)

            # Display the number of entries
            num_entries = len(extracted_data)
            print(f">>>    {num_entries} entries found.")

            # Display the number of emails, names, and institutions
            num_emails = sum(1 for entry in extracted_data if entry['Email'] is not None)
            num_names = sum(1 for entry in extracted_data if entry['First Name'] is not None and entry['Last name'] is not None)
            num_institutions = sum(1 for entry in extracted_data if entry['Institution'] is not None)

            print(f">>>    {num_emails} emails found.")
            print(f">>>    {num_names} names found.")
            print(f">>>    {num_institutions} institutions found.")

        else:
            raise FileNotFoundError(f"\nError: The input file '{input_file_path}' does not exist.")

    except Exception as e:
        print(f"Error: {e}")

    # Ask the user to press a button to close the program
    input("\nPress Enter to close.")
