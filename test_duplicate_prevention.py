#!/usr/bin/env python3
"""
Test script to verify duplicate email prevention is working correctly
"""

import os
import json
import tempfile
import csv
from pathlib import Path

# Import the email sender functions
import sys
sys.path.append(str(Path(__file__).parent))
from email_sender import (
    is_email_already_sent, 
    add_sent_email, 
    load_sent_emails_log,
    get_sent_emails_stats,
    SENT_EMAILS_LOG
)

def test_duplicate_prevention():
    """Test the duplicate email prevention system"""
    
    print("🧪 Testing Duplicate Email Prevention System")
    print("=" * 50)
    
    # Clean up any existing test log
    test_log_backup = None
    if os.path.exists(SENT_EMAILS_LOG):
        print(f"📋 Backing up existing log: {SENT_EMAILS_LOG}")
        with open(SENT_EMAILS_LOG, 'r') as f:
            test_log_backup = f.read()
        os.remove(SENT_EMAILS_LOG)
    
    try:
        # Test 1: Fresh email should not be marked as sent
        print("\n🔍 Test 1: Fresh email check")
        test_email = "test@example.com"
        is_sent, info = is_email_already_sent(test_email, "en")
        print(f"   Email: {test_email}")
        print(f"   Already sent: {is_sent}")
        assert not is_sent, "Fresh email should not be marked as sent"
        print("   ✅ PASSED: Fresh email correctly identified as not sent")
        
        # Test 2: Add email to log
        print("\n📝 Test 2: Adding email to log")
        add_sent_email(test_email, "Test Company", "en")
        print(f"   Added: {test_email} for Test Company in English")
        
        # Verify it was added
        is_sent, info = is_email_already_sent(test_email, "en")
        print(f"   Now already sent: {is_sent}")
        print(f"   Last send info: {info}")
        assert is_sent, "Email should now be marked as sent"
        assert info['company'] == "Test Company", "Company should match"
        assert info['language'] == "en", "Language should match"
        print("   ✅ PASSED: Email correctly added and retrieved from log")
        
        # Test 3: Same email, different language
        print("\n🌍 Test 3: Same email, different language")
        is_sent_pt, info_pt = is_email_already_sent(test_email, "pt")
        print(f"   Same email in Portuguese - already sent: {is_sent_pt}")
        assert not is_sent_pt, "Same email in different language should be allowed"
        print("   ✅ PASSED: Different language correctly allowed")
        
        # Test 4: Add Portuguese version
        print("\n📝 Test 4: Adding Portuguese version")
        add_sent_email(test_email, "Test Company", "pt")
        is_sent_pt, info_pt = is_email_already_sent(test_email, "pt")
        print(f"   Portuguese version now sent: {is_sent_pt}")
        assert is_sent_pt, "Portuguese version should now be marked as sent"
        print("   ✅ PASSED: Multiple languages per email work correctly")
        
        # Test 5: Case insensitive check
        print("\n🔤 Test 5: Case insensitive email check")
        test_email_upper = "TEST@EXAMPLE.COM"
        is_sent_upper, _ = is_email_already_sent(test_email_upper, "en")
        print(f"   Uppercase email: {test_email_upper}")
        print(f"   Already sent: {is_sent_upper}")
        assert is_sent_upper, "Email check should be case insensitive"
        print("   ✅ PASSED: Case insensitive check works")
        
        # Test 6: Statistics
        print("\n📊 Test 6: Statistics")
        stats = get_sent_emails_stats()
        print(f"   Unique emails: {stats['total_unique_emails']}")
        print(f"   Total sends: {stats['total_sends']}")
        print(f"   By language: {stats['by_language']}")
        assert stats['total_unique_emails'] == 1, "Should have 1 unique email"
        assert stats['total_sends'] == 2, "Should have 2 total sends (EN + PT)"
        assert stats['by_language']['en'] == 1, "Should have 1 English send"
        assert stats['by_language']['pt'] == 1, "Should have 1 Portuguese send"
        print("   ✅ PASSED: Statistics are correct")
        
        # Test 7: Create test CSV and verify filtering
        print("\n📄 Test 7: CSV filtering simulation")
        test_emails = [
            {"Company": "Already Sent Co", "Email": test_email},  # Should be skipped
            {"Company": "New Company", "Email": "new@example.com"},  # Should be sent
            {"Company": "Another New", "Email": "another@example.com"},  # Should be sent
        ]
        
        emails_to_send = []
        emails_to_skip = []
        
        for row in test_emails:
            email = row['Email']
            is_sent, last_send = is_email_already_sent(email, "en")
            if not is_sent:
                emails_to_send.append(row)
            else:
                emails_to_skip.append(row)
        
        print(f"   Total emails in CSV: {len(test_emails)}")
        print(f"   Emails to send: {len(emails_to_send)}")
        print(f"   Emails to skip: {len(emails_to_skip)}")
        
        assert len(emails_to_skip) == 1, "Should skip 1 email"
        assert len(emails_to_send) == 2, "Should send 2 emails"
        assert emails_to_skip[0]['Email'] == test_email, "Should skip the already sent email"
        print("   ✅ PASSED: CSV filtering works correctly")
        
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Duplicate email prevention is working correctly")
        print("✅ System will reliably prevent sending duplicate emails")
        
        # Show final log content
        print("\n📋 Final log content:")
        log_data = load_sent_emails_log()
        print(json.dumps(log_data, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        raise
    
    finally:
        # Restore original log if it existed
        if test_log_backup:
            print(f"\n🔄 Restoring original log")
            with open(SENT_EMAILS_LOG, 'w') as f:
                f.write(test_log_backup)
        elif os.path.exists(SENT_EMAILS_LOG):
            print(f"\n🧹 Cleaning up test log")
            os.remove(SENT_EMAILS_LOG)

if __name__ == "__main__":
    test_duplicate_prevention()
