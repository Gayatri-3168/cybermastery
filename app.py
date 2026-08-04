import re
import os
import time
import json
from datetime import datetime, timedelta
from flask_mail import Mail, Message
import random
from sqlalchemy.exc import IntegrityError
from flask import Flask, render_template, redirect, request, send_file, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, login_user, logout_user,
    login_required, current_user, UserMixin
)
from config import Config
from flask import Flask, request, jsonify, render_template
import requests
import random
import string
#from google import genai
# Multiplayer Mission Pool
MULTIPLAYER_MISSION_POOL = [
    {
        "type": "phishing_detection",
        "data": {
            "scenario": "🚨 ALERT: Suspicious email detected in CEO's inbox",
            "task": "You are the security analyst. Analyze this email and determine if it's legitimate or phishing:",
            "email": "From: security@microsoft.com\nSubject: URGENT: Account Suspension Notice\n\nDear User,\n\nWe detected unusual login attempts on your account from IP: 192.168.1.100\n\nClick here immediately to secure your account: http://bit.ly/secure-now\n\nFailure to act within 24 hours will result in permanent account suspension.\n\nMicrosoft Security Team",
            "options": ["Legitimate - Allow", "Phishing - Block"],
            "correct_answer": "Phishing - Block",
            "explanation": "Correct! This is phishing: Uses shortened URL, creates urgency, generic greeting, Microsoft never uses bit.ly links."
        }
    },
    {
        "type": "malware_response",
        "data": {
            "scenario": "🦠 MALWARE ALERT: Employee clicked suspicious attachment",
            "task": "An employee reports opening an invoice attachment. Now their computer shows this pop-up:",
            "alert": "⚠️ YOUR FILES ARE ENCRYPTED!\n\nAll your documents have been locked with military-grade encryption.\n\nPay 0.5 Bitcoin within 72 hours to receive decryption key.\n\nTimer: 71:59:45\n\nWhat is your immediate action?",
            "options": [
                "Pay the ransom immediately",
                "Disconnect from network and isolate the machine",
                "Restart computer in safe mode",
                "Try to decrypt files with free tools"
            ],
            "correct_answer": "Disconnect from network and isolate the machine",
            "explanation": "Correct! First step is containment - disconnect to prevent spread, then contact IT security team."
        }
    },
    {
        "type": "password_security",
        "data": {
            "scenario": "🔐 PASSWORD AUDIT: Weak passwords detected",
            "task": "Security scan found these passwords. Which requires immediate action?",
            "passwords": [
                "user1: password123",
                "user2: Summer2024!",
                "user3: Tr0ub4dor&3",
                "user4: Qwerty123!"
            ],
            "options": [
                "user1 - password123",
                "user2 - Summer2024!",
                "user3 - Tr0ub4dor&3",
                "user4 - Qwerty123!"
            ],
            "correct_answer": "user1 - password123",
            "explanation": "Correct! 'password123' is extremely weak and commonly used. Requires immediate password reset."
        }
    },
    {
        "type": "social_engineering",
        "data": {
            "scenario": "📞 PHONE ALERT: Suspicious call reported",
            "task": "Employee received this call. How should they respond?",
            "call": "\"Hello, this is John from IT Support. We're doing system updates and I need your password to verify your account. Can you provide it now?\"",
            "options": [
                "Give the password to help IT",
                "Ask for employee ID first",
                "Refuse and report to real IT",
                "Provide partial information"
            ],
            "correct_answer": "Refuse and report to real IT",
            "explanation": "Correct! IT never asks for passwords over phone. This is a classic social engineering attack."
        }
    },
    {
        "type": "data_breach",
        "data": {
            "scenario": "🚨 DATA BREACH: Third-party vendor compromised",
            "task": "Your vendor reports a breach affecting customer data. What's your FIRST action?",
            "alert": "URGENT: Our database was accessed. Customer names, emails, and phone numbers may be exposed.",
            "options": [
                "Wait for more details",
                "Change all customer passwords immediately",
                "Assess impact and notify affected customers",
                "Delete all customer data"
            ],
            "correct_answer": "Assess impact and notify affected customers",
            "explanation": "Correct! First assess scope of breach, then comply with notification requirements within legal timeframes."
        }
    },
    {
        "type": "wifi_security",
        "data": {
            "scenario": "📶 REMOTE WORK: Employee needs secure connection",
            "task": "Employee is working from coffee shop and needs to access sensitive company files. Which connection is safest?",
            "networks": [
                "Free_Public_WiFi",
                "CoffeeShop_Guest",
                "Starbucks_Free_WiFi",
                "Mobile Hotspot (4G/5G)"
            ],
            "options": [
                "Free_Public_WiFi",
                "CoffeeShop_Guest", 
                "Starbucks_Free_WiFi",
                "Mobile Hotspot (4G/5G)"
            ],
            "correct_answer": "Mobile Hotspot (4G/5G)",
            "explanation": "Correct! Mobile hotspot provides encrypted, secure connection. Public WiFi can be intercepted."
        }
    },
    {
        "type": "usb_security",
        "data": {
            "scenario": "💾 PHYSICAL SECURITY: Suspicious USB found",
            "task": "Security guard found this USB in parking lot labeled 'Employee Salaries Q4'. What do you do?",
            "usb": "USB Drive Label: 'Employee Salaries Q4 - Confidential'\nFound: Employee Parking Lot, Near Entrance",
            "options": [
                "Plug in to check contents",
                "Give to IT security team",
                "Format and reuse",
                "Throw in trash"
            ],
            "correct_answer": "Give to IT security team",
            "explanation": "Correct! Unknown USBs can contain malware. Always have security professionals examine them first."
        }
    },
    {
        "type": "website_spoofing",
        "data": {
            "scenario": "🌐 FAKE WEBSITE: Employee reports suspicious login page",
            "task": "Employee tried to login at company portal but noticed something wrong. Analyze this URL:",
            "url": "https://cornpany-portal.com/login (note: 'cornpany' not 'company')",
            "options": [
                "Legitimate - allow access",
                "Fake - block and report",
                "Check SSL certificate first",
                "Allow but monitor"
            ],
            "correct_answer": "Fake - block and report",
            "explanation": "Correct! 'cornpany' is a typo-squatting attack. Block access and report to security team."
        }
    },
    {
        "type": "backup_recovery",
        "data": {
            "scenario": "💾 BACKUP FAILURE: Critical system down",
            "task": "Main server crashed. Backup system shows this status. What's your recovery plan?",
            "backup_status": "Local Backup: FAILED (corrupted)\nCloud Backup: AVAILABLE (24 hours old)\nOff-site Backup: AVAILABLE (48 hours old)",
            "options": [
                "Wait for local backup repair",
                "Restore from cloud backup (24h old)",
                "Restore from off-site backup (48h old)",
                "Rebuild from scratch"
            ],
            "correct_answer": "Restore from cloud backup (24h old)",
            "explanation": "Correct! Use most recent available backup (cloud) to minimize data loss, then fix local backup."
        }
    },
    {
        "type": "access_control",
        "data": {
            "scenario": "👤 ACCESS VIOLATION: Former employee still has access",
            "task": "Audit shows terminated employee still has active VPN access. Immediate action needed:",
            "employee": "John Smith - Terminated 2 weeks ago\nVPN Access: ACTIVE\nLast Login: Yesterday at 11:30 PM",
            "options": [
                "Send email reminder to return equipment",
                "Immediately revoke all access",
                "Monitor for suspicious activity",
                "Wait until next business day"
            ],
            "correct_answer": "Immediately revoke all access",
            "explanation": "Correct! Immediate access revocation is critical for security. Former employees should have no access."
        }
    },
    {
        "type": "email_filtering",
        "data": {
            "scenario": "📧 EMAIL SECURITY: Bulk suspicious emails detected",
            "task": "Email system flagged 500+ messages with similar characteristics. What's your action?",
            "emails": "500+ emails from different senders\nAll contain: 'Urgent Account Verification'\nAll have: Suspicious links\nTargets: All departments",
            "options": [
                "Delete all emails immediately",
                "Quarantine and analyze samples",
                "Forward to all employees as warning",
                "Ignore as false positives"
            ],
            "correct_answer": "Quarantine and analyze samples",
            "explanation": "Correct! Quarantine prevents delivery while analysis determines if it's a coordinated attack."
        }
    },
    {
        "type": "patch_management",
        "data": {
            "scenario": "🔧 CRITICAL VULNERABILITY: Zero-day announced",
            "task": "Security alert: Critical vulnerability in your web server. Attack already in the wild. Timeline?",
            "alert": "CVE-2024-XXXXX: Remote Code Execution\nCVSS: 10.0 (Critical)\nExploit: Publicly Available\nAffected: Your Web Servers",
            "options": [
                "Wait for official patch",
                "Patch within 24 hours",
                "Patch within 4 hours",
                "Take servers offline immediately"
            ],
            "correct_answer": "Patch within 4 hours",
            "explanation": "Correct! Critical vulnerabilities with public exploits require emergency patching within hours."
        }
    },
    {
        "type": "incident_response",
        "data": {
            "scenario": "🚨 ACTIVE ATTACK: System under attack right now",
            "task": "Security dashboard shows active intrusion. What's your priority?",
            "dashboard": "🔴 ACTIVE ATTACKS: 3\n📍 Source: Unknown\n🎯 Target: Database Server\n⏰ Duration: 12 minutes\n📊 Data Exfiltration: 2GB",
            "options": [
                "Document everything for later",
                "Contain and stop the attack",
                "Preserve evidence for prosecution",
                "Call management meeting"
            ],
            "correct_answer": "Contain and stop the attack",
            "explanation": "Correct! First priority is containment - stop the bleeding, then investigate and preserve evidence."
        }
    },
    {
        "type": "physical_security",
        "data": {
            "scenario": "🚪 BUILDING SECURITY: Tailgating incident",
            "task": "Security camera shows someone following authorized employee through secure door. Action?",
            "incident": "Employee A scanned badge\nPerson B followed through door before it closed\nPerson B not wearing company badge\nTime: 2:15 AM",
            "options": [
                "Review tomorrow during business hours",
                "Send security to investigate immediately",
                "Assume it's employee forgetting badge",
                "Email reminder about security policy"
            ],
            "correct_answer": "Send security to investigate immediately",
            "explanation": "Correct! Tailgating is serious security breach. Immediate investigation required."
        }
    },
    {
        "type": "cloud_security",
        "data": {
            "scenario": "☁️ CLOUD LEAK: S3 bucket exposed",
            "task": "Automated scan found public S3 bucket with sensitive data. What's urgent action?",
            "bucket": "Bucket: company-backup-files\nStatus: PUBLIC (world-readable)\nContents: Customer database backups\nSize: 15GB\nLast modified: 1 hour ago",
            "options": [
                "Notify cloud provider",
                "Make bucket private immediately",
                "Check access logs first",
                "Document for compliance report"
            ],
            "correct_answer": "Make bucket private immediately",
            "explanation": "Correct! Immediate containment (make private) prevents further data exposure, then investigate."
        }
    }
]

def generate_random_missions(count=10):
    """Generate random missions from the mission pool"""
    return random.sample(MULTIPLAYER_MISSION_POOL, min(count, len(MULTIPLAYER_MISSION_POOL)))

def get_time_remaining(challenge):
    """Calculate time remaining for a challenge"""
    if not challenge.started_at:
        return None
    
    elapsed = datetime.utcnow() - challenge.started_at
    remaining_seconds = (challenge.duration_minutes * 60) - elapsed.total_seconds()
    
    if remaining_seconds <= 0:
        return 0
    
    return int(remaining_seconds)

