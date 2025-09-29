#!/usr/bin/env python3
"""
Simple health check script for Railway deployment
"""

import requests
import sys
import os
import time

def check_health():
    """Check if the Streamlit app is responding"""
    port = os.environ.get('PORT', '8501')
    
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            # Try to connect to the Streamlit health endpoint
            response = requests.get(
                f'http://localhost:{port}/_stcore/health',
                timeout=5
            )
            
            if response.status_code == 200:
                print(f"✅ Health check passed on port {port}")
                return True
                
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1}/{max_attempts}: Health check failed - {e}")
            
        time.sleep(2)
    
    print(f"❌ Health check failed after {max_attempts} attempts")
    return False

if __name__ == "__main__":
    success = check_health()
    sys.exit(0 if success else 1)