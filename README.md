# 🌍 LCA Metals Prediction System

## 📋 Project Overview

The **LCA Metals Prediction System** is a comprehensive machine learning-powered web application that predicts environmental and circularity parameters for metal production processes. This system provides data-driven insights for Life Cycle Assessment (LCA) optimization, helping industries make sustainable decisions in metal production and recycling.

### 🎯 Key Features

- **🤖 Advanced ML Pipeline**: Multi-output regression models with 87%+ accuracy on environmental targets
- **🌐 Interactive Web Interface**: Streamlit-based application with real-time predictions
- **📊 Rich Visualizations**: Interactive charts, Sankey diagrams, and comprehensive dashboards
- **💡 Smart Recommendations**: AI-powered sustainability improvement suggestions
- **🔄 Pathway Comparison**: Compare different production scenarios and their impacts
- **📈 Performance Analytics**: Detailed analysis of environmental and circularity metrics

## 🏗️ Project Structure

```
NEW SIH/
├── 📁 data/
│   ├── improved_realistic_lca_metals.csv    # Main dataset (3000+ samples)
│   └── raw.csv                              # Original raw data
├── 📁 notebooks/
│   └── 2.ml_pipeline.ipynb                  # Complete ML development pipeline
├── 📁 app/
│   ├── app.py                               # Main Streamlit application (2089 lines)
│   ├── plots.py                             # Interactive visualization functions  
│   ├── recommendations.py                   # Intelligent recommendation engine (1836 lines)
│   ├── launch.py                            # Application launcher script
│   └── launch.bat                           # Windows batch launcher
├── 📁 models/
│   ├── best_environmental_model.joblib      # Trained environmental model
│   ├── best_circularity_model.joblib       # Trained circularity model
│   ├── scaler.joblib                        # Feature scaler
│   ├── label_encoders.joblib                # Category encoders
│   └── feature_columns.joblib               # Feature column definitions
├── 📁 tests/
│   └── test_predictions.py                  # Model testing scripts
├── requirements.txt                         # Python dependencies
└── README.md                                # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+ 
- pip (Python package manager)
- 4GB+ RAM (recommended)
- Modern web browser

### Installation

1. **Clone or Download the Project**
   ```bash
   git clone <repository-url>
   cd "NEW SIH"
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Launch the Application**
   
   **Option A: Using Python**
   ```bash
   cd app
   python launch.py
   ```
   
   **Option B: Using Batch File (Windows)**
   ```bash
   cd app
   launch.bat
   ```

4. **Access the Web Interface**
   - Open your browser and go to: `http://localhost:8501`
   - The application will automatically open in your default browser

## 💻 Using the Application

### 1. **Parameter Input**
- Use the sidebar to input metal production parameters:
  - **Metal Type**: Select from Aluminum, Steel, Copper, Zinc, Lead
  - **Process Type**: Choose Primary, Secondary, or Hybrid
  - **Production Scale**: Industrial, Pilot, or Laboratory
  - **Advanced Parameters**: Temperature, pressure, efficiency metrics

### 2. **Generate Predictions**
- Click "🔮 Predict LCA Parameters" to get instant results
- View environmental impacts (Energy, Emissions, Water Use)
- Analyze circularity metrics (Recycling Rate, Reuse Potential)

### 3. **Compare Pathways**
- Add multiple production scenarios to comparison
- Analyze trade-offs between different approaches
- Export comparison results for further analysis

### 4. **Explore Visualizations**
- **Sankey Diagrams**: Material and energy flow analysis
- **Environmental Charts**: Impact comparisons across metals
- **Circularity Analysis**: Recycling vs sustainability metrics
- **Interactive Dashboards**: Comprehensive performance overview

### 5. **Get Recommendations**
- Access AI-powered improvement suggestions
- Environmental optimization strategies
- Circularity enhancement recommendations
- Process-specific improvement plans
## 🧠 Machine Learning Pipeline

### Model Performance
- **Environmental Targets**: 87%+ accuracy (Energy, Emissions, Water)
- **Circularity Targets**: Specialized optimization (challenging metrics)
- **Overall Performance**: 45% combined accuracy across all targets

### Training Features
- **Categorical**: Metal_Type, Process_Type, Production_Scale
- **Numerical**: Process_Temperature, Process_Pressure, Process_Efficiency
- **Advanced**: Heat_Recovery_Rate, Waste_Heat_Utilization, Energy_Recovery_Rate

### Model Architecture
- **Primary Model**: Random Forest with 200 estimators
- **Optimization**: GridSearchCV with cross-validation
- **Output Format**: Multi-target regression (7 simultaneous predictions)

## 📊 Key Metrics & Targets

### Environmental Parameters
- **Energy Use** (MJ/kg): Primary energy consumption
- **CO₂ Emissions** (kg/kg): Carbon footprint assessment  
- **Water Use** (L/kg): Water consumption analysis

### Circularity Parameters
- **Circularity Index** (0-1): Overall circular economy score
- **Recycled Content** (%): Percentage of recycled materials
- **Reuse Potential** (0-1): Material reusability assessment
- **End-of-Life Score** (0-1): Disposal/recycling effectiveness

## 🎨 Visualization Features

### Available Charts
1. **Material Flow Sankey**: 16-node comprehensive flow diagram
2. **Environmental Comparison**: Multi-metal impact analysis
3. **Circularity Scatter Plot**: Performance vs recycled content
4. **Interactive Dashboard**: Combined performance metrics
5. **Pathway Comparison**: Side-by-side scenario analysis

