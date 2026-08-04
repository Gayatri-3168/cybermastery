#!/usr/bin/env python3

import os
import sys

# Set Gemini API key before importing app
os.environ['GEMINI_API_KEY'] = 'AIzaSyDm0SBD-4VCXokAm462YCrwka2VJq9JgiE'

# Now import and run the app
from app import app

if __name__ == "__main__":
    print("🚀 Starting CyberMastery with Gemini AI...")
    print("🔑 Gemini API Key configured")
    print("🤖 Chatbot ready with AI responses")
    print("=" * 50)
    
    # Run Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
