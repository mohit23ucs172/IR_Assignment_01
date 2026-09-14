"""
Utility functions for Information Retrieval Assignment
Includes CSV operations, table printing, timing, and graph generation
"""

import os
import csv
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from tabulate import tabulate
from typing import List, Dict, Tuple, Any


def load_csv(filepath: str) -> pd.DataFrame:
    """
    Load CSV file and return as pandas DataFrame
    
    Args:
        filepath: Path to CSV file
        
    Returns:
        DataFrame with CSV data
    """
    try:
        df = pd.read_csv(filepath)
        return df
    except FileNotFoundError:
        print(f"Error: File {filepath} not found")
        return None
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return None


def save_csv(data: pd.DataFrame, filepath: str) -> bool:
    """
    Save DataFrame to CSV file
    
    Args:
        data: DataFrame to save
        filepath: Path where to save CSV
        
    Returns:
        True if successful, False otherwise
    """
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        data.to_csv(filepath, index=False)
        print(f"âœ“ Saved: {filepath}")
        return True
    except Exception as e:
        print(f"Error saving CSV: {e}")
        return False


def print_table(data: List[Dict], headers: str = "keys", title: str = None) -> None:
    """
    Print data as formatted table using tabulate
    
    Args:
        data: List of dictionaries or list of lists
        headers: Header format (default "keys" for dict list)
        title: Optional title to print above table
    """
    if title:
        print(f"\n{'='*80}")
        print(f"  {title}")
        print(f"{'='*80}")
    
    if isinstance(data, pd.DataFrame):
        print(tabulate(data, headers='keys', tablefmt='grid', showindex=False))
    else:
        print(tabulate(data, headers=headers, tablefmt='grid'))


def measure_time(func, *args, **kwargs) -> Tuple[Any, float]:
    """
    Measure execution time of a function
    
    Args:
        func: Function to execute
        *args: Positional arguments
        **kwargs: Keyword arguments
        
    Returns:
        Tuple of (result, execution_time_in_seconds)
    """
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    return result, (end_time - start_time)


def create_bar_chart(data: Dict[str, int], title: str, xlabel: str, 
                     ylabel: str, filepath: str, figsize: Tuple[int, int] = (12, 6)) -> None:
    """
    Create and save a bar chart
    
    Args:
        data: Dictionary with labels and values
        title: Chart title
        xlabel: X-axis label
        ylabel: Y-axis label
        filepath: Path to save chart
        figsize: Figure size (width, height)
    """
    plt.figure(figsize=figsize)
    keys = list(data.keys())
    values = list(data.values())
    
    colors = plt.cm.Set3(np.linspace(0, 1, len(keys)))
    bars = plt.bar(keys, values, color=colors, edgecolor='black', linewidth=1.5)
    
    plt.title(title, fontsize=16, fontweight='bold', pad=20)
    plt.xlabel(xlabel, fontsize=12, fontweight='bold')
    plt.ylabel(ylabel, fontsize=12, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    print(f"âœ“ Chart saved: {filepath}")
    plt.close()


def create_comparison_chart(data_dict: Dict[str, Dict[str, int]], title: str, 
                           xlabel: str, ylabel: str, filepath: str, 
                           figsize: Tuple[int, int] = (14, 7)) -> None:
    """
    Create comparison chart with multiple datasets
    
    Args:
        data_dict: Dictionary of {label: {key: value}}
        title: Chart title
        xlabel: X-axis label
        ylabel: Y-axis label
        filepath: Path to save chart
        figsize: Figure size
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    x = np.arange(len(list(data_dict[list(data_dict.keys())[0]].keys())))
    width = 0.25
    multiplier = 0
    
    colors = plt.cm.Set2(np.linspace(0, 1, len(data_dict)))
    
    for i, (dataset_name, dataset_values) in enumerate(data_dict.items()):
        offset = width * multiplier
        values = list(dataset_values.values())
        bars = ax.bar(x + offset, values, width, label=dataset_name, 
                     color=colors[i], edgecolor='black', linewidth=1.2)
        
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}',
                   ha='center', va='bottom', fontsize=8)
        
        multiplier += 1
    
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel(xlabel, fontsize=12, fontweight='bold')
    ax.set_ylabel(ylabel, fontsize=12, fontweight='bold')
    ax.set_xticks(x + width)
    ax.set_xticklabels(list(list(data_dict.values())[0].keys()), rotation=45, ha='right')
    ax.legend(loc='upper left', fontsize=10)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    fig.tight_layout()
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    fig.savefig(filepath, dpi=300, bbox_inches='tight')
    print(f"âœ“ Comparison chart saved: {filepath}")
    plt.close()


def create_line_chart(data: Dict[str, List[float]], title: str, xlabel: str, 
                      ylabel: str, filepath: str, figsize: Tuple[int, int] = (12, 6)) -> None:
    """
    Create line chart for trend analysis
    
    Args:
        data: Dictionary with labels and value lists
        title: Chart title
        xlabel: X-axis label
        ylabel: Y-axis label
        filepath: Path to save chart
        figsize: Figure size
    """
    plt.figure(figsize=figsize)
    
    colors = plt.cm.tab10(np.linspace(0, 1, len(data)))
    
    for i, (label, values) in enumerate(data.items()):
        plt.plot(values, marker='o', linewidth=2.5, markersize=6, 
                label=label, color=colors[i])
    
    plt.title(title, fontsize=16, fontweight='bold', pad=20)
    plt.xlabel(xlabel, fontsize=12, fontweight='bold')
    plt.ylabel(ylabel, fontsize=12, fontweight='bold')
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    print(f"âœ“ Line chart saved: {filepath}")
    plt.close()


def count_occurrences(items: List[str], pattern: str = None) -> int:
    """
    Count occurrences of items or pattern in list
    
    Args:
        items: List to search in
        pattern: Optional pattern to search for
        
    Returns:
        Count of occurrences
    """
    if pattern is None:
        return len(items)
    return sum(1 for item in items if pattern.lower() in item.lower())


def calculate_statistics(data: List[float]) -> Dict[str, float]:
    """
    Calculate basic statistics for list of numbers
    
    Args:
        data: List of numeric values
        
    Returns:
        Dictionary with mean, median, std dev, min, max
    """
    arr = np.array(data)
    return {
        'mean': float(np.mean(arr)),
        'median': float(np.median(arr)),
        'std_dev': float(np.std(arr)),
        'min': float(np.min(arr)),
        'max': float(np.max(arr))
    }


def format_time(seconds: float) -> str:
    """
    Format seconds to readable time string
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted string like "1.234s" or "123ms"
    """
    if seconds < 0.001:
        return f"{seconds*1000000:.2f}Âµs"
    elif seconds < 1:
        return f"{seconds*1000:.2f}ms"
    else:
        return f"{seconds:.2f}s"


def print_section(title: str) -> None:
    """
    Print a formatted section header
    
    Args:
        title: Section title
    """
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


def ensure_output_dir(output_dir: str) -> None:
    """
    Ensure output directory exists
    
    Args:
        output_dir: Directory path to create
    """
    os.makedirs(output_dir, exist_ok=True)

