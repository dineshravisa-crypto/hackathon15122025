# Health Insurance Prediction API Documentation

## Overview

The FastAPI application now includes health insurance charge prediction endpoints alongside the existing chatbot functionality. The model uses multiple regression to predict insurance charges based on customer attributes.

## New Endpoints

### 1. Predict Insurance Charges

**Endpoint:** `POST /insurance/predict`

**Description:** Predicts health insurance charges based on customer parameters.

**Request Body:**
```json
{
  "age": 29,
  "sex": "male",
  "bmi": 20.0,
  "children": 0,
  "smoker": "no",
  "region": "southeast"
}
```

**Parameters:**
- `age` (integer): Age of the person
- `sex` (string): Gender - must be "male" or "female"
- `bmi` (float): Body Mass Index
- `children` (integer): Number of children/dependents (0-5)
- `smoker` (string): Smoking status - must be "yes" or "no"
- `region` (string): Region - must be one of:
  - "southwest"
  - "southeast"
  - "northwest"
  - "northeast"

**Response:**
```json
{
  "predicted_charges": 1458.91,
  "input_parameters": {
    "age": 29,
    "sex": "male",
    "bmi": 20.0,
    "children": 0,
    "smoker": "no",
    "region": "southeast"
  }
}
```

**Example cURL:**
```bash
curl -X POST "http://localhost:8000/insurance/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "age": 29,
    "sex": "male",
    "bmi": 20.0,
    "children": 0,
    "smoker": "no",
    "region": "southeast"
  }'
```

**Example Python:**
```python
import requests

response = requests.post(
    "http://localhost:8000/insurance/predict",
    json={
        "age": 29,
        "sex": "male",
        "bmi": 20.0,
        "children": 0,
        "smoker": "no",
        "region": "southeast"
    }
)

result = response.json()
print(f"Predicted Charges: ${result['predicted_charges']:,.2f}")
```

### 2. Get Model Information

**Endpoint:** `GET /insurance/model-info`

**Description:** Returns information about the trained prediction model.

**Response:**
```json
{
  "model_loaded": true,
  "training_samples": 1338,
  "r_squared": 0.751,
  "features": ["age", "sex", "bmi", "children", "smoker", "region"]
}
```

**Example cURL:**
```bash
curl -X GET "http://localhost:8000/insurance/model-info"
```

## Setup

### 1. Environment Variables

Add the following to your `.env` file (optional):

```env
HEALTH_INSURANCE_DATA=E:/MLCourse/Datasets/health_insurance.csv
```

If not specified, the default path will be used.

### 2. Install Dependencies

Make sure all required packages are installed:

```bash
pip install fastapi uvicorn pandas numpy scikit-learn statsmodels
```

### 3. Start the Server

```bash
# Option 1: Using uvicorn directly
uvicorn main:app --reload

# Option 2: Using Python
python main.py

# Option 3: Using the start script (Windows)
start.bat
```

The API will be available at `http://localhost:8000`

### 4. Test the API

Run the test script:

```bash
python test_insurance_prediction.py
```

Or use the interactive API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Model Details

### Training Data
- Dataset: Health Insurance dataset (1338 samples)
- Features: age, sex, bmi, children, smoker, region
- Target: charges (insurance cost in USD)

### Preprocessing
- **Sex**: Converted to numeric (male=1, female=0)
- **Smoker**: Converted to numeric (yes=1, no=0)
- **Region**: Converted to numeric (southwest=0, southeast=1, northwest=2, northeast=3)
- **Scaling**: All features are standardized using StandardScaler

### Model Performance
- **Algorithm**: Ordinary Least Squares (OLS) Regression
- **R-squared**: ~0.75 (75% of variance explained)
- **Key Findings**:
  - Smoking status has the strongest correlation with charges (~0.79)
  - Age and BMI also show significant positive correlations
  - Sex and region have minimal impact

## Example Use Cases

### Example 1: Young, Healthy Non-Smoker
```json
{
  "age": 25,
  "sex": "female",
  "bmi": 22.0,
  "children": 0,
  "smoker": "no",
  "region": "southeast"
}
```
Expected result: Low charges (~$2,500-$4,000)

