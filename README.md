# fz-cast3m

Cast3m plugin for the new Funz fz framework.

This repository contains the port of the [old Cast3m plugin](https://github.com/Funz/plugin-cast3m) to the new [fz framework](https://github.com/Funz/fz).

## Overview

Cast3m is a finite element software developed by CEA (French Alternative Energies and Atomic Energy Commission) for structural and fluid mechanics simulations. This plugin enables the fz framework to:

- Parse Cast3m input files (`.dgibi` format)
- Identify variables using `$` prefix with `()` delimiters
- Execute Cast3m calculations
- Extract output variables from results

## Installation

### Prerequisites

1. Install the fz framework:
```bash
pip install funz-fz
```

2. Install Cast3m (castem2000 or cast3m executable must be in PATH)

### Using this Plugin

Clone this repository to use the Cast3m model and calculator:

```bash
git clone https://github.com/Funz/fz-cast3m.git
cd fz-cast3m
```

## Usage

### Input File Format

Cast3m uses `.dgibi` files with the following syntax:

- **Variables**: `$(variable_name)` - Will be substituted by fz
- **Comments**: Lines starting with `*`
- **Output variables**: Defined using `MESS 'varname=' varname;` syntax

Example input file (`poutre_parametric.dgibi`):
```
* POUTRE CONSOLE EN FLEXION SIMPLE
OPTI DIME 2 ELEM SEG2;

long = $(long);
haut = $(haut);
larg = $(larg);
F = $(F);

* ... calculation code ...

MESS 'dep_P2=' dep_P2;

FIN;
```

### Parse Input Variables

```bash
fzi samples/poutre_parametric.dgibi --model Cast3m
```

### Compile Input Files

```bash
fzc samples/poutre_parametric.dgibi \
  --model Cast3m \
  --variables '{"long": 0.30, "haut": 0.001, "larg": 0.01, "F": 1.0}' \
  --output compiled/
```

### Read Output Files

```bash
fzo results/ --model Cast3m
```

### Run Parametric Study

```bash
fzr samples/poutre_parametric.dgibi \
  --model Cast3m \
  --variables '{"long": [0.25, 0.30, 0.35], "haut": 0.001, "larg": 0.01, "F": [0.5, 1.0, 1.5]}' \
  --calculator localhost \
  --results results/
```

## Plugin Structure

```
.fz/
├── models/
│   └── Cast3m.json          # Model definition with output parsing
└── calculators/
    ├── localhost.json        # Local calculator configuration
    └── Cast3m.sh            # Cast3m execution script

samples/
├── poutre.dgibi             # Sample beam calculation
├── poutre_parametric.dgibi  # Parametric beam example
└── outvar.dgibi             # Output variables example
```

## Model Definition

The Cast3m model (`.fz/models/Cast3m.json`) defines:

- **Variable syntax**: `$` prefix with `()` delimiters
- **Formula syntax**: `%` prefix with `[]` delimiters  
- **Comment lines**: Lines starting with `*`
- **Output parsing**: Python scripts to extract results from:
  - `castem.out`: Main output file with `MESS` variables
  - `*.txt`: Text files from `SORT 'CHAI'` commands
  - `*.csv`: CSV files from `SORT 'EXCE'` commands

### Output Variables

The plugin supports three types of output extraction:

1. **MESS variables** (from `castem.out`):
   ```
   MESS 'dep_P2=' dep_P2;
   ```

2. **Text file outputs** (from `SORT 'CHAI'`):
   ```
   OPTI SORT 'result.txt';
   SORT 'CHAI' variable;
   ```

3. **CSV file outputs** (from `SORT 'EXCE'`):
   ```
   OPTI SORT 'results.csv';
   SORT 'EXCE' table_var;
   ```

## Output Parsing Logic

The output parsing is implemented in Python within the model JSON file:

- **_mess_vars**: Extracts scalar variables from `castem.out` using regex pattern matching
- **_chai_files**: Reads text files and extracts numeric values
- **_csv_files**: Parses CSV files with semicolon delimiters and returns column data as arrays

This replicates the logic from the original Java implementation in `Cast3mIOPlugin.java`.

## Examples

See the `samples/` directory for example input files.

### Simple Execution

Run a single calculation:
```bash
cd samples
bash ../.fz/calculators/Cast3m.sh poutre.dgibi
```

### Parametric Study

Run multiple cases with different parameters:
```bash
fzr samples/poutre_parametric.dgibi \
  --model Cast3m \
  --variables '{
    "long": [0.20, 0.25, 0.30, 0.35, 0.40],
    "haut": [0.001, 0.002],
    "larg": 0.01,
    "F": 1.0
  }' \
  --calculator localhost \
  --results beam_study/ \
  --format table
```

## Original Plugin Reference

This plugin is a port of the original Cast3m plugin:
- Repository: https://github.com/Funz/plugin-cast3m
- Key file ported: `src/main/java/org/funz/Cast3m/Cast3mIOPlugin.java`

The main difference is that the output parsing logic (previously in Java's `readOutput` method) is now implemented as Python scripts in the JSON model definition.

## Documentation

- Cast3m official website: http://www-cast3m.cea.fr/
- fz framework: https://github.com/Funz/fz
- Original plugin: https://github.com/Funz/plugin-cast3m

## License

See LICENSE file (inherited from original plugin).

## Copyright

Original plugin:
- Copyright: IRSN, Paris, FRANCE
- Developed by: Artenum SARL
- Authors: Laurent Mallet, Arnaud Trouche

Ported to fz framework: 2024