def get_escape_hint(puzzle_text):
    text = puzzle_text.lower()

    # Phishing / Fake links
    if "bit.ly" in text or "shortened" in text or "login here" in text:
        return "Shortened links can hide malicious websites. Always verify the real destination before clicking."

    if "domain" in text or "hr-payroll" in text or "look alike" in text:
        return "Attackers often use domains that look similar to real company websites."

    # Password reuse
    if "same password" in text or "reuse" in text:
        return "Using the same password across platforms increases the impact of a single data breach."

    # Unsafe websites
    if "https" in text or "http" in text:
        return "Websites without HTTPS do not encrypt your data and can expose credentials."

    # Browser extensions
    if "extension" in text or "install" in text:
        return "Malicious browser extensions can monitor activity and steal information."

    # Social engineering / fake profiles
    if "friend request" in text or "stranger" in text or "profile" in text:
        return "Fake profiles are commonly used to collect personal information."

    # Data leakage / ethics
    if "company data" in text or "personal email" in text:
        return "Sending company data to personal accounts violates security policies."

    # Pirated / cracked software
    if "cracked" in text or "pirated" in text:
        return "Pirated software often contains hidden malware or backdoors."

    # Default fallback
    return "Think carefully about what security rule is being violated in this situation."
    
app=Flask(__name__)

# Initialize Gemini AI
"""try:
    import google.genai as genai
    GEMINI_API_KEY = 'AIzaSyDm0SBD-4VCXokAm462YCrwka2VJq9JgiE'
    gemini_client = genai.Client(api_key=GEMINI_API_KEY)
    print("✅ Gemini AI initialized successfully")
except ImportError as e:
    print(f"❌ Failed to import google.genai: {e}")
    genai = None
    gemini_client = None"""

@app.route("/chatbot", methods=["POST"])
def chatbot():
    """Fast AI-powered chatbot for CyberMastery game and topics"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'reply': 'Please ask me something about CyberMastery!'})
        
        # Quick responses for common questions (no AI needed)
        quick_responses = {
            'hi': '👋 Hello! I\'m CyberBot! Ask me about missions, XP, badges, or cybersecurity! 🎮',
            'hello': '👋 Hello! I\'m CyberBot! Ask me about missions, XP, badges, or cybersecurity! 🎮',
            'what is phishing': '🎣 Phishing is when scammers send fake messages to steal your info! Learn to spot them in our missions! 🛡️',
            'how do missions work': '🎯 Complete 5 learning modules → unlock missions → 10 levels → escape rooms! Earn XP and badges! 🏆',
            'how do i earn xp': '⭐ Earn XP by answering questions correctly in missions and learning modules! 🎮',
            'what are badges': '🏆 Cyber Beginner (2 missions) → Cyber Expert (5 missions)! Show off your skills! 🎯',
            'what are learning modules': '📚 5 interactive modules per mission to learn cybersecurity basics! 🔐',
            'learning modules': '📚 Each mission has 5 learning modules! Complete them all to unlock the mission! 🎯',
            'how many learning modules': '🔢 5 learning modules per mission! Study them before attempting mission questions! 📚',
            'what do learning modules teach': '� Modules teach: phishing, passwords, browsing, social media, cyber ethics! 🛡️',
            'how do learning modules work': '📖 Read interactive content → answer questions → unlock missions! 🎮',
            'are learning modules required': '✅ Yes! Complete all 5 modules to unlock mission levels! 🔓',
            'learning module content': '📚 Interactive lessons with real-world scenarios and cybersecurity best practices! 🌐',
            'module difficulty': '📈 Progressive difficulty! Start with basics, advance to complex topics! ⬆️',
            'social engineering': '� Social engineering tricks people into revealing info! Learn to spot manipulation in our missions! 🛡️',
            'password safety': '🔐 Use strong, unique passwords! Enable 2FA! Learn password security in our missions! 🔑',
            'browsing safety': '🌐 Check HTTPS, avoid suspicious links! Learn safe browsing in our missions! 🔒',
            'what are escape rooms': '🚪 Unlock escape rooms after completing missions! Test your cybersecurity skills! 🎮',
            'how do i unlock missions': '🔓 Complete 5 learning modules to unlock your first mission! Keep learning! 📚',
            'what topics are covered': '📚 Phishing, passwords, browsing, social media, cyber ethics! All through interactive missions! 🛡️',
            'how do i level up': '⬆️ Answer questions correctly in missions and modules to level up and earn XP! 🎮',
            'what is cybermastery': '🎮 CyberMastery is a gamified cybersecurity learning platform! Learn through missions and earn badges! 🏆',
            'module completion': '✅ Complete all 5 modules to unlock mission! Track your progress in the dashboard! 📊',
            'learning path': '🛤️ Modules → Missions → Levels → Escape Rooms! Your cybersecurity learning journey! 🗺️',
            'module assessment': '📝 Each module has interactive questions to test your understanding! 🎯',
            'module topics': '📋 Module 1: Phishing, Module 2: Passwords, Module 3: Browsing, Module 4: Social Media, Module 5: Ethics! 📚'
        }
        
        # Check for quick response first (more precise matching)
        user_lower = user_message.lower()
        
        # Exact matches first
        if user_lower in quick_responses:
            return jsonify({"reply": quick_responses[user_lower]})
        
        # Then check for partial matches (more specific)
        for key, response in quick_responses.items():
            if key in user_lower and len(key) > 10:  # Only match longer keys
                return jsonify({"reply": response})
        
        # Try Gemini AI for other questions (with timeout protection)
        try:
            import google.genai as genai
            GEMINI_API_KEY = 'AIzaSyDm0SBD-4VCXokAm462YCrwka2VJq9JgiE'
            client = genai.Client(api_key=GEMINI_API_KEY)
            
            # Ultra-short prompt for speed
            system_prompt = "You are CyberBot for CyberMastery. Answer about missions, XP, badges, phishing, passwords. Be concise, use emojis."
            
            full_prompt = f"{system_prompt}\n\nQ: {user_message}\nA:"
            
            response = client.models.generate_content(
                model="gemini-flash-latest",
                contents=full_prompt
            )
            
            ai_reply = response.text.strip()
            print(f"✅ Fast AI Response: {ai_reply}")
            return jsonify({"reply": ai_reply})
            
        except Exception as e:
            print(f"❌ AI Error: {e}")
        
        # Fast fallback responses
        fallback_responses = [
            "🎮 I'm here to help with CyberMastery! Ask about missions, XP, or cybersecurity! 🛡️",
            "📚 Learn through missions: 5 modules → unlock content → earn badges! 🏆",
            "🔐 CyberMastery makes learning security fun with games and escape rooms! �",
            "⭐ Earn XP and badges as you progress through cybersecurity missions! 🏆"
        ]
        
        return jsonify({
            "reply": fallback_responses[hash(user_message) % len(fallback_responses)]
        })
        
    except Exception as e:
        print(f"❌ Chatbot Error: {e}")
        return jsonify({"reply": "🤖 Sorry, try asking about missions or cybersecurity! 🎮"})

app.config.from_object(Config)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
mail=Mail(app)

class RLProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    score = db.Column(db.Integer, default=0)

class UserMissionProgress(db.Model):
    __tablename__ = "user_mission_progress"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    mission_id = db.Column(db.Integer, db.ForeignKey("mission.id"), nullable=False)

    learning_completed = db.Column(db.Boolean, default=False)
    levels_completed = db.Column(db.Boolean, default=False)
    escape_completed = db.Column(db.Boolean, default=False)
    mission_completed = db.Column(db.Boolean, default=False)

    

class EscapeRoom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mission_id = db.Column(db.Integer)
    role = db.Column(db.String(20))  # student / employee
    puzzle = db.Column(db.Text)

    # store multiple answers as comma-separated
    correct_answers = db.Column(db.Text)

    explanation = db.Column(db.Text)


class EscapeProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    mission_id = db.Column(db.Integer)
    completed = db.Column(db.Boolean, default=False)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'mission_id'),
    )

class Analytics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    mission_id = db.Column(db.Integer)
    correct = db.Column(db.Boolean)
    time_taken = db.Column(db.Integer)
# ================= MODELS ================= #

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(20))
    password = db.Column(db.String(200))
    xp = db.Column(db.Integer, default=0)

class Mission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(20))
    name = db.Column(db.String(100))
    order = db.Column(db.Integer)


class Level(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mission_id = db.Column(db.Integer)
    level_number = db.Column(db.Integer)
    scenario = db.Column(db.Text)

    option_a = db.Column(db.String(255))
    option_b = db.Column(db.String(255))
    option_c = db.Column(db.String(255))
    option_d = db.Column(db.String(255))

    correct_answer = db.Column(db.String(1))
    explanation = db.Column(db.Text)


class LearningModule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mission_id = db.Column(db.Integer)
    module_number = db.Column(db.Integer)   # 1 to 5
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    video_url = db.Column(db.String(300))


class LearningModuleVideo(db.Model):
    __tablename__ = "learning_module_video"
    
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey("learning_module.id"), nullable=False)
    video_number = db.Column(db.Integer, nullable=False)  # 1 to 5
    video_url = db.Column(db.String(300), nullable=False)
    
    # Define the foreign key constraint name to match the database
    __table_args__ = (
        db.ForeignKeyConstraint(['module_id'], ['learning_module.id'], name='fk_module_video'),
    )


class LearningProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    mission_id = db.Column(db.Integer)
    module_id = db.Column(db.Integer)   # 👈 ADD THIS
    completed = db.Column(db.Boolean, default=False)


class Progress(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    mission_id = db.Column(db.Integer, db.ForeignKey("mission.id"))

    current_level = db.Column(db.Integer, default=1)
    completed = db.Column(db.Boolean, default=False)

    # 🔥 NEW — REQUIRED FOR XP LOGIC
    attempts_left = db.Column(db.Integer, default=3)


class Badge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    name = db.Column(db.String(50))

class PhishGame(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text)
    is_phishing = db.Column(db.Boolean)
    explanation = db.Column(db.Text)


class UserBadge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    badge_name = db.Column(db.String(50))

class MultiplayerChallenge(db.Model):
    __tablename__ = "multiplayer_challenge"
    
    id = db.Column(db.Integer, primary_key=True)
    challenge_code = db.Column(db.String(10), unique=True, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    status = db.Column(db.String(20), default="waiting")  # waiting, active, completed
    started_at = db.Column(db.DateTime)  # When challenge actually starts
    duration_minutes = db.Column(db.Integer, default=10)  # 10 minutes per challenge
    
class ChallengeParticipant(db.Model):
    __tablename__ = "challenge_participant"
    
    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey("multiplayer_challenge.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    score = db.Column(db.Integer, default=0)
    current_mission = db.Column(db.Integer, default=1)
    is_completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)
    
class ChallengeMission(db.Model):
    __tablename__ = "challenge_mission"
    
    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey("multiplayer_challenge.id"), nullable=False)
    mission_number = db.Column(db.Integer, nullable=False)  # 1 to 10
    mission_type = db.Column(db.String(50), nullable=False)  # phishing, password, social_engineering, etc.
    mission_data = db.Column(db.Text, nullable=False)  # JSON string with mission details
    correct_answer = db.Column(db.String(255), nullable=False)
    points = db.Column(db.Integer, default=1)

class Puzzle(db.Model):
    __tablename__ = "puzzle"
    
    id = db.Column(db.Integer, primary_key=True)
    puzzle_text = db.Column(db.Text, nullable=False)
    hint = db.Column(db.Text)
    answer = db.Column(db.String(255), nullable=False)
    xp_reward = db.Column(db.Integer, default=10)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'puzzle_text': self.puzzle_text,
            'hint': self.hint,
            'xp_reward': self.xp_reward,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class PuzzleProgress(db.Model):
    __tablename__ = "puzzle_progress"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    puzzle_id = db.Column(db.Integer, db.ForeignKey("puzzle.id"))
    solved = db.Column(db.Boolean, default=False)
    solved_at = db.Column(db.DateTime)
    xp_earned = db.Column(db.Integer, default=0)
    time_taken = db.Column(db.Integer)  # seconds
    hint_used = db.Column(db.Boolean, default=False)
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'puzzle_id'),
    )

def send_badge_email(email, badge):
    try:
        print(f" Attempting to send badge email to: {email}")
        print(f" Badge: {badge}")
        print(f" Mail server: {app.config.get('MAIL_SERVER')}")
        print(f" Mail port: {app.config.get('MAIL_PORT')}")
        print(f" Mail username: {app.config.get('MAIL_USERNAME')}")
        
        msg = Message(
            subject=" Congratulations! You Earned a Badge",
            recipients=[email],
            body=f"""
Congratulations!

You have successfully earned the badge:
 {badge}

