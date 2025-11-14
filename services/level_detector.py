import re
from datetime import datetime


def parse_years_from_text(text: str) -> float:
    total_years = 0.0
    
    pattern1 = r'(\d+(?:\.\d+)?)\s*(?:năm|years?|yr)'
    matches = re.findall(pattern1, text, re.IGNORECASE)
    for match in matches:
        try:
            years = float(match)
            total_years += years
        except ValueError:
            continue
    
    date_range_pattern = r'(\d{1,2}[/-]\d{4}|\d{4})\s*[-–—]\s*(\d{1,2}[/-]\d{4}|\d{4}|hiện tại|present|now|nay)'
    matches = re.findall(date_range_pattern, text, re.IGNORECASE)
    
    current_year = datetime.now().year
    current_month = datetime.now().month
    
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
            
            years = (end_year - start_year) + (end_month - start_month) / 12.0
            if years > 0:
                total_years += years
        except (ValueError, IndexError):
            continue
    
    pattern3 = r'(?:từ|from)\s+(\d{4})\s+(?:đến|to|–|-)\s+(\d{4}|hiện tại|present|now|nay)'
    matches = re.findall(pattern3, text, re.IGNORECASE)
    for start_year_str, end_year_str in matches:
        try:
            start_year = int(start_year_str)
            if end_year_str.lower() in ['hiện tại', 'present', 'now', 'nay']:
                end_year = current_year
            else:
                end_year = int(end_year_str)
            
            years = end_year - start_year
            if years > 0:
                total_years += years
        except ValueError:
            continue
    
    return round(total_years, 1)


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
    text_lower = cv_text.lower()
    
    for keyword in experience_keywords:
        pattern = rf'{keyword}.*?(?=\n\n|\n[A-ZÀ-Ỹ][^:]*:|$)'
        match = re.search(pattern, cv_text, re.IGNORECASE | re.DOTALL)
        if match:
            experience_section = match.group(0)
            break
    
    if not experience_section:
        experience_section = cv_text
    
    total_years = parse_years_from_text(experience_section)
    
    if total_years < 1:
        return "intern"
    elif total_years < 3:
        return "junior"
    elif total_years < 5:
        return "mid"
    else:
        return "senior"

