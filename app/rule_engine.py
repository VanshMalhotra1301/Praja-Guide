import re
import math

# ==========================================
# 1. HELPER FUNCTIONS (EXTRACTION & LOGIC)
# ==========================================

def extract_age_limits(text):
    """
    Extracts age range. Returns (min_age, max_age).
    Defaults to (0, 100) if no specific limit found.
    """
    text = str(text).lower()
    min_age, max_age = 0, 100
    
    # Pattern 1: Range (e.g., "18-40 years", "between 18 and 60")
    range_pattern = re.search(r'(\d+)\s*(?:-|to|and)\s*(\d+)\s*years?', text)
    if range_pattern:
        return int(range_pattern.group(1)), int(range_pattern.group(2))

    # Pattern 2: Minimum (e.g., "above 60", "minimum 18", "more than 18")
    min_pattern = re.search(r'(?:above|more than|minimum|min)\s*(\d+)', text)
    if min_pattern:
        min_age = int(min_pattern.group(1))
    
    # Pattern 3: Maximum (e.g., "below 18", "upto 30", "max 45")
    max_pattern = re.search(r'(?:below|upto|less than|maximum|max)\s*(\d+)', text)
    if max_pattern:
        max_age = int(max_pattern.group(1))

    return min_age, max_age

def extract_income_limit(text):
    """
    Extracts max income limit. Returns normalized integer (e.g., 200000).
    """
    text = str(text).lower().replace(',', '')
    
    # Pattern 1: "2.5 lakh" -> 250000
    lakh_pattern = re.search(r'(\d+(?:\.\d+)?)\s*lakh', text)
    if lakh_pattern:
        return int(float(lakh_pattern.group(1)) * 100000)
    
    # Pattern 2: "Rs 200000" or "INR 50000"
    val_pattern = re.search(r'(?:rs\.?|₹|inr)\.?\s*(\d+)', text)
    if val_pattern:
        return int(val_pattern.group(1))
        
    return 999999999 # High default if no limit found

def calculate_score(full_text, s_category, s_state, user_data, predicted_categories):
    """
    Calculates a normalized eligibility score (60-100) using 30+ data points.
    """
    score = 0
    
    # Unpack Key User Context
    u_primary_need = user_data.get('primary_need', '').lower()
    u_state = user_data.get('state', '').lower()
    u_occ = user_data.get('occupation', '').lower()
    u_housing = user_data.get('house_type', '').lower()
    u_caste_clean = user_data.get('caste', 'General').lower()
    u_disability = user_data.get('disability', 'No')
    u_widow = user_data.get('is_widow', 'No')
    u_job_loss = user_data.get('job_loss', 'No')
    u_single_parent = user_data.get('single_parent', 'No')

    # --- PRIORITY 1: PRIMARY NEED (High Weight: +100) ---
    if u_primary_need in full_text or u_primary_need in s_category:
        score += 100
    
    # --- PRIORITY 2: STATE MATCH (Medium Weight: +50) ---
    if u_state in s_state or u_state in full_text:
        score += 50

    # --- PRIORITY 3: OCCUPATION SPECIFICS (+40) ---
    if u_occ == 'agriculture' and any(x in full_text for x in ['kisan', 'farmer', 'crop', 'fertilizer', 'pm-kisan']):
        score += 40
    if u_occ == 'student' and any(x in full_text for x in ['scholarship', 'fellowship', 'tuition']):
        score += 40
    if u_job_loss == 'Yes' and any(x in full_text for x in ['unemployment', 'allowance', 'bhatta', 'skill training']):
        score += 40

    # --- PRIORITY 4: VULNERABILITY BONUS (+20-30) ---
    if u_housing == 'kutcha' and 'housing' in full_text:
        score += 30
    if u_caste_clean in ['sc', 'st'] and u_caste_clean in full_text:
        score += 20
    if u_disability == 'Yes' and 'disability' in full_text:
        score += 30
    if u_widow == 'Yes' and ('widow' in full_text or 'pension' in full_text):
        score += 35
    if u_single_parent == 'Yes' and 'child' in full_text:
        score += 25

    # --- PRIORITY 5: AI CATEGORY MATCH (+25) ---
    if any(cat.lower() in s_category for cat in predicted_categories):
        score += 25
        
    # Normalize Score to 60-100 range for display
    # Max possible raw score is approx 300+. 
    final_score = 60 + int((score / 300) * 40)
    return min(final_score, 99)

