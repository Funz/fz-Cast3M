#!/usr/bin/env python3
"""
Parse Cast3m output files and extract variables.
This script replicates the logic from Cast3mIOPlugin.java readOutput method.
"""

import re
import json
import glob
import csv
import sys
import os


def is_float(value):
    """Check if a string can be converted to float."""
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False


def read_mess_vars(outfile="castem.out"):
    """
    Read scalar variables from castem.out file.
    Looks for patterns like: varname=value
    Replicates readOutTxt from Cast3mIOPlugin.java
    """
    results = {}
    
    if not os.path.exists(outfile):
        return results
    
    try:
        with open(outfile, 'r', errors='ignore') as f:
            lines = f.readlines()
        
        # Pattern to match: varname=numerical_value
        # Supports formats like: dep_P2=-5.14286E-02
        pattern = re.compile(r'([\w_]+)=([\d\.\+\-E]+)', re.IGNORECASE)
        
        for line in lines:
            # Skip lines starting with $ (these are echoed input lines)
            if line.strip().startswith('$'):
                continue
            
            # Split by semicolon to get the code part (before comments)
            code = line.split(';')[0]
            
            # Search for the pattern
            match = pattern.search(code)
            if match:
                var_name = match.group(1)
                var_value = match.group(2)
                try:
                    results[var_name] = float(var_value)
                except ValueError:
                    # If can't convert, store as NaN
                    results[var_name] = float('nan')
    
    except Exception as e:
        print(f"Error reading {outfile}: {e}", file=sys.stderr)
    
    return results


def read_text_files():
    """
    Read non-CSV text files (from SORT 'CHAI' commands).
    Replicates readNonCsvFiles from Cast3mIOPlugin.java
    """
    results = {}
    
    # Find all .txt files except castem.out
    txt_files = [f for f in glob.glob("*.txt") if f != "castem.out"]
    
    for filename in txt_files:
        try:
            with open(filename, 'r', errors='ignore') as f:
                content = f.read().strip()
            
            # Try to parse as float
            if is_float(content):
                # Use filename without extension as variable name
                var_name = os.path.splitext(filename)[0]
                results[var_name] = float(content)
            else:
                # Store as string if not numeric
                var_name = os.path.splitext(filename)[0]
                results[var_name] = content
        
        except Exception as e:
            print(f"Error reading {filename}: {e}", file=sys.stderr)
    
    return results


def read_csv_files():
    """
    Read CSV files (from SORT 'EXCE' commands).
    Replicates readCsvFiles from Cast3mIOPlugin.java
    """
    results = {}
    
    csv_files = glob.glob("*.csv")
    
    for filename in csv_files:
        try:
            with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
                reader = csv.reader(f, delimiter=';')
                lines = list(reader)
            
            if not lines:
                continue
            
            # Transpose the data to get columns
            columns = list(zip(*lines))
            
            # Check if first row contains headers (non-numeric)
            has_header = not is_float(columns[0][0]) if columns else False
            
            for col in columns:
                if has_header:
                    # First element is the column name
                    col_name = col[0]
                    col_values = col[1:]
                    
                    # Convert to float array
                    try:
                        results[col_name] = [float(v) for v in col_values if v.strip()]
                    except ValueError:
                        # If conversion fails, skip this column
                        pass
                else:
                    # No header, use filename as base name
                    base_name = os.path.splitext(filename)[0]
                    
                    # For files without headers, store the entire data
                    # This matches the behavior in readCsvFileNoHeader
                    try:
                        # Convert entire table to numeric array
                        data = [[float(v) for v in row] for row in lines if any(row)]
                        # Store with filename as key
                        results[base_name] = data
                    except ValueError:
                        pass
                    break  # Only process once for files without headers
        
        except Exception as e:
            print(f"Error reading {filename}: {e}", file=sys.stderr)
    
    return results


def main():
    """Main function to extract all outputs and return as JSON."""
    all_results = {}
    
    # Read MESS variables from castem.out
    mess_vars = read_mess_vars()
    all_results.update(mess_vars)
    
    # Read text files (CHAI outputs)
    text_vars = read_text_files()
    all_results.update(text_vars)
    
    # Read CSV files (EXCEL outputs)
    csv_vars = read_csv_files()
    all_results.update(csv_vars)
    
    # Output as JSON
    # Note: fz will parse this JSON and store it in the 'outputs' column
    # Users can access individual variables like: df['outputs'].apply(lambda x: x.get('dep_P2'))
    print(json.dumps(all_results))


if __name__ == "__main__":
    main()