Keep learning and leveling up in CyberMastery 
"""
        )
        
        print(" Sending email...")
        result = mail.send(msg)
        print(f" Email sent successfully. Result: {result}")

    except Exception as e:
        print(f" Email error: {e}")
        print(f" Error type: {type(e).__name__}")
        # Print more details about the error
        import traceback
        print(f" Full error: {traceback.format_exc()}")
        
        # Check for common Gmail issues
        if "BadCredentials" in str(e):
            print(" Gmail authentication failed - check password or enable 'Less secure app access'")
        elif "SMTPAuthenticationError" in str(type(e).__name__):
            print(" SMTP authentication failed - check credentials")
        elif "ConnectionRefusedError" in str(type(e).__name__):
            print(" Connection refused - check network/firewall")

def seed_phish_game():
    data = [
        ("Your bank account will be blocked. Click here!", True,
         "Banks never send urgent links."),
        ("Amazon: Your order has been shipped.", False,
         "This is a normal transactional message."),
        ("HR asks payroll update via link.", True,
         "Payroll updates must be done in official portals.")
    ]

    for d in data:
        db.session.add(PhishGame(
            message=d[0],
            is_phishing=d[1],
            explanation=d[2]
        ))
    db.session.commit()

def choose_difficulty(user_id):
    profile = RLProfile.query.filter_by(user_id=user_id).first()

    if not profile:
        profile = RLProfile(user_id=user_id)
        db.session.add(profile)
        db.session.commit()

    if profile.score < 0:
        return "easy"
    elif profile.score < 30:
        return "medium"
    return "hard"

def award_badge_once(user_id, badge_name):
    exists = UserBadge.query.filter_by(
        user_id=user_id,
        badge_name=badge_name
    ).first()

    if not exists:
        db.session.add(UserBadge(
            user_id=user_id,
            badge_name=badge_name
        ))
        db.session.commit()


def check_and_award_badges(user):
    completed = UserMissionProgress.query.filter_by(
        user_id=user.id,
        escape_completed=True
    ).count()

    print(f"Checking badges for user {user.id}: {completed} completed missions")

    badge_awarded = False
    badge_name = None

    # First, try to fix database if needed
    try:
        if completed >= 5:
            # Check if expert badge already awarded
            try:
                expert_badge = UserBadge.query.filter_by(
                    user_id=user.id,
                    badge_name="Cyber Expert"
                ).first()
                
                if not expert_badge:
                    award_badge_once(user.id, "Cyber Expert")
                    user.xp += 50
                    badge_awarded = True
                    badge_name = "Cyber Expert"
                    print(f"Awarded Cyber Expert badge to user {user.id}")
            except Exception as e:
                print(f"Database error checking Expert badge: {e}")
                # Try direct SQL approach
                try:
                    with db.engine.connect() as conn:
                        result = conn.execute(db.text(
                            "SELECT COUNT(*) FROM user_badge WHERE user_id = :user_id AND badge_name = 'Cyber Expert'"
                        ), {"user_id": user.id})
                        count = result.scalar()
                        
                        if count == 0:
                            conn.execute(db.text(
                                "INSERT INTO user_badge (user_id, badge_name) VALUES (:user_id, 'Cyber Expert')"
                            ), {"user_id": user.id})
                            conn.commit()
                            user.xp += 50
                            badge_awarded = True
                            badge_name = "Cyber Expert"
                            print(f"Awarded Cyber Expert badge via SQL to user {user.id}")
                except Exception as sql_error:
                    print(f"SQL approach also failed: {sql_error}")
        
        elif completed >= 2:
            # Check if beginner badge already awarded
            try:
                beginner_badge = UserBadge.query.filter_by(
                    user_id=user.id,
                    badge_name="Cyber Beginner"
                ).first()
                
                if not beginner_badge:
                    award_badge_once(user.id, "Cyber Beginner")
                    user.xp += 20
                    badge_awarded = True
                    badge_name = "Cyber Beginner"
                    print(f"Awarded Cyber Beginner badge to user {user.id}")
            except Exception as e:
                print(f"Database error checking Beginner badge: {e}")
                # Try direct SQL approach
                try:
                    with db.engine.connect() as conn:
                        result = conn.execute(db.text(
                            "SELECT COUNT(*) FROM user_badge WHERE user_id = :user_id AND badge_name = 'Cyber Beginner'"
                        ), {"user_id": user.id})
                        count = result.scalar()
                        
                        if count == 0:
                            conn.execute(db.text(
                                "INSERT INTO user_badge (user_id, badge_name) VALUES (:user_id, 'Cyber Beginner')"
                            ), {"user_id": user.id})
                            conn.commit()
                            user.xp += 20
                            badge_awarded = True
                            badge_name = "Cyber Beginner"
                            print(f"Awarded Cyber Beginner badge via SQL to user {user.id}")
                except Exception as sql_error:
                    print(f"SQL approach also failed: {sql_error}")

    except Exception as e:
        print(f"Error in badge checking: {e}")

    db.session.commit()
    
    # 📧 SEND EMAIL FOR BADGE
    if badge_awarded:
        print(f"Sending badge email to {user.email} for {badge_name}")
        try:
            send_badge_email(user.email, badge_name)
        except Exception as e:
            print(f"Failed to send badge email: {e}")
    else:
        print(f"No badge awarded for user {user.id} (completed: {completed})")

@app.route("/challenges")
@login_required
def list_challenges():
    """List all available challenges for users to join"""
    try:
        # Get all active challenges
        challenges = MultiplayerChallenge.query.filter_by(is_active=True).all()
        
        challenge_list = []
        for challenge in challenges:
            creator = User.query.get(challenge.created_by)
            
            # Check if current user has already joined
            participant = ChallengeParticipant.query.filter_by(
                challenge_id=challenge.id,
                user_id=current_user.id
            ).first()
            
            challenge_list.append({
                "code": challenge.challenge_code,
                "question": challenge.question,
                "created_by": creator.username,
                "created_at": challenge.created_at.isoformat(),
                "expires_at": challenge.expires_at.isoformat() if challenge.expires_at else None,
                "has_joined": participant is not None,
                "participant_count": ChallengeParticipant.query.filter_by(challenge_id=challenge.id).count()
            })
        
        return jsonify({
            "status": "success",
            "challenges": challenge_list
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to load challenges: {str(e)}"
        })

@app.route("/multiplayer")
@login_required
def multiplayer_home():
    """Multiplayer challenge home page"""
    return render_template("multiplayer.html")

@app.route("/create-challenge", methods=["POST"])
@login_required
def create_challenge():
    """Create a new multiplayer challenge room"""
    try:
        # Generate unique challenge code
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        # Check if code already exists
        while MultiplayerChallenge.query.filter_by(challenge_code=code).first():
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        # Create challenge
        challenge = MultiplayerChallenge(
            challenge_code=code,
            created_by=current_user.id,
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )
        db.session.add(challenge)
        db.session.commit()
        
        print(f"✅ Created challenge with code: {code}, ID: {challenge.id}")
        
        # Generate 10 random missions for this challenge
        missions = generate_random_missions(10)
        for i, mission in enumerate(missions, 1):
            challenge_mission = ChallengeMission(
                challenge_id=challenge.id,
                mission_number=i,
                mission_type=mission["type"],
                mission_data=json.dumps(mission["data"]),
                correct_answer=mission["data"]["correct_answer"],
                points=1
            )
            db.session.add(challenge_mission)
        
        # Add creator as participant
        participant = ChallengeParticipant(
            challenge_id=challenge.id,
            user_id=current_user.id
        )
        db.session.add(participant)
        db.session.commit()
        
        print(f"✅ Added {len(missions)} missions and 1 participant to challenge {code}")
        
        return jsonify({
            "status": "success",
            "challenge_code": code,
            "message": f"Challenge room created! Share code: {code}"
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to create challenge: {str(e)}"
        })

@app.route("/join-challenge/<string:code>", methods=["POST"])
@login_required
def join_challenge(code):
    """Join a multiplayer challenge room"""
    try:
        print(f"🔍 Looking for challenge code: {code}")
        
        # First check if any challenges exist
        all_challenges = MultiplayerChallenge.query.all()
        print(f"📊 Total challenges in database: {len(all_challenges)}")
        
        for challenge in all_challenges:
            print(f"📝 Challenge: {challenge.challenge_code}, Active: {challenge.is_active}")
        
        challenge = MultiplayerChallenge.query.filter_by(
            challenge_code=code,
            is_active=True
        ).first()
        
        print(f"🎯 Found challenge: {challenge}")
        
        if not challenge:
            return jsonify({
                "status": "error",
                "message": f"Challenge not found or expired. Code: {code}"
            })
        
        # Check if user already joined
        existing = ChallengeParticipant.query.filter_by(
            challenge_id=challenge.id,
            user_id=current_user.id
        ).first()
        
        if existing:
            return jsonify({
                "status": "error",
                "message": "Already joined this challenge"
            })
        
        # Check if challenge is full (max 2 players)
        participant_count = ChallengeParticipant.query.filter_by(challenge_id=challenge.id).count()
        if participant_count >= 2:
            return jsonify({
                "status": "error",
                "message": "Challenge is full (2 players max)"
            })
        
        # Add participant
        participant = ChallengeParticipant(
            challenge_id=challenge.id,
            user_id=current_user.id
        )
        db.session.add(participant)
        db.session.commit()
        
        # If this is the second player, start the challenge
        if participant_count == 1:
            challenge.status = "active"
            challenge.started_at = datetime.utcnow()
            db.session.commit()
            print(f"🚀 Challenge {code} started with 2 players!")
        
        return jsonify({
            "status": "success",
            "message": "Joined challenge successfully!",
            "challenge": {
                "code": code,
                "created_by": User.query.get(challenge.created_by).username,
                "status": challenge.status,
                "participant_count": participant_count + 1
            }
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to join challenge: {str(e)}"
        })

@app.route("/challenge-game/<string:code>")
@login_required
def challenge_game(code):
    """Dedicated challenge game page"""
    try:
        challenge = MultiplayerChallenge.query.filter_by(challenge_code=code).first()
        
        if not challenge:
            return render_template("error.html", message="Challenge not found")
        
        # Check if user is participant
        participant = ChallengeParticipant.query.filter_by(
            challenge_id=challenge.id,
            user_id=current_user.id
        ).first()
        
        if not participant:
            return render_template("error.html", message="You are not part of this challenge")
        
        return render_template("challenge_game.html", code=code)
        
    except Exception as e:
        return render_template("error.html", message=f"Error loading challenge: {str(e)}")

@app.route("/challenge-status/<string:code>")
@login_required
def challenge_status(code):
    """Get challenge status and participants"""
    try:
        challenge = MultiplayerChallenge.query.filter_by(challenge_code=code).first()
        
        if not challenge:
            return jsonify({
                "status": "error",
                "message": "Challenge not found"
            })
        
        # Get participants
        participants = db.session.query(ChallengeParticipant, User).join(
            User, ChallengeParticipant.user_id == User.id
        ).filter(ChallengeParticipant.challenge_id == challenge.id).all()
        
        participant_list = []
        for participant, user in participants:
            participant_list.append({
                "username": user.username,
                "score": participant.score,
                "current_mission": participant.current_mission,
                "is_completed": participant.is_completed,
                "completed_at": participant.completed_at.isoformat() if participant.completed_at else None
            })
        
        return jsonify({
            "status": "success",
            "challenge": {
                "code": code,
                "status": challenge.status,
                "created_by": User.query.get(challenge.created_by).username,
                "created_at": challenge.created_at.isoformat(),
                "expires_at": challenge.expires_at.isoformat() if challenge.expires_at else None,
                "is_active": challenge.is_active,
                "started_at": challenge.started_at.isoformat() if challenge.started_at else None,
                "duration_minutes": challenge.duration_minutes,
                "time_remaining": get_time_remaining(challenge) if challenge.started_at else None
            },
            "participants": participant_list
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to get status: {str(e)}"
        })

@app.route("/get-mission/<string:code>/<int:mission_number>")
@login_required
def get_mission(code, mission_number):
    """Get a specific mission for the challenge"""
    try:
        challenge = MultiplayerChallenge.query.filter_by(challenge_code=code).first()
        
        if not challenge:
            return jsonify({
                "status": "error",
                "message": "Challenge not found"
            })
        
        # Check if user is participant
        participant = ChallengeParticipant.query.filter_by(
            challenge_id=challenge.id,
            user_id=current_user.id
        ).first()
        
        if not participant:
            return jsonify({
                "status": "error",
                "message": "Not joined this challenge"
            })
        
        # Get the mission
        mission = ChallengeMission.query.filter_by(
            challenge_id=challenge.id,
            mission_number=mission_number
        ).first()
        
        if not mission:
            return jsonify({
                "status": "error",
                "message": "Mission not found"
            })
        
        # Parse mission data
        try:
            mission_data = json.loads(mission.mission_data)
            print(f"🔍 Mission {mission_number} data loaded: {mission_data}")
        except Exception as e:
            print(f"❌ Error parsing mission data: {e}")
            mission_data = {"error": "Failed to parse mission data"}
        
        return jsonify({
            "status": "success",
            "mission": {
                "number": mission_number,
                "type": mission.mission_type,
                "data": mission_data,
                "total_missions": 10
            }
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to get mission: {str(e)}"
        })

@app.route("/submit-mission/<string:code>/<int:mission_number>", methods=["POST"])
@login_required
def submit_mission(code, mission_number):
    """Submit answer for a mission"""
    try:
        answer = request.form.get("answer")
        
        # Handle None or empty answers
        if answer is None or answer == "":
            return jsonify({
                "status": "error",
                "message": "No answer provided"
            })
        
        challenge = MultiplayerChallenge.query.filter_by(challenge_code=code).first()
        
        if not challenge:
            return jsonify({
                "status": "error",
                "message": "Challenge not found"
            })
        
        # Check if user is participant
        participant = ChallengeParticipant.query.filter_by(
            challenge_id=challenge.id,
            user_id=current_user.id
        ).first()
        
        if not participant:
            return jsonify({
                "status": "error",
                "message": "Not joined this challenge"
            })
        
        # Get the mission
        mission = ChallengeMission.query.filter_by(
            challenge_id=challenge.id,
            mission_number=mission_number
        ).first()
        
        if not mission:
            return jsonify({
                "status": "error",
                "message": "Mission not found"
            })
        
        # Check answer (handle None values properly)
        correct_answer = mission.correct_answer
        if correct_answer is None:
            return jsonify({
                "status": "error",
                "message": "Mission has no correct answer configured"
            })
        
        # Convert both to strings and trim whitespace for comparison
        answer_str = str(answer).strip()
        correct_answer_str = str(correct_answer).strip()
        
        is_correct = answer_str.lower() == correct_answer_str.lower()
        
        if is_correct:
            participant.score += mission.points
        
        # Move to next mission
        participant.current_mission = mission_number + 1
        
        # Check if completed all missions
        if mission_number >= 10:
            participant.is_completed = True
            participant.completed_at = datetime.utcnow()
            
            # Check if both players completed
            all_participants = ChallengeParticipant.query.filter_by(challenge_id=challenge.id).all()
            if all(p.is_completed for p in all_participants):
                challenge.status = "completed"
                # Determine winner and award XP
                determine_winner_and_award_xp(challenge.id)
        
        db.session.commit()
        
        mission_data = json.loads(mission.mission_data)
        
        return jsonify({
            "status": "success",
            "correct": is_correct,
            "explanation": mission_data.get("explanation", ""),
            "score": participant.score,
            "current_mission": participant.current_mission,
            "is_completed": participant.is_completed,
            "next_mission": mission_number + 1 if mission_number < 10 else None
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to submit mission: {str(e)}"
        })

def determine_winner_and_award_xp(challenge_id):
    """Determine winner and award XP"""
    try:
        participants = ChallengeParticipant.query.filter_by(challenge_id=challenge_id).all()
        
        if not participants:
            return
        
        # Find winner (highest score)
        winner = max(participants, key=lambda p: p.score)
        
        # Award XP to winner (higher XP for competitive challenges)
        xp_reward = 150  # Increased XP for multiplayer challenges
        winner_user = User.query.get(winner.user_id)
        winner_user.xp += xp_reward
        
        # Send email notification
        send_badge_email(winner_user.email, f"Multiplayer Challenge Winner! (+{xp_reward} XP)")
        
        print(f"🏆 Player {winner_user.username} won challenge {challenge_id} with {winner.score} points! +{xp_reward} XP")
        
        db.session.commit()
        
    except Exception as e:
        print(f"Error determining winner: {e}")

@app.route("/debug/simulate-new-badge")
@login_required
def simulate_new_badge():
    """Simulate earning a NEW badge to test email notification"""
    try:
        print(f"🎖️ Simulating new badge award for user {current_user.id}")
        
        # First, remove the test badge if it exists to ensure it's "new"
        existing_test = UserBadge.query.filter_by(
            user_id=current_user.id,
            badge_name="Test Debug Badge"
        ).first()
        
        if existing_test:
            db.session.delete(existing_test)
            db.session.commit()
            print("🗑️ Removed existing test badge")
        
        # Now award it as a NEW badge (this should trigger email)
        award_badge_once(current_user.id, "Test Debug Badge")
        
        # Check if this was actually a new badge award
        badge_awarded = True
        badge_name = "Test Debug Badge"
        
        # Send email for this NEW badge
        print(f"📧 Sending NEW badge email to {current_user.email} for {badge_name}")
        send_badge_email(current_user.email, badge_name)
        
        return jsonify({
            "status": "success",
            "message": "Simulated new badge award and email sent!",
            "note": "This simulates earning a brand new badge"
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to simulate new badge: {str(e)}"
        })

@app.route("/debug/award-test-badge")
@login_required
def award_test_badge():
    """Manually award a test badge to trigger email"""
    try:
        print(f"🎖️ Awarding test badge to user {current_user.id}")
        
        # Check if user already has this test badge
        existing = UserBadge.query.filter_by(
            user_id=current_user.id,
            badge_name="Test Debug Badge"
        ).first()
        
        if existing:
            return jsonify({
                "status": "info",
                "message": "Test badge already exists"
            })
        
        # Award the test badge
        award_badge_once(current_user.id, "Test Debug Badge")
        
        # Send email for this test badge
        print(f"📧 Sending test badge email to {current_user.email}")
        send_badge_email(current_user.email, "Test Debug Badge")
        
        return jsonify({
            "status": "success",
            "message": "Test badge awarded and email sent!"
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to award test badge: {str(e)}"
        })

@app.route("/debug/test-badge")
@login_required
def test_badge():
    """Manually trigger badge checking for current user"""
    try:
        print(f"🏆 Manually checking badges for user {current_user.id}")
        check_and_award_badges(current_user)
        
        # Check current badges
        badges = UserBadge.query.filter_by(user_id=current_user.id).all()
        badge_list = [badge.badge_name for badge in badges]
        
        return jsonify({
            "status": "success",
            "message": "Badge check completed",
            "badges": badge_list,
            "user_xp": current_user.xp
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to check badges: {str(e)}"
        })

@app.route("/debug/fix-database")
@login_required
def fix_database():
    """Fix database schema issues"""
    try:
        # Direct SQL commands to fix the user_badge table
        with db.engine.connect() as conn:
            # Check current columns
            result = conn.execute(db.text("DESCRIBE user_badge"))
            columns = [row[0] for row in result]
            print(f"Current columns: {columns}")
            
            # Add created_at column if it doesn't exist
            if 'created_at' not in columns:
                print("Adding created_at column to user_badge table")
                conn.execute(db.text("ALTER TABLE user_badge ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"))
                conn.commit()
            
            # If table has 'badge' instead of 'badge_name', fix it
            if any('badge' in col for col in columns) and 'badge_name' not in columns:
                print("Fixing: Renaming 'badge' to 'badge_name'")
                conn.execute(db.text("ALTER TABLE user_badge CHANGE COLUMN badge badge_name VARCHAR(50)"))
                conn.commit()
                
            # Create table if it doesn't exist
            conn.execute(db.text("""
                CREATE TABLE IF NOT EXISTS user_badge (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    badge_name VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.commit()
            
        return jsonify({
            "status": "success",
            "message": "Database schema fixed successfully!"
        })
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to fix database: {str(e)}"
        })

