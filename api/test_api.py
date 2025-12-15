"""
Simple test script to verify the API is working correctly
Run this after starting the server to test all endpoints
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"
SESSION_ID = "test-session-" + str(int(time.time()))

def print_response(response):
    """Pretty print API response"""
    print(f"Status: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)
    print("-" * 60)

def test_health():
    """Test health endpoint"""
    print("\n1. Testing Health Check...")
    response = requests.get(f"{BASE_URL}/health")
    print_response(response)
    return response.status_code == 200

def test_greeting():
    """Test basic greeting"""
    print("\n2. Testing Greeting...")
    data = {
        "message": "Hello Commander Data! My name is Test User.",
        "session_id": SESSION_ID
    }
    response = requests.post(f"{BASE_URL}/chat", json=data)
    print_response(response)
    return response.status_code == 200

def test_math():
    """Test math calculation"""
    print("\n3. Testing Math Calculation...")
    data = {
        "message": "What is ((5 * 5) ^ 2)?",
        "session_id": SESSION_ID
    }
    response = requests.post(f"{BASE_URL}/chat", json=data)
    print_response(response)
    return response.status_code == 200

def test_memory():
    """Test conversation memory"""
    print("\n4. Testing Memory (remembering name)...")
    data = {
        "message": "What is my name?",
        "session_id": SESSION_ID
    }
    response = requests.post(f"{BASE_URL}/chat", json=data)
    print_response(response)
    return response.status_code == 200

def test_data_info():
    """Test RAG retrieval"""
    print("\n5. Testing RAG (Data's information)...")
    data = {
        "message": "Where were you created?",
        "session_id": SESSION_ID
    }
    response = requests.post(f"{BASE_URL}/chat", json=data)
    print_response(response)
    return response.status_code == 200

def test_session_info():
    """Test session info endpoint"""
    print("\n6. Testing Session Info...")
    response = requests.get(f"{BASE_URL}/sessions/{SESSION_ID}")
    print_response(response)
    return response.status_code == 200

def test_list_sessions():
    """Test list sessions endpoint"""
    print("\n7. Testing List Sessions...")
    response = requests.get(f"{BASE_URL}/sessions")
    print_response(response)
    return response.status_code == 200

def main():
    """Run all tests"""
    print("=" * 60)
    print("Commander Data Agent API - Test Suite")
    print("=" * 60)
    print(f"Base URL: {BASE_URL}")
    print(f"Test Session ID: {SESSION_ID}")
    
    tests = [
        ("Health Check", test_health),
        ("Greeting", test_greeting),
        ("Math Calculation", test_math),
        ("Memory", test_memory),
        ("RAG Retrieval", test_data_info),
        ("Session Info", test_session_info),
        ("List Sessions", test_list_sessions),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, "✓ PASSED" if passed else "✗ FAILED"))
        except requests.exceptions.ConnectionError:
            print(f"\n❌ ERROR: Cannot connect to {BASE_URL}")
            print("Make sure the server is running: python main.py")
            return
        except Exception as e:
            print(f"\n❌ ERROR in {test_name}: {str(e)}")
            results.append((test_name, f"✗ ERROR: {str(e)}"))
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    for test_name, result in results:
        print(f"{test_name:.<40} {result}")
    print("=" * 60)
    
    passed = sum(1 for _, r in results if "PASSED" in r)
    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed. Check the output above.")

if __name__ == "__main__":
    main()

