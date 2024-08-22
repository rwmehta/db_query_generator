import json

def parse_table_columns(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    table_entries = {}
    current_table = ''
    table_description = ''

    for line in lines:
        line = line.strip()
        if ':' in line and not line.startswith('-'):
            current_table, table_description = line.split(':', 1)
            current_table = current_table.strip()
            table_description = table_description.strip()
        elif line.startswith('-'):
            column_name, column_detail = line.split(':', 1)
            column_detail = column_detail.strip()
            column_name = column_name.strip('- ').strip()
            key = f'{current_table}.{column_name}'
            value = f'Table: {current_table} - Description: {table_description} - Column: {column_name} - Detail: {column_detail}'
            table_entries[key] = value

    return table_entries

def save_to_json(data, output_file):
    with open(output_file, 'w') as json_file:
        json.dump(data, json_file, indent=4)

# Example usage
file_path = './database_description.txt'
output_file = './table_columns.json'

contexts = parse_table_columns(file_path)
save_to_json(contexts, output_file)

print(f"JSON file saved to: {output_file}")
