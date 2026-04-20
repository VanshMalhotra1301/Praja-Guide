from flask import Blueprint, render_template, request
from .ml_engine import predict_category
from .rule_engine import filter_schemes
import pandas as pd
import os
import re
import random
from datetime import datetime

main = Blueprint('main', __name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(os.path.dirname(BASE_DIR), 'data', 'updated_data.csv')

try:
    print(f"Loading Database from: {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)
    print(f"Database loaded: {len(df)} schemes found.")
except Exception as e:
    print(f"CRITICAL ERROR: Could not load CSV. {e}")
    df = pd.DataFrame()

# ==========================================
# 1. HELPER FUNCTIONS (ENHANCED AI LOGIC)
# ==========================================

def extract_financial_value(text):
    """
    Extracts money value from scheme details using Regex.
    Returns integer value (e.g., 5000).
    """
    text = str(text).lower().replace(',', '')
    
    # Pattern: "Rs 5000", "INR 20000"
    amount_match = re.search(r'(?:rs\.?|inr|₹)\s*(\d+)', text)
    if amount_match:
        return int(amount_match.group(1))
        
    # Pattern: "2 Lakh"
    lakh_match = re.search(r'(\d+(?:\.\d+)?)\s*lakh', text)
    if lakh_match:
        return int(float(lakh_match.group(1)) * 100000)
        
    return 0

def calculate_eligibility_score(scheme, user_data, predicted_categories):
    """
    Advanced Scoring Engine: Generates a confidence score (60-99).
    Now considers Vulnerability, Social Status, and recent shocks (Job Loss).
    """
    full_text = (str(scheme.get('scheme_name')) + " " + str(scheme.get('details'))).lower()
    category = str(scheme.get('schemeCategory', '')).lower()
    score = 65  # Base Score

    # 1. Primary Need Alignment (+15)
    if user_data['primary_need'].lower() in category:
        score += 15

    # 2. Vulnerability Boosters (+10 to +20)
    # Priority for Kutcha houses in Housing schemes
    if user_data.get('house_type') == 'Kutcha' and 'housing' in category:
        score += 15
    
    # Priority for Widows in Pension schemes
    if user_data.get('is_widow') == 'Yes' and ('pension' in category or 'widow' in full_text):
        score += 20
        
    # Priority for Job Loss in Employment schemes
    if user_data.get('job_loss') == 'Yes' and ('employment' in category or 'training' in category):
        score += 15

    # Priority for Single Parents
    if user_data.get('single_parent') == 'Yes' and 'child' in full_text:
        score += 10

    # 3. Economic Status (+5)
    if user_data['income'] < 200000:
        score += 5

    # 4. Social Category (+10)
    if user_data['caste'] in ['SC', 'ST'] and user_data['caste'].lower() in full_text:
        score += 10
        
    # 5. ML Model Confidence (+5)
    if any(cat in category for cat in predicted_categories):
        score += 5

    return min(score, 99)

def generate_ai_explanation(scheme, user_data):
    """
    Generates a conversational 'Why am I eligible?' response.
    """
    scheme_text = (str(scheme.get('scheme_name')) + str(scheme.get('details'))).lower()
    category = str(scheme.get('schemeCategory', '')).lower()
    reasons = []

    # Reason 1: Occupation & Status
    if user_data['occupation'] == 'Agriculture' and 'farmer' in scheme_text:
        reasons.append("you are a Farmer")
    elif user_data['is_student'] == 'Yes' and 'scholarship' in scheme_text:
        reasons.append("you are a Student")
    elif user_data.get('job_loss') == 'Yes' and 'employment' in category:
        reasons.append("you recently faced employment challenges")
    elif user_data.get('skill_training') == 'No' and 'skill' in category:
        reasons.append("you are looking for skill development")

    # Reason 2: Living Condition
    if user_data.get('house_type') == 'Kutcha' and 'housing' in category:
        reasons.append("you live in a temporary structure")
    elif user_data.get('electricity') == 'No' and 'electr' in scheme_text:
        reasons.append("you lack electricity access")

    # Reason 3: Social/Demographic
    if user_data['gender'] == 'Female' and 'women' in scheme_text:
        reasons.append("this scheme specifically empowers women")
    elif user_data.get('is_widow') == 'Yes' and 'pension' in category:
        reasons.append("it provides financial support for widows")
    elif user_data['caste'] in ['SC', 'ST'] and user_data['caste'].lower() in scheme_text:
        reasons.append(f"it supports the {user_data['caste']} community")
    
    # Financial Hook
    benefit = extract_financial_value(scheme.get('details', ''))
    benefit_text = f" providing approx ₹{benefit:,} in benefits" if benefit > 0 else ""

    if not reasons:
        return f"Your profile matches the general eligibility criteria{benefit_text}."
    
    return f"You are eligible because {', and '.join(reasons)}{benefit_text}."

def get_document_checklist(category):
    """
    Returns a simulated document list based on scheme category.
    """
    cat_lower = str(category).lower()
    docs = ["Aadhaar Card", "Bank Account Passbook", "Passport Size Photo"]
    
    if "education" in cat_lower or "scholarship" in cat_lower:
        docs.extend(["Student ID Card", "Previous Year Marksheet", "Admission Receipt"])
    elif "agriculture" in cat_lower or "farmer" in cat_lower:
        docs.extend(["Land Ownership Records (Khasra/Khatauni)", "Kisan Credit Card"])
    elif "health" in cat_lower:
        docs.extend(["Doctor's Certificate", "Hospital Discharge Summary", "Ayushman Card"])
    elif "housing" in cat_lower:
        docs.extend(["Domicile Certificate", "Income Certificate", "BPL Card"])
    elif "pension" in cat_lower:
        docs.extend(["Age Proof", "Retirement Order", "Income Certificate"])
    elif "business" in cat_lower or "loan" in cat_lower:
        docs.extend(["Project Report", "PAN Card", "ITR (if available)"])
    else:
        docs.append("Income Certificate")
        
    return docs

# ==========================================
# 2. MAIN ROUTES
# ==========================================

@main.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@main.route('/find-schemes', methods=['GET', 'POST'])
def find_schemes():
    if request.method == 'POST':
        try:
            # ==========================================
            # PHASE 1: DATA COLLECTION (7-STEP WIZARD)
            # ==========================================
            
            # --- STEP 1: BASIC IDENTITY ---
            age_group = request.form.get('age_group', '18-25')
            gender = request.form.get('gender', '')
            state = request.form.get('state', '')
            district = request.form.get('district', '')
            area_type = request.form.get('area_type', 'Urban')
            marital_status = request.form.get('marital_status', 'Single')

            # --- STEP 2: FAMILY PROFILE ---
            dependents = int(request.form.get('dependents', 0))
            children_studying = request.form.get('children_studying', 'No')
            has_senior_citizens = request.form.get('has_senior_citizens', 'No')
            single_parent = request.form.get('single_parent', 'No')
            is_widow = request.form.get('is_widow', 'No')
            bpl_card = request.form.get('bpl_card', 'No')

            # --- STEP 3: EDUCATION & SKILLS ---
            education_level = request.form.get('education_level', '')
            is_student = request.form.get('is_student', 'No')
            skill_training = request.form.get('skill_training', 'No')

            # --- STEP 4: EMPLOYMENT & ECONOMY ---
            occupation = request.form.get('occupation', '')
            employment_status = request.form.get('employment_status', '')
            income_range = request.form.get('income_range', '')
            job_loss = request.form.get('job_loss', 'No')
            
            # --- STEP 5: AGRICULTURE (Conditional) ---
            land_ownership = request.form.get('land_ownership', 'No')
            land_size = request.form.get('land_size', '0')
            livestock = request.form.get('livestock', 'No')

            # --- STEP 6: SOCIAL & LIVING CONDITIONS ---
            social_category = request.form.get('social_category', 'General')
            minority_status = request.form.get('minority_status', 'No')
            disability = request.form.get('disability', 'No')
            chronic_illness = request.form.get('illness', 'No')
            ex_serviceman = request.form.get('ex_serviceman', 'No')
            house_type = request.form.get('house_type', 'Pucca')
            housing_ownership = request.form.get('housing_ownership', 'Owned')
            electricity = request.form.get('electricity', 'Yes')

            # --- STEP 7: FINANCIAL INCLUSION ---
            bank_account = request.form.get('bank_account', 'Yes')
            aadhaar_linked = request.form.get('aadhaar_linked', 'Yes')
            primary_need = request.form.get('primary_need', 'General')

            # ==========================================
            # PHASE 2: DATA NORMALIZATION
            # ==========================================
            
            # Map Income Range to Integer
            income_map = {
                'Below 1 Lakh': 90000, 
                '1-3 Lakhs': 200000, 
                '3-5 Lakhs': 400000, 
                '5-8 Lakhs': 600000, 
                'Above 8 Lakhs': 900000
            }
            income = income_map.get(income_range, 100000)

            # Map Age Group to Integer
            age_map = {
                'Below 18': 16, 
                '18-25': 21, 
                '26-40': 30, 
                '41-60': 50, 
                'Above 60': 65
            }
            age = age_map.get(age_group, 25)

            # ==========================================
            # PHASE 3: CONTEXT GENERATION (LSTM INPUT)
            # ==========================================
            user_query = f"I am a {age} year old {gender} from {state}, {district}. "
            user_query += f"I am {marital_status} with {dependents} dependents. "
            user_query += f"Occupation: {occupation}, Income: {income_range}. "
            user_query += f"Caste: {social_category}. Housing: {house_type}. "
            user_query += f"My primary goal is {primary_need}. "
            
            # Add specific triggers for ML Model context
            if job_loss == 'Yes': user_query += "Recently lost job. "
            if is_widow == 'Yes' or marital_status == 'Widowed': user_query += "I am a widow needing pension. "
            if children_studying == 'Yes': user_query += "I have children in school. "
            if single_parent == 'Yes': user_query += "I am a single parent. "
            if occupation == 'Agriculture': user_query += f"Farmer with {land_size} acres. "
            if livestock == 'Yes': user_query += "I own livestock. "
            if skill_training == 'No': user_query += "Looking for skill development. "
            if disability == 'Yes': user_query += "I am a person with disability. "
            if housing_ownership == 'Rented': user_query += "I live in a rented house. "
            if bpl_card == 'Yes': user_query += "I have a BPL card. "
            if minority_status == 'Yes': user_query += "I belong to a minority community. "
            if ex_serviceman == 'Yes': user_query += "I am an ex-serviceman. "
            if chronic_illness == 'Yes': user_query += "There is chronic illness in my family. "

            # ==========================================
            # PHASE 4: PROCESSING & FILTERING
            # ==========================================
            
            # 1. ML Prediction
            predicted_categories = predict_category(user_query)

            # 2. Consolidated User Data Dictionary for Rule Engine
            user_data = {
                'age': age, 
                'income': income, 
                'state': state, 
                'gender': gender,
                'caste': social_category, 
                'disability': disability, 
                'occupation': occupation,
                'employment_status': employment_status, 
                'residence': area_type,
                'marital_status': marital_status, 
                'education': education_level,
                'is_student': is_student, 
                'house_type': house_type,
                'land_ownership': land_ownership, 
                'primary_need': primary_need,
                
                # Extended Fields for Advanced Scoring
                'is_widow': is_widow, 
                'single_parent': single_parent,
                'job_loss': job_loss, 
                'housing_ownership': housing_ownership,
                'has_senior_citizens': has_senior_citizens,
                'skill_training': skill_training,
                'electricity': electricity
            }

            # 3. Rule Engine Filtering
            eligible_schemes = filter_schemes(df, user_data, predicted_categories)
            
            # ==========================================
            # PHASE 5: ENHANCEMENT & SCORING
            # ==========================================
            enhanced_schemes = []
            total_benefit_value = 0
            current_date = datetime.now().strftime("%Y-%m-%d")

            for scheme in eligible_schemes:
                # Calculate Advanced Score
                score = calculate_eligibility_score(scheme, user_data, predicted_categories)
                
                # Generate AI Explanation
                explanation = generate_ai_explanation(scheme, user_data)
                
                # Extract Financial Value
                benefit_val = extract_financial_value(scheme.get('details', ''))
                total_benefit_value += benefit_val

                # Construct Enhanced Object
                enhanced_scheme = scheme.copy()
                enhanced_scheme.update({
                    'eligibility_score': score,
                    'ai_explanation': explanation,
                    'documents': get_document_checklist(scheme.get('schemeCategory', '')),
                    'application_status': "Not Applied",
                    'verified': True,
                    'last_updated': current_date,
                    'source': "Official Government Portal",
                    'estimated_benefit': benefit_val
                })
                enhanced_schemes.append(enhanced_scheme)

            # Sort by Score (Descending)
            enhanced_schemes.sort(key=lambda x: x['eligibility_score'], reverse=True)

            # Summary for Dashboard
            financial_summary = {
                "total_benefit": total_benefit_value,
                "monthly_estimate": int(total_benefit_value / 12),
                "scheme_count": len(enhanced_schemes)
            }

            return render_template(
                'results.html', 
                schemes=enhanced_schemes, 
                categories=predicted_categories,
                financial_summary=financial_summary
            )

        except Exception as e:
            print(f"Post Error: {e}")
            import traceback
            traceback.print_exc()
            return render_template('find_schemes.html', error="Error processing profile. Please try again.")

    return render_template('find_schemes.html')

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/tech')
def tech():
    return render_template('tech.html')

@main.route('/team')
def team():
    return render_template('team.html')