### Interactive Elements
- Hover tooltips with detailed information
- Zoom and pan capabilities
- Export options (PNG, HTML, PDF)
- Customizable color schemes
- Responsive design for all screen sizes

## 🔧 Technical Specifications

### Dependencies
```
streamlit>=1.28.0          # Web application framework
plotly>=5.15.0            # Interactive plotting
pandas>=2.0.0             # Data manipulation
numpy>=1.24.0             # Numerical computation
scikit-learn>=1.3.0       # Machine learning
joblib>=1.3.0             # Model serialization
```

### System Requirements
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Storage**: 500MB free space
- **CPU**: Multi-core processor recommended
- **Network**: Internet connection for initial setup

## 📈 Advanced Features

### Recommendation Engine
- **Environmental Optimization**: Process efficiency improvements
- **Circularity Enhancement**: Recycling and reuse strategies
- **Cost-Benefit Analysis**: Economic impact assessment
- **Implementation Roadmaps**: Step-by-step improvement plans

### Data Export Options
- **CSV Export**: Prediction results and comparisons
- **PDF Reports**: Comprehensive analysis documents
- **Chart Images**: High-resolution visualization exports
- **JSON Data**: API-compatible data formats

## 🧪 Testing & Validation

### Model Testing
```bash
cd tests
python test_predictions.py
```

### Sample Predictions
- Test various metal-process combinations
- Validate prediction ranges and accuracy
- Compare with historical data benchmarks

## 🚨 Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

2. **Port Already in Use**
   ```bash
   streamlit run app.py --server.port 8502
   ```

3. **Model Loading Issues**
   - Ensure all `.joblib` files are in `models/` directory
   - Check file permissions and integrity

4. **Memory Issues**
   - Close other applications
   - Increase system virtual memory
   - Use smaller batch sizes for predictions

### Performance Optimization
- **Fast Mode**: Disable complex visualizations for faster loading
- **Batch Processing**: Process multiple predictions simultaneously
- **Caching**: Streamlit automatically caches frequent operations

## 📚 Documentation

### Key Files Documentation
- **`app.py`**: Main application with 50+ functions and comprehensive UI
- **`plots.py`**: 10+ visualization functions with Plotly integration
- **`recommendations.py`**: 25+ recommendation algorithms
- **`2.ml_pipeline.ipynb`**: Complete ML development with 40+ cells

### API Reference
- **Prediction Functions**: Model inference and result formatting
- **Visualization Functions**: Chart generation and customization
- **Recommendation Functions**: Analysis and suggestion generation

## 🌟 Future Enhancements

### Planned Features
- **Real-time Data Integration**: Live industrial data feeds
- **Advanced ML Models**: Deep learning and ensemble methods
- **Multi-language Support**: Internationalization capabilities
- **Mobile Application**: Responsive mobile interface
- **API Endpoints**: RESTful API for external integrations

### Research Opportunities
- **Enhanced Circularity Modeling**: Improved prediction accuracy
- **Process Optimization**: Advanced algorithms for efficiency
- **Economic Integration**: Cost modeling and financial analysis
- **Environmental Impact**: Extended LCA parameters

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Make changes and test thoroughly
4. Submit pull request with detailed description

### Coding Standards
- **Python Style**: PEP 8 compliance
- **Documentation**: Comprehensive docstrings
- **Testing**: Unit tests for all functions
- **Error Handling**: Robust exception management

## 📄 License

This project is developed for educational and research purposes. Please contact the development team for commercial usage rights and licensing information.

## 👥 Team & Support

### Development Team
- **ML Engineers**: Model development and optimization
- **Frontend Developers**: Streamlit application and UI/UX
- **Data Scientists**: Analysis and validation
- **Sustainability Experts**: Domain knowledge and recommendations

### Contact Information
- **Technical Support**: Create GitHub issues for bugs
- **Feature Requests**: Use issue templates for enhancements
- **General Inquiries**: Contact through project repository

---

## 🎉 Getting Started Checklist

- [ ] Python 3.8+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Launch application (`python app/launch.py`)
- [ ] Access web interface (`http://localhost:8501`)
- [ ] Test sample predictions
- [ ] Explore visualization features
- [ ] Review recommendations engine
- [ ] Export sample results

**Ready to optimize your metal production sustainability? Start predicting now! 🚀**

---

*Last Updated: 2024 | Version: 1.0.0 | Status: Production Ready*

## Usage

### 1. Exploratory Data Analysis
```bash
jupyter notebook notebooks/lca_metals_eda.ipynb
```

### 2. Machine Learning Pipeline
```bash
jupyter notebook notebooks/ml_pipeline.ipynb
```

### 3. Making Predictions
```python
from src.model import LCAPredictor

# Initialize predictor
predictor = LCAPredictor()

# Make prediction
result = predictor.predict_single(
    metal="Steel",
    process_type="Recycled", 
    end_of_life="Recycled"
)

print(result)
```

## Model Performance
The trained model predicts 6 indicators:

**Environmental Indicators:**
- Energy_Use_MJ_per_kg
- Emission_kgCO2_per_kg  
- Water_Use_l_per_kg

**Circularity Indicators:**
- Circularity_Index
- Recycled_Content_pct
#   H a r i - S I H  
 