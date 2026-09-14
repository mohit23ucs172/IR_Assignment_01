"""
Setup and execution orchestrator for the Information Retrieval Assignment
Coordinates all tasks and generates complete project output
"""

import os
import sys
import subprocess
import time
from pathlib import Path


class ProjectExecutor:
    """Orchestrate project setup and execution"""
    
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.code_dir = os.path.join(self.base_dir, 'code')
        self.output_dir = os.path.join(self.base_dir, 'output')
    
    def run_command(self, cmd, description):
        """Run a command and report status"""
        print(f"\n{'='*80}")
        print(f"  {description}")
        print(f"{'='*80}\n")
        
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=self.code_dir,
                capture_output=False
            )
            if result.returncode == 0:
                print(f"\nâœ“ {description} - SUCCESS")
                return True
            else:
                print(f"\nâœ— {description} - FAILED")
                return False
        except Exception as e:
            print(f"\nâœ— Error: {e}")
            return False
    
    def setup_project(self):
        """Setup project structure and dependencies"""
        print("\n" + "="*80)
        print("  INFORMATION RETRIEVAL ASSIGNMENT - SETUP")
        print("="*80)
        
        # Ensure output directories exist
        os.makedirs(os.path.join(self.output_dir, 'graphs'), exist_ok=True)
        print("\nâœ“ Project directories verified")
        
        # Install dependencies
        print("\nInstalling Python dependencies...")
        subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '-q', '-r', 'requirements.txt'],
            cwd=self.code_dir,
            capture_output=True
        )
        print("âœ“ Dependencies installed")
        
        # Download spaCy model
        print("Downloading spaCy language model...")
        subprocess.run(
            [sys.executable, '-m', 'spacy', 'download', 'en_core_web_sm', '-q'],
            capture_output=True
        )
        print("âœ“ spaCy model ready")
    
    def run_all_tasks(self):
        """Execute all analysis tasks"""
        print("\n" + "="*80)
        print("  EXECUTING ALL TASKS")
        print("="*80)
        
        tasks = [
            (f'{sys.executable} tokenizer_analysis.py', 'Task 1: Tokenizer Analysis'),
            (f'{sys.executable} regex_normalizer.py', 'Task 2: Regex Normalization'),
            (f'{sys.executable} generate_report.py', 'Report Generation')
        ]
        
        results = {}
        for cmd, description in tasks:
            results[description] = self.run_command(cmd, description)
            time.sleep(0.5)
        
        return results
    
    def verify_outputs(self):
        """Verify all expected output files exist"""
        print("\n" + "="*80)
        print("  VERIFYING OUTPUT FILES")
        print("="*80 + "\n")
        
        expected_files = {
            'CSV Results': [
                os.path.join(self.output_dir, 'tokenizer_results.csv'),
                os.path.join(self.output_dir, 'tokenizer_comparison.csv'),
                os.path.join(self.output_dir, 'regex_results.csv')
            ],
            'Graphs': [
                os.path.join(self.output_dir, 'graphs', 'token_count.png'),
                os.path.join(self.output_dir, 'graphs', 'emoji_preservation.png'),
                os.path.join(self.output_dir, 'graphs', 'hashtag_analysis.png'),
                os.path.join(self.output_dir, 'graphs', 'tokenizer_comparison.png'),
                os.path.join(self.output_dir, 'graphs', 'char_reduction.png')
            ],
            'Report': [
                os.path.join(self.base_dir, 'report', 'report.docx')
            ],
            'Documentation': [
                os.path.join(self.base_dir, 'README.md')
            ]
        }
        
        all_good = True
        for category, files in expected_files.items():
            print(f"{category}:")
            for file_path in files:
                if os.path.exists(file_path):
                    size = os.path.getsize(file_path)
                    size_str = f"{size/1024:.1f}KB" if size < 1024*1024 else f"{size/(1024*1024):.1f}MB"
                    print(f"  âœ“ {os.path.basename(file_path)} ({size_str})")
                else:
                    print(f"  âœ— {os.path.basename(file_path)} - NOT FOUND")
                    all_good = False
            print()
        
        return all_good
    
    def print_summary(self, results):
        """Print execution summary"""
        print("\n" + "="*80)
        print("  EXECUTION SUMMARY")
        print("="*80 + "\n")
        
        for task, success in results.items():
            status = "âœ“ SUCCESS" if success else "âœ— FAILED"
            print(f"{task}: {status}")
        
        all_success = all(results.values())
        
        print("\n" + "="*80)
        if all_success:
            print("  âœ“ ALL TASKS COMPLETED SUCCESSFULLY!")
        else:
            print("  âš  SOME TASKS ENCOUNTERED ISSUES")
        print("="*80 + "\n")
        
        print("Project Location: " + self.base_dir)
        print("Output Directory: " + self.output_dir)
        print("README: " + os.path.join(self.base_dir, 'README.md'))
        print("\nTo run the menu system:")
        print(f"  python {os.path.join(self.code_dir, 'main.py')}")
        
        return all_success


def main():
    """Main execution"""
    executor = ProjectExecutor()
    
    # Setup
    executor.setup_project()
    
    # Run all tasks
    results = executor.run_all_tasks()
    
    # Verify outputs
    outputs_ok = executor.verify_outputs()
    
    # Summary
    success = executor.print_summary(results) and outputs_ok
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

