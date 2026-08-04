#!/usr/bin/env python3

from app import app, db, User, UserMissionProgress, Progress

def check_database_state():
    """Check database state for employee users"""
    
    print("🔍 Checking Database State...")
    print("=" * 50)
    
    with app.app_context():
        try:
            # Check all users and their roles
            users = User.query.all()
            print(f"\n👥 Total Users: {len(users)}")
            
            for user in users:
                print(f"  User {user.id}: {user.username} ({user.role}) - XP: {user.xp}")
            
            # Check UserMissionProgress for employees
            print(f"\n📊 UserMissionProgress Records:")
            employee_progress = UserMissionProgress.query.join(User).filter(
                User.role == 'employee'
            ).all()
            
            for progress in employee_progress:
                user = User.query.get(progress.user_id)
                print(f"  Mission {progress.mission_id} for User {user.username} ({user.role}):")
                print(f"    learning_completed: {progress.learning_completed}")
                print(f"    levels_completed: {progress.levels_completed}")
                print(f"    escape_completed: {progress.escape_completed}")
                print(f"    mission_completed: {progress.mission_completed}")
            
            # Check Progress table for employees
            print(f"\n📈 Progress Records:")
            progress_records = Progress.query.join(User).filter(
                User.role == 'employee'
            ).all()
            
            for prog in progress_records:
                user = User.query.get(prog.user_id)
                print(f"  Mission {prog.mission_id} for User {user.username} ({user.role}):")
                print(f"    current_level: {prog.current_level}")
                print(f"    completed: {prog.completed}")
                print(f"    attempts_left: {prog.attempts_left}")
            
            print(f"\n✅ Database check completed!")
            
        except Exception as e:
            print(f"❌ Error checking database: {e}")

if __name__ == "__main__":
    check_database_state()
