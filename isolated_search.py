#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Isolated Google search script to avoid encoding issues
This script runs in a separate process with full encoding control
"""

import sys
import os

# Force UTF-8 encoding from the very start
os.environ['PYTHONIOENCODING'] = 'utf-8:replace'
os.environ['PYTHONUTF8'] = '1'
os.environ['PYTHONLEGACYWINDOWSSTDIO'] = '0'
os.environ['PYTHONLEGACYWINDOWSIOENCODING'] = '0'

if sys.platform.startswith('win'):
    import codecs
    import subprocess
    
    # Set console code page
    try:
        subprocess.run(['chcp', '65001'], shell=True, capture_output=True)
    except:
        pass
    
    # Force stdout encoding
    try:
        if hasattr(sys.stdout, 'buffer'):
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, errors='replace')
    except:
        pass

def isolated_google_search(query, num_results=50):
    """Perform Google search in isolated environment"""
    try:
        from googlesearch import search
        
        # Clean the query
        safe_query = query.encode('ascii', 'ignore').decode('ascii')
        if not safe_query.strip():
            safe_query = ''.join(c for c in query if ord(c) < 128)
        
        # Perform search
        results = list(search(safe_query, num_results=num_results))
        
        # Output results
        for url in results:
            try:
                print(url.encode('utf-8', errors='replace').decode('utf-8'))
            except:
                print(str(url))
                
    except Exception as e:
        print(f"SEARCH_ERROR: {e}")

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        query = sys.argv[1]
        num_results = int(sys.argv[2])
        isolated_google_search(query, num_results)
    else:
        print("SEARCH_ERROR: Invalid arguments")
