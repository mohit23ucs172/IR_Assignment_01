"""
Information Retrieval Assignment - Main Entry Point
Menu-driven interface for running tokenizer analysis and regex normalization
"""

import os
import sys
import subprocess
from pathlib import Path

# Add code directory to path
code_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, code_dir)

from utils import print_section


class Menu:
    """Menu system for assignment"""
    
    def __init__(self):
        self.base_dir = os.path.dirname(code_dir)
        self.code_dir = code_dir
        self.running = True
    
    def clear_screen(self) -> None:
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_banner(self) -> None:
        """Print application banner"""
        print("\n")
        print("â•”" + "=" * 78 + "â•—")
        print("â•‘" + " " * 78 + "â•‘")
        print("â•‘" + "  INFORMATION RETRIEVAL ASSIGNMENT - Menu System".center(78) + "â•‘")
        print("â•‘" + "  Tokenizer Analysis & Regex Preprocessing Pipeline".center(78) + "â•‘")
        print("â•‘" + " " * 78 + "â•‘")
        print("â•š" + "=" * 78 + "â•")
        print()
    
    def print_menu(self) -> None:
        """Print main menu"""
        print_section("MAIN MENU")
        print("1. Run Tokenizer Analysis (Task 1)")
        print("   - Compare NLTK word_tokenize, NLTK TweetTokenizer, and spaCy")
        print("   - Analyze effectiveness on social media posts")
        print()
        print("2. Run Regex Normalization (Task 2)")
        print("   - Normalize repeated characters in posts")
        print("   - Transform 'goooood' -> 'good'")
        print()
        print("3. Run Both Tasks")
        print("   - Execute tokenizer analysis followed by regex normalization")
        print()
        print("4. View Results Summary")
        print("   - Display previously generated results")
        print()
        print("5. View Output Folder")
        print("   - Open output directory in file explorer")
        print()
        print("0. Exit")
        print()
    
    def run_tokenizer_analysis(self) -> bool:
        """Execute tokenizer analysis"""
        print_section("TASK 1: TOKENIZER ANALYSIS")
        print("Starting tokenizer analysis...\n")
        
        tokenizer_script = os.path.join(self.code_dir, 'tokenizer_analysis.py')
        
        try:
            result = subprocess.run(
                [sys.executable, tokenizer_script],
                cwd=self.code_dir,
                capture_output=False
            )
            return result.returncode == 0
        except Exception as e:
            print(f"âœ— Error running tokenizer analysis: {e}")
            return False
    
    def run_regex_normalization(self) -> bool:
        """Execute regex normalization"""
        print_section("TASK 2: REGEX NORMALIZATION")
        print("Starting regex normalization...\n")
        
        normalizer_script = os.path.join(self.code_dir, 'regex_normalizer.py')
        
        try:
            result = subprocess.run(
                [sys.executable, normalizer_script],
                cwd=self.code_dir,
                capture_output=False
            )
            return result.returncode == 0
        except Exception as e:
            print(f"âœ— Error running regex normalization: {e}")
            return False
    
    def run_both_tasks(self) -> None:
        """Execute both tasks sequentially"""
        print_section("RUNNING BOTH TASKS")
        
        print("\n[1/2] Running Tokenizer Analysis...")
        tokenizer_success = self.run_tokenizer_analysis()
        
        print("\n\n[2/2] Running Regex Normalization...")
        normalizer_success = self.run_regex_normalization()
        
        print_section("EXECUTION SUMMARY")
        print(f"Tokenizer Analysis:    {'âœ“ SUCCESS' if tokenizer_success else 'âœ— FAILED'}")
        print(f"Regex Normalization:   {'âœ“ SUCCESS' if normalizer_success else 'âœ— FAILED'}")
        
        if tokenizer_success and normalizer_success:
            print("\nâœ“ All tasks completed successfully!")
        else:
            print("\nâš  Some tasks failed. Please check the output above.")
    
    def view_results_summary(self) -> None:
        """View previously generated results"""
        output_dir = os.path.join(self.base_dir, 'output')
        
        print_section("RESULTS SUMMARY")
        
        if not os.path.exists(output_dir):
            print("Output directory not found. Please run the tasks first.")
            return
        
        # Check for result files
        tokenizer_results = os.path.join(output_dir, 'tokenizer_results.csv')
        tokenizer_comparison = os.path.join(output_dir, 'tokenizer_comparison.csv')
        regex_results = os.path.join(output_dir, 'regex_results.csv')
        
        print("Generated Output Files:\n")
        
        if os.path.exists(tokenizer_results):
            size_mb = os.path.getsize(tokenizer_results) / 1024 / 1024
            print(f"  âœ“ tokenizer_results.csv ({size_mb:.2f} MB)")
        else:
            print(f"  âœ— tokenizer_results.csv (not generated)")
        
        if os.path.exists(tokenizer_comparison):
            size_mb = os.path.getsize(tokenizer_comparison) / 1024 / 1024
            print(f"  âœ“ tokenizer_comparison.csv ({size_mb:.2f} MB)")
        else:
            print(f"  âœ— tokenizer_comparison.csv (not generated)")
        
        if os.path.exists(regex_results):
            size_mb = os.path.getsize(regex_results) / 1024 / 1024
            print(f"  âœ“ regex_results.csv ({size_mb:.2f} MB)")
        else:
            print(f"  âœ— regex_results.csv (not generated)")
        
        # Check for graphs
        graphs_dir = os.path.join(output_dir, 'graphs')
        if os.path.exists(graphs_dir):
            graphs = [f for f in os.listdir(graphs_dir) if f.endswith('.png')]
            if graphs:
                print(f"\n  Generated Graphs ({len(graphs)}):")
                for graph in sorted(graphs):
                    print(f"    â€¢ {graph}")
        
        print("\nDataset Files:")
        dataset_dir = os.path.join(self.base_dir, 'dataset')
        if os.path.exists(dataset_dir):
            datasets = [f for f in os.listdir(dataset_dir) if f.endswith('.csv')]
            for dataset in sorted(datasets):
                filepath = os.path.join(dataset_dir, dataset)
                size_kb = os.path.getsize(filepath) / 1024
                print(f"  âœ“ {dataset} ({size_kb:.2f} KB)")
    
    def open_output_folder(self) -> None:
        """Open output folder in file explorer"""
        output_dir = os.path.join(self.base_dir, 'output')
        
        if not os.path.exists(output_dir):
            print(f"Output directory does not exist: {output_dir}")
            return
        
        try:
            if os.name == 'nt':  # Windows
                os.startfile(output_dir)
            elif sys.platform == 'darwin':  # macOS
                os.system(f'open "{output_dir}"')
            else:  # Linux
                os.system(f'xdg-open "{output_dir}"')
            print(f"âœ“ Opened: {output_dir}")
        except Exception as e:
            print(f"âœ— Error opening folder: {e}")
    
    def get_choice(self) -> str:
        """Get user menu choice"""
        while True:
            choice = input("\nEnter your choice (0-5): ").strip()
            if choice in ['0', '1', '2', '3', '4', '5']:
                return choice
            print("Invalid choice. Please enter 0-5.")
    
    def run(self) -> None:
        """Run menu system"""
        self.clear_screen()
        self.print_banner()
        
        print("Welcome to the Information Retrieval Assignment Menu!")
        print("This system allows you to run tokenizer analysis and regex preprocessing.\n")
        
        while self.running:
            self.print_menu()
            choice = self.get_choice()
            
            if choice == '0':
                print("\n" + "="*80)
                print("  Thank you for using Information Retrieval Assignment!")
                print("  For more information, see README.md")
                print("="*80 + "\n")
                self.running = False
            
            elif choice == '1':
                self.run_tokenizer_analysis()
                input("\nPress Enter to continue...")
            
            elif choice == '2':
                self.run_regex_normalization()
                input("\nPress Enter to continue...")
            
            elif choice == '3':
                self.run_both_tasks()
                input("\nPress Enter to continue...")
            
            elif choice == '4':
                self.view_results_summary()
                input("\nPress Enter to continue...")
            
            elif choice == '5':
                self.open_output_folder()
                input("\nPress Enter to continue...")
            
            # Clear screen for next iteration
            if self.running:
                self.clear_screen()
                self.print_banner()


def main():
    """Main entry point"""
    try:
        menu = Menu()
        menu.run()
    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nâœ— Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

