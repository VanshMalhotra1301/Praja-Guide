import re

def calculate_eligibility_score(scheme, user_data, predicted_categories):
    """
    Advanced Scoring Engine: Generates a confidence score (60-99).
    Now considers Vulnerability, Social Status, and recent shocks (Job Loss).
    """
    full_text = (str(scheme.get('scheme_name')) + " " + str(scheme.get('details'))).lower()
    category = str(scheme.get('schemeCategory', '')).lower()
    score = 65  # Base Score

    # 1. Primary Need Alignment (+15)
    if user_data.get('primary_need', '').lower() in category:
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
    # Ensure income is treated as an integer
    try:
        income = int(user_data.get('income', 999999))
    except (ValueError, TypeError):
        income = 999999
        
    if income < 200000:
        score += 5

    # 4. Social Category (+10)
    user_caste = user_data.get('caste', 'General')
    if user_caste in ['SC', 'ST'] and user_caste.lower() in full_text:
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
    occupation = user_data.get('occupation', '')
    if occupation == 'Agriculture' and 'farmer' in scheme_text:
        reasons.append("you are a Farmer")
    elif user_data.get('is_student') == 'Yes' and 'scholarship' in scheme_text:
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
    if user_data.get('gender') == 'Female' and 'women' in scheme_text:
        reasons.append("this scheme specifically empowers women")
    elif user_data.get('is_widow') == 'Yes' and 'pension' in category:
        reasons.append("it provides financial support for widows")
    
    user_caste = user_data.get('caste', 'General')
    if user_caste in ['SC', 'ST'] and user_caste.lower() in scheme_text:
        reasons.append(f"it supports the {user_caste} community")
    
    # Financial Hook
    benefit = extract_financial_value(scheme.get('details', ''))
    benefit_text = f" providing approx ₹{benefit:,} in benefits" if benefit > 0 else ""

    if not reasons:
        return f"Your profile matches the general eligibility criteria{benefit_text}."
    
    return f"You are eligible because {', and '.join(reasons)}{benefit_text}."

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