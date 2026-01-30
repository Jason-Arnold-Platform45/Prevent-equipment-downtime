# Research: Moirai Sensor Failure Prediction

**Branch**: `001-moirai-sensor-prediction` | **Date**: 2026-01-30

## Technology Stack Decisions

### Decision 1: Programming Language

**Decision**: Python 3.11+

**Rationale**:
- Moirai model (uni2ts library) is Python-native and requires PyTorch
- The model is distributed via Hugging Face and integrates with GluonTS
- Python has the strongest ecosystem for ML/data science workloads
- FastAPI provides high-performance async web serving for Python

**Alternatives Considered**:
- Node.js: Rejected - No native Moirai/PyTorch support; would require Python subprocess
- Rust: Rejected - No uni2ts bindings available; unnecessary complexity
- Java: Rejected - Limited ML ecosystem compared to Python

### Decision 2: ML Framework

**Decision**: Salesforce Moirai (uni2ts library) with PyTorch backend

**Rationale**:
- Moirai is a time series foundation model specifically designed for forecasting
- Available in three sizes: Small (14M), Base (91M), Large (311M params)
- Supports probabilistic forecasting with confidence intervals (critical for sensor risk assessment)
- Pre-trained on LOTSA dataset (27B observations across 9 domains)
- Moirai-1.0-R models are publicly available on Hugging Face

**Alternatives Considered**:
- Amazon Chronos: Similar capability but Moirai shows better benchmarks on GIFT-Eval
- Google TimesFM: Moirai-MoE uses 65x fewer activated parameters with comparable accuracy
- Custom LSTM/Transformer: Rejected - Foundation models eliminate need for custom training

### Decision 3: Web Framework

**Decision**: FastAPI

**Rationale**:
- High-performance async Python web framework
- Built-in OpenAPI/Swagger documentation
- Native support for JSON request/response handling
- Excellent integration with Pydantic for data validation
- Async support beneficial for ML inference workloads

**Alternatives Considered**:
- Flask: Lower performance, less modern async support
- Django: Overkill for API-focused service; heavier framework
- Tornado: Less popular, smaller ecosystem

### Decision 4: Storage

**Decision**: Use existing EAIMMS PostgreSQL database on Railway

**Rationale**:
- Existing production database already contains sensor monitoring data
- `monitoring_plans_task_results` table has time-series sensor readings
- `monitoring_plans_points` table defines sensor/monitoring points
- `equipments_equipment` and related tables provide equipment context
- `ai_assessments` table provides pattern for storing AI predictions
- No need to duplicate data or maintain sync between systems

**Database Connection** (Railway):
- **Project**: Applied-AI-Eng-Demo
- **Service**: eaimms-staging (PostGIS)
- **Host**: gondola.proxy.rlwy.net:59528
- **Database**: railway

**Existing Tables Used**:
| Table | Purpose | Records |
|-------|---------|---------|
| monitoring_plans_task_results | Sensor time-series data | 81 |
| monitoring_plans_points | Sensor point definitions | 67 |
| monitoring_plans_tasks | Links points to results | - |
| equipments_equipment | Equipment being monitored | 11 |
| ai_assessments | Pattern for AI predictions | 7,789 |

**New Table**: `moirai_predictions` - Store Moirai failure predictions

**Alternatives Considered**:
- New separate database: Rejected - Would require data duplication and sync
- SQLite for development: Rejected - Need to test against real schema

### Decision 5: Testing Framework

**Decision**: pytest with pytest-asyncio

**Rationale**:
- Python standard for testing
- Rich plugin ecosystem (coverage, fixtures, parametrize)
- pytest-asyncio for testing async FastAPI endpoints
- Familiar to most Python developers

**Alternatives Considered**:
- unittest: Built-in but verbose; pytest is more expressive
- nose2: Less maintained than pytest

### Decision 6: Frontend Framework

**Decision**: React with TypeScript (for dashboard)

**Rationale**:
- Industry standard for interactive dashboards
- Strong typing with TypeScript reduces bugs
- Rich charting libraries (Recharts, Chart.js) for sensor visualization
- Component-based architecture suits dashboard widgets

