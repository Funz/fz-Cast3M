# Cast3m Plugin Example

This document demonstrates the complete workflow of using the Cast3m plugin with the fz framework.

## Prerequisites

```bash
# Install fz
pip install git+https://github.com/Funz/fz.git

# Install Cast3m (if not already installed)
# The castem2000 or cast3m executable must be in your PATH
```

## Example 1: Parse Input Variables

Identify variables in a parametric Cast3m input file:

```bash
cd fz-cast3m
python3 -c "
import fz
variables = fz.fzi('examples/Cast3m/poutre_parametric.dgibi', 'Cast3m')
print('Variables found:', list(variables.keys()))
"
```

Output:
```
Variables found: ['F', 'haut', 'larg', 'long']
```

## Example 2: Compile Input File with Values

Substitute variables with specific values:

```bash
python3 -c "
import fz
variables = {
    'long': 0.30,
    'haut': 0.001,
    'larg': 0.01,
    'F': 1.0
}
fz.fzc('examples/Cast3m/poutre_parametric.dgibi', variables, 'Cast3m', output_dir='compiled')
print('Compiled file created in: compiled/')
"
```

Check the compiled file:
```bash
cat "compiled/long=0.3,haut=0.001,larg=0.01,F=1.0/poutre_parametric.dgibi" | head -25
```

## Example 3: Parse Output Files

Given a directory with Cast3m output files (castem.out, *.txt, *.csv), extract the results:

```bash
# Create a test output directory
mkdir -p test_results
cd test_results

# Create sample output files
cat > castem.out << 'OUTEOF'
$  * MESS 'dep_P2=' dep_P2; 
 dep_P2=-5.14286E-02
$  * MESS 'stress=' stress;
 stress=2.1E+08
OUTEOF

echo "12.5" > displacement.txt

cat > forces.csv << 'CSVEOF'
TIME;F_X;F_Y
0.0;100.0;200.0
0.01;101.5;201.2
0.02;103.0;202.5
CSVEOF

cd ..

# Parse the outputs
python3 -c "
import fz
import json
result = fz.fzo('test_results', 'Cast3m')
print(json.dumps(result, indent=2, default=str))
"
```

Output:
```json
{
  "path": ["test_results"],
  "outputs": [{
    "dep_P2": -0.0514286,
    "stress": 210000000.0,
    "displacement": 12.5,
    "TIME": [0.0, 0.01, 0.02],
    "F_X": [100.0, 101.5, 103.0],
    "F_Y": [200.0, 201.2, 202.5]
  }]
}
```

## Example 4: Complete Parametric Study (Without Actual Cast3m)

This example demonstrates the workflow without running Cast3m (for testing):

```bash
python3 << 'PYEOF'
import fz
import json

# Step 1: Parse input variables
print("Step 1: Parsing input variables...")
variables = fz.fzi('examples/Cast3m/poutre_parametric.dgibi', 'Cast3m')
print(f"Found variables: {list(variables.keys())}")

# Step 2: Define parameter grid
print("\nStep 2: Defining parameter grid...")
param_grid = {
    'long': [0.25, 0.30, 0.35],
    'haut': 0.001,
    'larg': 0.01,
    'F': [0.5, 1.0, 1.5]
}
print(f"Parameter combinations: {3 * 1 * 1 * 3} = 9 cases")

# Step 3: Compile input files
print("\nStep 3: Compiling input files...")
fz.fzc('examples/Cast3m/poutre_parametric.dgibi', param_grid, 'Cast3m', output_dir='param_study')
print("Compiled files created in param_study/")

# List generated directories
import os
from pathlib import Path
cases = sorted([d.name for d in Path('param_study').iterdir() if d.is_dir()])
print(f"\nGenerated {len(cases)} case directories:")
for case in cases[:3]:
    print(f"  - {case}")
print(f"  ... and {len(cases) - 3} more")

PYEOF
```

## Example 5: Full Workflow with Actual Cast3m Execution

If you have Cast3m installed, you can run a complete parametric study:

```bash
# Note: This requires Cast3m to be installed and in PATH

python3 << 'PYEOF'
import fz

# Define parameters
param_grid = {
    'long': [0.25, 0.30],
    'haut': 0.001,
    'larg': 0.01,
    'F': [0.5, 1.0]
}

# Run parametric study
results = fz.fzr(
    'examples/Cast3m/poutre_parametric.dgibi',
    param_grid,
    'Cast3m',
    calculators=['localhost'],
    results_dir='beam_study'
)

# Display results
print("Results:")
print(results)

# Access specific output values
if 'outputs' in results:
    for i, outputs_dict in enumerate(results['outputs']):
        if outputs_dict and 'dep_P2' in outputs_dict:
            print(f"Case {i}: dep_P2 = {outputs_dict['dep_P2']}")

PYEOF
```

## Working with Results

The results are returned as a dictionary (or DataFrame if pandas is available) with:
- `path`: The path to each case directory
- `outputs`: A dictionary containing all extracted variables

To access individual variables from the outputs:

```python
import fz

result = fz.fzo('test_results', 'Cast3m')

# Access outputs for the first (and only) path
outputs = result['outputs'][0]

# Access individual variables
dep_P2 = outputs['dep_P2']
stress = outputs['stress']
time_series = outputs['TIME']
forces_x = outputs['F_X']

print(f"Displacement at P2: {dep_P2}")
print(f"Stress: {stress}")
print(f"Time series: {time_series}")
print(f"Forces in X direction: {forces_x}")
```

## Cleanup

```bash
rm -rf compiled param_study test_results beam_study
```