### Example 2: Middle-Aged Smoker
```json
{
  "age": 45,
  "sex": "male",
  "bmi": 32.5,
  "children": 2,
  "smoker": "yes",
  "region": "northwest"
}
```
Expected result: High charges (~$25,000-$35,000)

### Example 3: Older Non-Smoker
```json
{
  "age": 60,
  "sex": "male",
  "bmi": 25.0,
  "children": 3,
  "smoker": "no",
  "region": "southwest"
}
```
Expected result: Moderate charges (~$12,000-$18,000)

## Error Handling

### Common Errors

**503 Service Unavailable**
```json
{
  "detail": "Insurance prediction model not available. Please check if the data file exists."
}
```
Solution: Ensure the health_insurance.csv file exists at the specified path.

**400 Bad Request - Invalid Region**
```json
{
  "detail": "Invalid region. Must be one of: ['southwest', 'southeast', 'northwest', 'northeast']"
}
```
Solution: Use one of the valid region values.

**422 Validation Error**
```json
{
  "detail": [
    {
      "loc": ["body", "age"],
      "msg": "value is not a valid integer",
      "type": "type_error.integer"
    }
  ]
}
```
Solution: Ensure all parameters match the required data types.

## Integration Examples

### JavaScript/Frontend
```javascript
async function predictInsurance(customerData) {
  try {
    const response = await fetch('http://localhost:8000/insurance/predict', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(customerData)
    });
    
    const result = await response.json();
    console.log(`Predicted Charges: $${result.predicted_charges}`);
    return result;
  } catch (error) {
    console.error('Error:', error);
  }
}

// Usage
predictInsurance({
  age: 29,
  sex: "male",
  bmi: 20.0,
  children: 0,
  smoker: "no",
  region: "southeast"
});
```

### Python SDK
```python
class InsurancePredictor:
    def __init__(self, api_url="http://localhost:8000"):
        self.api_url = api_url
    
    def predict(self, age, sex, bmi, children, smoker, region):
        """Predict insurance charges"""
        response = requests.post(
            f"{self.api_url}/insurance/predict",
            json={
                "age": age,
                "sex": sex,
                "bmi": bmi,
                "children": children,
                "smoker": smoker,
                "region": region
            }
        )
        response.raise_for_status()
        return response.json()
    
    def get_model_info(self):
        """Get model information"""
        response = requests.get(f"{self.api_url}/insurance/model-info")
        response.raise_for_status()
        return response.json()

# Usage
predictor = InsurancePredictor()
result = predictor.predict(
    age=29,
    sex="male",
    bmi=20.0,
    children=0,
    smoker="no",
    region="southeast"
)
print(f"Predicted Charges: ${result['predicted_charges']:,.2f}")
```

## API Architecture

The insurance prediction functionality is integrated into the existing FastAPI application:

```
main.py
├── Insurance Prediction Module
│   ├── Model Initialization (on startup)
│   ├── Data Loading & Preprocessing
│   ├── Model Training (OLS Regression)
│   └── Prediction Endpoints
└── Chatbot Agent Module (existing)
    ├── RAG System
    ├── Tool Integration
    └── Chat Endpoints
```

Both systems run independently and can be used simultaneously.

## Performance Considerations

- **Model Loading**: Model is trained once on startup (~1-2 seconds)
- **Prediction Time**: < 10ms per prediction
- **Memory Usage**: ~50MB for model and scaler
- **Concurrency**: FastAPI handles concurrent requests efficiently

## Next Steps

1. **Model Improvements**:
   - Add cross-validation
   - Try other algorithms (Random Forest, Gradient Boosting)
   - Feature engineering (age groups, BMI categories)

2. **API Enhancements**:
   - Batch prediction endpoint
   - Model versioning
   - Prediction confidence intervals
   - Input validation improvements

3. **Monitoring**:
   - Add prediction logging
   - Track model performance metrics
   - Monitor API usage statistics

## Support

For issues or questions:
1. Check the API documentation at `/docs`
2. Review the test script: `test_insurance_prediction.py`
3. Examine the logs for error messages

