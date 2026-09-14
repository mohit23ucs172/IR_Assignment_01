"""
Task 2: Regex-based Preprocessing Pipeline
Normalize repeated characters in social media posts using regex only.
Transform 'goooood' -> 'good', 'soooo' -> 'so', etc.
"""

import re
import os
import sys
import time
import pandas as pd
from pathlib import Path
from typing import List, Dict, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import (load_csv, save_csv, print_table, measure_time, 
                   create_bar_chart, print_section, ensure_output_dir,
                   format_time)


class RegexNormalizer:
    """Normalize repeated characters using regex patterns"""
    
    def __init__(self, dataset_path: str, output_dir: str = "../output"):
        """
        Initialize regex normalizer
        
        Args:
            dataset_path: Path to posts with repeated characters CSV
            output_dir: Output directory for results
        """
        self.dataset_path = dataset_path
        self.output_dir = output_dir
        self.posts_df = None
        self.results = []
        
        # Regex pattern to match repeated characters (3 or more)
        self.repeat_pattern = re.compile(r'(.)\1{2,}')
        
        ensure_output_dir(self.output_dir)
    
    def load_data(self) -> bool:
        """Load posts with repeated characters"""
        self.posts_df = load_csv(self.dataset_path)
        if self.posts_df is None:
            return False
        print(f"âœ“ Loaded {len(self.posts_df)} posts from dataset")
        return True
    
    def normalize_text(self, text: str) -> str:
        """
        Normalize repeated characters in text using regex
        
        Rules:
        - Replace 3+ consecutive identical characters with just 2
        - Preserves other text exactly as is
        
        Args:
            text: Input text with repeated characters
            
        Returns:
            Normalized text with reduced repetitions
        """
        # Pattern explanation:
        # (.)    - Capture any single character
        # \1{2,} - Followed by 2 or more repetitions of that character
        # Replace with \1\1 (keep just 2 occurrences)
        
        normalized = self.repeat_pattern.sub(r'\1\1', text)
        return normalized
    
    def count_repeated_chars(self, text: str) -> int:
        """
        Count number of repeated character groups in text
        
        Args:
            text: Input text
            
        Returns:
            Number of repeated character sequences found
        """
        return len(self.repeat_pattern.findall(text))
    
    def extract_repeated_patterns(self, text: str) -> List[str]:
        """
        Extract all repeated character patterns from text
        
        Args:
            text: Input text
            
        Returns:
            List of repeated patterns found
        """
        # Find all matches with their context
        patterns = []
        for match in re.finditer(r'(.)\1{2,}', text):
            patterns.append(match.group(0))
        return patterns
    
    def calculate_reduction(self, original: str, normalized: str) -> int:
        """
        Calculate character reduction from normalization
        
        Args:
            original: Original text
            normalized: Normalized text
            
        Returns:
            Number of characters removed
        """
        return len(original) - len(normalized)
    
    def process_post(self, post_id: int, original_text: str) -> Dict:
        """
        Process single post and normalize repeated characters
        
        Args:
            post_id: Post ID
            original_text: Original post text
            
        Returns:
            Dictionary with processing results
        """
        normalized_text = self.normalize_text(original_text)
        repeated_count = self.count_repeated_chars(original_text)
        char_reduction = self.calculate_reduction(original_text, normalized_text)
        repeated_patterns = self.extract_repeated_patterns(original_text)
        
        return {
            'id': post_id,
            'original_post': original_text,
            'normalized_post': normalized_text,
            'repeated_char_count': repeated_count,
            'chars_removed': char_reduction,
            'char_reduction_percent': (char_reduction / len(original_text) * 100) if len(original_text) > 0 else 0,
            'repeated_patterns': ', '.join(repeated_patterns) if repeated_patterns else 'None'
        }
    
    def run_normalization(self) -> bool:
        """Run normalization on all posts"""
        print_section("RUNNING REGEX NORMALIZATION")
        
        if not self.load_data():
            return False
        
        print("Normalizing posts using regex pipeline...\n")
        
        start_time = time.time()
        
        for idx, row in self.posts_df.iterrows():
            result = self.process_post(row['id'], row['original_post'])
            self.results.append(result)
            
            if (idx + 1) % 25 == 0:
                print(f"  Processed {idx + 1}/{len(self.posts_df)} posts")
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print(f"\nâœ“ Normalization complete! ({format_time(processing_time)})")
        return True
    
    def save_results(self) -> bool:
        """Save normalization results to CSV"""
        if not self.results:
            print("No results to save")
            return False
        
        results_df = pd.DataFrame(self.results)
        output_file = os.path.join(self.output_dir, 'regex_results.csv')
        
        save_csv(results_df, output_file)
        return True
    
    def generate_statistics(self) -> Dict:
        """Generate normalization statistics"""
        if not self.results:
            return {}
        
        results_df = pd.DataFrame(self.results)
        
        stats = {
            'total_posts': len(results_df),
            'posts_with_repetitions': len(results_df[results_df['repeated_char_count'] > 0]),
            'total_char_reduction': int(results_df['chars_removed'].sum()),
            'avg_chars_removed_per_post': results_df['chars_removed'].mean(),
            'max_chars_removed': int(results_df['chars_removed'].max()),
            'avg_reduction_percent': results_df['char_reduction_percent'].mean(),
            'max_reduction_percent': results_df['char_reduction_percent'].max(),
            'total_repeated_sequences': int(results_df['repeated_char_count'].sum())
        }
        
        return stats
    
    def generate_graphs(self) -> None:
        """Generate visualization graphs"""
        if not self.results:
            print("No results for graphing")
            return
        
        results_df = pd.DataFrame(self.results)
        graphs_dir = os.path.join(self.output_dir, 'graphs')
        ensure_output_dir(graphs_dir)
        
        # Graph: Character reduction distribution
        reduction_data = {
            'No Reduction': len(results_df[results_df['chars_removed'] == 0]),
            '1-5 chars': len(results_df[(results_df['chars_removed'] > 0) & (results_df['chars_removed'] <= 5)]),
            '6-10 chars': len(results_df[(results_df['chars_removed'] > 5) & (results_df['chars_removed'] <= 10)]),
            '10+ chars': len(results_df[results_df['chars_removed'] > 10])
        }
        create_bar_chart(
            reduction_data,
            title='Character Reduction Distribution',
            xlabel='Reduction Range',
            ylabel='Number of Posts',
            filepath=os.path.join(graphs_dir, 'char_reduction.png')
        )
    
    def print_examples(self, num_examples: int = 10) -> None:
        """Print example transformations"""
        if not self.results:
            return
        
        print_section("EXAMPLE TRANSFORMATIONS")
        
        # Filter posts with actual changes
        changed_posts = [r for r in self.results if r['chars_removed'] > 0]
        
        if not changed_posts:
            print("No posts with character repetitions found")
            return
        
        # Sort by character reduction
        changed_posts.sort(key=lambda x: x['chars_removed'], reverse=True)
        
        # Show top examples
        examples_to_show = changed_posts[:min(num_examples, len(changed_posts))]
        
        table_data = []
        for post in examples_to_show:
            table_data.append({
                'ID': post['id'],
                'Original': post['original_post'][:40],
                'Normalized': post['normalized_post'][:40],
                'Chars Removed': post['chars_removed'],
                'Patterns': post['repeated_patterns'][:30]
            })
        
        print_table(table_data, title="Top 10 Examples of Repeated Character Normalization")
    
    def print_detailed_example(self, post_id: int = None) -> None:
        """Print detailed example of single post transformation"""
        print_section("DETAILED TRANSFORMATION EXAMPLE")
        
        if post_id is None and self.results:
            # Find post with most changes
            post = max(self.results, key=lambda x: x['chars_removed'])
        elif post_id:
            post = next((r for r in self.results if r['id'] == post_id), None)
        else:
            print("No posts available")
            return
        
        if not post:
            print("Post not found")
            return
        
        print(f"\nPost ID: {post['id']}")
        print(f"\nOriginal:   {post['original_post']}")
        print(f"Normalized: {post['normalized_post']}")
        print(f"\nRepeated Patterns Found: {post['repeated_patterns']}")
        print(f"Character Reduction: {post['chars_removed']} chars ({post['char_reduction_percent']:.1f}%)")
        
        # Show character-by-character comparison
        print("\nCharacter-by-character breakdown:")
        print(f"  Original length:   {len(post['original_post'])} characters")
        print(f"  Normalized length: {len(post['normalized_post'])} characters")
        print(f"  Reduction:         {post['chars_removed']} characters ({post['char_reduction_percent']:.1f}%)")
    
    def print_summary(self) -> None:
        """Print normalization summary"""
        if not self.results:
            print("No results to display")
            return
        
        print_section("REGEX NORMALIZATION SUMMARY")
        
        stats = self.generate_statistics()
        
        print(f"Total Posts Processed:          {stats['total_posts']}")
        print(f"Posts with Repetitions:         {stats['posts_with_repetitions']}")
        print(f"Posts without Changes:          {stats['total_posts'] - stats['posts_with_repetitions']}")
        print(f"\nTotal Character Reduction:      {stats['total_char_reduction']} characters")
        print(f"Average Reduction per Post:     {stats['avg_chars_removed_per_post']:.2f} characters")
        print(f"Maximum Reduction in Single Post: {stats['max_chars_removed']} characters")
        print(f"\nAverage Reduction Percentage:   {stats['avg_reduction_percent']:.2f}%")
        print(f"Maximum Reduction Percentage:   {stats['max_reduction_percent']:.2f}%")
        print(f"\nTotal Repeated Sequences Found: {stats['total_repeated_sequences']}")
        
        # Additional insights
        results_df = pd.DataFrame(self.results)
        
        print("\n" + "="*80)
        print("  CHARACTER REDUCTION BREAKDOWN")
        print("="*80 + "\n")
        
        no_change = len(results_df[results_df['chars_removed'] == 0])
        light = len(results_df[(results_df['chars_removed'] > 0) & (results_df['chars_removed'] <= 5)])
        moderate = len(results_df[(results_df['chars_removed'] > 5) & (results_df['chars_removed'] <= 10)])
        heavy = len(results_df[results_df['chars_removed'] > 10])
        
        print(f"No reduction:                   {no_change} posts ({no_change/len(results_df)*100:.1f}%)")
        print(f"Light reduction (1-5 chars):    {light} posts ({light/len(results_df)*100:.1f}%)")
        print(f"Moderate reduction (6-10):      {moderate} posts ({moderate/len(results_df)*100:.1f}%)")
        print(f"Heavy reduction (10+ chars):    {heavy} posts ({heavy/len(results_df)*100:.1f}%)")


def main():
    """Main execution"""
    # Get base directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dataset_path = os.path.join(base_dir, 'dataset', 'repeated_char_posts.csv')
    output_dir = os.path.join(base_dir, 'output')
    
    # Initialize and run normalizer
    normalizer = RegexNormalizer(dataset_path, output_dir)
    
    if normalizer.run_normalization():
        normalizer.save_results()
        normalizer.generate_graphs()
        normalizer.print_summary()
        normalizer.print_examples(10)
        normalizer.print_detailed_example()
        print("\nâœ“ Regex normalization complete!")
        return True
    else:
        print("âœ— Normalization failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

