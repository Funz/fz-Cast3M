# Cast3m Model Files

## Overview

This directory contains the Cast3m model definition and output parsing scripts for the fz framework.

## Files

- **Cast3m.json**: Model definition with variable syntax and embedded output parser
- **parse_cast3m_output.py**: Full-featured Python script for parsing Cast3m outputs (documented version)
- **parse_compact.py**: Compact version of the parser (for reference)

## Design Decisions

### Embedded Python Script in Cast3m.json

The output parser is embedded directly in Cast3m.json using a bash heredoc syntax:

```json
{
  "output": {
    "outputs": "python3 << 'PYEOF'\n...python code...\nPYEOF\n"
  }
}
```

**Why embedded instead of referencing parse_cast3m_output.py?**

1. **Portability**: The embedded script works regardless of the current working directory or where fz is executed from.
2. **No path dependencies**: When fz executes the output command, it runs from the output directory. A file reference would need complex path resolution.
3. **Self-contained**: The model file is fully self-contained and can be copied/shared without additional files.
4. **Follows fz patterns**: Similar to the Telemac example in the fz framework.

**Note on exception handling in embedded version:**

The embedded script uses bare `except:` clauses for maximum robustness - it will attempt to parse all available outputs even if some fail. This is intentional to ensure partial results are always returned. The standalone `parse_cast3m_output.py` uses more specific exception types for better debugging.

The standalone `parse_cast3m_output.py` is kept for:
- Documentation and readability
- Testing and development
- Users who want to customize or understand the parsing logic
- Better error messages and specific exception handling

## Output Parsing Logic

The parser replicates the behavior of the original Java plugin (`Cast3mIOPlugin.java`):

1. **MESS variables** (from `castem.out`):
   - Searches for patterns like `varname=value`
   - Skips lines starting with `$` (echoed input lines)
   - Extracts scalar numeric values

2. **Text file outputs** (from `*.txt` files):
   - Reads simple text files created by `SORT 'CHAI'` commands
   - Converts numeric content to floats
   - Stores non-numeric content as strings

3. **CSV file outputs** (from `*.csv` files):
   - Parses CSV files created by `SORT 'EXCE'` commands
   - Uses semicolon (`;`) as delimiter
   - Handles both files with headers and without headers
   - Returns arrays for each column

All results are returned as a single JSON object with variable names as keys.

## Usage

The model is loaded automatically by fz when you use the "Cast3m" model alias:

```python
import fz

# Parse variables
variables = fz.fzi('input.dgibi', 'Cast3m')

# Compile with values
fz.fzc('input.dgibi', {'var1': 1.0, 'var2': 2.0}, 'Cast3m', output_dir='output')

# Parse outputs
results = fz.fzo('output_dir', 'Cast3m')
# Access outputs: results['outputs'][0]['varname']
```

## Customization

To customize the output parsing:

1. Copy `parse_cast3m_output.py` to your project
2. Modify the script as needed
3. Update Cast3m.json to reference your custom script (you'll need to handle path resolution)
4. Or embed your modified version in Cast3m.json following the same pattern

Example of referencing an external script (if in same directory as output):

```json
{
  "output": {
    "outputs": "python3 ./my_custom_parser.py"
  }
}
```

Note: This only works if you copy the script to each output directory or use absolute paths.
