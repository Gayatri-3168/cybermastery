#!/usr/bin/env python3
"""
Reseed escape rooms database with updated missions 1-10
"""

from app import app, db, EscapeRoom, seed_escape_rooms

def main():
    print("🔄 Reseeding escape rooms database...")
    
    with app.app_context():
        # Clear existing escape rooms
        print("🗑️ Clearing existing escape rooms...")
        EscapeRoom.query.delete()
        db.session.commit()
        
        # Add updated escape rooms (missions 1-10 for both roles)
        print("📦 Adding updated escape rooms...")
        seed_escape_rooms()
        
        print("✅ Database reseeded successfully!")
        print("🎯 Now supporting missions 1-10 for both student and employee roles")
    
    print("\n📋 Restart your Flask app to load the new data.")

if __name__ == "__main__":
    main()
