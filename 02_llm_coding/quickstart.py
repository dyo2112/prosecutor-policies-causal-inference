#!/usr/bin/env python3
"""
Quick Start Script for Prosecutor Policy Coding
Sets up and runs a small test batch to validate the system
"""

import os
import sys
from pathlib import Path
import subprocess


def check_environment():
    """Check if environment is properly configured"""
    print("="*80)
    print("ENVIRONMENT CHECK")
    print("="*80)
    
    issues = []
    
    # Check Python version
    if sys.version_info < (3, 9):
        issues.append(f"Python 3.9+ required (you have {sys.version_info.major}.{sys.version_info.minor})")
    else:
        print("✓ Python version OK")
    
    # Check API key
    if not os.environ.get('ANTHROPIC_API_KEY'):
        issues.append("ANTHROPIC_API_KEY environment variable not set")
        print("✗ Missing API key")
        print("\n  Set your API key with:")
        print("  export ANTHROPIC_API_KEY='your-key-here'")
    else:
        print("✓ API key found")
    
    # Check required packages
    try:
        import anthropic
        print("✓ anthropic package installed")
    except ImportError:
        issues.append("anthropic package not installed")
        print("✗ anthropic package missing")
    
    try:
        import pypdf
        print("✓ pypdf installed")
    except ImportError:
        issues.append("pypdf not installed")
        print("✗ pypdf missing")
    
    try:
        import pdfplumber
        print("✓ pdfplumber installed")
    except ImportError:
        issues.append("pdfplumber not installed")
        print("✗ pdfplumber missing")
    
    try:
        from docx import Document
        print("✓ python-docx installed")
    except ImportError:
        issues.append("python-docx not installed")
        print("✗ python-docx missing")
    
    if issues:
        print("\n" + "="*80)
        print("SETUP REQUIRED")
        print("="*80)
        print("\nPlease fix these issues:\n")
        for issue in issues:
            print(f"  • {issue}")
        print("\nRun: pip install -r requirements.txt")
        return False
    
    print("\n✓ All checks passed!")
    return True


def get_user_input():
    """Get configuration from user"""
    print("\n" + "="*80)
    print("CONFIGURATION")
    print("="*80)
    
    config = {}
    
    # Documents directory
    print("\nEnter the path to your folder containing prosecutor policy documents:")
    print("(e.g., /Users/dvir/Documents/prosecutor_policies)")
    config['documents_dir'] = input("Documents folder: ").strip()
    
    if not Path(config['documents_dir']).exists():
        print(f"Warning: Directory {config['documents_dir']} does not exist!")
        return None
    
    # Metadata file
    print("\nEnter the path to your metadata CSV file:")
    print("(e.g., /Users/dvir/Documents/prosecutor_policies_metadata.csv)")
    config['metadata_file'] = input("Metadata file: ").strip()
    
    if not Path(config['metadata_file']).exists():
        print(f"Warning: File {config['metadata_file']} does not exist!")
        return None
    
    # Output directory
    print("\nWhere should output files be saved?")
    print("(e.g., /Users/dvir/Documents/output)")
    config['output_dir'] = input("Output directory: ").strip()
    
    output_path = Path(config['output_dir'])
    output_path.mkdir(exist_ok=True, parents=True)
    
    config['output_file'] = str(output_path / "coded_prosecutor_policies.csv")
    
    return config


def run_test_batch(config):
    """Run a small test batch"""
    print("\n" + "="*80)
    print("RUNNING TEST BATCH (10 documents)")
    print("="*80)
    
    # Create a temporary test script
    test_script = f"""
import sys
sys.path.insert(0, '/home/claude')

from prosecutor_policy_coder import PipelineManager

pipeline = PipelineManager(
    documents_dir="{config['documents_dir']}",
    metadata_file="{config['metadata_file']}",
    output_file="{config['output_file']}"
)

pipeline.run_pipeline(batch_size=10, max_docs=10)

print("\\n" + "="*80)
print("TEST BATCH COMPLETE")
print("="*80)
print(f"Results saved to: {config['output_file']}")
print("\\nNext steps:")
print("1. Review the output file")
print("2. Check coding_pipeline.log for any errors")
print("3. If satisfied, run full pipeline with max_docs=None")
"""
    
    # Write and execute
    with open('/tmp/test_batch.py', 'w') as f:
        f.write(test_script)
    
    try:
        subprocess.run([sys.executable, '/tmp/test_batch.py'], check=True)
        return True
    except subprocess.CalledProcessError:
        print("\nError running test batch. Check coding_pipeline.log for details.")
        return False


def main():
    """Main entry point"""
    print("""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║              PROSECUTOR POLICY DOCUMENT CODING SYSTEM                         ║
║                          Quick Start Setup                                    ║
║                                                                               ║
║                    CLJC, UC Berkeley School of Law                            ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
""")
    
    # Check environment
    if not check_environment():
        print("\nSetup incomplete. Please fix issues and try again.")
        return
    
    # Get configuration
    print("\nLet's configure your analysis...")
    config = get_user_input()
    
    if not config:
        print("\nConfiguration failed. Please check paths and try again.")
        return
    
    # Confirm with user
    print("\n" + "="*80)
    print("CONFIGURATION SUMMARY")
    print("="*80)
    print(f"Documents folder: {config['documents_dir']}")
    print(f"Metadata file: {config['metadata_file']}")
    print(f"Output directory: {config['output_dir']}")
    print(f"Output file: {config['output_file']}")
    
    print("\nReady to run test batch with 10 documents.")
    print("This will cost approximately $0.30 in API credits.")
    
    response = input("\nProceed? (y/n): ").strip().lower()
    
    if response != 'y':
        print("\nCancelled. Run this script again when ready.")
        return
    
    # Run test
    success = run_test_batch(config)
    
    if success:
        print("\n" + "="*80)
        print("SUCCESS!")
        print("="*80)
        print(f"\nTest results saved to: {config['output_file']}")
        print("\nNext steps:")
        print("1. Review the coded data:")
        print(f"   pandas.read_csv('{config['output_file']}')")
        print("\n2. Run validation:")
        print(f"   python validate_coding.py")
        print("\n3. If satisfied, run full pipeline:")
        print(f"   python prosecutor_policy_coder.py")
        print("   (Remember to set max_docs=None in the script)")
    else:
        print("\nTest batch encountered errors. Check the logs.")


if __name__ == "__main__":
    main()
