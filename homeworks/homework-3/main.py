import requests
import zipfile
import os
from fastmcp import FastMCP
from minsearch import Index

mcp = FastMCP("Demo 🚀")

# Global index for documentation search
_docs_index = None

def scrape_web_impl(url: str) -> str:
    jina_url = f"https://r.jina.ai/{url}"
    response = requests.get(jina_url, timeout=30)
    response.raise_for_status()
    return response.text

def initialize_docs_index(zip_path: str = "/tmp/main.zip") -> Index:
    """
    Initialize and cache the documentation search index.
    Extracts markdown/mdx files from the fastmcp repository zip.
    """
    global _docs_index
    
    if _docs_index is not None:
        return _docs_index
    
    if not os.path.exists(zip_path):
        raise FileNotFoundError(f"Zip file not found: {zip_path}")
    
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
    
    # Create and fit the index
    _docs_index = Index(
        text_fields=['content', 'filename'],
        keyword_fields=[]
    )
    _docs_index.fit(documents)
    
    return _docs_index

@mcp.tool
def scrape_web(url: str) -> str:
    """Download webpage content as markdown using Jina Reader"""
    return scrape_web_impl(url)

@mcp.tool
def search_documentation(query: str, num_results: int = 5) -> str:
    """
    Search the FastMCP documentation index for relevant documents.
    
    Args:
        query: Search query string
        num_results: Number of results to return (default: 5)
    
    Returns:
        Formatted string with search results
    """
    try:
        # Initialize index if not already done
        index = initialize_docs_index()
        
        # Perform search
        results = index.search(query, num_results=num_results)
        
        # Format results
        output = f"Search results for '{query}':\n\n"
        for i, result in enumerate(results, 1):
            output += f"{i}. File: {result['filename']}\n"
            # Show first 300 characters of content
            content_preview = result['content'][:300].replace('\n', ' ')
            output += f"   Preview: {content_preview}...\n\n"
        
        return output
    except Exception as e:
        return f"Error searching documentation: {str(e)}"

if __name__ == "__main__":
    # Pre-initialize the index on startup for faster first search
    try:
        initialize_docs_index()
        print("Documentation index initialized successfully")
    except Exception as e:
        print(f"Warning: Could not initialize documentation index: {e}")
    
    mcp.run()