@app.route("/debug/check-escape-rooms")
@login_required
def check_escape_rooms():
    """Check which escape rooms exist in database"""
    try:
        escape_rooms = EscapeRoom.query.all()
        rooms_data = []
        for room in escape_rooms:
            rooms_data.append({
                "mission_id": room.mission_id,
                "role": room.role,
                "puzzle": room.puzzle[:50] + "..." if len(room.puzzle) > 50 else room.puzzle
            })
        
        return jsonify({
            "status": "success",
            "total_rooms": len(rooms_data),
            "rooms": rooms_data
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to check escape rooms: {str(e)}"
        })

@app.route("/debug/unlock-escape-room/<int:mission_id>")
@login_required
def unlock_escape_room(mission_id):
    """Manually unlock escape room for testing"""
    try:
        mission_progress = UserMissionProgress.query.filter_by(
            user_id=current_user.id,
            mission_id=mission_id
        ).first()
        
        if mission_progress:
            mission_progress.levels_completed = True
            db.session.commit()
            return jsonify({
                "status": "success",
                "message": f"Escape room for mission {mission_id} unlocked!"
            })
        else:
            # Create new record if it doesn't exist
            db.session.add(UserMissionProgress(
                user_id=current_user.id,
                mission_id=mission_id,
                learning_completed=True,
                levels_completed=True,
                escape_completed=False,
                mission_completed=False
            ))
            db.session.commit()
            return jsonify({
                "status": "success",
                "message": f"Created and unlocked escape room for mission {mission_id}!"
            })
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to unlock: {str(e)}"
        })

@app.route("/debug/seed-escape-rooms")
@login_required
def seed_escape_rooms_route():
    """Seed escape rooms into database"""
    try:
        seed_escape_rooms()
        return jsonify({
            "status": "success",
            "message": "Escape rooms seeded successfully!"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to seed escape rooms: {str(e)}"
        })

@app.route("/debug/clear-cookies")
def clear_cookies():
    """Clear all cookies for fresh testing"""
    response = make_response("All cookies cleared! Refresh the page.")
    
    # Clear all cookies by setting them to expire immediately
    cookies_to_clear = [
        'level_completed_1', 'level_completed_2', 'level_completed_3', 'level_completed_4', 'level_completed_5',
        'level_completed_6', 'level_completed_7', 'level_completed_8', 'level_completed_9', 'level_completed_10',
        'escape_completed_1', 'escape_completed_2', 'escape_completed_3', 'escape_completed_4', 'escape_completed_5',
        'escape_completed_6', 'escape_completed_7', 'escape_completed_8', 'escape_completed_9', 'escape_completed_10',
        'escape_attempts_1', 'escape_attempts_2', 'escape_attempts_3', 'escape_attempts_4', 'escape_attempts_5',
        'escape_attempts_6', 'escape_attempts_7', 'escape_attempts_8', 'escape_attempts_9', 'escape_attempts_10'
    ]
    
    for cookie_name in cookies_to_clear:
        response.set_cookie(cookie_name, '', expires=0)
    
    return response

@app.route("/debug/reset-employee-data")
@login_required
def reset_employee_data():
    """Reset employee test data to fix escape room access"""
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
        
        return jsonify({
            "status": "success",
            "message": f"Reset {len(employee_progress)} employee records. Try escape rooms now!"
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to reset: {str(e)}"
        })