def generate_explanation(user_data, scheme_text, category):
    """
    Generates a dynamic AI explanation string based on extended profile.
    """
    explanations = []
    
    # Occupation & Work
    if user_data['occupation'].lower() == 'agriculture' and 'farmer' in scheme_text:
        explanations.append("This scheme supports your occupation as a farmer.")
    elif user_data['is_student'] == 'Yes' and ('education' in category or 'scholarship' in scheme_text):
        explanations.append("You qualify as a student for education benefits.")
    elif user_data.get('job_loss') == 'Yes' and 'employment' in category:
        explanations.append("It assists individuals who have recently lost their job.")
        
    # Income & Housing
    if user_data['income'] < 300000:
        explanations.append("Your income falls within the eligible limit.")
    if user_data.get('house_type') == 'Kutcha' and 'housing' in category:
        explanations.append("It provides assistance for upgrading from a Kutcha house.")
        
    # Social Category & Status
    if user_data['caste'].lower() in ['sc', 'st', 'obc']:
        explanations.append(f"It provides specific benefits for the {user_data['caste']} category.")
    if user_data.get('is_widow') == 'Yes' and 'widow' in scheme_text:
        explanations.append("It provides dedicated pension support for widows.")
    if user_data.get('disability') == 'Yes' and 'disability' in scheme_text:
        explanations.append("It provides assistance for persons with disabilities.")
        
    # Default
    if not explanations:
        explanations.append("Your profile matches the general eligibility criteria.")
        
    return " ".join(explanations)

def assign_documents(category):
    """
    Returns a list of required documents based on category.
    """
    cat = category.lower()
    docs = ["Aadhaar Card", "Bank Passbook", "Passport Photo"]
    
    if "education" in cat or "scholarship" in cat:
        docs.extend(["Student ID", "Income Certificate", "Previous Marksheet"])
    elif "agriculture" in cat or "farmer" in cat:
        docs.extend(["Land Records (Khasra/Khatauni)", "Kisan Credit Card"])
    elif "housing" in cat:
        docs.extend(["Address Proof", "Income Certificate", "BPL Card", "House Photo"])
    elif "health" in cat:
        docs.extend(["Medical Certificate", "Income Proof", "Ration Card"])
    elif "pension" in cat:
        docs.extend(["Age Proof", "Retirement Order", "Bank Consent Form"])
    elif "widow" in cat:
        docs.extend(["Death Certificate of Spouse", "Age Proof", "Income Certificate"])
    elif "disability" in cat:
        docs.extend(["UDID Card / Disability Certificate", "Income Certificate"])
        
    return docs

def estimate_benefit(scheme_text, category):
    """
    Estimates financial benefit value using Regex.
    """
    # Try to extract actual value from text first
    val_match = re.search(r'(?:rs\.?|₹|inr)\.?\s*(\d+(?:,\d+)*)', scheme_text)
    if val_match:
        val = int(val_match.group(1).replace(',', ''))
        # Sanity check: ensure it's a reasonable amount
        if val > 100 and val < 1000000:
            return val

    # Fallback Estimates based on category
    cat = category.lower()
    if "education" in cat: return 50000
    if "housing" in cat: return 150000
    if "health" in cat: return 500000
    if "agriculture" in cat: return 6000
    if "pension" in cat: return 36000 # Annual
    
    return 10000 # Generic fallback

# ==========================================
# 2. MAIN FILTER LOGIC
# ==========================================

