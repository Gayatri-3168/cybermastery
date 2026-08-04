#!/usr/bin/env python3

from app import app, db, Level

def check_level_answer():
    """Check the correct answer for level 1"""
    
    print("🔍 Checking Level 1 Answer...")
    print("=" * 40)
    
    with app.app_context():
        try:
            level = Level.query.get(1)
            if level:
                print(f"Level {level.id}: {level.level_number}")
                print(f"Correct Answer: {level.correct_answer}")
                print(f"Option A: {level.option_a}")
                print(f"Option B: {level.option_b}")
                print(f"Option C: {level.option_c}")
                print(f"Option D: {level.option_d}")
                print(f"Scenario: {level.scenario[:100]}...")
            else:
                print("❌ Level 1 not found")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_level_answer()
