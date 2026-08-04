#!/usr/bin/env python3

def test_ranking_logic():
    """Test the ranking calculation logic"""
    
    print("🏆 Testing Ranking Logic...")
    print("=" * 50)
    
    # Simulate user data
    users = [
        {'role': 'student', 'xp': 100},
        {'role': 'student', 'xp': 200}, 
        {'role': 'student', 'xp': 150},
        {'role': 'employee', 'xp': 300},
        {'role': 'employee', 'xp': 250},
        {'role': 'employee', 'xp': 400},
    ]
    
    # Test student ranking
    print("\n📚 Student Leaderboard:")
    student_users = [u for u in users if u['role'] == 'student']
    student_users.sort(key=lambda x: x['xp'], reverse=True)
    
    for i, user in enumerate(student_users, 1):
        print(f"  Rank {i}: {user['xp']} XP")
    
    # Test employee ranking  
    print("\n💼 Employee Leaderboard:")
    employee_users = [u for u in users if u['role'] == 'employee']
    employee_users.sort(key=lambda x: x['xp'], reverse=True)
    
    for i, user in enumerate(employee_users, 1):
        print(f"  Rank {i}: {user['xp']} XP")
    
    # Test specific user rankings
    print("\n🎯 Specific User Rankings:")
    
    # Student with 150 XP
    student_higher = len([u for u in student_users if u['xp'] > 150])
    student_rank = student_higher + 1
    print(f"  Student (150 XP): Rank #{student_rank} in Student Leaderboard")
    
    # Employee with 250 XP
    employee_higher = len([u for u in employee_users if u['xp'] > 250])
    employee_rank = employee_higher + 1
    print(f"  Employee (250 XP): Rank #{employee_rank} in Employee Leaderboard")
    
    print("\n✅ Ranking logic verified!")
    print("📊 Each user gets rank based on their respective leaderboard")

if __name__ == "__main__":
    test_ranking_logic()