@app.route("/debug/init-test-data")
@login_required
def init_test_data():
    """Initialize test progress data for debugging"""
    try:
        # First, let's check what exists
        existing_progress = UserMissionProgress.query.filter_by(
            user_id=current_user.id
        ).all()
        
        print(f"Existing UserMissionProgress records: {len(existing_progress)}")
        for ep in existing_progress:
            print(f"  Mission {ep.mission_id}: levels_completed={ep.levels_completed}")
        
        # Delete existing test data for this user
        UserMissionProgress.query.filter_by(user_id=current_user.id).delete()
        Progress.query.filter_by(user_id=current_user.id).delete()
        
        # Create fresh UserMissionProgress for missions 1, 2, and 6 with levels_completed=True
        # Only for students to test escape room functionality
        if current_user.role == 'student':
            for mission_id in [1, 2, 6]:
                db.session.add(UserMissionProgress(
                    user_id=current_user.id,
                    mission_id=mission_id,
                    learning_completed=True,  # Set to true for testing
                    levels_completed=True,   # Set to true for testing
                    escape_completed=False,
                    mission_completed=False
                ))
                print(f"Created UserMissionProgress for student mission {mission_id} with levels_completed=True")
        
        # Create Progress records with current_level > 10
        for mission_id in [1, 2, 6]:
            db.session.add(Progress(
                user_id=current_user.id,
                mission_id=mission_id,
                current_level=11,  # Set beyond level 10
                completed=False,
                attempts_left=3
            ))
            print(f"Created Progress for mission {mission_id} with current_level=11")
        
        db.session.commit()
        print("Test data committed successfully!")
        
        return jsonify({
            "status": "success",
            "message": "Test data initialized. Try escape rooms now!"
        })
        
    except Exception as e:
        print(f"Error in init_test_data: {e}")
        db.session.rollback()
        return jsonify({
            "status": "error", 
            "message": f"Failed to initialize test data: {str(e)}"
        })

@app.route("/debug/progress")
@login_required
def debug_progress():
    """Debug route to check user progress"""
    user_missions = UserMissionProgress.query.filter_by(
        user_id=current_user.id
    ).all()
    
    progress_info = []
    for um in user_missions:
        progress_info.append({
            "mission_id": um.mission_id,
            "learning_completed": um.learning_completed,
            "levels_completed": um.levels_completed,
            "escape_completed": um.escape_completed,
            "mission_completed": um.mission_completed
        })
    
    # Check regular progress too
    regular_progress = Progress.query.filter_by(
        user_id=current_user.id
    ).all()
    
    regular_info = []
    for rp in regular_progress:
        regular_info.append({
            "mission_id": rp.mission_id,
            "current_level": rp.current_level,
            "completed": rp.completed,
            "attempts_left": rp.attempts_left
        })
    
    return jsonify({
        "user_mission_progress": progress_info,
        "regular_progress": regular_info
    })

@app.route("/badge/<name>/download")
def download_badge(name):
    return send_file(f"static/badges/{name}.pdf", as_attachment=True)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# ================= AUTH ================= #

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/help")
def help_page():
    return render_template("help.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    error = None

    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]

        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):
            error = "Invalid email format. Please enter a valid email address."
        elif len(password) < 8:
            error = "Password must be at least 8 characters long."
        elif not re.search(r"[A-Z]", password):
            error = "Password must contain at least one uppercase letter."
        elif not re.search(r"[0-9]", password):
            error = "Password must contain at least one number."
        elif not re.search(r"[@$!%*?&]", password):
            error = "Password must contain at least one special character (@$!%*?&)."
        elif User.query.filter_by(email=email).first():
            error = "Email already registered. Please use a different email or login."
        else:
            user = User(username=username, email=email, password=password, role=role)
            db.session.add(user)
            db.session.commit()
            return redirect("/login")

    return render_template("register.html", error=error)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(email=request.form["email"]).first()
        if user and user.password == request.form["password"]:
            login_user(user)
            return redirect("/dashboard")
        else:
            error = "Invalid email or password. Please try again."
            return render_template("login.html", error=error)
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")


# ================= DASHBOARD ================= #

@app.route("/dashboard")
@login_required
def dashboard():
    try:
        # Use raw SQL to avoid SQLAlchemy metadata issues
        with db.engine.connect() as conn:
            result = conn.execute(db.text(
                "SELECT id, user_id, badge_name FROM user_badge WHERE user_id = :user_id"
            ), {"user_id": current_user.id})
            
            # Convert to badge-like objects
            badges = []
            for row in result:
                badge = {
                    'id': row[0],
                    'user_id': row[1], 
                    'badge_name': row[2]
                }
                badges.append(badge)
            print(f"Found badges for user {current_user.id}: {badges}")
    except Exception as e:
        print(f"Error fetching badges: {e}")
        badges = []
    
    # Calculate rank based on user's role (student or employee leaderboard)
    higher = User.query.filter(User.role == current_user.role, User.xp > current_user.xp).count()
    rank = higher + 1
    return render_template("dashboard.html", badges=badges, rank=rank)


# ================= CYBER PUZZLE ================= #

@app.route("/cyber-puzzle")
@login_required
def cyber_puzzle():
    """Main cyber puzzle page"""
    try:
        # Get a random puzzle that user hasn't solved yet
        solved_puzzle_ids = db.session.query(PuzzleProgress.puzzle_id).filter_by(
            user_id=current_user.id, 
            solved=True
        ).all()
        solved_ids = [pid[0] for pid in solved_puzzle_ids]
        
        # Get random puzzle not yet solved
        available_puzzles = Puzzle.query.filter(
            ~Puzzle.id.in_(solved_ids) if solved_ids else True
        ).all()
        
        if not available_puzzles:
            # User has solved all puzzles, get a random one for practice
            puzzle = Puzzle.query.order_by(db.func.random()).first()
        else:
            puzzle = random.choice(available_puzzles)
        
        # Convert puzzle to dictionary for JSON serialization
        puzzle_dict = {
            'id': puzzle.id,
            'puzzle_text': puzzle.puzzle_text,
            'hint': puzzle.hint,
            'xp_reward': puzzle.xp_reward,
            'created_at': puzzle.created_at.isoformat() if puzzle.created_at else None
        }
        
        return render_template("cyber_puzzle.html", puzzle=puzzle_dict)
        
    except Exception as e:
        print(f"Error loading puzzle: {e}")
        # Fallback to any puzzle
        puzzle = Puzzle.query.first()
        puzzle_dict = {
            'id': puzzle.id,
            'puzzle_text': puzzle.puzzle_text,
            'hint': puzzle.hint,
            'xp_reward': puzzle.xp_reward,
            'created_at': puzzle.created_at.isoformat() if puzzle.created_at else None
        }
        return render_template("cyber_puzzle.html", puzzle=puzzle_dict)

@app.route("/get-puzzle", methods=["POST"])
@login_required
def get_puzzle():
    """Get a new random puzzle"""
    try:
        # Get solved puzzles
        solved_puzzle_ids = db.session.query(PuzzleProgress.puzzle_id).filter_by(
            user_id=current_user.id, 
            solved=True
        ).all()
        solved_ids = [pid[0] for pid in solved_puzzle_ids]
        
        # Get random unsolved puzzle
        available_puzzles = Puzzle.query.filter(
            ~Puzzle.id.in_(solved_ids) if solved_ids else True
        ).all()
        
        if not available_puzzles:
            puzzle = Puzzle.query.order_by(db.func.random()).first()
        else:
            puzzle = random.choice(available_puzzles)
        
        return jsonify({
            "status": "success",
            "puzzle": puzzle.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to get puzzle: {str(e)}"
        })

@app.route("/submit-puzzle-answer", methods=["POST"])
@login_required
def submit_puzzle_answer():
    """Submit puzzle answer and award XP"""
    try:
        data = request.get_json()
        puzzle_id = data.get('puzzle_id')
        answer = data.get('answer')
        time_taken = data.get('time_taken', 0)
        hint_used = data.get('hint_used', False)
        
        print(f"🔍 Debug: Received answer submission")
        print(f"   Puzzle ID: {puzzle_id}")
        print(f"   User Answer: '{answer}'")
        print(f"   Time Taken: {time_taken}")
        print(f"   Hint Used: {hint_used}")
        
        # Get puzzle
        puzzle = Puzzle.query.get(puzzle_id)
        if not puzzle:
            print(f"❌ Puzzle not found: {puzzle_id}")
            return jsonify({
                "status": "error",
                "message": "Puzzle not found"
            })
        
        print(f"🎯 Debug: Correct Answer: '{puzzle.answer}'")
        print(f"   User Answer (cleaned): '{answer.lower().strip()}'")
        print(f"   Match: {answer.lower().strip() == puzzle.answer.lower().strip()}")
        
        # Check if already solved
        existing = PuzzleProgress.query.filter_by(
            user_id=current_user.id,
            puzzle_id=puzzle_id
        ).first()
        
        # Calculate XP
        base_xp = puzzle.xp_reward
        
        # Bonus XP for speed (solved in under 15 seconds)
        speed_bonus = 5 if time_taken < 15 else 0
        
        # Penalty for using hint
        hint_penalty = 3 if hint_used else 0
        
        total_xp = base_xp + speed_bonus - hint_penalty
        
        # Check answer
        if answer.lower().strip() == puzzle.answer.lower().strip():
            print(f"✅ Correct answer detected!")
            # Correct answer
            if existing:
                # Update existing record
                existing.solved = True
                existing.solved_at = datetime.utcnow()
                existing.xp_earned = total_xp
                existing.time_taken = time_taken
                existing.hint_used = hint_used
            else:
                # Create new record
                progress = PuzzleProgress(
                    user_id=current_user.id,
                    puzzle_id=puzzle_id,
                    solved=True,
                    solved_at=datetime.utcnow(),
                    xp_earned=total_xp,
                    time_taken=time_taken,
                    hint_used=hint_used
                )
                db.session.add(progress)
            
            # Award XP to user
            current_user.xp += total_xp
            db.session.commit()
            
            return jsonify({
                "status": "success",
                "message": f"Puzzle Solved! +{total_xp} XP",
                "xp_earned": total_xp,
                "base_xp": base_xp,
                "speed_bonus": speed_bonus,
                "hint_penalty": hint_penalty,
                "correct": True
            })
        else:
            print(f"❌ Incorrect answer detected!")
            # Incorrect answer
            return jsonify({
                "status": "incorrect",
                "message": "Incorrect answer, try again",
                "correct": False
            })
            
    except Exception as e:
        print(f"❌ Error in submit_puzzle_answer: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Failed to submit answer: {str(e)}"
        })

@app.route("/puzzle-stats")
@login_required
def puzzle_stats():
    """Get user's puzzle statistics"""
    try:
        solved_count = PuzzleProgress.query.filter_by(
            user_id=current_user.id,
            solved=True
        ).count()
        
        total_xp_from_puzzles = db.session.query(
            db.func.sum(PuzzleProgress.xp_earned)
        ).filter_by(
            user_id=current_user.id,
            solved=True
        ).scalar() or 0
        
        total_puzzles = Puzzle.query.count()
        
        return jsonify({
            "status": "success",
            "solved_count": solved_count,
            "total_puzzles": total_puzzles,
            "total_xp": total_xp_from_puzzles,
            "completion_rate": round((solved_count / total_puzzles * 100), 1) if total_puzzles > 0 else 0
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to get stats: {str(e)}"
        })


# ================= LEARNING MODULE FLOW ================= #
@app.route("/learning-modules")
@login_required
def learning_modules():

    missions = Mission.query.filter_by(
        role=current_user.role
    ).order_by(Mission.order).all()

    completed_learning = LearningProgress.query.filter_by(
        user_id=current_user.id,
        completed=True
    ).all()

    completed_ids = [lp.mission_id for lp in completed_learning]

    data = []
    for m in missions:
        data.append({
            "id": m.id,
            "name": m.name,
            "completed": m.id in completed_ids
        })

    return render_template("learning_modules.html", missions=data)

@app.route("/mission/<int:mission_id>/learn", methods=["GET", "POST"])
@login_required
def learn(mission_id):

    rewatch = request.args.get("rewatch")  # NEW

    modules = LearningModule.query.filter_by(mission_id=mission_id).all()

    progress = LearningProgress.query.filter_by(
        user_id=current_user.id,
        mission_id=mission_id
    ).all()

    completed_ids = [p.module_id for p in progress]

    # If rewatch mode → show ALL modules
    if rewatch:
        return render_template(
            "learn.html",
            modules=modules,
            completed_ids=completed_ids
        )

    # Normal learning flow (one-by-one)
    next_module = None
    for m in modules:
        if m.id not in completed_ids:
            next_module = m
            break

    if request.method == "POST":
        if next_module:
            db.session.add(LearningProgress(
                user_id=current_user.id,
                mission_id=mission_id,
                module_id=next_module.id,
                completed=True
            ))
            db.session.commit()
            return redirect(f"/mission/{mission_id}/learn")
        else:
            # All modules completed, redirect to completion page
            mission = db.session.get(Mission, mission_id)
            return render_template("learning_done.html", mission=mission)

    # All completed → show completion page
    if not next_module:
        mission = db.session.get(Mission, mission_id)
        return render_template("learning_done.html", mission=mission)

    return render_template("learn.html", modules=[next_module], completed_ids=completed_ids)

