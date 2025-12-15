"""
Test script for the Health Insurance Prediction API endpoints
"""

import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint"""
    print("\n" + "="*60)
    print("Testing Health Check Endpoint")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_model_info():
    """Test the model info endpoint"""
    print("\n" + "="*60)
    print("Testing Model Info Endpoint")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/insurance/model-info")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_insurance_prediction(test_case):
    """Test the insurance prediction endpoint"""
    print("\n" + "="*60)
    print(f"Testing Insurance Prediction: {test_case['description']}")
    print("="*60)
    
    print(f"Input: {json.dumps(test_case['data'], indent=2)}")
    
    response = requests.post(
        f"{BASE_URL}/insurance/predict",
        json=test_case['data']
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.json()

def main():
    """Run all tests"""
    print("="*60)
    print("HEALTH INSURANCE PREDICTION API TEST")
    print("="*60)
    
    # Test 1: Health check
    try:
        test_health_check()
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Model info
    try:
        test_model_info()
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: Young male, non-smoker, low BMI
    test_cases = [
        {
            "description": "Young male, non-smoker, low BMI",
            "data": {
                "age": 29,
                "sex": "male",
                "bmi": 20.0,
                "children": 0,
                "smoker": "no",
                "region": "southeast"
            }
        },
        {
            "description": "Middle-aged female, smoker, high BMI",
            "data": {
                "age": 45,
                "sex": "female",
                "bmi": 32.5,
                "children": 2,
                "smoker": "yes",
                "region": "northwest"
            }
        },
        {
            "description": "Older male, non-smoker, normal BMI",
            "data": {
                "age": 60,
                "sex": "male",
                "bmi": 25.0,
                "children": 3,
                "smoker": "no",
                "region": "southwest"
            }
        },
        {
            "description": "Young female, smoker, overweight",
            "data": {
                "age": 25,
                "sex": "female",
                "bmi": 28.0,
                "children": 1,
                "smoker": "yes",
                "region": "northeast"
            }
        }
    ]
    
    results = []
    for test_case in test_cases:
        try:
            result = test_insurance_prediction(test_case)
            results.append(result)
        except Exception as e:
            print(f"Error: {e}")
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY OF PREDICTIONS")
    print("="*60)
    for i, (test_case, result) in enumerate(zip(test_cases, results), 1):
        print(f"\n{i}. {test_case['description']}")
        print(f"   Input: Age={test_case['data']['age']}, Sex={test_case['data']['sex']}, "
              f"BMI={test_case['data']['bmi']}, Children={test_case['data']['children']}, "
              f"Smoker={test_case['data']['smoker']}, Region={test_case['data']['region']}")
        if 'predicted_charges' in result:
            print(f"   Predicted Charges: ${result['predicted_charges']:,.2f}")
        else:
            print(f"   Error: {result}")

if __name__ == "__main__":
    main()

