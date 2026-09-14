"""
Task 1: Tokenizer Analysis
Compare NLTK word_tokenize, NLTK TweetTokenizer, and spaCy tokenizer
on informal English social media posts.
"""

import re
import os
import sys
import time
import emoji
import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple

import nltk
from nltk.tokenize import word_tokenize, TweetTokenizer
import spacy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import (load_csv, save_csv, print_table, measure_time, 
                   create_bar_chart, create_comparison_chart, print_section,
                   ensure_output_dir, calculate_statistics)

# Download NLTK data if not already present
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)


class TokenizerAnalyzer:
    """Analyze and compare different tokenization methods"""
    
    def __init__(self, dataset_path: str, output_dir: str = "../output"):
        """
        Initialize tokenizer analyzer
        
        Args:
            dataset_path: Path to social media posts CSV
            output_dir: Output directory for results
        """
        self.dataset_path = dataset_path
        self.output_dir = output_dir
        self.posts_df = None
        self.results = []
        self.tokenizers_results = {
            'nltk_word': [],
            'nltk_tweet': [],
            'spacy': []
        }
        
        # Initialize tokenizers
        self.nltk_word_tokenizer = word_tokenize
        self.nltk_tweet_tokenizer = TweetTokenizer()
        
        # Load spaCy model with fallback
        self.spacy_nlp = None
        try:
            self.spacy_nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("[!] spaCy model 'en_core_web_sm' not found.")
            print("[!] Using blank spaCy model as fallback...")
            self.spacy_nlp = spacy.blank("en")
        
        ensure_output_dir(self.output_dir)
    
    def load_data(self) -> bool:
        """Load social media posts dataset"""
        self.posts_df = load_csv(self.dataset_path)
        if self.posts_df is None:
            return False
        print(f"[+] Loaded {len(self.posts_df)} posts from dataset")
        return True
    
    def tokenize_with_nltk_word(self, text: str) -> List[str]:
        """Tokenize using NLTK word_tokenize"""
        return word_tokenize(text)
    
    def tokenize_with_nltk_tweet(self, text: str) -> List[str]:
        """Tokenize using NLTK TweetTokenizer"""
        return self.nltk_tweet_tokenizer.tokenize(text)
    
    def tokenize_with_spacy(self, text: str) -> List[str]:
        """Tokenize using spaCy"""
        doc = self.spacy_nlp(text)
        return [token.text for token in doc]
    
    def count_hashtags(self, tokens: List[str]) -> int:
        """Count hashtags in token list"""
        return sum(1 for token in tokens if token.startswith('#'))
    
    def count_mentions(self, tokens: List[str]) -> int:
        """Count @mentions in token list"""
        return sum(1 for token in tokens if token.startswith('@'))
    
    def count_urls(self, tokens: List[str]) -> int:
        """Count URLs in token list"""
        url_pattern = r'https?://|www\.'
        return sum(1 for token in tokens if re.match(url_pattern, token))
    
    def count_emojis(self, text: str) -> int:
        """Count emojis in text"""
        return len(emoji.emoji_list(text))
    
    def count_punctuation(self, tokens: List[str]) -> int:
        """Count punctuation tokens"""
        punct_pattern = r'^[!\"#$%&\'()*+,\-./:;<=>?@\[\\\]^_`{|}~]+$'
        return sum(1 for token in tokens if re.match(punct_pattern, token))
    
    def analyze_post(self, post_id: int, post_text: str) -> Dict:
        """
        Analyze single post with all tokenizers
        
        Args:
            post_id: Post ID
            post_text: Post text content
            
        Returns:
            Dictionary with analysis results
        """
        result = {'id': post_id, 'text': post_text[:50] + '...' if len(post_text) > 50 else post_text}
        
        # NLTK word_tokenize
        nltk_word_tokens = self.tokenize_with_nltk_word(post_text.lower())
        result['nltk_word_tokens'] = len(nltk_word_tokens)
        result['nltk_word_hashtags'] = self.count_hashtags(nltk_word_tokens)
        result['nltk_word_mentions'] = self.count_mentions(nltk_word_tokens)
        result['nltk_word_urls'] = self.count_urls(nltk_word_tokens)
        result['nltk_word_punctuation'] = self.count_punctuation(nltk_word_tokens)
        
        # NLTK TweetTokenizer
        nltk_tweet_tokens = self.tokenize_with_nltk_tweet(post_text)
        result['nltk_tweet_tokens'] = len(nltk_tweet_tokens)
        result['nltk_tweet_hashtags'] = self.count_hashtags(nltk_tweet_tokens)
        result['nltk_tweet_mentions'] = self.count_mentions(nltk_tweet_tokens)
        result['nltk_tweet_urls'] = self.count_urls(nltk_tweet_tokens)
        result['nltk_tweet_punctuation'] = self.count_punctuation(nltk_tweet_tokens)
        
        # spaCy tokenizer
        spacy_tokens = self.tokenize_with_spacy(post_text)
        result['spacy_tokens'] = len(spacy_tokens)
        result['spacy_hashtags'] = self.count_hashtags(spacy_tokens)
        result['spacy_mentions'] = self.count_mentions(spacy_tokens)
        result['spacy_urls'] = self.count_urls(spacy_tokens)
        result['spacy_punctuation'] = self.count_punctuation(spacy_tokens)
        
        # Emoji count (same for all)
        result['emoji_count'] = self.count_emojis(post_text)
        
        return result
    
    def run_analysis(self) -> bool:
        """Run tokenizer analysis on all posts"""
        print_section("RUNNING TOKENIZER ANALYSIS")
        
        if not self.load_data():
            return False
        
        print("Analyzing posts with all tokenizers...\n")
        
        start_time = time.time()
        
        for idx, row in self.posts_df.iterrows():
            result = self.analyze_post(row['id'], row['post'])
            self.results.append(result)
            
            if (idx + 1) % 20 == 0:
                print(f"  Processed {idx + 1}/{len(self.posts_df)} posts")
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print(f"\nâœ“ Analysis complete! ({processing_time:.2f}s)")
        return True
    
    def generate_comparison_table(self) -> pd.DataFrame:
        """Generate summary comparison table"""
        if not self.results:
            return None
        
        results_df = pd.DataFrame(self.results)
        
        # Calculate averages
        comparison = {
            'Tokenizer': ['NLTK Word', 'NLTK Tweet', 'spaCy'],
            'Avg Tokens': [
                results_df['nltk_word_tokens'].mean(),
                results_df['nltk_tweet_tokens'].mean(),
                results_df['spacy_tokens'].mean()
            ],
            'Hashtags Preserved': [
                results_df['nltk_word_hashtags'].sum(),
                results_df['nltk_tweet_hashtags'].sum(),
                results_df['spacy_hashtags'].sum()
            ],
            'Mentions Preserved': [
                results_df['nltk_word_mentions'].sum(),
                results_df['nltk_tweet_mentions'].sum(),
                results_df['spacy_mentions'].sum()
            ],
            'URLs Preserved': [
                results_df['nltk_word_urls'].sum(),
                results_df['nltk_tweet_urls'].sum(),
                results_df['spacy_urls'].sum()
            ],
            'Punctuation Tokens': [
                results_df['nltk_word_punctuation'].mean(),
                results_df['nltk_tweet_punctuation'].mean(),
                results_df['spacy_punctuation'].mean()
            ]
        }
        
        return pd.DataFrame(comparison)
    
    def save_results(self) -> bool:
        """Save tokenizer results to CSV"""
        if not self.results:
            print("No results to save")
            return False
        
        results_df = pd.DataFrame(self.results)
        output_file = os.path.join(self.output_dir, 'tokenizer_results.csv')
        
        save_csv(results_df, output_file)
        
        # Save comparison table
        comparison_df = self.generate_comparison_table()
        comparison_file = os.path.join(self.output_dir, 'tokenizer_comparison.csv')
        save_csv(comparison_df, comparison_file)
        
        return True
    
    def generate_graphs(self) -> None:
        """Generate visualization graphs"""
        if not self.results:
            print("No results for graphing")
            return
        
        results_df = pd.DataFrame(self.results)
        graphs_dir = os.path.join(self.output_dir, 'graphs')
        ensure_output_dir(graphs_dir)
        
        # Graph 1: Token count comparison
        token_data = {
            'NLTK Word': int(results_df['nltk_word_tokens'].mean()),
            'NLTK Tweet': int(results_df['nltk_tweet_tokens'].mean()),
            'spaCy': int(results_df['spacy_tokens'].mean())
        }
        create_bar_chart(
            token_data,
            title='Average Token Count by Tokenizer',
            xlabel='Tokenizer',
            ylabel='Average Tokens per Post',
            filepath=os.path.join(graphs_dir, 'token_count.png')
        )
        
        # Graph 2: Emoji preservation
        emoji_data = {
            'Posts with Emojis': len(results_df[results_df['emoji_count'] > 0]),
            'Posts without Emojis': len(results_df[results_df['emoji_count'] == 0])
        }
        create_bar_chart(
            emoji_data,
            title='Emoji Presence in Dataset',
            xlabel='Category',
            ylabel='Number of Posts',
            filepath=os.path.join(graphs_dir, 'emoji_preservation.png')
        )
        
        # Graph 3: Hashtag analysis
        hashtag_data = {
            'NLTK Word': int(results_df['nltk_word_hashtags'].sum()),
            'NLTK Tweet': int(results_df['nltk_tweet_hashtags'].sum()),
            'spaCy': int(results_df['spacy_hashtags'].sum())
        }
        create_bar_chart(
            hashtag_data,
            title='Total Hashtags Preserved by Tokenizer',
            xlabel='Tokenizer',
            ylabel='Number of Hashtags Preserved',
            filepath=os.path.join(graphs_dir, 'hashtag_analysis.png')
        )
        
        # Graph 4: Tokenizer comparison (multi-metric)
        comparison_data = {
            'NLTK Word': {
                'Mentions': int(results_df['nltk_word_mentions'].sum()),
                'URLs': int(results_df['nltk_word_urls'].sum()),
                'Hashtags': int(results_df['nltk_word_hashtags'].sum())
            },
            'NLTK Tweet': {
                'Mentions': int(results_df['nltk_tweet_mentions'].sum()),
                'URLs': int(results_df['nltk_tweet_urls'].sum()),
                'Hashtags': int(results_df['nltk_tweet_hashtags'].sum())
            },
            'spaCy': {
                'Mentions': int(results_df['spacy_mentions'].sum()),
                'URLs': int(results_df['spacy_urls'].sum()),
                'Hashtags': int(results_df['spacy_hashtags'].sum())
            }
        }
        create_comparison_chart(
            comparison_data,
            title='Feature Preservation Across Tokenizers',
            xlabel='Feature Type',
            ylabel='Count',
            filepath=os.path.join(graphs_dir, 'tokenizer_comparison.png')
        )
        
        print_section("GRAPHS GENERATED")
    
    def print_summary(self) -> None:
        """Print analysis summary"""
        if not self.results:
            print("No results to display")
            return
        
        print_section("TOKENIZER ANALYSIS SUMMARY")
        
        results_df = pd.DataFrame(self.results)
        comparison_df = self.generate_comparison_table()
        
        print(f"Total Posts Analyzed: {len(results_df)}")
        print(f"Posts with Emojis: {len(results_df[results_df['emoji_count'] > 0])}")
        print(f"Posts with Hashtags: {len(results_df[results_df['nltk_tweet_hashtags'] > 0])}")
        print(f"Posts with Mentions: {len(results_df[results_df['nltk_tweet_mentions'] > 0])}")
        
        print_table(comparison_df, title="Tokenizer Comparison Summary")
        
        # Statistics
        print("\n" + "="*80)
        print("  DETAILED STATISTICS")
        print("="*80 + "\n")
        
        for tokenizer in ['nltk_word', 'nltk_tweet', 'spacy']:
            token_col = f'{tokenizer}_tokens'
            stats = calculate_statistics(results_df[token_col].tolist())
            
            tokenizer_name = {
                'nltk_word': 'NLTK Word Tokenizer',
                'nltk_tweet': 'NLTK Tweet Tokenizer',
                'spacy': 'spaCy Tokenizer'
            }[tokenizer]
            
            print(f"\n{tokenizer_name}:")
            print(f"  Mean Tokens:   {stats['mean']:.2f}")
            print(f"  Median Tokens: {stats['median']:.2f}")
            print(f"  Std Dev:       {stats['std_dev']:.2f}")
            print(f"  Min Tokens:    {int(stats['min'])}")
            print(f"  Max Tokens:    {int(stats['max'])}")


def main():
    """Main execution"""
    # Get base directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dataset_path = os.path.join(base_dir, 'dataset', 'social_media_posts.csv')
    output_dir = os.path.join(base_dir, 'output')
    
    # Initialize and run analyzer
    analyzer = TokenizerAnalyzer(dataset_path, output_dir)
    
    if analyzer.run_analysis():
        analyzer.save_results()
        analyzer.generate_graphs()
        analyzer.print_summary()
        print("\nâœ“ Tokenizer analysis complete!")
        return True
    else:
        print("âœ— Analysis failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

