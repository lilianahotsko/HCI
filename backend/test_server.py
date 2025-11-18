#!/usr/bin/env python3
"""
Simple test script to verify the Flask server can start and respond
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from app import app
    
    print("✓ App imported successfully")
    
    with app.test_client() as client:
        # Test health endpoint
        response = client.get('/api/health')
        print(f"✓ Health endpoint status: {response.status_code}")
        print(f"✓ Response: {response.get_json()}")
        
        # Test participant creation
        response = client.post('/api/experiment/participant', 
                             json={'participant_id': 'TEST001'})
        print(f"✓ Participant endpoint status: {response.status_code}")
        if response.status_code == 200:
            print(f"✓ Response: {response.get_json()}")
        else:
            print(f"✗ Error: {response.get_data(as_text=True)}")
            
    print("\n✓ All tests passed! Server should work correctly.")
    print("\nTo start the server, run:")
    print("  python app.py")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