# ================= MISSIONS ================= #

@app.route("/missions")
@login_required
def missions():

    missions = Mission.query.filter_by(
        role=current_user.role
    ).order_by(Mission.order).all()

    data = []

    for m in missions:
        # 🔥 ENSURE UserMissionProgress EXISTS FOR EACH MISSION
        mission_progress = UserMissionProgress.query.filter_by(
            user_id=current_user.id,
            mission_id=m.id
        ).first()
        
        if not mission_progress:
            mission_progress = UserMissionProgress(
                user_id=current_user.id,
                mission_id=m.id
            )
            db.session.add(mission_progress)
        
        completed_modules = LearningProgress.query.filter_by(
            user_id=current_user.id,
            mission_id=m.id,
            completed=True
        ).count()

        unlocked = completed_modules >= 5   # 5 learning modules

        data.append({
            "id": m.id,
            "name": m.name,
            "order": m.order,
            "unlocked": unlocked
        })
    
    db.session.commit()

    return render_template("missions.html", missions=data)




# ================= LEVEL LIST (LOCKED) ================= #

@app.route("/mission/<int:mission_id>/levels")
@login_required
def levels(mission_id):

    completed_modules = LearningProgress.query.filter_by(
        user_id=current_user.id,
        mission_id=mission_id,
        completed=True
    ).count()

    if completed_modules < 5:
        return redirect(f"/mission/{mission_id}/learn")

    # 🔥 ENSURE UserMissionProgress EXISTS
    mission_progress = UserMissionProgress.query.filter_by(
        user_id=current_user.id,
        mission_id=mission_id
    ).first()
    
    if not mission_progress:
        mission_progress = UserMissionProgress(
            user_id=current_user.id,
            mission_id=mission_id
        )
        db.session.add(mission_progress)
        db.session.commit()

    prog = Progress.query.filter_by(
        user_id=current_user.id,
        mission_id=mission_id
    ).first()

    if not prog:
        prog = Progress(user_id=current_user.id, mission_id=mission_id)
        db.session.add(prog)
        db.session.commit()

    levels = Level.query.filter_by(
        mission_id=mission_id
    ).order_by(Level.level_number).all()

    data = []
    for l in levels:
        data.append({
            "id": l.id,
            "num": l.level_number,
            "open": l.level_number <= prog.current_level
        })

    mission = db.session.get(Mission, mission_id)

    return render_template("levels.html", levels=data, mission=mission)



def generate_hint(scenario, user_answer, correct_answer):
    """
    Dynamic hint logic (non-rule-based explanation style)
    """
    if "urgent" in scenario.lower() or "immediately" in scenario.lower():
        return "Be cautious of urgency. Attackers often create panic to force quick actions."

    if "link" in scenario.lower() or "click" in scenario.lower():
        return "Think about whether clicking unknown links is safe."

    if "otp" in scenario.lower() or "password" in scenario.lower():
        return "Sensitive information like OTPs or passwords should never be shared."

    return "Analyze the sender, intent, and request carefully before responding."
# ================= PLAY LEVEL ================= #
@app.route("/level/<int:level_id>", methods=["GET", "POST"])
@login_required
def play_level(level_id):

    level = Level.query.get_or_404(level_id)

    prog = Progress.query.filter_by(
        user_id=current_user.id,
        mission_id=level.mission_id
    ).first()

    if not prog:
        prog = Progress(
            user_id=current_user.id,
            mission_id=level.mission_id,
            current_level=1,
            attempts_left=3,
            completed=False
        )
        db.session.add(prog)
        db.session.commit()

    feedback = None
    hint = None
    points_awarded = 0

    # 🔁 Replay detection (DB based – correct)
    is_replay = level.level_number < prog.current_level

    # 🎯 Last level = 10
    is_last_level = level.level_number == 10

    if request.method == "POST":
        selected = request.form.get("answer")

        # =========================
        # ✅ CORRECT ANSWER
        # =========================
        if selected == level.correct_answer:
            feedback = "correct"

            if not is_replay and prog.current_level == level.level_number:
                # XP based on remaining attempts
                if prog.attempts_left == 3:
                    points_awarded = 10
                elif prog.attempts_left == 2:
                    points_awarded = 5
                else:
                    points_awarded = 2

                current_user.xp += points_awarded

                # Move to next level
                prog.current_level += 1
                prog.attempts_left = 3

                # If last level → unlock escape room
                if is_last_level:
                    prog.completed = True

                    mission_progress = UserMissionProgress.query.filter_by(
                        user_id=current_user.id,
                        mission_id=level.mission_id
                    ).first()

                    if not mission_progress:
                        mission_progress = UserMissionProgress(
                            user_id=current_user.id,
                            mission_id=level.mission_id
                        )
                        db.session.add(mission_progress)

                    mission_progress.levels_completed = True

            db.session.commit()

        # =========================
        # ❌ WRONG ANSWER
        # =========================
        else:
            feedback = "wrong"

            if not is_replay and prog.attempts_left > 0:
                prog.attempts_left -= 1
                current_user.xp = max(0, current_user.xp - 3)
                points_awarded = -3

            hint = generate_hint(
                level.scenario,
                selected,
                level.correct_answer
            )

            db.session.commit()

    return render_template(
        "level.html",
        level=level,
        feedback=feedback,
        hint=hint,
        attempts_left=prog.attempts_left,
        is_replay=is_replay,
        points_awarded=points_awarded,
        is_last_level=is_last_level
    )
@app.route("/escape/<int:mission_id>", methods=["GET", "POST"])
@login_required
def escape_room(mission_id):

    # 1️⃣ CHECK MISSION PROGRESS (10 levels required)
    mission_progress = UserMissionProgress.query.filter_by(
        user_id=current_user.id,
        mission_id=mission_id
    ).first()

    if not mission_progress or not mission_progress.levels_completed:
        return render_template(
                "escape_locked.html",
                            mission_id=mission_id
                                     ), 403

    # 2️⃣ LOAD ESCAPE PUZZLE (ROLE-BASED)
    puzzle = EscapeRoom.query.filter_by(
        mission_id=mission_id,
        role=current_user.role
    ).first()

    if not puzzle:
        return "Escape Room not configured", 404

    # 3️⃣ COOKIE-BASED ATTEMPTS (NO DB COLUMN)
    escape_attempts = int(request.cookies.get(f"escape_attempts_{mission_id}", 0))

    # 4️⃣ REPLAY DETECTION
    is_replay = mission_progress.escape_completed

    feedback = None
    hint = None
    xp_earned = 0

    # -------------------------
    # POST REQUEST
    # -------------------------
    if request.method == "POST":
        user_answer = request.form.get("answer", "").lower().strip()
        valid_answers = [a.strip() for a in puzzle.correct_answers.lower().split(",")]

        # =====================
        # ✅ CORRECT ANSWER
        # =====================
        if user_answer in valid_answers:
            feedback = "correct"

            if not is_replay:
                escape_attempts += 1

                # 🎯 XP RULES (AS YOU ASKED)
                if escape_attempts == 1:
                    xp_earned = 50
                elif escape_attempts == 2:
                    xp_earned = 20
                else:
                    xp_earned = 10

                current_user.xp += xp_earned

                # MARK COMPLETION
                mission_progress.escape_completed = True
                mission_progress.mission_completed = True

                # UPDATE PROGRESS TABLE
                prog = Progress.query.filter_by(
                    user_id=current_user.id,
                    mission_id=mission_id
                ).first()
                if prog:
                    prog.completed = True

                # 🏅 BADGE CHECK
                check_and_award_badges(current_user)

            db.session.commit()

            response = make_response(render_template(
                "escape_room.html",
                puzzle=puzzle,
                success=f"🎉 Escape Room Completed! +{xp_earned} XP",
                xp_earned=xp_earned,
                show_back_button=True
            ))

            # SAVE ATTEMPTS
            response.set_cookie(
                f"escape_attempts_{mission_id}",
                str(escape_attempts),
                max_age=86400 * 30
            )
            return response

        # =====================
        # ❌ WRONG ANSWER
        # =====================
        else:
            if not is_replay:
                current_user.xp = max(0, current_user.xp - 3)
                db.session.commit()

            hint = get_escape_hint(puzzle.puzzle)

            return render_template(
                "escape_room.html",
                puzzle=puzzle,
                error="❌ Wrong answer. −3 XP",
                hint=hint
            )

    # -------------------------
    # GET REQUEST (HINT)
    # -------------------------
    if request.args.get("hint") == "true" and not is_replay:
        current_user.xp = max(0, current_user.xp - 1)
        db.session.commit()
        hint = get_escape_hint(puzzle.puzzle)

    return render_template("escape_room.html", puzzle=puzzle, hint=hint)

def seed_escape_rooms():
    rooms = [

        # =========================
        # MISSION 1 – PHISHING AWARENESS
        # =========================

        EscapeRoom(
            mission_id=1,
            role="student",
            puzzle="You receive a mail: 'Your exam result is delayed. Login here: bit.ly/exam-login'. What is wrong?",
            correct_answers="phishing,phishing link,fake link,malicious link",
            explanation="Shortened links hide malicious domains and are commonly used in phishing."
        ),

        EscapeRoom(
            mission_id=1,
            role="employee",
            puzzle="HR asks to verify salary via link: hr-payroll-secure.com. What is the issue?",
            correct_answers="fake domain,phishing,look alike domain",
            explanation="Attackers use look-alike domains to trick employees."
        ),

        # =========================
        # MISSION 2 – PASSWORD SAFETY
        # =========================

        EscapeRoom(
            mission_id=2,
            role="student",
            puzzle="Password 'College@123' is used for Gmail and LMS. Identify the risk.",
            correct_answers="password reuse,credential reuse",
            explanation="Reusing passwords allows attackers to access multiple accounts."
        ),

        EscapeRoom(
            mission_id=2,
            role="employee",
            puzzle="Same password is used for office VPN and LinkedIn. What is the danger?",
            correct_answers="credential stuffing,password reuse",
            explanation="Leaked credentials can compromise corporate systems."
        ),

        # =========================
        # MISSION 3 – SAFE INTERNET BROWSING
        # =========================

        EscapeRoom(
            mission_id=3,
            role="student",
            puzzle="You are asked to enter login details on a website without HTTPS. What should you do?",
            correct_answers="do not enter credentials,unsafe website,no https",
            explanation="HTTP websites can expose sensitive data to attackers."
        ),

        EscapeRoom(
            mission_id=3,
            role="employee",
            puzzle="A pop-up asks to install a browser extension to view content. What is the risk?",
            correct_answers="malware,unsafe extension,malicious extension",
            explanation="Malicious extensions can steal data or monitor activity."
        ),

        # =========================
        # MISSION 4 – SOCIAL MEDIA SECURITY
        # =========================

        EscapeRoom(
            mission_id=4,
            role="student",
            puzzle="You receive a friend request from a stranger asking personal details. What is the risk?",
            correct_answers="social engineering,identity theft",
            explanation="Attackers collect personal data through fake profiles."
        ),

        EscapeRoom(
            mission_id=4,
            role="employee",
            puzzle="You share office photos with ID cards visible on LinkedIn. What is the issue?",
            correct_answers="data leakage,information exposure",
            explanation="Sensitive information can be exploited for attacks."
        ),

        # =========================
        # MISSION 5 – CYBER ETHICS & DIGITAL SAFETY
        # =========================

        EscapeRoom(
            mission_id=5,
            role="student",
            puzzle="You download cracked software for assignments. What is the risk?",
            correct_answers="malware,illegal software,security risk",
            explanation="Pirated software often contains malware."
        ),

        EscapeRoom(
            mission_id=5,
            role="employee",
            puzzle="You copy company data to personal email for convenience. What policy is violated?",
            correct_answers="data policy violation,ethical violation,data leakage",
            explanation="Unauthorized data transfer violates cybersecurity ethics."
        ),

        # =========================
        # MISSION 6 – NETWORK SECURITY (Employee)
        # =========================

        EscapeRoom(
            mission_id=6,
            role="employee",
            puzzle="Email asks you to disable security software for 'urgent update'. What is the risk?",
            correct_answers="malware,security risk,vulnerability,infection",
            explanation="Disabling security software makes your system vulnerable to malware attacks."
        ),

        # =========================
        # MISSION 7 – INCIDENT RESPONSE (Employee)
        # =========================

        EscapeRoom(
            mission_id=7,
            role="employee",
            puzzle="Colleague shares 'password123' for network access. What is the issue?",
            correct_answers="weak password,shared credential,security risk",
            explanation="Default passwords are easily compromised."
        ),

        # =========================
        # MISSION 8 – COMPLIANCE & GOVERNANCE (Employee)
        # =========================

        EscapeRoom(
            mission_id=8,
            role="employee",
            puzzle="Ransomware message appears on screen. What is the priority action?",
            correct_answers="disconnect network,contact IT,do not pay",
            explanation="Paying ransomware encourages more attacks."
        ),

        # =========================
        # MISSION 9 – ADVANCED THREAT PROTECTION (Employee)
        # =========================

        EscapeRoom(
            mission_id=9,
            role="employee",
            puzzle="Vendor requests admin access for 'system maintenance'. What should you verify?",
            correct_answers="verify identity,check authorization,contact supervisor",
            explanation="Always verify vendor identity and permissions."
        ),

        # =========================
        # MISSION 10 – DATA PRIVACY & COMPLIANCE (Employee)
        # =========================

        EscapeRoom(
            mission_id=10,
            role="employee",
            puzzle="Cloud storage request lacks proper authorization. What is missing?",
            correct_answers="approval,documentation,compliance",
            explanation="Proper authorization ensures data security."
        ),

    ]

    db.session.add_all(rooms)
    db.session.commit()

