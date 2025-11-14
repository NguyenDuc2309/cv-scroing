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


LEVEL_WEIGHTS: Dict[str, Dict[str, float]] = {
    # Intern: tập trung education, skills, format; bonus chỉ cộng nhẹ
    "intern": {
        "format": 15,
        "experience": 15,
        "skills": 20,
        "soft_skills": 15,
        "education": 20,
        # field_match hiện chỉ dùng để tham chiếu, không ảnh hưởng mạnh
        "field_match": 0,
        "portfolio": 5,
        "certificates": 3,
        "awards": 3,
        "scholarships": 2,
        "side_projects": 1,
        "community": 1,
    },
    # Fresher: bắt đầu tăng experience, portfolio, giảm education
    "fresher": {
        "format": 10,
        "experience": 25,
        "skills": 20,
        "soft_skills": 10,
        "education": 15,
        "field_match": 0,
        "portfolio": 8,
        "certificates": 5,
        "awards": 3,
        "scholarships": 2,
        "side_projects": 1,
        "community": 1,
    },
    # Junior: kinh nghiệm và skills chiếm trọng số lớn
    "junior": {
        "format": 8,
        "experience": 35,
        "skills": 25,
        "soft_skills": 15,
        "education": 5,
        "field_match": 0,
        "portfolio": 7,
        "certificates": 3,
        "awards": 0.5,
        "scholarships": 0.5,
        "side_projects": 0.5,
        "community": 0.5,
    },
    # Mid: kinh nghiệm, skills, soft_skills là chính; education/bonus gần như phụ
    "mid": {
        "format": 5,
        "experience": 45,
        "skills": 25,
        "soft_skills": 15,
        "education": 3,
        "field_match": 0,
        "portfolio": 5,
        "certificates": 2,
        "awards": 0,
        "scholarships": 0,
        "side_projects": 0,
        "community": 0,
    },
    # Senior: impact/experience + skills là chủ đạo
    "senior": {
        "format": 5,
        "experience": 60,
        "skills": 25,
        "soft_skills": 10,
        "education": 0,
        "field_match": 0,
        "portfolio": 0,
        "certificates": 0,
        "awards": 0,
        "scholarships": 0,
        "side_projects": 0,
        "community": 0,
    },
}


def _normalize_level(level: str) -> str:
    l = (level or "").strip().lower()
    if l in LEVEL_WEIGHTS:
        return l
    # Fallback: map unknown to nearest reasonable bucket
    if l in {"internship", "intern-level"}:
        return "intern"
    if l in {"jr", "junior-level"}:
        return "junior"
    if l in {"middle", "mid-level"}:
        return "mid"
    if l in {"sr", "senior-level", "lead"}:
        return "senior"
    return "junior"


def calculate_overall_score(level: str, core_scores: Dict[str, Dict[str, Any]], bonus_scores: Dict[str, Dict[str, Any]]) -> int:
    """
    Tính overall_score chính xác dựa trên level và bảng trọng số core/bonus.

    - Core criteria: dùng score thực tế (hoặc 0 nếu thiếu).
    - Bonus criteria: nếu thiếu thông tin thì dùng NEUTRAL_BONUS_SCORE (không phạt nặng).
    
    Returns:
        int: Điểm tổng thể (0-100) được tính toán chính xác theo trọng số.
    """
    norm_level = _normalize_level(level)
    weights = LEVEL_WEIGHTS.get(norm_level, LEVEL_WEIGHTS["junior"])

    total_weight = 0.0
    weighted_sum = 0.0

    all_scores = {}
    all_scores.update(core_scores)
    all_scores.update(bonus_scores)

    missing_core = []
    missing_bonus = []

    for key, weight in weights.items():
        if weight <= 0:
            continue

        comp = all_scores.get(key)
        if comp and isinstance(comp, dict):
            try:
                score_val = int(comp.get("score", 0))
            except (TypeError, ValueError):
                score_val = 0
                logger.warning(f"Invalid score value for {key}, using 0")
        else:
            # Thiếu dữ liệu: core -> 0, bonus -> neutral
            if key in BONUS_KEYS:
                score_val = NEUTRAL_BONUS_SCORE
                missing_bonus.append(key)
            else:
                score_val = 0
                missing_core.append(key)

        score_val = max(0, min(100, score_val))

        weighted_sum += score_val * weight
        total_weight += weight

    if total_weight <= 0:
        logger.error(f"Total weight is 0 for level {norm_level}, returning 0")
        return 0

    overall = round(weighted_sum / total_weight)
    final_score = max(0, min(100, overall))
    
    if missing_core:
        logger.warning(f"Missing core criteria: {missing_core}")
    if missing_bonus:
        logger.debug(f"Missing bonus criteria (using neutral score): {missing_bonus}")
    
    logger.info(f"Calculated overall_score: {final_score} for level: {norm_level} (weighted_sum: {weighted_sum:.2f}, total_weight: {total_weight:.2f})")
    
    return final_score


