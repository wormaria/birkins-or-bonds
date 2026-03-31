"""
main.py — Run the entire Birkins or Bonds pipeline.

Usage:
    python -m src.main
"""

import sys
from pathlib import Path

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data_collection import save_datasets
from src.analysis import run_full_analysis
from src.visualizations import generate_all_charts


def main():
    print("=" * 60)
    print("  BIRKINS OR BONDS")
    print("  Luxury Handbags as Alternative Investments")
    print("=" * 60)

    # Step 1: Collect & build datasets
    print("\n📦 Step 1: Building datasets...")
    save_datasets()

    # Step 2: Run quantitative analysis
    print("\n📊 Step 2: Running analysis...")
    run_full_analysis()

    # Step 3: Generate visualizations
    print("\n🎨 Step 3: Generating charts...")
    generate_all_charts()

    print("\n" + "=" * 60)
    print("  ✅ Pipeline complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
