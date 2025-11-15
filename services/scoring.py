from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


CORE_KEYS = {
    "format",
    "experience",
    "skills",
    "soft_skills",
    "education",
    "field_match",
}

BONUS_KEYS = {
    "portfolio",
    "certificates",
    "awards",
    "scholarships",
    "side_projects",
    "community",
}

NEUTRAL_BONUS_SCORE = 35

BONUS_CAP: Dict[str, float] = {
    "intern": 0.20,
    "fresher": 0.20,
    "junior": 0.15,
    "mid": 0.10,
    "senior": 0.05,
}

LEVEL_WEIGHTS: Dict[str, Dict[str, float]] = {
    "intern": {
      "format": 20,
      "experience": 10,
      "skills": 25,
      "soft_skills": 15,
      "education": 20,
      "field_match": 10
    },
    "fresher": {
      "experience": 25,
      "skills": 30,
      "soft_skills": 15,
      "education": 15,
      "format": 10,
      "field_match": 5
    },
    "junior": {
      "experience": 45,
      "skills": 30,
      "soft_skills": 15,
      "format": 5,
      "field_match": 3,
      "education": 2
    },
    "mid": {
      "experience": 55,
      "skills": 30,
      "soft_skills": 15,
      "format": 0,
      "field_match": 0,
      "education": 0
    },
    "senior": {
      "experience": 55,
      "skills": 30,
      "soft_skills": 10,
      "format": 0,
      "field_match": 0,
      "education": 5
    }
}


def _normalize_level(level: str) -> str:
    l = (level or "").strip().lower()
    if l in LEVEL_WEIGHTS:
        return l
    if l in {"internship", "intern-level"}:
        return "intern"
    if l in {"jr", "junior-level"}:
        return "junior"
    if l in {"middle", "mid-level"}:
        return "mid"
    if l in {"sr", "senior-level", "lead"}:
        return "senior"
    return "junior"


def apply_credibility_penalty(credibility_issues: list) -> int:
    """
    Áp dụng penalty cho các vấn đề về độ tin cậy của CV.
    
    Args:
        credibility_issues: Danh sách các vấn đề về độ tin cậy (ví dụ: future dates, inconsistent info)
    
    Returns:
        int: Số điểm bị trừ (âm) hoặc 0 nếu không có vấn đề
    """
    if not credibility_issues:
        return 0
    
    penalty = 0
    for issue in credibility_issues:
        issue_lower = str(issue).lower()
        if any(keyword in issue_lower for keyword in ["tương lai", "future", "chưa đến", "sắp tới"]):
            penalty -= 7 if any(severe in issue_lower for severe in ["nhiều", "multiple", "nhiều mốc"]) else 3
        elif any(keyword in issue_lower for keyword in ["không nhất quán", "inconsistent", "mâu thuẫn"]):
            penalty -= 5
        else:
            penalty -= 2
    
    return max(-10, penalty)


def calculate_overall_score(
    level: str, 
    core_scores: Dict[str, Dict[str, Any]], 
    bonus_scores: Dict[str, Dict[str, Any]],
    credibility_issues: list = None
) -> int:
    """
    Tính overall_score chính xác dựa trên level và bảng trọng số core/bonus.
    
    Công thức mới:
    - Core score = weighted sum của 6 core items (trọng số tổng = 100%)
    - Bonus avg = trung bình của 6 bonus items (missing → neutral 35)
    - Overall = core_score * (1 - bonus_cap) + bonus_avg * bonus_cap
    - Apply credibility_penalty nếu có
    
    Args:
        level: Level của ứng viên (intern, fresher, junior, mid, senior)
        core_scores: Dict chứa scores của 6 core criteria
        bonus_scores: Dict chứa scores của 6 bonus criteria
        credibility_issues: Danh sách các vấn đề về độ tin cậy (optional)
    
    Returns:
        int: Điểm tổng thể (0-100) được tính toán chính xác theo trọng số.
    """
    norm_level = _normalize_level(level)
    core_weights = LEVEL_WEIGHTS.get(norm_level, LEVEL_WEIGHTS["junior"])
    bonus_cap = BONUS_CAP.get(norm_level, BONUS_CAP["junior"])
    
    if credibility_issues is None:
        credibility_issues = []
    
    # Tính core_score: weighted sum của core items
    core_score = 0.0
    total_core_weight = 0.0
    missing_core = []
    
    for key in CORE_KEYS:
        weight = core_weights.get(key, 0)
        if weight <= 0:
            continue
        
        comp = core_scores.get(key)
        if comp and isinstance(comp, dict):
            try:
                score_val = int(comp.get("score", 0))
            except (TypeError, ValueError):
                score_val = 0
                logger.warning(f"Invalid score value for core {key}, using 0")
        else:
            score_val = 0
            missing_core.append(key)
        
        score_val = max(0, min(100, score_val))
        core_score += score_val * weight
        total_core_weight += weight
    
    if total_core_weight <= 0:
        logger.error(f"Total core weight is 0 for level {norm_level}, returning 0")
        return 0
    
    core_score = core_score / total_core_weight
    bonus_sum = 0.0
    bonus_count = 0
    missing_bonus = []
    
    for key in BONUS_KEYS:
        comp = bonus_scores.get(key)
        if comp and isinstance(comp, dict):
            try:
                score_val = int(comp.get("score", 0))
            except (TypeError, ValueError):
                score_val = NEUTRAL_BONUS_SCORE
                logger.warning(f"Invalid score value for bonus {key}, using neutral score")
        else:
            score_val = NEUTRAL_BONUS_SCORE
            missing_bonus.append(key)
        
        score_val = max(0, min(100, score_val))
        bonus_sum += score_val
        bonus_count += 1
    
    bonus_avg = bonus_sum / bonus_count if bonus_count > 0 else NEUTRAL_BONUS_SCORE
    
    overall = core_score * (1 - bonus_cap) + bonus_avg * bonus_cap
    credibility_penalty = apply_credibility_penalty(credibility_issues)
    overall += credibility_penalty
    
    final_score = max(0, min(100, round(overall)))
    
    if missing_core:
        logger.warning(f"Missing core criteria: {missing_core}")
    if missing_bonus:
        logger.debug(f"Missing bonus criteria (using neutral score): {missing_bonus}")
    if credibility_penalty < 0:
        logger.info(f"Applied credibility penalty: {credibility_penalty} points")
    
    logger.info(
        f"Calculated overall_score: {final_score} for level: {norm_level} "
        f"(core_score: {core_score:.2f}, bonus_avg: {bonus_avg:.2f}, "
        f"bonus_cap: {bonus_cap:.2f}, penalty: {credibility_penalty})"
    )
    
    return final_score


