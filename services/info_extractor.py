import re
from typing import Dict


def extract_email(text: str) -> str:
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    matches = re.findall(email_pattern, text)
    if matches:
        return matches[0]
    return ""


def extract_phone(text: str) -> str:
    cleaned_text = re.sub(r'[^\d+\s\-()]', '', text)
    vn_mobile_pattern = r'(?:0|\+84)[\s\-]?[3-9][\d\s\-]{8,9}'
    intl_pattern = r'\+[\d\s\-]{10,}'
    simple_pattern = r'\d{10,11}'
    
    patterns = [
        (vn_mobile_pattern, cleaned_text),
        (intl_pattern, cleaned_text),
        (simple_pattern, cleaned_text)
    ]
    
    for pattern, search_text in patterns:
        matches = re.findall(pattern, search_text)
        if matches:
            phone = re.sub(r'[\s\-]', '', matches[0])
            if 10 <= len(re.sub(r'[^\d]', '', phone)) <= 15:
                return phone
    
    return ""


def extract_name(text: str) -> str:
    lines = text.split('\n')
    
    for line in lines[:10]:
        line = line.strip()
        if not line or len(line) < 3 or len(line) > 50:
            continue
        if '@' in line or re.search(r'\d{10,}', line):
            continue
        skip_keywords = ['cv', 'resume', 'curriculum vitae', 'phone', 'email', 'address', 
                        'địa chỉ', 'điện thoại', 'thư điện tử', 'kinh nghiệm', 'kỹ năng']
        if any(keyword.lower() in line.lower() for keyword in skip_keywords):
            continue
        if re.match(r'^[A-Za-zÀ-ỹ\s]+$', line):
            return line
    
    return ""


def extract_info(cv_text: str) -> Dict[str, str]:
    return {
        "name": extract_name(cv_text),
        "phone": extract_phone(cv_text),
        "email": extract_email(cv_text),
        "location": ""
    }

