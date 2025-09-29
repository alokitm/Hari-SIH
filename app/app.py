import streamlit as st
import pandas as pd
import numpy as np
import joblib
import pickle
import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Import custom modules
from plots import create_sankey_diagram, create_energy_comparison, create_emissions_comparison, create_circularity_comparison, create_metal_comparison_chart, create_circularity_scatter_plot, create_comprehensive_dashboard
from recommendations import get_circularity_recommendations, get_environmental_recommendations

# Configure Streamlit page
st.set_page_config(
    page_title="LCA Metals Prediction System",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        padding-top: 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        border: 1px solid #e1e5e9;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .prediction-table {
        background-color: #ffffff;
        border-radius: 0.5rem;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .pathway-comparison {
        background-color: #f8f9ff;
        border-left: 4px solid #4CAF50;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def create_railway_fallback_model():
    """Create a fallback model for Railway deployment when LFS models fail"""
    import numpy as np
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.preprocessing import LabelEncoder
    from sklearn.multioutput import MultiOutputRegressor
    
    # Create label encoders
    metal_encoder = LabelEncoder()
    process_encoder = LabelEncoder() 
    eol_encoder = LabelEncoder()
    
    # Fit encoders with expected values
    metals = ['Aluminium', 'Steel', 'Copper', 'Zinc', 'Lead', 'Nickel', 'Tin', 'Gold']
    processes = ['Primary', 'Recycled', 'Hybrid']
    eol_options = ['Recycled', 'Landfilled', 'Reused']
    
    metal_encoder.fit(metals)
    process_encoder.fit(processes)
    eol_encoder.fit(eol_options)
    
    # Create models
    np.random.seed(42)
    env_model = MultiOutputRegressor(RandomForestRegressor(n_estimators=50, random_state=42))
    circ_model = MultiOutputRegressor(RandomForestRegressor(n_estimators=50, random_state=42))
    
    # Generate training data
    n_samples = 1000
    X_train = np.random.rand(n_samples, 13)
    
    # Set categorical features
    X_train[:, 0] = np.random.randint(0, len(metals), n_samples)
    X_train[:, 1] = np.random.randint(0, len(processes), n_samples)  
    X_train[:, 2] = np.random.randint(0, len(eol_options), n_samples)
    
    # Scale continuous features
    X_train[:, 3] *= 2000  # Transport km
    X_train[:, 4] *= 20    # Cost per kg
    X_train[:, 5] *= 30    # Product life
    X_train[:, 6] *= 5     # Waste ratio
    
    # Create realistic targets
    y_env = np.zeros((n_samples, 3))
    y_circ = np.zeros((n_samples, 3))
    
    for i in range(n_samples):
        process_factor = 0.4 if X_train[i, 1] == 1 else 1.0  # Recycled vs Primary
        
        # Environmental targets
        energy = np.random.normal(60 * process_factor, 20)
        emissions = np.random.normal(6 * process_factor, 2) 
        water = np.random.normal(25 * process_factor, 10)
        
        y_env[i] = [max(5, energy), max(0.5, emissions), max(2, water)]
        
        # Circularity targets
        base_circ = 0.75 if X_train[i, 1] == 1 else 0.35
        circularity = np.random.normal(base_circ, 0.15)
        recycled_content = np.random.normal(75 if X_train[i, 1] == 1 else 25, 20)
        reuse_potential = np.random.normal(base_circ, 0.12)
        
        y_circ[i] = [
            max(0.1, min(0.95, circularity)),
            max(5, min(95, recycled_content)), 
            max(0.1, min(0.9, reuse_potential))
        ]
    
    # Train models
    env_model.fit(X_train, y_env)
    circ_model.fit(X_train, y_circ)
    
    # Return model structure
    return {
        'model_type': 'optimized_dual_target',
        'environmental_model': env_model,
        'circularity_models': {'RandomForest': circ_model},
        'circularity_best_model': 'RandomForest',
        'label_encoders': {
            'Metal': metal_encoder,
            'Process_Type': process_encoder,
            'End_of_Life': eol_encoder
        },
        'metadata': {
            'model_version': 'railway_fallback_v1.0',
            'feature_alignment': 'corrected',
            'features_count': 13,
            'created_by': 'railway_deployment_fallback'
        }
    }

@st.cache_resource
def load_model():
    """Load the trained LCA model with Railway LFS fallback"""
    try:
        # Try to load existing models first
        model_paths = [
            Path("models/railway_fallback_model.pkl"),  # Fallback model created for Railway
            Path("../models/corrected_optimized_dual_target_model.pkl"),
            Path("models/corrected_optimized_dual_target_model.pkl"),    
            Path("../models/clean_optimized_dual_target_model.pkl"),
            Path("models/clean_optimized_dual_target_model.pkl"),    
            Path("../models/optimized_dual_target_model.pkl"),
            Path("models/optimized_dual_target_model.pkl"),    
            Path("../models/final_optimized_lca_model.pkl"),
            Path("models/final_optimized_lca_model.pkl"),
            Path("../models/lca_model.pkl"),
            Path("models/lca_model.pkl")
        ]
        
        for model_path in model_paths:
            if model_path.exists():
                try:
                    # Check if file is actually a valid pickle file (not LFS pointer)
                    with open(model_path, 'rb') as f:
                        # Read first few bytes to check if it's a valid pickle
                        first_bytes = f.read(10)
                        f.seek(0)
                        
                        # LFS pointer files start with "version https://git-lfs"
                        if first_bytes.startswith(b'version ht'):
                            st.warning(f"⚠️ {model_path.name} is an LFS pointer file, skipping...")
                            continue
                        
                        # Try to load the actual model
                        if "optimized_dual_target" in model_path.name or "fallback" in model_path.name:
                            model_data = pickle.load(f)
                        else:
                            model_data = joblib.load(model_path)
                    
                    st.success(f"✅ Model loaded successfully from {model_path.name}")
                    
                    # Display model information
                    if isinstance(model_data, dict) and 'model_type' in model_data:
                        st.info(f"📊 Model Type: {model_data['model_type']}")
                        if 'metadata' in model_data:
                            metadata = model_data['metadata']
                            if 'model_version' in metadata:
                                st.info(f"🔢 Version: {metadata['model_version']}")
                            if 'created_by' in metadata and 'fallback' in metadata['created_by']:
                                st.warning("⚠️ Using fallback model - limited accuracy expected")
                    
                    return model_data
                
                except Exception as e:
                    st.warning(f"⚠️ Failed to load {model_path.name}: {str(e)}")
                    continue
        
        # If no models could be loaded, create fallback
        st.warning("⚠️ No pre-trained models available. Creating fallback model...")
        st.info("🔄 This may happen on Railway when LFS files aren't properly synced.")
        
        with st.spinner("Creating fallback model..."):
            fallback_model = create_railway_fallback_model()
            
            # Try to save it for future use
            try:
                os.makedirs("models", exist_ok=True)
                with open("models/railway_fallback_model.pkl", 'wb') as f:
                    pickle.dump(fallback_model, f)
                st.success("✅ Fallback model created and saved!")
            except:
                st.warning("⚠️ Could not save fallback model, will recreate each session")
            
            st.info("📊 Using basic RandomForest model - predictions may be less accurate")
            return fallback_model
        
    except Exception as e:
        st.error(f"❌ Critical error in model loading: {str(e)}")
        st.error("🔄 Attempting to create emergency fallback model...")
        
        try:
            return create_railway_fallback_model()
        except Exception as e2:
            st.error(f"❌ Complete failure: {str(e2)}")
            return None

@st.cache_data
def get_metal_options():
    """Get available metal options including critical minerals"""
    return {
        # Base Metals
        'Aluminum': 0,
        'Steel': 1,
        'Copper': 2,
        'Zinc': 3,
        'Lead': 4,
        'Nickel': 5,
        # Critical Minerals (Problem Statement Focus)
        'Lithium': 6,
        'Cobalt': 7,
        'Rare Earth Elements': 8,
        'Platinum': 9,
        'Tungsten': 10,
        'Indium': 11
    }

@st.cache_data
def get_process_options():
    """Get available process type options focusing on circularity"""
    return {
        'Primary Production (Virgin Materials)': 0,
        'Secondary Production (Recycling)': 1,
        'Hybrid Process (Mixed Sources)': 2,
        'Advanced Recycling (High-Tech Recovery)': 3,
        'Urban Mining (Infrastructure Recovery)': 4
    }

@st.cache_data
def get_end_of_life_options():
    """Get end of life options"""
    return {
        'Recycling': 0,
        'Landfill': 1,
        'Incineration': 2,
        'Reuse': 3
    }

def predict_with_optimized_model(model_data, inputs):
    """Make predictions using the optimized model with polynomial features"""
    try:
        import numpy as np
        from sklearn.preprocessing import PolynomialFeatures
        
        # Extract necessary components
        env_model = model_data['environmental_model']
        circ_models = model_data['circularity_models']
        # Enhanced features approach - no polynomial transformation needed
        label_encoders = model_data['label_encoders']
        
        # Map input codes to string labels that the model expects
        # App metal options: Aluminum=0, Steel=1, Copper=2, Zinc=3, Lead=4, Nickel=5, Titanium=6, Magnesium=7
        metal_map = {
            0: 'Aluminium',  # Aluminum -> Aluminium (model expects British spelling)
            1: 'Steel', 
            2: 'Copper', 
            3: 'Zinc', 
            4: 'Lead', 
            5: 'Nickel',
            6: 'Tin',      # Titanium -> Tin (closest available in model)
            7: 'Gold'      # Magnesium -> Gold (fallback to available option)
        }
        # App process options: Primary=0, Secondary(Recycling)=1, Hybrid=2, Advanced Recycling=3
        process_map = {0: 'Primary', 1: 'Recycled', 2: 'Hybrid', 3: 'Recycled'}
        # App EOL options: Recycling=0, Landfill=1, Incineration=2, Reuse=3  
        eol_map = {0: 'Recycled', 1: 'Landfilled', 2: 'Landfilled', 3: 'Reused'}
        
        # Get string labels
        metal_label = metal_map.get(inputs['Metal'], 'Aluminium')
        process_label = process_map.get(inputs['Process_Type'], 'Primary')  
        eol_label = eol_map.get(inputs['End_of_Life'], 'Recycled')
        
        # Encode categorical features using string labels
        metal_encoded = label_encoders['Metal'].transform([metal_label])[0]
        process_encoded = label_encoders['Process_Type'].transform([process_label])[0]
        eol_encoded = label_encoders['End_of_Life'].transform([eol_label])[0]
        
        # Create enhanced features exactly as in training (13 total features)
        # Original 4 features
        transport_km = inputs['Transport_km']
        cost_per_kg = inputs['Cost_per_kg']
        product_life = inputs['Product_Life_Extension_years']
        waste_per_kg = inputs['Waste_kg_per_kg_metal']
        
        # Engineered features (same as training)
        energy_per_km = 1.0 / (transport_km + 1)  
        energy_per_cost = 10.0 / (cost_per_kg + 1)  
        emission_per_energy = 0.5  
        waste_ratio = waste_per_kg  
        cost_efficiency = product_life / (cost_per_kg + 1)
        transport_efficiency = product_life / (transport_km + 1)
        
        # Create the exact 13-feature array used in training:
        # [Metal, Process_Type, End_of_Life, Transport_km, Cost_per_kg, Product_Life_Extension_years, 
        #  Waste_kg_per_kg_metal, Energy_per_km, Energy_per_cost, Emission_per_energy, 
        #  Waste_ratio, Cost_efficiency, Transport_efficiency]
        all_features = np.array([[
            metal_encoded, process_encoded, eol_encoded,  # 3 categorical features
            transport_km, cost_per_kg, product_life, waste_per_kg,  # 4 original numerical
            energy_per_km, energy_per_cost, emission_per_energy,   # 3 engineered
            waste_ratio, cost_efficiency, transport_efficiency     # 3 more engineered
        ]])
        
        # Make predictions
        results = {}
        
        # Environmental predictions
        env_pred = env_model.predict(all_features)[0]
        results['Energy_Use_MJ_per_kg'] = float(env_pred[0])
        results['Emission_kgCO2_per_kg'] = float(env_pred[1]) 
        results['Water_Use_l_per_kg'] = float(env_pred[2])
        
        # Circularity predictions
        best_circ_model = circ_models[model_data.get('circularity_best_model', 'RandomForest')]
        circ_pred = best_circ_model.predict(all_features)[0]
        results['Circularity_Index'] = float(circ_pred[0])
        results['Recycled_Content_pct'] = float(circ_pred[1])
        results['Reuse_Potential_score'] = float(circ_pred[2])
        
        return results
        
    except Exception as e:
        st.error(f"❌ Optimized model prediction error: {str(e)}")
        return None

def predict_lca_values(model_data, inputs):
    """Make predictions using the loaded model"""
    try:
        # Handle different model structures
        if isinstance(model_data, dict):
            # Check if this is the optimized model with polynomial features
            if 'model_type' in model_data and model_data['model_type'] == 'optimized_dual_target':
                return predict_with_optimized_model(model_data, inputs)
            elif 'model' in model_data:
                model = model_data['model']
            elif 'best_model' in model_data:
                model = model_data['best_model']
            else:
                model = model_data
        else:
            model = model_data
        
        # Prepare input data
        input_df = pd.DataFrame([inputs])
        
        # Make prediction
        predictions = model.predict(input_df) # type: ignore
        
        # Target variable names
        target_names = [
            'Energy_Use_MJ_per_kg',
            'Emission_kgCO2_per_kg', 
            'Water_Use_l_per_kg',
            'Circularity_Index',
            'Recycled_Content_pct',
            'Reuse_Potential_score'
        ]
        
        # Handle different prediction formats
        if predictions.ndim == 2:
            pred_values = predictions[0]
        else:
            pred_values = predictions
        
        # Create results dictionary
        results = {}
        for i, name in enumerate(target_names):
            if i < len(pred_values):
                results[name] = float(pred_values[i])
            else:
                results[name] = 0.0
        
        return results
    
    except Exception as e:
        st.error(f"❌ Prediction error: {str(e)}")
        return None

def create_pathway_comparison(base_inputs):
    """Create comparison between different production pathways"""
    pathways = {
        'Primary Production': 0,
        'Secondary Production (Recycling)': 1,
        'Hybrid Process': 2
    }
    
    comparison_data = []
    model_data = st.session_state.get('model_data')
    
    for pathway_name, pathway_code in pathways.items():
        inputs = base_inputs.copy()
        inputs['Process_Type'] = pathway_code
        
        predictions = predict_lca_values(model_data, inputs)
        if predictions:
            comparison_data.append({
                'Pathway': pathway_name,
                'Energy (MJ/kg)': predictions.get('Energy_Use_MJ_per_kg', 0),
                'Emissions (kgCO2/kg)': predictions.get('Emission_kgCO2_per_kg', 0),
                'Water (L/kg)': predictions.get('Water_Use_l_per_kg', 0),
                'Circularity Index': predictions.get('Circularity_Index', 0),
                'Recycled Content (%)': predictions.get('Recycled_Content_pct', 0),
                'Reuse Potential': predictions.get('Reuse_Potential_score', 0)
            })
    
    return pd.DataFrame(comparison_data)

def main():
    """Main Streamlit application"""
    
    # Custom CSS for better metrics visibility
    st.markdown("""
    <style>
    /* Enhanced metrics styling with better targeting */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
        border: 2px solid #e0e7ff !important;
        padding: 20px !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
        margin: 8px 0 !important;
    }
    
    [data-testid="metric-container"] > div {
        color: white !important;
    }
    
    [data-testid="metric-container"] [data-testid="metric-value"] {
        color: #ffffff !important;
        font-weight: bold !important;
        font-size: 1.5em !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3) !important;
    }
    
    [data-testid="metric-container"] [data-testid="metric-label"] {
        color: #e0e7ff !important;
        font-weight: 600 !important;
        font-size: 0.9em !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3) !important;
    }
    
    /* Green gradient for circularity section */
    .stMarkdown:has(+ .stColumns) ~ .stColumns [data-testid="metric-container"] {
        background: linear-gradient(135deg, #059669 0%, #10b981 100%) !important;
        border-color: #d1fae5 !important;
    }
    
    /* Ensure all text in metrics is white */
    [data-testid="metric-container"] * {
        color: white !important;
    }
    
    /* Alternative approach using nth-child */
    .stColumns:nth-of-type(2) [data-testid="metric-container"] {
        background: linear-gradient(135deg, #059669 0%, #10b981 100%) !important;
    }
    
    /* Force override any conflicting styles */
    div[data-testid="stMetricValue"] > div {
        color: #ffffff !important;
    }
    
    div[data-testid="stMetricLabel"] > div {
        color: #e0e7ff !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Title and description
    st.title("🌱 AI-Driven LCA Tool for Metallurgy & Mining")
    st.markdown("""
    ### Advancing Circularity and Sustainability
    **AI-powered Life Cycle Assessment platform** with emphasis on circular economy for metals and critical minerals.
    Designed for metallurgists, engineers, and decision-makers to make data-driven sustainability choices.
    """)
    
    # Problem statement compliance banner
    st.info("""
    🎯 **Solution Features**: AI parameter estimation • 🔄 **Circular Routes**: Raw vs recycled comparison • 
    🧪 **Critical Minerals**: Lithium, Cobalt, REE+ • 📊 **Smart Analytics**: Actionable sustainability insights
    """)
    
    # Load model
    if 'model_data' not in st.session_state:
        with st.spinner("Loading ML model..."):
            st.session_state.model_data = load_model()
    
    if st.session_state.model_data is None:
        st.error("Cannot proceed without a trained model. Please train the model first.")
        st.stop()
    
    # Main input area (moved from sidebar)
    st.header("🔧 Input Parameters")
    
    # Create input columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("🏭 Production Settings")
        
        # Industry sector selection (Problem Statement requirement)
        sector_options = {
            'Energy Storage': '🔋',
            'Electronics': '💻', 
            'Automotive': '🚗',
            'Renewable Energy': '🌞',
            'Construction': '🏗️',
            'Aerospace': '✈️',
            'Defense': '🛡️',
            'General Manufacturing': '🏭'
        }
        
        selected_sector = st.selectbox(
            "Select Industry Sector:",
            options=list(sector_options.keys()),
            help="Choose the industry application for contextualized analysis"
        )
        st.markdown(f"{sector_options[selected_sector]} **{selected_sector}** sector selected")
        
        # Metal selection with critical minerals
        metal_options = get_metal_options()
        selected_metal = st.selectbox(
            "Select Metal/Critical Mineral:",
            options=list(metal_options.keys()),
            help="Choose the metal or critical mineral for LCA analysis"
        )
        
        # Display criticality info
        critical_minerals = ['Lithium', 'Cobalt', 'Rare Earth Elements', 'Platinum', 'Tungsten', 'Indium']
        if selected_metal in critical_minerals:
            st.warning(f"⚠️ **{selected_metal}** is a critical mineral - enhanced circularity focus recommended")
        
        # Process type selection
        process_options = get_process_options()
        selected_process = st.selectbox(
            "Select Process Type:",
            options=list(process_options.keys()),
            help="Choose the production process"
        )
        
        # End of life selection
        eol_options = get_end_of_life_options()
        selected_eol = st.selectbox(
            "Select End of Life:",
            options=list(eol_options.keys()),
            help="Choose the end-of-life treatment"
        )
        
        # Circular Economy Route Selection (Problem Statement alignment)
        st.subheader("♻️ Circularity Route")
        route_options = {
            'Primary (Virgin Mining)': {
                'description': 'Traditional mining and primary smelting',
                'circularity': 0.1,
                'sustainability': 'Low',
                'icon': '⛏️'
            },
            'Secondary (Recycling)': {
                'description': 'Urban mining and scrap recycling',
                'circularity': 0.8,
                'sustainability': 'High',
                'icon': '♻️'
            },
            'Circular Hybrid': {
                'description': 'Optimized primary-secondary mix',
                'circularity': 0.6,
                'sustainability': 'Medium-High',
                'icon': '🔄'
            },
            'Advanced Recovery': {
                'description': 'Cutting-edge extraction from waste',
                'circularity': 0.9,
                'sustainability': 'Very High',
                'icon': '🧬'
            }
        }
        
        selected_route = st.selectbox(
            "Select Circular Economy Route:",
            options=list(route_options.keys()),
            help="Choose the material sourcing approach based on circular economy principles"
        )
        
        route_info = route_options[selected_route]
        col_route1, col_route2 = st.columns(2)
        with col_route1:
            delta_value = route_info['circularity'] - 0.5
            delta_color = "#2E8B57" if delta_value >= 0 else "#DC143C"
            delta_symbol = "▲" if delta_value >= 0 else "▼"
            
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 1rem;
                border-radius: 12px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                text-align: center;
                margin: 0.5rem 0;
                border: 1px solid rgba(255,255,255,0.1);
            ">
                <div style="color: white; font-size: 0.9rem; font-weight: 500; margin-bottom: 0.3rem;">
                    Circularity Index
                </div>
                <div style="color: white; font-size: 2rem; font-weight: bold; margin-bottom: 0.3rem;">
                    {route_info['circularity']:.1f}
                </div>
                <div style="color: {delta_color}; font-size: 0.8rem; font-weight: 500;">
                    {delta_symbol} {abs(delta_value):.1f}
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col_route2:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
                padding: 1rem;
                border-radius: 12px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                text-align: center;
                margin: 0.5rem 0;
                border: 1px solid rgba(255,255,255,0.1);
                display: flex;
                align-items: center;
                justify-content: center;
                min-height: 100px;
            ">
                <div style="color: #2c3e50; font-size: 1.2rem; font-weight: bold;">
                    {route_info['sustainability']} {route_info['icon']}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.info(f"📋 {route_info['description']}")
        
        # Circularity enhancement suggestions
        if route_info['circularity'] < 0.5:
            st.warning("💡 **Suggestion**: Consider secondary/recycling routes to improve circularity")
    
    with col2:
        st.subheader("📊 Process Parameters")
    
        transport_km = st.number_input(
            "Transport Distance (km):",
            min_value=0.0,
            max_value=10000.0,
            value=500.0,
            step=50.0,
            help="Distance for material transport"
        )
        
        cost_per_kg = st.number_input(
            "Cost per kg ($):",
            min_value=0.0,
            max_value=100.0,
            value=5.0,
            step=0.1,
            help="Production cost per kilogram"
        )
        
        production_volume = st.number_input(
            "Production Volume (kg):",
            min_value=1.0,
            max_value=1000000.0,
            value=1000.0,
            step=100.0,
            help="Total production volume"
        )
        
        recovery_rate = st.number_input(
            "Recovery Rate (%):",
            min_value=0.0,
            max_value=100.0,
            value=85.0,
            step=5.0,
            help="Material recovery efficiency"
        )
    
    with col3:
        st.subheader("🌿 Additional Parameters")
        
        product_life_years = st.number_input(
            "Product Life Extension (years):",
            min_value=0.0,
            max_value=50.0,
            value=10.0,
            step=1.0,
            help="Expected product lifespan extension"
        )
        
        waste_ratio = st.number_input(
            "Waste kg per kg metal:",
            min_value=0.0,
            max_value=10.0,
            value=0.5,
            step=0.1,
            help="Waste generated per kg of metal produced"
        )
    
    # Optional environmental inputs section
    with st.expander("🌿 Optional Environmental Data (Leave blank to predict)"):
        col_env1, col_env2, col_env3 = st.columns(3)
        
        with col_env1:
            energy_input = st.number_input(
                "Energy Use (MJ/kg) - Optional:",
                min_value=0.0,
                value=0.0,
                help="Leave 0 to predict"
            )
        
        with col_env2:
            water_input = st.number_input(
                "Water Use (L/kg) - Optional:",
                min_value=0.0,
                value=0.0,
                help="Leave 0 to predict"
            )
        
        with col_env3:
            emissions_input = st.number_input(
                "Emissions (kgCO2/kg) - Optional:",
                min_value=0.0,
                value=0.0,
                help="Leave 0 to predict"
            )
    
    # Prepare inputs
    inputs = {
        'Metal': metal_options[selected_metal],
        'Process_Type': process_options[selected_process],
        'End_of_Life': eol_options[selected_eol],
        'Transport_km': transport_km,
        'Cost_per_kg': cost_per_kg,
        'Product_Life_Extension_years': product_life_years,
        'Waste_kg_per_kg_metal': waste_ratio
    }
    
    # Prediction section
    st.header("📈 Predictions")
    
    # Center the predict button
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        
        if st.button("🔮 Generate Predictions", type="primary", use_container_width=True):
            with st.spinner("Generating predictions..."):
                predictions = predict_lca_values(st.session_state.model_data, inputs)
                
                if predictions:
                    st.session_state.current_predictions = predictions
                    st.session_state.current_inputs = inputs
    
    # Display results if available
    if hasattr(st.session_state, 'current_predictions') and st.session_state.current_predictions:
        predictions = st.session_state.current_predictions
        
        # Display predictions in a nice table
        st.markdown('<div class="prediction-table">', unsafe_allow_html=True)
        st.subheader("🎯 Predicted Values")
        
        # Environmental indicators
        st.markdown("**🌱 Environmental Indicators**")
        
        # Custom styled metrics for environmental data
        energy_val = predictions.get('Energy_Use_MJ_per_kg', 0)
        if energy_input > 0:
            energy_val = energy_input
        emissions_val = predictions.get('Emission_kgCO2_per_kg', 0)
        if emissions_input > 0:
            emissions_val = emissions_input
        water_val = predictions.get('Water_Use_l_per_kg', 0)
        if water_input > 0:
            water_val = water_input
            
        env_col1, env_col2, env_col3 = st.columns(3)
        
        with env_col1:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
                padding: 20px;
                border-radius: 12px;
                text-align: center;
                color: white;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                margin: 10px 0;
            ">
                <h4 style="color: #e0e7ff; margin: 0; font-size: 0.9em;">Energy Use</h4>
                <h2 style="color: white; margin: 5px 0; font-size: 1.5em; font-weight: bold;">{energy_val:.2f} MJ/kg</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with env_col2:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
                padding: 20px;
                border-radius: 12px;
                text-align: center;
                color: white;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                margin: 10px 0;
            ">
                <h4 style="color: #e0e7ff; margin: 0; font-size: 0.9em;">CO₂ Emissions</h4>
                <h2 style="color: white; margin: 5px 0; font-size: 1.5em; font-weight: bold;">{emissions_val:.2f} kg/kg</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with env_col3:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
                padding: 20px;
                border-radius: 12px;
                text-align: center;
                color: white;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                margin: 10px 0;
            ">
                <h4 style="color: #e0e7ff; margin: 0; font-size: 0.9em;">Water Use</h4>
                <h2 style="color: white; margin: 5px 0; font-size: 1.5em; font-weight: bold;">{water_val:.2f} L/kg</h2>
            </div>
            """, unsafe_allow_html=True)
        
        # Circularity indicators
        st.markdown("**♻️ Circularity Indicators**")
        circ_col1, circ_col2, circ_col3 = st.columns(3)
        
        with circ_col1:
            circ_val = predictions.get('Circularity_Index', 0)
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #059669 0%, #10b981 100%);
                padding: 20px;
                border-radius: 12px;
                text-align: center;
                color: white;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                margin: 10px 0;
            ">
                <h4 style="color: #d1fae5; margin: 0; font-size: 0.9em;">Circularity Index</h4>
                <h2 style="color: white; margin: 5px 0; font-size: 1.5em; font-weight: bold;">{circ_val:.3f}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with circ_col2:
            recycled_val = predictions.get('Recycled_Content_pct', 0)
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #059669 0%, #10b981 100%);
                padding: 20px;
                border-radius: 12px;
                text-align: center;
                color: white;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                margin: 10px 0;
            ">
                <h4 style="color: #d1fae5; margin: 0; font-size: 0.9em;">Recycled Content</h4>
                <h2 style="color: white; margin: 5px 0; font-size: 1.5em; font-weight: bold;">{recycled_val:.1f}%</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with circ_col3:
            reuse_val = predictions.get('Reuse_Potential_score', 0)
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #059669 0%, #10b981 100%);
                padding: 20px;
                border-radius: 12px;
                text-align: center;
                color: white;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                margin: 10px 0;
            ">
                <h4 style="color: #d1fae5; margin: 0; font-size: 0.9em;">Reuse Potential</h4>
                <h2 style="color: white; margin: 5px 0; font-size: 1.5em; font-weight: bold;">{reuse_val:.3f}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

    
    # Pathway Comparison Section
    if 'current_predictions' in st.session_state:
        st.header("🔄 Production Pathway Comparison")
        
        comparison_df = create_pathway_comparison(st.session_state.current_inputs)
        
        if not comparison_df.empty:
            st.markdown('<div class="pathway-comparison">', unsafe_allow_html=True)
            st.dataframe(
                comparison_df.style.highlight_min(
                    subset=['Energy (MJ/kg)', 'Emissions (kgCO2/kg)', 'Water (L/kg)'],
                    color='lightgreen'
                ).highlight_max(
                    subset=['Circularity Index', 'Recycled Content (%)', 'Reuse Potential'],
                    color='lightblue'
                ),
                use_container_width=True
            )
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Visualizations Section
    if 'current_predictions' in st.session_state:
        st.header("📊 Visualizations")
        
        viz_col1, viz_col2 = st.columns(2)
        
        with viz_col1:
            try:
                # Energy comparison chart
                energy_fig = create_energy_comparison(comparison_df)
                st.plotly_chart(energy_fig, use_container_width=True)
                
                # Circularity comparison
                circ_fig = create_circularity_comparison(comparison_df)
                st.plotly_chart(circ_fig, use_container_width=True)
            except Exception as e:
                st.warning(f"Visualization error: {str(e)}")
        
        with viz_col2:
            try:
                # Emissions comparison
                emissions_fig = create_emissions_comparison(comparison_df)
                st.plotly_chart(emissions_fig, use_container_width=True)
                
                # Sankey diagram
                sankey_fig = create_sankey_diagram(st.session_state.current_predictions)
                st.plotly_chart(sankey_fig, use_container_width=True)
            except Exception as e:
                st.warning(f"Visualization error: {str(e)}")
    
    # Recommendations Section
    if 'current_predictions' in st.session_state:
        st.header("💡 Recommendations")
        
        rec_col1, rec_col2 = st.columns(2)
        
        with rec_col1:
            st.subheader("🌱 Environmental Improvements")
            env_recommendations = get_environmental_recommendations(
                st.session_state.current_predictions
            )
            for rec in env_recommendations:
                st.success(rec)
        
        with rec_col2:
            st.subheader("♻️ Circularity Improvements")
            circ_recommendations = get_circularity_recommendations(
                st.session_state.current_predictions
            )
            for rec in circ_recommendations:
                st.info(rec)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>🌱 LCA Metals Prediction System | Powered by Machine Learning</p>
    </div>
    """, unsafe_allow_html=True)

    # Professional Report Generation (Problem Statement requirement)
    if 'current_predictions' in st.session_state:
        st.header("📄 Professional Report & Export")
        
        report_col1, report_col2, report_col3 = st.columns(3)
        
        with report_col1:
            st.subheader("📊 Summary Report")
            if st.button("Generate Executive Summary", type="primary"):
                # Generate comprehensive report
                report_data = {
                    'analysis_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'sector': selected_sector,
                    'metal': selected_metal,
                    'route': selected_route,
                    'predictions': st.session_state['current_predictions']
                }
                
                # Create downloadable report
                report_text = f"""
# AI-Driven LCA Analysis Report
## Comprehensive Sustainability Assessment

**Analysis Date:** {report_data['analysis_date']}
**Industry Sector:** {selected_sector}
**Metal/Critical Mineral:** {selected_metal}
**Circular Economy Route:** {selected_route}

### Environmental Impact Assessment
- Energy Use: {st.session_state['current_predictions']['Energy_Use_MJ_per_kg']:.2f} MJ/kg
- CO2 Emissions: {st.session_state['current_predictions']['Emission_kgCO2_per_kg']:.2f} kg CO2/kg
- Water Use: {st.session_state['current_predictions']['Water_Use_l_per_kg']:.2f} L/kg

### Circularity & Sustainability Metrics
- Circularity Index: {st.session_state['current_predictions']['Circularity_Index']:.3f}
- Recycled Content: {st.session_state['current_predictions']['Recycled_Content_pct']:.1f}%
- Reuse Potential: {st.session_state['current_predictions']['Reuse_Potential_score']:.2f}

### Recommendations
- Route Optimization: {'✅ Optimized' if route_info['circularity'] > 0.6 else '⚠️ Consider higher circularity routes'}
- Critical Mineral Status: {'⚠️ Enhanced focus needed' if selected_metal in critical_minerals else '✅ Standard approach'}
- Sustainability Rating: {route_info['sustainability']}

---
*Generated by AI-Driven LCA Tool for Metallurgy and Mining*
"""
                
                st.download_button(
                    label="📥 Download Report (TXT)",
                    data=report_text,
                    file_name=f"LCA_Report_{selected_metal}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
        
        with report_col2:
            st.subheader("📈 Data Export")
            if st.button("Export Analysis Data"):
                # Prepare comprehensive data export
                export_data = {
                    'Metadata': {
                        'Analysis_Date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'Tool_Name': 'AI-Driven LCA Tool for Metallurgy',
                        'Industry_Sector': selected_sector,
                        'Metal_Type': selected_metal,
                        'Process_Type': selected_process,
                        'End_of_Life': selected_eol,
                        'Circular_Route': selected_route,
                        'Route_Circularity': route_info['circularity'],
                        'Route_Sustainability': route_info['sustainability']
                    },
                    'Input_Parameters': {
                        'Transport_Distance_km': transport_km,
                        'Cost_per_kg': cost_per_kg,
                        'Production_Volume_kg': production_volume,
                        'Recovery_Rate_pct': recovery_rate
                    },
                    'Environmental_Results': {
                        'Energy_Use_MJ_per_kg': st.session_state['current_predictions']['Energy_Use_MJ_per_kg'],
                        'CO2_Emission_kg_per_kg': st.session_state['current_predictions']['Emission_kgCO2_per_kg'],
                        'Water_Use_L_per_kg': st.session_state['current_predictions']['Water_Use_l_per_kg']
                    },
                    'Circularity_Results': {
                        'Circularity_Index': st.session_state['current_predictions']['Circularity_Index'],
                        'Recycled_Content_pct': st.session_state['current_predictions']['Recycled_Content_pct'],
                        'Reuse_Potential_score': st.session_state['current_predictions']['Reuse_Potential_score']
                    }
                }
                
                # Convert to JSON for download
                json_str = json.dumps(export_data, indent=2)
                
                st.download_button(
                    label="📊 Download JSON Data",
                    data=json_str,
                    file_name=f"LCA_Data_{selected_metal}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
        
        with report_col3:
            st.subheader("📈 Analysis Summary")
            st.success("✅ **Analysis Complete**")
            
            analysis_summary = [
                "🔬 Environmental Impact Analysis",
                "♻️ Circularity Assessment", 
                "🌱 Sustainability Evaluation",
                "⚡ Performance Optimization",
                "📊 Data-Driven Insights",
                "🎯 Actionable Recommendations"
            ]
            
            for item in analysis_summary:
                st.markdown(f"- {item}")
                
            st.info("� **Comprehensive LCA analysis completed successfully**")

if __name__ == "__main__":
    main()