# ================= LEADERBOARDS ================= #

@app.route("/student/leaderboard")
@login_required
def student_leaderboard():
    users = User.query.filter_by(role="student") \
        .order_by(User.xp.desc()).all()

    try:
        # Use raw SQL to avoid SQLAlchemy metadata issues
        with db.engine.connect() as conn:
            result = conn.execute(db.text(
                "SELECT id, user_id, badge_name FROM user_badge WHERE user_id = :user_id"
            ), {"user_id": current_user.id})
            
            # Convert to badge-like objects
            badges = []
            for row in result:
                badge = {
                    'id': row[0],
                    'user_id': row[1], 
                    'badge_name': row[2]
                }
                badges.append(badge)
    except Exception as e:
        print(f"Error fetching badges: {e}")
        badges = []

    completed_missions = UserMissionProgress.query.filter_by(
        user_id=current_user.id,
        mission_completed=True
    ).count()

    total_missions = Mission.query.filter_by(
        role="student"
    ).count()

    return render_template(
        "student_leaderboard.html",
        users=users,
        badges=badges,
        completed_missions=completed_missions,
        total_missions=total_missions
    )

@app.route("/employee/leaderboard")
@login_required
def employee_leaderboard():
    users = User.query.filter_by(role="employee") \
        .order_by(User.xp.desc()).all()

    try:
        # Use raw SQL to avoid SQLAlchemy metadata issues
        with db.engine.connect() as conn:
            result = conn.execute(db.text(
                "SELECT id, user_id, badge_name FROM user_badge WHERE user_id = :user_id"
            ), {"user_id": current_user.id})
            
            # Convert to badge-like objects
            badges = []
            for row in result:
                badge = {
                    'id': row[0],
                    'user_id': row[1], 
                    'badge_name': row[2]
                }
                badges.append(badge)
    except Exception as e:
        print(f"Error fetching badges: {e}")
        badges = []

    completed_missions = UserMissionProgress.query.filter_by(
        user_id=current_user.id,
        mission_completed=True
    ).count()

    total_missions = Mission.query.filter_by(
        role="employee"
    ).count()

    return render_template(
        "employee_leaderboard.html",
        users=users,
        badges=badges,
        completed_missions=completed_missions,
        total_missions=total_missions
    )
# ================= GAME DATA ================= #

'''student_missions = {

    "Phishing Awareness": [
        ("Your bank email says your account will be blocked in 30 minutes.",
         "Click the link", "Ignore the email", "Report as phishing", "Reply with details",
         "C", "Banks never create urgency via email links."),

        ("You receive an email from unknown sender with an attachment.",
         "Open attachment", "Delete email", "Report phishing", "Reply asking details",
         "C", "Attachments can contain malware."),

        ("Email claims lottery win and asks personal details.",
         "Share details", "Ignore", "Report phishing", "Forward to friends",
         "C", "Lottery scams steal personal data."),

        ("Sender address looks like support@paypa1.com",
         "Trust email", "Click link", "Report phishing", "Reply",
         "C", "Look-alike domains are phishing tricks."),

        ("SMS says account suspended, click link.",
         "Click link", "Ignore", "Report smishing", "Reply STOP",
         "C", "Smishing is phishing via SMS."),

        ("Email asks to reset password immediately.",
         "Reset via link", "Ignore", "Verify official site", "Reply",
         "C", "Always verify via official website."),

        ("Email requests OTP for verification.",
         "Share OTP", "Ignore", "Report phishing", "Reply",
         "C", "OTP should never be shared."),

        ("Social media message with suspicious link.",
         "Open link", "Ignore", "Report user", "Reply",
         "C", "Social platforms are common phishing targets."),

        ("Fake invoice email from unknown vendor.",
         "Pay invoice", "Ignore", "Report phishing", "Reply",
         "C", "Unknown invoices are scams."),

        ("Email claims account hacked and asks details.",
         "Share details", "Panic", "Report phishing", "Reply",
         "C", "Attackers exploit fear.")
    ],

    "Password Safety": [
        ("Which password is strongest?",
         "123456", "password", "Gayatri123", "G@y@tr1!2025",
         "D", "Strong passwords use length, symbols, and randomness."),

        ("Is reusing passwords safe?",
         "Yes", "No", "Sometimes", "Only for email",
         "B", "Password reuse increases breach risk."),

        ("Best way to store passwords?",
         "Notebook", "Browser notes", "Password manager", "Memory",
         "C", "Password managers encrypt credentials."),

        ("Sharing password with friend is okay?",
         "Yes", "No", "If trusted", "Once only",
         "B", "Passwords should never be shared."),

        ("What improves security most?",
         "Short password", "Password reuse", "2FA", "Username change",
         "C", "2FA adds an extra protection layer."),

        ("Which is unsafe?",
         "Unique password", "Long password", "Using name", "Password manager",
         "C", "Personal info is easy to guess."),

        ("Best practice after breach?",
         "Ignore", "Change password", "Reuse old", "Tell friend",
         "B", "Compromised passwords must be changed."),

        ("Which password is weak?",
         "Qw!9@Z", "A8$kL!", "welcome123", "M#9Lp!",
         "C", "Dictionary words are weak."),

        ("Where should passwords not be stored?",
         "Password manager", "Encrypted vault", "Sticky note", "Secure app",
         "C", "Physical notes can be stolen."),

        ("Passphrase example?",
         "dog", "password", "ILoveCyber@2025!", "123456",
         "C", "Passphrases are long & memorable.")
    ],

    "Safe Internet Browsing": [
        ("Secure website indicator?",
         "http", "https", "popup", "ads",
         "B", "HTTPS encrypts communication."),

        ("Public Wi-Fi risk?",
         "Fast speed", "Free access", "Data interception", "None",
         "C", "Attackers can spy on traffic."),

        ("What to do before download?",
         "Download immediately", "Check source", "Ignore warnings", "Disable antivirus",
         "B", "Trusted sources reduce malware risk."),

        ("Fake website clue?",
         "Good design", "Misspelled URL", "Fast load", "Images",
         
         "B", "Misspellings indicate phishing."),

        ("Browser warning means?",
         "Ignore", "Safe site", "Potential danger", "Update browser",
         "C", "Warnings protect users."),

        ("Pop-up says virus detected",
         "Click fix", "Restart", "Close pop-up", "Call number",
         "C", "Fake alerts trick users."),

        ("File extension .exe from email?",
         "Open", "Delete", "Scan antivirus", "Forward",
         "B", "Executables can install malware."),

        ("HTTPS lock icon means?",
         "Website trusted", "Encrypted connection", "Virus free", "Verified owner",
         "B", "Encryption protects data."),

        ("Best browser habit?",
         "Disable updates", "Ignore security", "Regular updates", "Reuse passwords",
         "C", "Updates fix vulnerabilities."),

        ("Unknown website asking login?",
         "Enter details", "Ignore", "Verify domain", "Save password",
         "C", "Always verify authenticity.")
    ],

    "Social Media Security": [
        ("Stranger friend request?",
         "Accept", "Ignore", "Check profile", "Share number",
         "C", "Fake profiles are common."),

        ("Oversharing risk?",
         "None", "Privacy loss", "More likes", "Followers",
         "B", "Oversharing exposes personal info."),

        ("Location sharing risk?",
         "Fun", "Convenience", "Tracking", "Safe",
         "C", "Location reveals movements."),

        ("Unknown link in DM?",
         "Click", "Ignore", "Report", "Reply",
         "C", "DMs are phishing channels."),

        ("Best privacy setting?",
         "Public", "Friends only", "Everyone", "Disabled",
         "B", "Limits audience."),

        ("Account hacked action?",
         "Ignore", "Change password", "Post apology", "Delete app",
         "B", "Secure account immediately."),

        ("Two-factor on social media?",
         "Not needed", "Optional", "Recommended", "Risky",
         "C", "Adds extra security."),

        ("Fake giveaway post?",
         "Share", "Click", "Report", "Tag friends",
         "C", "Scams spread via giveaways."),

        ("Profile picture misuse?",
         "Harmless", "Privacy risk", "Fun", "Ignore",
         "B", "Images can be misused."),

        ("Cyberbullying response?",
         "Ignore", "Respond angrily", "Report & block", "Share",
         "C", "Reporting stops abuse.")
    ],

    "Cyber Ethics & Digital Safety": [
        ("Copy project without credit?",
         "Allowed", "Not allowed", "Depends", "Encouraged",
         "B", "Plagiarism is unethical."),

        ("Downloading pirated software?",
         "Legal", "Illegal", "Safe", "Recommended",
         "B", "Violates copyright laws."),

        ("Ethical hacking means?",
         "Illegal hacking", "Authorized testing", "Spying", "Stealing data",
         "B", "Ethical hacking requires permission."),

        ("Sharing others data?",
         "Okay", "Illegal", "Safe", "Normal",
         "B", "Violates privacy."),

        ("Digital footprint means?",
         "Online traces", "Hardware", "Files", "Passwords",
         "A", "Everything left online."),

        ("Cybercrime example?",
         "Online shopping", "Phishing", "Browsing", "Email",
         "B", "Phishing is illegal."),

        ("Respecting privacy?",
         "Optional", "Mandatory", "Ignore", "Not needed",
         "B", "Privacy is a right."),

        ("Reporting cybercrime?",
         "Ignore", "Report authorities", "Share online", "Delete account",
         "B", "Reporting helps stop crime."),

        ("Using cracked software?",
         "Safe", "Risky", "Legal", "Free",
         "B", "Cracked software may contain malware."),

        ("Cyber ethics goal?",
         "Harm", "Profit", "Responsible use", "Control",
         "C", "Ethics guide safe behavior.")
    ]
}

employee_missions = {

    "Corporate Phishing": [
        ("HR email asks to download policy urgently.",
         "Download file", "Verify sender", "Ignore", "Forward",
         "B", "Internal emails should be verified."),

        ("CEO asks gift cards via email.",
         "Buy cards", "Reply", "Verify request", "Ignore",
         "C", "CEO fraud is common."),

        ("Email requests payroll update.",
         "Update details", "Verify HR portal", "Reply", "Ignore",
         "B", "Payroll changes require verification."),

        ("Invoice from unknown vendor.",
         "Pay", "Ignore", "Verify vendor", "Forward",
         "C", "Invoice fraud targets companies."),

        ("Link asks corporate login.",
         "Enter details", "Verify URL", "Ignore", "Reply",
         "B", "Credential harvesting is common."),

        ("Attachment labelled confidential.",
         "Open", "Scan", "Verify sender", "Forward",
         "C", "Confidential labels are bait."),

        ("Email from IT asking password.",
         "Share", "Refuse & report", "Ignore", "Reply",
         "B", "IT never asks passwords."),

        ("Unexpected meeting invite link.",
         "Click", "Verify organizer", "Ignore", "Reply",
         "B", "Fake meetings spread malware."),

        ("Vendor email asks bank change.",
         "Approve", "Verify call", "Ignore", "Reply",
         "B", "Vendor fraud is common."),

        ("Urgent security alert email.",
         "Click link", "Verify SOC", "Ignore", "Reply",
         "B", "Security alerts must be verified.")
    ],

    "Social Engineering": [
        ("Caller claims IT support.",
         "Share password", "Refuse & report", "Ignore", "Help",
         "B", "Social engineers impersonate IT."),

        ("Tailgating request.",
         "Allow", "Deny", "Report", "Ignore",
         "B", "Physical security matters."),

        ("Unknown USB found.",
         "Plug in", "Ignore", "Report to IT", "Take home",
         "C", "USBs can carry malware."),

        ("Colleague asks login temporarily.",
         "Share", "Refuse", "Ignore", "Help",
         "B", "Credentials are personal."),

        ("Survey asks internal info.",
         "Fill", "Verify source", "Ignore", "Reply",
         "B", "Surveys can collect sensitive data."),

        ("Fake LinkedIn recruiter.",
         "Share resume", "Verify profile", "Ignore", "Reply",
         "B", "Recruitment scams exist."),

        ("Badge forgotten request.",
         "Allow entry", "Deny & report", "Ignore", "Help",
         "B", "Access control is critical."),

        ("Urgent call from manager?",
         "Comply", "Verify separately", "Ignore", "Help",
         "B", "Always verify urgent requests."),

        ("Email asks org chart.",
         "Send", "Verify", "Ignore", "Reply",
         "B", "Org charts aid attackers."),

        ("Caller asks employee data.",
         "Share", "Refuse", "Ignore", "Reply",
         "B", "Data disclosure is risky.")
    ],

    "Ransomware Awareness": [
        ("Ransom note appears.",
         "Pay ransom", "Disconnect network", "Restart", "Ignore",
         "B", "Disconnect stops spread."),

        ("Suspicious file encrypted data.",
         "Open", "Delete", "Report IT", "Ignore",
         "C", "IT must respond quickly."),

        ("Backup importance?",
         "Optional", "Critical", "Not needed", "Rare",
         "B", "Backups enable recovery."),

        ("Email attachment .exe",
         "Open", "Delete", "Scan", "Forward",
         "B", "Executables are dangerous."),

        ("Ransom email threat.",
         "Pay", "Report", "Ignore", "Reply",
         "B", "Do not negotiate."),

        ("Outdated system risk?",
         "None", "High", "Low", "Optional",
         "B", "Unpatched systems are targets."),

        ("Disable antivirus?",
         "Yes", "No", "Sometimes", "If slow",
         "B", "AV protects systems."),

        ("Suspicious macros?",
         "Enable", "Disable", "Ignore", "Share",
         "B", "Macros spread malware."),

        ("Unexpected software update?",
         "Install", "Verify IT", "Ignore", "Reply",
         "B", "Fake updates spread malware."),

        ("Ransomware prevention?",
         "Backups & patches", "Ignore", "Pay ransom", "Disable AV",
         "A", "Prevention is best defense.")
    ],

    "Network Security": [
        ("Best network protection?",
         "Firewall", "Open WiFi", "Shared login", "Disable updates",
         "A", "Firewalls control traffic."),

        ("Public WiFi usage?",
         "Safe", "Unsafe", "Always OK", "Preferred",
         "B", "Public WiFi is risky."),

        ("VPN purpose?",
         "Speed", "Encryption", "Ads", "Gaming",
         "B", "VPN encrypts traffic."),

        ("Shared admin accounts?",
         "Allowed", "Not allowed", "Recommended", "Easy",
         "B", "Accountability matters."),

        ("Strong network password?",
         "Short", "Default", "Complex", "Name",
         "C", "Complex passwords protect networks."),

        ("Unused ports?",
         "Open", "Close", "Ignore", "Share",
         "B", "Unused ports are attack surfaces."),

        ("IDS purpose?",
         "Detect intrusion", "Block WiFi", "Speed", "Backup",
         "A", "IDS detects threats."),

        ("Regular updates?",
         "Optional", "Mandatory", "Ignore", "Rare",
         "B", "Updates fix vulnerabilities."),

        ("Network monitoring?",
         "Unnecessary", "Important", "Ignore", "Optional",
         "B", "Monitoring detects attacks."),

        ("Least privilege means?",
         "Full access", "Minimum access", "Shared access", "No control",
         "B", "Limits damage.")
    ],

    "Data Privacy & Compliance": [
        ("Customer data access?",
         "Anyone", "Authorized only", "Public", "Social media",
         "B", "Privacy laws apply."),

        ("GDPR purpose?",
         "Marketing", "Data protection", "Sales", "Tracking",
         "B", "GDPR protects personal data."),

        ("Emailing sensitive data?",
         "Plain text", "Encrypted", "Ignore", "Forward",
         "B", "Encryption protects data."),

        ("USB with data lost?",
         "Ignore", "Report incident", "Buy new", "Delete",
         "B", "Incidents must be reported."),

        ("Data retention?",
         "Forever", "As required", "Never", "Random",
         "B", "Minimize stored data."),

        ("Access logs?",
         "Unneeded", "Important", "Optional", "Ignore",
         "B", "Logs ensure accountability."),

        ("Sharing data externally?",
         "Allowed", "Restricted", "Free", "Encouraged",
         "B", "External sharing needs approval."),

        ("PII means?",
         "Public info", "Personal data", "Passwords", "Files",
         "B", "PII identifies individuals."),

        ("Privacy breach response?",
         "Hide", "Report", "Ignore", "Delete data",
         "B", "Timely reporting required."),

        ("Compliance goal?",
         "Profit", "Trust & legality", "Control", "Surveillance",
         "B", "Compliance builds trust.")
    ]
}
'''
def insert_missions(role, data):
    order = 1
    for name, levels in data.items():
        m = Mission(role=role, name=name, order=order)
        db.session.add(m)
        db.session.flush()

        for i, l in enumerate(levels, 1):
            db.session.add(Level(
                mission_id=m.id,
                level_number=i,
                scenario=l[0],
                option_a=l[1],
                option_b=l[2],
                option_c=l[3],
                option_d=l[4],
                correct_answer=l[5],
                explanation=l[6]
            ))
        order += 1
