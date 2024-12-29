import csv

# Constants
END_OF_HEADER = "*" * 20
FIELDNAMES = ['RunDate', 'Date', 'Time', 'Room', 'LineNo', 'FileNum', 'Defendant', 
              'Complainant', 'Attorney', 'Cont', 'Bond', 'Fingerprint', 'AKA']

def is_report_header(line):
    return "RUN DATE:" in line and line[0] != "1"

def process_report_header(line, infile):
    data = {}
    while END_OF_HEADER not in line:
        if "RUN DATE" in line:
            data['RunDate'] = line[12:30].strip()
        elif "COURT DATE:" in line:
            data['Date'] = line[22:38].strip()
            data['Time'] = line[44:60].strip()
            data['Room'] = line[78:].strip()
        line = infile.readline()
    return data

def is_page_header(line):
    return line[0] == "1" and "RUN DATE:" not in line

def process_page_header(line, infile):
    while END_OF_HEADER not in line:
        line = infile.readline()

def is_defendant_line(line):
    try:
        int(line[:6].strip())  # Verify the first six characters can be cast to int
        return True
    except ValueError:
        return False

def process_defendant_line(line):
    data = {
        'LineNo': line[:6].strip(),
        'FileNum': line[8:20].strip(),
        'Defendant': line[20:42].strip(),
        'Bond': '',
        'Fingerprint': False,
        'AKA': ''
    }
    if len(line) >= 85:
        data['Complainant'] = line[42:57].strip()
        data['Attorney'] = line[57:84].strip()
        data['Cont'] = line[84:].strip()
    elif len(line) >= 58:
        data['Complainant'] = line[42:57].strip()
        data['Attorney'] = line[57:].strip()
        data['Cont'] = ''
    else:
        data['Complainant'] = line[42:].strip()
        data['Attorney'] = ''
        data['Cont'] = ''
    return data

def clean_aka(aka):
    """Cleans, deduplicates, and corrects misspellings in the AKA field."""
    if not aka.strip():
        return ""
    # Dictionary of known corrections (add more as needed)
    name_corrections = {
        "WHISNANT": "WHISENANT",
          "WAYLAN": "WAYLAND"  # Correct misspelling
    }
    # Split names by commas and remove empty parts
    names = [name.strip() for name in aka.split(",") if name.strip()]
    # Correct names based on the dictionary
    corrected_names = []
    for name in names:
        corrected_name = name_corrections.get(name.upper(), name.upper())  # Correct if in dictionary
        if corrected_name not in corrected_names:
            corrected_names.append(corrected_name)
    # Combine corrected and unique names into a single string
    return " ".join(corrected_names)


def write_csv_record(writer, report_data, defendant_data):
    """Writes a single record to the CSV file."""
    defendant_data['AKA'] = clean_aka(defendant_data['AKA'])
    record = report_data.copy()
    record.update(defendant_data)
    writer.writerow(record)

def main():
    filenames = [
        "Court1.txt", "Court2.txt", "Court3.txt", "Court4.txt",
        "Court5.txt", "Court6.txt", "Court7.txt", "Court8.txt"
    ]
    output_filename = "Court_Case_Data.csv"

    with open(output_filename, 'w', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=FIELDNAMES)
        writer.writeheader()

        for input_filename in filenames:
            try:
                print(f"Processing file: {input_filename}")
                with open(input_filename, 'r') as infile:
                    report_data = {}
                    defendant_data = {}

                    for line in infile:
                        if line.strip() == '':
                            continue
                        if is_page_header(line):
                            process_page_header(line, infile)
                        elif is_report_header(line):
                            report_data = process_report_header(line, infile)
                        elif is_defendant_line(line):
                            if defendant_data:
                                write_csv_record(writer, report_data, defendant_data)
                            defendant_data = process_defendant_line(line)
                        elif "BOND:" in line:
                            defendant_data['Bond'] = line[25:].strip()
                        elif "FINGERPRINTED" in line:
                            defendant_data['Fingerprint'] = True
                        elif "AKA:" in line:
                            aka_value = line[19:].strip()
                            if defendant_data['AKA']:
                                defendant_data['AKA'] += f", {aka_value}"
                            else:
                                defendant_data['AKA'] = aka_value

                    if defendant_data:
                        write_csv_record(writer, report_data, defendant_data)

            except FileNotFoundError:
                print(f"File not found: {input_filename}")
            except Exception as e:
                print(f"Error processing {input_filename}: {e}")

    print(f"Data successfully written to {output_filename}")

if __name__ == "__main__":
    main()
