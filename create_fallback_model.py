"""
Fallback model generator for Railway deployment
Creates a simple working model when LFS models are not available
"""

import pickle
import os

try:
    import numpy as np
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.preprocessing import LabelEncoder
    from sklearn.multioutput import MultiOutputRegressor
except ImportError as e:
    print(f"⚠️ Missing dependencies: {e}")
    print("Installing required packages...")
    import subprocess
    subprocess.check_call(["pip", "install", "scikit-learn", "numpy"])
    
    import numpy as np
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.preprocessing import LabelEncoder
    from sklearn.multioutput import MultiOutputRegressor

def create_simple_fallback_model():
    """Create a simple fallback model that works with the app structure"""
    
    print("Creating fallback model for Railway deployment...")
    
    # Create label encoders
    metal_encoder = LabelEncoder()
    process_encoder = LabelEncoder()
    eol_encoder = LabelEncoder()
    
    # Fit with expected categories (matching app.py expectations)
    metals = ['Aluminium', 'Steel', 'Copper', 'Zinc', 'Lead', 'Nickel', 'Tin', 'Gold']
    processes = ['Primary', 'Recycled', 'Hybrid']
    eol_options = ['Recycled', 'Landfilled', 'Reused']
    
    metal_encoder.fit(metals)
    process_encoder.fit(processes)
    eol_encoder.fit(eol_options)
    
    # Create simple models
    np.random.seed(42)  # For reproducible results
    
    # Environmental model (predicts: Energy, Emissions, Water)
    env_model = MultiOutputRegressor(RandomForestRegressor(n_estimators=50, random_state=42))
    
    # Circularity model (predicts: Circularity Index, Recycled Content %, Reuse Potential)
    circ_model = MultiOutputRegressor(RandomForestRegressor(n_estimators=50, random_state=42))
    
    # Generate realistic training data (13 features as expected)
    n_samples = 1000
    
    # Features: Metal, Process, EOL, Transport_km, Cost_per_kg, Product_Life, Waste_ratio, + 6 engineered features
    X_train = np.random.rand(n_samples, 13)
    
    # Make categorical features integer-like
    X_train[:, 0] = np.random.randint(0, len(metals), n_samples)  # Metal
    X_train[:, 1] = np.random.randint(0, len(processes), n_samples)  # Process
    X_train[:, 2] = np.random.randint(0, len(eol_options), n_samples)  # EOL
    
    # Scale continuous features to realistic ranges
    X_train[:, 3] *= 2000  # Transport_km: 0-2000
    X_train[:, 4] *= 20    # Cost_per_kg: 0-20
    X_train[:, 5] *= 30    # Product_Life: 0-30 years
    X_train[:, 6] *= 5     # Waste_ratio: 0-5
    
    # Create realistic target values
    # Environmental targets (Energy MJ/kg, Emissions kgCO2/kg, Water L/kg)
    y_env = np.zeros((n_samples, 3))
    for i in range(n_samples):
        # Base values depend on process type
        process_factor = 0.3 if X_train[i, 1] == 1 else 1.0  # Recycled vs Primary
        
        energy = np.random.normal(50 * process_factor, 15)  # 20-80 MJ/kg
        emissions = np.random.normal(5 * process_factor, 2)  # 2-8 kgCO2/kg
        water = np.random.normal(20 * process_factor, 8)    # 10-30 L/kg
        
        y_env[i] = [max(1, energy), max(0.1, emissions), max(0.5, water)]
    
    # Circularity targets (Circularity Index 0-1, Recycled Content %, Reuse Potential 0-1)
    y_circ = np.zeros((n_samples, 3))
    for i in range(n_samples):
        # Higher circularity for recycled processes
        base_circ = 0.8 if X_train[i, 1] == 1 else 0.3
        
        circularity = np.random.normal(base_circ, 0.1)
        recycled_content = np.random.normal(70 if X_train[i, 1] == 1 else 20, 15)
        reuse_potential = np.random.normal(base_circ, 0.1)
        
        y_circ[i] = [
            max(0, min(1, circularity)),
            max(0, min(100, recycled_content)),
            max(0, min(1, reuse_potential))
        ]
    
    # Train models
    env_model.fit(X_train, y_env)
    circ_model.fit(X_train, y_circ)
    
    # Create the model data structure expected by app.py
    model_data = {
        'model_type': 'optimized_dual_target',
        'environmental_model': env_model,
        'circularity_models': {
            'RandomForest': circ_model
        },
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
            'created_by': 'railway_deployment_fallback',
            'description': 'Simple fallback model for Railway deployment when LFS models unavailable'
        }
    }
    
    return model_data

def save_fallback_model():
    """Save the fallback model to the models directory"""
    
    # Create models directory if it doesn't exist
    os.makedirs('models', exist_ok=True)
    
    # Generate the fallback model
    model_data = create_simple_fallback_model()
    
    # Save it
    fallback_path = 'models/railway_fallback_model.pkl'
    
    try:
        with open(fallback_path, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"✅ Fallback model saved to {fallback_path}")
        print("📊 Model includes:")
        print("  - Environmental predictions (Energy, Emissions, Water)")
        print("  - Circularity predictions (Index, Recycled Content, Reuse Potential)")
        print("  - Label encoders for categorical variables")
        print("  - Compatible with 13-feature input structure")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to save fallback model: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Creating Railway deployment fallback model...")
    
    success = save_fallback_model()
    
    if success:
        print("\n✅ SUCCESS: Fallback model created!")
        print("The Streamlit app should now work on Railway.")
    else:
        print("\n❌ FAILED: Could not create fallback model.")