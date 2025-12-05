#!/usr/bin/env python3
"""
Basic test suite for fz-Cast3m plugin.

These tests verify the plugin structure.
They test:
- Model file validity
- Variable parsing
- Input file compilation
- Calculator configuration
"""

import os
import json
import tempfile
import sys


def test_model_files():
    """Test that all model JSON files are valid and have required fields."""
    print("Testing model files...")
    
    models = [
        ".fz/models/Cast3m.json"
    ]
    
    required_fields = ["id", "varprefix", "delim", "commentline", "output"]
    
    for model_file in models:
        print(f"  Checking {model_file}...", end=" ")
        
        # Check file exists
        assert os.path.exists(model_file), f"File not found: {model_file}"
        
        # Load and validate JSON
        with open(model_file, 'r') as f:
            model = json.load(f)
        
        # Check required fields
        for field in required_fields:
            assert field in model, f"Missing field '{field}' in {model_file}"
        
        # Check output section has at least one variable
        assert len(model["output"]) > 0, f"No output variables in {model_file}"
        
        print("✓")
    
    print("  All model files valid!\n")


def test_calculator_files():
    """Test that calculator JSON files are valid."""
    print("Testing calculator configuration files...")

    calculators = [
        ".fz/calculators/localhost_Cast3m.json"
    ]
    
    for calc_file in calculators:
        print(f"  Checking {calc_file}...", end=" ")
        
        # Check file exists
        assert os.path.exists(calc_file), f"File not found: {calc_file}"
        
        # Load and validate JSON
        with open(calc_file, 'r') as f:
            calc = json.load(f)
        
        # Check required fields
        assert "uri" in calc, f"Missing 'uri' field in {calc_file}"
        assert "models" in calc, f"Missing 'models' field in {calc_file}"
        
        print("✓")
    
    print("  All calculator files valid!\n")


def test_calculator_scripts():
    """Test that calculator shell scripts exist and are executable."""
    print("Testing calculator shell scripts...")
    
    scripts = [
        ".fz/calculators/Cast3m.sh"
    ]
    
    for script_file in scripts:
        print(f"  Checking {script_file}...", end=" ")
        
        # Check file exists
        assert os.path.exists(script_file), f"File not found: {script_file}"
        
        # Check if executable
        assert os.access(script_file, os.X_OK), f"Script not executable: {script_file}"
        
        print("✓")
    
    print("  All calculator scripts valid!\n")


def test_example_files():
    """Test that example files exist."""
    print("Testing example files...")
    
    examples = [
        "examples/Cast3m/poutre.dgibi",
        "examples/Cast3m/poutre_parametric.dgibi",
        "examples/Cast3m/outvar.dgibi"
    ]
    
    for example_file in examples:
        print(f"  Checking {example_file}...", end=" ")
        assert os.path.exists(example_file), f"File not found: {example_file}"
        print("✓")
    
    print("  All example files present!\n")


def test_with_fz():
    """Test integration with fz framework (if available)."""
    print("Testing fz framework integration...")
    
    try:
        import fz
        print("  fz module found ✓")
        
        # Test parsing input file
        print("  Testing fz.fzi() on poutre_parametric.dgibi...", end=" ")
        variables = fz.fzi("examples/Cast3m/poutre_parametric.dgibi", "Cast3m")
        assert "long" in variables, "Variable 'long' not found in parsed input"
        assert "haut" in variables, "Variable 'haut' not found in parsed input"
        assert "larg" in variables, "Variable 'larg' not found in parsed input"
        assert "F" in variables, "Variable 'F' not found in parsed input"
        print("✓")
        
        # Test compiling input file
        print("  Testing fz.fzc() compilation...", end=" ")
        with tempfile.TemporaryDirectory() as tmpdir:
            fz.fzc(
                "examples/Cast3m/poutre_parametric.dgibi",
                {"long": 0.30, "haut": 0.001, "larg": 0.01, "F": 1.0},
                "Cast3m",
                output_dir=tmpdir
            )
            
            # Check compiled file exists (it may be in a subdirectory)
            compiled_file = None
            for root, dirs, files in os.walk(tmpdir):
                if "poutre_parametric.dgibi" in files:
                    compiled_file = os.path.join(root, "poutre_parametric.dgibi")
                    break
            assert compiled_file is not None, "Compiled file not created"
            
            # Check variables were substituted
            with open(compiled_file, 'r') as f:
                content = f.read()
                assert "0.30" in content or "0.3" in content, "Variable long not substituted"
                assert "0.001" in content, "Variable haut not substituted"
                assert "0.01" in content, "Variable larg not substituted"
                assert "1.0" in content or "1" in content, "Variable F not substituted"
                assert "$(long)" not in content, "Variable marker $(long) still present"
                assert "$(haut)" not in content, "Variable marker $(haut) still present"
                assert "$(larg)" not in content, "Variable marker $(larg) still present"
                assert "$(F)" not in content, "Variable marker $(F) still present"
        print("✓")
        
        print("  fz integration tests passed!\n")
        
    except ImportError:
        print("  fz module not installed - skipping integration tests")
        print("  (Install with: pip install git+https://github.com/Funz/fz.git)\n")


def main():
    """Run all tests."""
    print("=" * 70)
    print("fz-Cast3m Plugin Test Suite")
    print("=" * 70)
    print()
    
    # Change to repository root if needed
    if not os.path.exists(".fz"):
        if os.path.exists("../fz-cast3m/.fz"):
            os.chdir("../fz-cast3m")
        else:
            print("Error: Could not find .fz directory")
            print("Please run this script from the fz-cast3m repository root")
            return 1
    
    try:
        test_model_files()
        test_calculator_files()
        test_calculator_scripts()
        test_example_files()
        test_with_fz()
        
        print("=" * 70)
        print("All tests passed! ✓")
        print("=" * 70)
        return 0
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
