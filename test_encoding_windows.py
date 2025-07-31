#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify Windows encoding fixes
"""

import sys
import os

# Apply the same Windows encoding fixes as in email_finder.py
if sys.platform.startswith('win'):
    import codecs
    import io
    import locale
    
    # Set environment variables for UTF-8 encoding
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONUTF8'] = '1'
    
    # Try to set console code page to UTF-8
    try:
        import subprocess
        subprocess.run(['chcp', '65001'], shell=True, capture_output=True)
    except:
        pass
    
    # Fix for Windows encoding issues with stdout
    try:
        # Check if stdout needs to be wrapped
        if hasattr(sys.stdout, 'buffer'):
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, errors='replace')
        elif not hasattr(sys.stdout, 'encoding') or sys.stdout.encoding.lower() != 'utf-8':
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach(), errors='replace')
    except Exception:
        # Fallback if stdout is already wrapped or other issues
        pass
    
    # Also handle stderr
    try:
        if hasattr(sys.stderr, 'buffer'):
            sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, errors='replace')
        elif not hasattr(sys.stderr, 'encoding') or sys.stderr.encoding.lower() != 'utf-8':
            sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach(), errors='replace')
    except Exception:
        pass

def safe_print(text, flush=False):
    """Safe print function that handles Unicode on Windows"""
    try:
        # First try normal print
        print(text, flush=flush)
    except (UnicodeEncodeError, UnicodeDecodeError) as e:
        try:
            # Try encoding as UTF-8 with error handling
            if isinstance(text, bytes):
                text = text.decode('utf-8', errors='replace')
            safe_text = str(text).encode('utf-8', errors='replace').decode('utf-8')
            print(safe_text, flush=flush)
        except Exception:
            # Final fallback: replace problematic characters with safe alternatives
            try:
                # Replace common emojis and special characters
                safe_text = str(text)
                replacements = {
                    '🔍': '[SEARCH]',
                    '✅': '[OK]',
                    '📧': '[EMAIL]',
                    '❌': '[ERROR]',
                    '📊': '[STATS]',
                    '💾': '[SAVE]',
                    '📁': '[FILE]',
                    '⏳': '[WAIT]',
                    '🚀': '[START]',
                    '💡': '[INFO]',
                    '🌐': '[WEB]',
                    '📍': '[LOCATION]',
                    '🔧': '[TOOL]',
                    '👋': '[WAVE]'
                }
                for emoji, replacement in replacements.items():
                    safe_text = safe_text.replace(emoji, replacement)
                
                # Remove any remaining non-ASCII characters
                safe_text = safe_text.encode('ascii', 'replace').decode('ascii')
                print(safe_text, flush=flush)
            except Exception:
                # Ultimate fallback
                print("[MESSAGE ENCODING ERROR]", flush=flush)
    except Exception as e:
        # Handle any other printing errors
        try:
            print(f"[PRINT ERROR: {e}]", flush=flush)
        except:
            pass

def test_encoding():
    """Test various encoding scenarios"""
    
    safe_print("🔍 Testing Windows encoding fixes...")
    safe_print("========================================")
    
    # Test 1: Basic emojis
    safe_print("📧 Test 1: Basic emojis")
    safe_print("✅ OK emoji")
    safe_print("❌ Error emoji")
    safe_print("🔍 Search emoji")
    
    # Test 2: Special characters
    safe_print("\n💾 Test 2: Special characters")
    safe_print("Açaí café naïve résumé")
    safe_print("Müller Zürich Düsseldorf")
    safe_print("São Paulo Niterói")
    
    # Test 3: Mixed content
    safe_print("\n🌐 Test 3: Mixed content")
    safe_print("🔍 Searching for: café@müller.com")
    safe_print("✅ Found email: test@résumé.org")
    safe_print("📊 Stats: 3 emails found")
    
    # Test 4: Problematic bytes simulation
    safe_print("\n🔧 Test 4: Problematic content handling")
    try:
        # Simulate the kind of content that might cause charmap errors
        test_bytes = b'\x8d\x9d\xa0\xb5'  # Bytes that often cause charmap issues
        try:
            decoded = test_bytes.decode('utf-8', errors='replace')
            safe_print(f"Decoded problematic bytes: {decoded}")
        except Exception as e:
            safe_print(f"❌ Error handling problematic bytes: {e}")
    except Exception as e:
        safe_print(f"❌ Error in test 4: {e}")
    
    safe_print("\n👋 Encoding test completed!")
    safe_print("If you can see all the emojis and special characters above,")
    safe_print("the encoding fixes are working correctly!")

if __name__ == "__main__":
    test_encoding()
