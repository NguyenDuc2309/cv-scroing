import re
import logging
from datetime import datetime
from typing import Tuple


def parse_years_with_role_type(text: str) -> Tuple[float, bool]:
    """
    Parse số năm kinh nghiệm và kiểm tra xem có phải toàn bộ là intern/trainee không.
    
    Returns:
        (weighted_years, is_only_intern_trainee)
    """
    date_range_pattern = r'(\d{1,2}[/-]\d{4}|\d{4})\s*[-–—]\s*(\d{1,2}[/-]\d{4}|\d{4}|hiện tại|present|now|nay)'
    matches = re.findall(date_range_pattern, text, re.IGNORECASE)
    
    current_year = datetime.now().year
    current_month = datetime.now().month
    
    intern_keywords = [
        r'intern',
        r'trainee',
        r'thực tập',
        r'thuc tap',
        r'internship',
        r'apprentice'
    ]
    
    fulltime_keywords = [
        r'engineer',
        r'developer',
        r'developer',
        r'analyst',
        r'manager',
        r'lead',
        r'senior',
        r'junior',
        r'associate',
        r'specialist',
        r'consultant',
        r'kỹ sư',
        r'chuyên viên',
        r'nhân viên'
    ]
    
    weighted_years = 0.0
    has_fulltime = False
    has_intern_trainee = False
    
    for start_str, end_str in matches:
        try:
            if '/' in start_str:
                parts = start_str.split('/')
                if len(parts) == 2:
                    start_month, start_year = int(parts[0]), int(parts[1])
                else:
                    start_year = int(parts[0])
                    start_month = 1
            else:
                start_year = int(start_str)
                start_month = 1
            
            if end_str.lower() in ['hiện tại', 'present', 'now', 'nay']:
                end_year = current_year
                end_month = current_month
            elif '/' in end_str:
                parts = end_str.split('/')
                if len(parts) == 2:
                    end_month, end_year = int(parts[0]), int(parts[1])
                else:
                    end_year = int(parts[0])
                    end_month = 12
            else:
                end_year = int(end_str)
                end_month = 12
            
            if start_year > current_year + 1:
                continue
            
            years = (end_year - start_year) + (end_month - start_month) / 12.0
            if years <= 0 or years >= 50:
                continue
            
            start_idx = text.lower().find(start_str.lower())
            if start_idx == -1:
                continue
            
            context_start = max(0, start_idx - 200)
            context_end = min(len(text), start_idx + 200)
            context = text[context_start:context_end].lower()
            
            is_intern_trainee = any(re.search(kw, context, re.IGNORECASE) for kw in intern_keywords)
            is_fulltime = any(re.search(kw, context, re.IGNORECASE) for kw in fulltime_keywords)
            
            if is_intern_trainee and not is_fulltime:
                weighted_years += years * 0.3
                has_intern_trainee = True
                logging.info(f"[LEVEL_DETECTOR] Found intern/trainee: {years} years → weighted {years * 0.3}")
            elif is_fulltime:
                weighted_years += years * 1.0
                has_fulltime = True
                logging.info(f"[LEVEL_DETECTOR] Found full-time: {years} years → weighted {years * 1.0}")
            else:
                weighted_years += years * 0.5
                logging.info(f"[LEVEL_DETECTOR] Found unknown role: {years} years → weighted {years * 0.5}")
                
        except (ValueError, IndexError):
            continue
    
    is_only_intern_trainee = has_intern_trainee and not has_fulltime
    
    logging.info(f"[LEVEL_DETECTOR] Weighted years: {weighted_years:.1f}, is_only_intern_trainee: {is_only_intern_trainee}")
    
    return round(weighted_years, 1), is_only_intern_trainee


def detect_level(cv_text: str) -> str:
    experience_keywords = [
        r'kinh nghiệm làm việc',
        r'work experience',
        r'professional experience',
        r'employment history',
        r'quá trình làm việc',
        r'công việc',
        r'employment'
    ]
    
    experience_section = ""
    
    for keyword in experience_keywords:
        pattern = rf'{keyword}.*?(?=\n\n|\n[A-ZÀ-Ỹ][^:]*:|$)'
        match = re.search(pattern, cv_text, re.IGNORECASE | re.DOTALL)
        if match:
            experience_section = match.group(0)
            break
    
    if not experience_section:
        experience_section = cv_text
    
    weighted_years, is_only_intern_trainee = parse_years_with_role_type(experience_section)
    
    if is_only_intern_trainee:
        if weighted_years < 0.5:
            level = "intern"
        elif weighted_years <= 1.5:
            level = "fresher"
        else:
            level = "fresher"
        logging.info(f"[LEVEL_DETECTOR] Only intern/trainee detected → max level: {level}")
    else:
        if weighted_years < 0.5:
            level = "intern"
        elif weighted_years <= 1.5:
            level = "fresher"
        elif weighted_years <= 3:
            level = "junior"
        elif weighted_years <= 5:
            level = "mid"
        else:
            level = "senior"
    
    logging.info(f"[LEVEL_DETECTOR] Final level: {level} (weighted_years: {weighted_years:.1f})")
    
    return level