def insert_learning_modules():
    missions = Mission.query.all()
    for m in missions:
        for i in range(1, 6):
            db.session.add(LearningModule(
                mission_id=m.id,
                module_number=i,   # 👈 ADD THIS
                title=f"Module {i} - {m.name}",
                description=f"Learning content for {m.name}",
                video_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            ))
    db.session.commit()




# ================= INIT DB ================= #

with app.app_context():
    # Drop tables in correct order to handle foreign key constraints
    try:
        # First, disable foreign key checks
        with db.engine.connect() as conn:
            conn.execute(db.text("SET FOREIGN_KEY_CHECKS = 0"))
            conn.commit()
        
        # Drop all tables
        #db.drop_all()
        
        # Re-enable foreign key checks
        with db.engine.connect() as conn:
            conn.execute(db.text("SET FOREIGN_KEY_CHECKS = 1"))
            conn.commit()
    except Exception as e:
        print(f"Error during drop_all: {e}")
        # Try to continue with create_all anyway
        pass
    
    db.create_all()

    # Remove all test debug badges from database
    try:
        test_badges = UserBadge.query.filter_by(badge_name="Test Debug Badge").all()
        if test_badges:
            for badge in test_badges:
                db.session.delete(badge)
            db.session.commit()
            print(f"🗑️ Removed {len(test_badges)} test debug badges from database")
    except Exception as e:
        print(f"Error removing test badges: {e}")

    # Add missing columns for multiplayer challenges
    try:
        with db.engine.connect() as conn:
            # Check if question column exists in multiplayer_challenge (old version)
            result = conn.execute(db.text("""
                SELECT COUNT(*) as count FROM information_schema.columns 
                WHERE table_name = 'multiplayer_challenge' AND column_name = 'question'
            """))
            question_exists = result.scalar()
            
            if question_exists:
                # Drop the old question column
                conn.execute(db.text("ALTER TABLE multiplayer_challenge DROP COLUMN question"))
                conn.commit()
                print("Dropped old question column from multiplayer_challenge")
            
            # Check if correct_answer column exists in multiplayer_challenge (old version)
            result = conn.execute(db.text("""
                SELECT COUNT(*) as count FROM information_schema.columns 
                WHERE table_name = 'multiplayer_challenge' AND column_name = 'correct_answer'
            """))
            correct_answer_exists = result.scalar()
            
            if correct_answer_exists:
                # Drop the old correct_answer column
                conn.execute(db.text("ALTER TABLE multiplayer_challenge DROP COLUMN correct_answer"))
                conn.commit()
                print("Dropped old correct_answer column from multiplayer_challenge")
            
            # Check if status column exists in multiplayer_challenge
            result = conn.execute(db.text("""
                SELECT COUNT(*) as count FROM information_schema.columns 
                WHERE table_name = 'multiplayer_challenge' AND column_name = 'status'
            """))
            status_exists = result.scalar()
            
            if not status_exists:
                conn.execute(db.text("""
                    ALTER TABLE multiplayer_challenge 
                    ADD COLUMN status VARCHAR(20) DEFAULT 'waiting'
                """))
                conn.commit()
                print("Added status column to multiplayer_challenge")
            
            # Check if started_at column exists in multiplayer_challenge
            result = conn.execute(db.text("""
                SELECT COUNT(*) as count FROM information_schema.columns 
                WHERE table_name = 'multiplayer_challenge' AND column_name = 'started_at'
            """))
            started_at_exists = result.scalar()
            
            if not started_at_exists:
                conn.execute(db.text("""
                    ALTER TABLE multiplayer_challenge 
                    ADD COLUMN started_at DATETIME
                """))
                conn.commit()
                print("Added started_at column to multiplayer_challenge")
            
            # Check if duration_minutes column exists in multiplayer_challenge
            result = conn.execute(db.text("""
                SELECT COUNT(*) as count FROM information_schema.columns 
                WHERE table_name = 'multiplayer_challenge' AND column_name = 'duration_minutes'
            """))
            duration_exists = result.scalar()
            
            if not duration_exists:
                conn.execute(db.text("""
                    ALTER TABLE multiplayer_challenge 
                    ADD COLUMN duration_minutes INTEGER DEFAULT 10
                """))
                conn.commit()
                print("Added duration_minutes column to multiplayer_challenge")
            
            # Check if score column exists in challenge_participant
            result = conn.execute(db.text("""
                SELECT COUNT(*) as count FROM information_schema.columns 
                WHERE table_name = 'challenge_participant' AND column_name = 'score'
            """))
            score_exists = result.scalar()
            
            if not score_exists:
                conn.execute(db.text("""
                    ALTER TABLE challenge_participant 
                    ADD COLUMN score INTEGER DEFAULT 0,
                    ADD COLUMN current_mission INTEGER DEFAULT 1,
                    ADD COLUMN is_completed BOOLEAN DEFAULT FALSE,
                    ADD COLUMN completed_at DATETIME
                """))
                conn.commit()
                print("Added missing columns to challenge_participant")
            
    except Exception as e:
        print(f"Migration error: {e}")

    if Mission.query.count() == 0:
        insert_missions("student", student_missions)
        insert_missions("employee", employee_missions)
        db.session.commit()

    if LearningModule.query.count() == 0:
        insert_learning_modules()
    
    if EscapeRoom.query.count() == 0:
        seed_escape_rooms()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)


