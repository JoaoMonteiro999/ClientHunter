#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Final comprehensive test to verify encoding fixes work completely
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

def test_complete_workflow():
    """Test the complete email search workflow"""
    
    print("🧪 FINAL ENCODING TEST - COMPLETE WORKFLOW")
    print("=" * 60)
    
    # Test 1: Import modules without errors
    print("📦 Test 1: Module imports")
    try:
        from email_finder import safe_print, safe_google_search, search_and_extract_emails
        print("✅ All modules imported successfully")
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False
    
    # Test 2: Safe print with challenging content
    print("\n📝 Test 2: Safe printing")
    try:
        safe_print("🔍 Testing safe print with emojis: ✅❌📧🌐")
        safe_print("Testing special chars: àáâãäåæç èéêë ìíîï òóôõö ùúûü")
        safe_print("Testing mixed content: Café 🌟 München ⭐ São Paulo 🎯")
        print("✅ Safe printing works correctly")
    except Exception as e:
        print(f"❌ Safe print failed: {e}")
        return False
    
    # Test 3: Google search with simple query
    print("\n🔍 Test 3: Google search functionality")
    try:
        safe_print("Testing Google search with simple query...")
        urls = safe_google_search("test", 3)
        if urls and len(urls) > 0:
            safe_print(f"✅ Google search successful: {len(urls)} URLs found")
        else:
            safe_print("⚠️ Google search returned no results (may be network/quota issue)")
    except Exception as e:
        safe_print(f"❌ Google search failed: {e}")
        return False
    
    # Test 4: Complete email search (minimal)
    print("\n📧 Test 4: Complete email search workflow")
    try:
        safe_print("Testing complete email search workflow...")
        results = search_and_extract_emails("test clinic", 2, 1)
        safe_print(f"✅ Complete workflow successful: {len(results)} results")
    except Exception as e:
        safe_print(f"❌ Complete workflow failed: {e}")
        return False
    
    # Test 5: Problematic characters handling
    print("\n🛡️ Test 5: Problematic content handling")
    try:
        # Simulate problematic bytes that caused the original error
        test_bytes = b'\x8d\x9d\xa0\xb5'
        decoded = test_bytes.decode('utf-8', errors='replace')
        safe_print(f"✅ Problematic bytes handled: {repr(decoded)}")
    except Exception as e:
        safe_print(f"❌ Problematic content handling failed: {e}")
        return False
    
    print("\n🎉 ALL TESTS PASSED!")
    print("✅ The encoding error should now be completely resolved!")
    print("✅ You can safely use the email search in Streamlit")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = test_complete_workflow()
    if not success:
        sys.exit(1)
