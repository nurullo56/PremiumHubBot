#!/usr/bin/env python3
"""
Database Code Consolidator
Consolidates all Python files from bot/database/ into a single .txt file
Each file is separated with clear headers showing the file path
"""

import os
from pathlib import Path
from datetime import datetime


def consolidate_database_code(
    database_dir: str = "bot/database",
    output_file: str = "database_consolidated.txt"
):
    """
    Consolidate all .py files from database directory into single txt file.
    
    Args:
        database_dir: Path to database directory
        output_file: Output file name
    """
    
    # Check if directory exists
    if not os.path.exists(database_dir):
        print(f"❌ Directory not found: {database_dir}")
        return
    
    # Collect all .py files
    py_files = []
    for root, dirs, files in os.walk(database_dir):
        # Skip __pycache__ directories
        dirs[:] = [d for d in dirs if d != '__pycache__']
        
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                py_files.append(file_path)
    
    # Sort files for consistent output
    py_files.sort()
    
    if not py_files:
        print(f"❌ No Python files found in {database_dir}")
        return
    
    print(f"📂 Found {len(py_files)} Python files")
    
    # Generate consolidated file
    separator = "=" * 80
    
    with open(output_file, 'w', encoding='utf-8') as outfile:
        # Write header
        outfile.write(f"{separator}\n")
        outfile.write(f"DATABASE CODE CONSOLIDATION\n")
        outfile.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        outfile.write(f"Source: {database_dir}/\n")
        outfile.write(f"Total files: {len(py_files)}\n")
        outfile.write(f"{separator}\n\n")
        
        # Write table of contents
        outfile.write("TABLE OF CONTENTS:\n")
        outfile.write("-" * 80 + "\n")
        for i, file_path in enumerate(py_files, 1):
            outfile.write(f"{i:2d}. {file_path}\n")
        outfile.write(f"\n{separator}\n\n\n")
        
        # Write each file
        for i, file_path in enumerate(py_files, 1):
            print(f"  [{i:2d}/{len(py_files)}] Processing: {file_path}")
            
            # File header
            outfile.write(f"\n{separator}\n")
            outfile.write(f"FILE {i}: {file_path}\n")
            outfile.write(f"{separator}\n\n")
            
            # File content
            try:
                with open(file_path, 'r', encoding='utf-8') as infile:
                    content = infile.read()
                    outfile.write(content)
                    
                    # Ensure file ends with newline
                    if not content.endswith('\n'):
                        outfile.write('\n')
                
                # Add spacing between files
                outfile.write(f"\n\n")
                
            except Exception as e:
                outfile.write(f"❌ ERROR READING FILE: {e}\n\n")
                print(f"    ⚠️ Error reading {file_path}: {e}")
        
        # Write footer
        outfile.write(f"\n{separator}\n")
        outfile.write(f"END OF CONSOLIDATION\n")
        outfile.write(f"Total files processed: {len(py_files)}\n")
        outfile.write(f"{separator}\n")
    
    # Get output file size
    file_size = os.path.getsize(output_file)
    if file_size < 1024:
        size_str = f"{file_size} bytes"
    elif file_size < 1024 * 1024:
        size_str = f"{file_size / 1024:.1f} KB"
    else:
        size_str = f"{file_size / (1024 * 1024):.1f} MB"
    
    print(f"\n✅ Consolidation complete!")
    print(f"📄 Output file: {output_file}")
    print(f"📊 File size: {size_str}")
    print(f"📝 Total files: {len(py_files)}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Consolidate database Python files into single txt file"
    )
    parser.add_argument(
        '--dir',
        default='bot/database',
        help='Database directory path (default: bot/database)'
    )
    parser.add_argument(
        '--output',
        default='database_consolidated.txt',
        help='Output file name (default: database_consolidated.txt)'
    )
    
    args = parser.parse_args()
    
    consolidate_database_code(args.dir, args.output)