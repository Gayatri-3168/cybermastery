#!/usr/bin/env python3

from app import app, db, UserMissionProgress
from flask import request

def reset_employee_test_data():
    """Reset employee test data to fix escape room access"""
    
    print("🧹 Resetting Employee Test Data...")
    print("=" * 50)
    
    with app.app_context():
        try:
            # Find all employee UserMissionProgress records with levels_completed=True
            employee_progress = UserMissionProgress.query.join(User).filter(
                User.role == 'employee',
                UserMissionProgress.levels_completed == True
            ).all()
            
            print(f"Found {len(employee_progress)} employee records with levels_completed=True")
            
            # Reset them to levels_completed=False
            for progress in employee_progress:
                progress.levels_completed = False
                progress.escape_completed = False
                progress.mission_completed = False
                print(f"Reset mission {progress.mission_id} for user {progress.user_id}")
            
            db.session.commit()
            print("✅ Employee test data reset successfully!")
            
            # Verify the reset
            remaining = UserMissionProgress.query.join(User).filter(
                User.role == 'employee',
                UserMissionProgress.levels_completed == True
            ).count()
            
            print(f"🔍 Remaining employee records with levels_completed=True: {remaining}")
            
            if remaining == 0:
                print("🎉 All employee test data cleaned! Employees should now access escape rooms normally.")
            else:
                print("⚠️  Some records still exist. Check database manually.")
                
        except Exception as e:
            print(f"❌ Error resetting data: {e}")

if __name__ == "__main__":
    reset_employee_test_data()
