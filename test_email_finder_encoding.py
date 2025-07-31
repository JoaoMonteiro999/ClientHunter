#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick test for email finder encoding fixes
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from email_finder import safe_print, processar_url

def test_email_finder_encoding():
    """Test the email finder with potential encoding issues"""
    
    safe_print("🧪 Testing Email Finder Encoding Fixes")
    safe_print("=" * 40)
    
    # Test 1: Safe print with emojis
    safe_print("📧 Test 1: Emoji printing test")
    safe_print("✅ This should work fine")
    safe_print("❌ Even problematic characters: àáâãäåæç")
    
    # Test 2: Test URL processing with a simple URL
    safe_print("\n🌐 Test 2: URL processing test")
    test_url = "https://httpbin.org/html"
    
    try:
        safe_print(f"Processing URL: {test_url}")
        result = processar_url(test_url)
        safe_print(f"✅ URL processed successfully")
        safe_print(f"   Company: {result['company']}")
        safe_print(f"   Emails found: {len(result['emails'])}")
        safe_print(f"   URL: {result['url']}")
    except Exception as e:
        safe_print(f"❌ URL processing failed: {e}")
    
    # Test 3: Test with potential encoding issues
    safe_print("\n🔧 Test 3: Encoding protection test")
    try:
        # Simulate problematic content
        test_bytes = b'\x8d\x9d\xa0\xb5'
        safe_print(f"Raw bytes: {test_bytes}")
        
        # Test decoding with our protection
        try:
            decoded = test_bytes.decode('utf-8', errors='replace')
            safe_print(f"Safely decoded: {repr(decoded)}")
        except Exception as e:
            safe_print(f"Decoding error handled: {e}")
            
    except Exception as e:
        safe_print(f"❌ Encoding test error: {e}")
    
    safe_print("\n🎉 Email Finder encoding test completed!")
    safe_print("If you see this message, the encoding fixes should work correctly.")

if __name__ == "__main__":
    test_email_finder_encoding()
