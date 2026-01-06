#!/usr/bin/env python3
"""
Search implementation using minsearch to index fastmcp documentation.
"""

import os
import zipfile
import json
from minsearch import Index

def extract_and_index_docs(zip_path: str) -> Index:
    """
    Extract markdown/mdx files from zip and index them with minsearch.
    
    Args:
        zip_path: Path to the zip file
        
    Returns:
        Indexed minsearch Index object
    """
    documents = []
    
    # Extract md and mdx files from zip
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for file_info in zip_ref.filelist:
            filename = file_info.filename
            
            # Only process .md and .mdx files
            if not filename.endswith(('.md', '.mdx')):
                continue
            
            # Read the content
            content = zip_ref.read(filename).decode('utf-8', errors='ignore')
            
            # Remove the first part of the path (e.g., "fastmcp-main/")
            # Split by '/' and skip the first part
            path_parts = filename.split('/')
            if len(path_parts) > 1:
                cleaned_filename = '/'.join(path_parts[1:])
            else:
                cleaned_filename = filename
            
            # Create document for indexing
            doc = {
                'content': content,
                'filename': cleaned_filename
            }
            documents.append(doc)
            print(f"Indexed: {cleaned_filename}")
    
    print(f"\nTotal documents indexed: {len(documents)}\n")
    
    # Create and fit the index
    index = Index(
        text_fields=['content', 'filename'],
        keyword_fields=[]
    )
    index.fit(documents)
    
    return index


def search(index: Index, query: str, num_results: int = 5) -> list:
    """
    Search the index for documents matching the query.
    
    Args:
        index: The minsearch Index object
        query: Search query string
        num_results: Number of results to return (default: 5)
        
    Returns:
        List of documents matching the query
    """
    results = index.search(query, num_results=num_results)
    return results


if __name__ == '__main__':
    # Path to the zip file
    zip_path = '/tmp/main.zip'
    
    # Check if zip exists
    if not os.path.exists(zip_path):
        print(f"Error: {zip_path} not found!")
        exit(1)
    
    # Extract and index documents
    print("Extracting and indexing documents...")
    index = extract_and_index_docs(zip_path)
    
    # Test search with "demo"
    query = "demo"
    print(f"\nSearching for: '{query}'")
    print(f"{'='*60}")
    results = search(index, query, num_results=5)
    
    print(f"\nTop {len(results)} results for '{query}':")
    print(f"{'='*60}")
    
    for i, result in enumerate(results, 1):
        print(f"\n{i}. Filename: {result['filename']}")
        # Show first 200 characters of content
        content_preview = result['content'][:200].replace('\n', ' ')
        print(f"   Preview: {content_preview}...")
    
    if results:
        first_result = results[0]['filename']
        print(f"\n{'='*60}")
        print(f"FIRST RESULT: {first_result}")
        print(f"{'='*60}")
