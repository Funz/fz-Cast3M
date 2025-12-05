# Cast3m Plugin Porting Summary

## Overview

This document summarizes the porting of the Cast3m plugin from the old Funz framework (Java-based) to the new fz framework (Python-based).

## Original Plugin

- **Repository**: https://github.com/Funz/plugin-cast3m
- **Key File**: `src/main/java/org/funz/Cast3m/Cast3mIOPlugin.java`
- **Helper**: `src/main/java/org/funz/Cast3m/DGibiHelper.java`

## New Plugin Structure

```
fz-cast3m/
├── .fz/
│   ├── models/
│   │   ├── Cast3m.json              # Model definition with embedded parser
│   │   ├── parse_cast3m_output.py   # Full parser (documented)
│   │   ├── parse_compact.py         # Compact parser
│   │   └── README.md                # Design documentation
│   └── calculators/
│       ├── Cast3m.sh                # Execution script
│       └── localhost.json           # Local calculator config
├── samples/
│   ├── poutre.dgibi                 # Simple example
│   ├── poutre_parametric.dgibi      # Parametric example
│   └── outvar.dgibi                 # Output examples
├── README.md                        # Main documentation
├── EXAMPLE.md                       # Usage examples
└── .gitignore
```

## Porting Details

### 1. Model Definition (Cast3m.json)

Translated from `Cast3mIOPlugin.java` constructor:

| Java                              | Python (JSON)           |
|-----------------------------------|-------------------------|
| `variableStartSymbol = "$"`       | `"varprefix": "$"`      |
| `variableLimit = "()"`            | `"delim": "()"`         |
| `formulaStartSymbol = "%"`        | `"formulaprefix": "%"`  |
| `formulaLimit = "[]"`             | `"delim": "[]"`         |
| `commentLine = "*"`               | `"commentline": "*"`    |

### 2. Output Parsing

Ported from `readOutput()`, `readOutTxt()`, `readNonCsvFiles()`, and `readCsvFiles()` methods:

**Java Implementation:**
```java
@Override
public Map<String, Object> readOutput(final File outdir) {
    final Map<String, Object> lout = super.readOutput(outdir);
    this.readOutTxt(outdir, lout);
    this.readNonCsvFiles(outdir, lout);
    this.readCsvFiles(outdir, lout);
    return lout;
}
```

**Python Implementation:**
```python
def main():
    all_results = {}
    all_results.update(read_mess_vars())
    all_results.update(read_text_files())
    all_results.update(read_csv_files())
    print(json.dumps(all_results))
```

### 3. DGibiHelper Functions

| Java Method                    | Python Implementation              |
|--------------------------------|-------------------------------------|
| `lookForScalar()`              | `read_mess_vars()` with regex      |
| `extractNonCsvVariables()`     | `read_text_files()` for .txt files |
| `extractCsvVariables()`        | `read_csv_files()` for .csv files  |
| `readCSV()`                    | Built-in `csv.reader()`            |

### 4. Calculator Script

Replaces the Java execution wrapper with a Bash script:

- Finds Cast3m executable (castem2000 or cast3m)
- Handles both file and directory inputs
- Validates input paths
- Redirects output to castem.out

## Key Differences from Original

### 1. Output Variable Discovery

**Old Plugin (Java):**
- `setInputFiles()` scans .dgibi files for MESS, SORT commands
- Populates `_output` map dynamically
- `readOutput()` reads based on discovered variables

**New Plugin (Python):**
- No dynamic discovery in model definition
- Parser reads all available outputs
- Returns everything as JSON dict
- Users access via `result['outputs'][0]['varname']`

### 2. Embedding Strategy

**Old Plugin:**
- Separate .jar file
- Loaded via classpath

**New Plugin:**
- Embedded Python in JSON using heredoc
- Self-contained model file
- No external dependencies beyond Python stdlib

### 3. Return Format

**Old Plugin:**
```java
Map<String, Object> outputs = readOutput(dir);
// outputs.get("dep_P2") -> Double
// outputs.get("TIME") -> double[]
```

**New Plugin:**
```python
result = fz.fzo("dir", "Cast3m")
# result['outputs'][0]['dep_P2'] -> float
# result['outputs'][0]['TIME'] -> list[float]
```

## Testing

All functionality verified:

✓ Variable parsing (fzi)
✓ Single value compilation (fzc)
✓ Parameter grid compilation (fzc)
✓ MESS variable extraction (fzo)
✓ Text file extraction (fzo)
✓ CSV file extraction (fzo)

## Migration Guide for Users

### Old Funz Framework

```bash
# Old way
./Funz.sh ParseInput -m Cast3m -if poutre.par.dgibi
./Funz.sh CompileInput -m Cast3m -if poutre.par.dgibi -iv long=0.3
./Funz.sh Run -m Cast3m -if poutre.par.dgibi -iv long=0.3,0.4,0.5
```

### New fz Framework

```bash
# New way
fzi poutre_parametric.dgibi --model Cast3m
fzc poutre_parametric.dgibi --model Cast3m --variables '{"long": 0.3}' --output compiled/
fzr poutre_parametric.dgibi --model Cast3m --variables '{"long": [0.3, 0.4, 0.5]}' --calculator localhost --results results/
```

Or in Python:

```python
import fz

# Parse variables
vars = fz.fzi("poutre_parametric.dgibi", "Cast3m")

# Compile
fz.fzc("poutre_parametric.dgibi", {"long": 0.3}, "Cast3m", "compiled")

# Run parametric study
results = fz.fzr(
    "poutre_parametric.dgibi",
    {"long": [0.3, 0.4, 0.5]},
    "Cast3m",
    calculators=["localhost"],
    results_dir="results"
)
```

## Files Modified/Created

### Created:
- `.fz/models/Cast3m.json` - Model definition
- `.fz/models/parse_cast3m_output.py` - Output parser (full)
- `.fz/models/parse_compact.py` - Output parser (compact)
- `.fz/models/README.md` - Design documentation
- `.fz/calculators/Cast3m.sh` - Execution script
- `.fz/calculators/localhost.json` - Calculator config
- `samples/poutre.dgibi` - Example 1
- `samples/poutre_parametric.dgibi` - Example 2 (parametric)
- `samples/outvar.dgibi` - Example 3 (outputs)
- `README.md` - Main documentation
- `EXAMPLE.md` - Usage examples
- `.gitignore` - Git ignore rules

### Total: 12 new files

## Conclusion

The Cast3m plugin has been successfully ported to the new fz framework. All core functionality from the original Java plugin is preserved and working:

- Variable parsing from .dgibi files
- Input file compilation with parameter substitution
- Output extraction from multiple sources (castem.out, .txt, .csv)
- Support for parametric studies

The new implementation is more lightweight, self-contained, and follows the patterns established in the fz framework.