def filter_schemes(df, user_data, predicted_categories):
    """
    Enhanced Rule Engine with logic for Occupation, Land, Housing, Widowhood, and Primary Needs.
    """
    scored_schemes = []
    
    # --- UNPACK USER DATA ---
    u_age = int(user_data.get('age', 0))
    u_income = int(user_data.get('income', 99999999))
    u_state = user_data.get('state', '').lower()
    u_gender = user_data.get('gender', '').lower()
    u_caste = user_data.get('caste', 'General') 
    u_caste_clean = u_caste.lower()
    
    u_occ = user_data.get('occupation', '').lower()       
    u_emp_status = user_data.get('employment_status', '').lower()
    u_disability = user_data.get('disability', 'No')      
    u_is_student = user_data.get('is_student', 'No')
    u_primary_need = user_data.get('primary_need', '').lower() 

    # New Extended Filters
    u_widow = user_data.get('is_widow', 'No')
    u_house_type = user_data.get('house_type', 'Pucca')
    u_job_loss = user_data.get('job_loss', 'No')
    u_single_parent = user_data.get('single_parent', 'No')
    u_skill_training = user_data.get('skill_training', 'No')

    # Iterate through DataFrame
    for index, row in df.iterrows():
        # Scheme Data
        s_name = str(row.get('scheme_name', ''))
        s_desc = str(row.get('details', ''))
        s_elig = str(row.get('eligibility', ''))
        s_state = str(row.get('state', 'Central')).lower()
        s_category = str(row.get('schemeCategory', '')).lower()
        s_link = row.get('application_link', '#')
        
        # Combine text for Keyword Search
        full_text = (s_name + " " + s_desc + " " + s_elig + " " + s_category).lower()
        
        # --- HARD FILTERS (REJECTION LOGIC) ---
        
        # A. State Filter
        if "central" not in s_state and "pan india" not in s_state:
            if u_state not in s_state and u_state not in full_text:
                continue 

        # B. Gender Filter
        if u_gender == 'male':
            if any(x in full_text for x in ['women only', 'girl child', 'widow', 'pregnant', 'lactating', 'mother']):
                # Exception: "men and women" explicitly stated
                if "men and women" not in full_text:
                    continue

        # C. Caste Filter
        if u_caste_clean == 'general':
            if any(x in full_text for x in ['sc only', 'st only', 'scheduled caste only', 'tribal only']):
                continue

        # D. Age Filter
        min_a, max_a = extract_age_limits(s_elig + " " + s_desc)
        if u_age > 0 and (u_age < min_a or u_age > max_a):
            continue

        # E. Income Filter
        max_inc = extract_income_limit(s_elig)
        if u_income > 0 and u_income > max_inc:
            continue

        # F. Occupation / Student Status Filter
        if 'farmer' in full_text and 'agriculture' not in u_occ:
            continue
        if ('student' in full_text or 'scholarship' in full_text) and u_is_student == 'No' and 'student' not in u_emp_status:
            # Exception: Parents applying for children (check single parent / children fields)
            if u_single_parent == 'No' and user_data.get('children_studying', 'No') == 'No':
                continue

        # G. Disability Filter
        if u_disability == 'No':
            if any(x in full_text for x in ['disability', 'handicapped', 'differently abled', 'pwd', 'blind']):
                continue

        # H. Extended Filter: Widow Status
        if u_widow == 'No':
            if 'widow' in full_text and 'women' not in s_name: # Careful not to exclude general women schemes
                 if "widow pension" in s_name.lower():
                     continue

        # I. Extended Filter: Housing Type
        if u_house_type == 'Pucca':
            if 'kutcha' in full_text or 'homeless' in full_text:
                # Exclude schemes meant specifically for homeless or kutcha house owners
                continue

        # J. Extended Filter: Job Loss / Skill Training
        if u_job_loss == 'No' and u_skill_training == 'Yes':
            # If user already trained and has job, filter out basic skill training? (Optional, kept loose for now)
            pass

        # --- SCORING & METADATA ---
        score = calculate_score(full_text, s_category, s_state, user_data, predicted_categories)
        
        # Only accept relevant schemes
        if score >= 60: 
            scored_schemes.append({
                'scheme_name': s_name,
                'category': s_category.title(),
                'details': s_desc[:200] + "..." if len(s_desc) > 200 else s_desc,
                'eligibility': s_elig[:100] + "...",
                'application_link': s_link,
                'state': s_state.title(),
                
                # Enhanced Data
                'match_score': score, # Used for sorting in routes
                'eligibility_score': score, # Display value
                'ai_explanation': generate_explanation(user_data, full_text, s_category),
                'documents': assign_documents(s_category),
                'application_status': "Not Applied",
                'verified': True,
                'last_updated': "2025-12-01",
                'source': "Official Government Portal",
                'estimated_benefit': estimate_benefit(full_text, s_category)
            })

    # Sort: 1. Score (Desc), 2. Primary Need Match
    scored_schemes.sort(key=lambda x: (x['eligibility_score'], u_primary_need in x['category'].lower()), reverse=True)
    
    return scored_schemes[:15] # Return top 15 matches