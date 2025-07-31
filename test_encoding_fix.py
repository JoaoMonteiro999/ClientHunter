#!/usr/bin/env python3
"""
Test script to verify encoding fixes work properly on Windows
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

def test_encoding_setup():
    """Test if our encoding setup works"""
    print("🧪 Testing encoding setup...")
    
    # Test Unicode characters
    test_chars = "🔍 ✅ 📧 ❌ 📊 💾 📁"
    print(f"Unicode test: {test_chars}")
    
    # Test special characters that might cause issues
    special_chars = "áéíóú àèìòù âêîôû ãẽĩõũ çñü ß €"
    print(f"Special chars test: {special_chars}")
    
    print("✅ Encoding test completed successfully!")

def test_web_request():
    """Test a simple web request with encoding handling"""
    print("\n🌐 Testing web request encoding...")
    
    try:
        import requests
        from bs4 import BeautifulSoup
        
        # Test with a simple website
        url = "https://httpbin.org/encoding/utf8"
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        response = requests.get(url, headers=headers, timeout=5)
        
        # Try our encoding detection logic
        try:
            if response.encoding and response.encoding.lower() != 'iso-8859-1':
                html = response.text
            else:
                try:
                    html = response.content.decode('utf-8')
                except UnicodeDecodeError:
                    try:
                        html = response.content.decode('cp1252')
                    except UnicodeDecodeError:
                        html = response.content.decode('utf-8', errors='ignore')
        except Exception:
            html = response.text
        
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text()
        
        print("✅ Web request encoding test successful!")
        print(f"📊 Response length: {len(text)} characters")
        
    except Exception as e:
        print(f"❌ Web request test failed: {e}")

def test_csv_operations():
    """Test CSV file operations with UTF-8"""
    print("\n📁 Testing CSV operations...")
    
    import csv
    test_file = "test_encoding.csv"
    
    try:
        # Test writing CSV with special characters
        test_data = [
            {'Company': 'Café München', 'Email': 'info@café-münchen.de'},
            {'Company': 'Açaí São Paulo', 'Email': 'contato@açaí.com.br'},
            {'Company': 'Résumé Paris', 'Email': 'hello@résumé.fr'}
        ]
        
        with open(test_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['Company', 'Email'])
            writer.writeheader()
            writer.writerows(test_data)
        
        # Test reading back
        with open(test_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            read_data = list(reader)
        
        print(f"✅ CSV test successful! Wrote and read {len(read_data)} rows")
        for row in read_data:
            print(f"   📧 {row['Company']} - {row['Email']}")
        
        # Clean up
        os.remove(test_file)
        
    except Exception as e:
        print(f"❌ CSV test failed: {e}")
        # Clean up even if failed
        if os.path.exists(test_file):
            os.remove(test_file)

if __name__ == "__main__":
    print("🔧 ClientHunter Encoding Fix Test")
    print("=" * 50)
    print(f"🖥️  Platform: {sys.platform}")
    print(f"🐍 Python: {sys.version}")
    print(f"📝 Default encoding: {sys.getdefaultencoding()}")
    print(f"📺 Stdout encoding: {getattr(sys.stdout, 'encoding', 'unknown')}")
    
    if sys.platform.startswith('win'):
        print("🪟 Windows detected - applying encoding fixes...")
        import codecs
        import io
        try:
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
        except:
            pass
        os.environ['PYTHONIOENCODING'] = 'utf-8'
    
    print("=" * 50)
    
    test_encoding_setup()
    test_web_request()
    test_csv_operations()
    
    print("\n🎉 All tests completed!")
    print("💡 If you see this message without errors, the encoding fix should work!")