**Alternatives Considered**:
- Vue.js: Viable but smaller ecosystem for data visualization
- Svelte: Less mature charting ecosystem
- Server-rendered (Jinja2): Rejected - Dashboard needs interactive filtering/sorting

## Moirai Model Integration Research

### Model Selection

**Recommended**: `Salesforce/moirai-1.0-R-base` (91M parameters)

**Rationale**:
- Balance between accuracy and inference speed
- Small (14M) may lack accuracy for critical predictions
- Large (311M) may exceed 60-second prediction target on modest hardware
- Base model provides good accuracy with reasonable resource requirements

### Input Data Requirements

```python
# Required format: Pandas DataFrame with datetime index
# Each column represents a sensor's time series
sensor_data = pd.DataFrame({
    'sensor_001': [...values...],
    'sensor_002': [...values...],
}, index=pd.DatetimeIndex([...timestamps...]))

# Convert to GluonTS format
from gluonts.dataset.pandas import PandasDataset
dataset = PandasDataset(dict(sensor_data))
```

### Key Parameters

| Parameter | Recommended Value | Notes |
|-----------|-------------------|-------|
| `context_length` | 200-1000 | Historical readings to consider |
| `prediction_length` | 24-168 | Hours ahead to predict (1-7 days) |
| `patch_size` | "auto" | Let model determine optimal |
| `num_samples` | 100 | For probabilistic forecasts |
| `batch_size` | 32 | Adjust based on memory |

### Risk Level Classification

**Algorithm**:
```
confidence_score = mean(forecast_samples)
variance = std(forecast_samples)

if confidence_score > threshold_high AND variance < var_threshold:
    risk_level = "HIGH"
elif confidence_score > threshold_medium:
    risk_level = "MEDIUM"
else:
    risk_level = "LOW"
```

### Licensing Consideration

**Important**: Moirai models are licensed under CC BY-NC 4.0 (non-commercial).

**Implications**:
- Free for research and internal use
- Commercial deployment requires Salesforce licensing agreement
- Document this constraint in deployment guidelines

## JSON Schema for Sensor Data Input

### Proposed Schema

```json
{
  "readings": [
    {
      "sensor_id": "string (required)",
      "timestamp": "ISO8601 datetime (required)",
      "value": "number (required)",
      "unit": "string (optional)",
      "quality": "enum: good|suspect|bad (optional, default: good)"
    }
  ],
  "metadata": {
    "equipment_id": "string (optional)",
    "location": "string (optional)",
    "sensor_type": "string (optional)"
  }
}
```

### Validation Rules

- Minimum 24 readings per sensor for reliable prediction
- Timestamps must be chronologically ordered
- Values must be numeric (no NaN/Inf)
- Sensor IDs must be unique within equipment context

## Performance Considerations

### Target: 60 seconds for 10,000 readings

**Benchmarks** (estimated):
- Data parsing/validation: ~2 seconds
- DataFrame conversion: ~1 second
- Model inference (base): ~30-45 seconds (GPU) / ~50-55 seconds (CPU)
- Result formatting: ~1 second

**Optimizations**:
1. Batch sensor data by equipment for parallel processing
2. Use GPU acceleration if available (CUDA/MPS)
3. Cache model in memory (load once at startup)
4. Async processing for concurrent requests

### Memory Requirements

- Model (base): ~400MB
- Input buffer (10k readings): ~50MB
- Working memory: ~500MB
- **Total recommended**: 2GB+ RAM

## Sources

- [Moirai: A Time Series Foundation Model for Universal Forecasting](https://www.salesforce.com/blog/moirai/)
- [uni2ts GitHub Repository](https://github.com/SalesforceAIResearch/uni2ts)
- [Moirai-1.0-R-Large on Hugging Face](https://huggingface.co/Salesforce/moirai-1.0-R-large)
- [Introducing Moirai 2.0](https://www.salesforce.com/blog/moirai-2-0/)
