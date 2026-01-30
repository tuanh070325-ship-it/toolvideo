from typing import Dict, Any, Optional

CHARACTER_PROFILES = {
    "grandparent_and_child": {
        "name": "Bà và cháu gái",
        "base_prompt": (
            "An elderly Vietnamese grandmother with gray hair in a bun, wearing a traditional brown 'áo bà ba', "
            "and a small 5-year-old girl with pigtails wearing a colorful dress."
        ),
        "style_hint": "Warm lighting, 3D animation style, Pixar-like facial expressions."
    },
    "entrepreneur": {
        "name": "Doanh nhân trẻ",
        "base_prompt": (
            "A successful young Vietnamese man in his 30s, wearing a sharp navy blue suit, "
            "modern glasses, confident smile, clean-cut hair."
        ),
        "style_hint": "Cinematic office lighting, professional 4k photorealistic style."
    },
    "student": {
        "name": "Sinh viên năng động",
        "base_prompt": (
            "A cheerful female university student with long black hair, wearing a white t-shirt and jeans, "
            "carrying a backpack, holding a phone."
        ),
        "style_hint": "Daylight, bright colors, anime-inspired semi-realistic style."
    },
    "chef": {
        "name": "Đầu bếp chuyên nghiệp",
        "base_prompt": (
            "A male chef with a white chef's hat and apron, friendly face, "
            "skillfully handling kitchen utensils."
        ),
        "style_hint": "Studio kitchen lighting, high contrast, vibrant food colors."
    }
}

def get_character_base_prompt(profile_key: str) -> Optional[str]:
    """Get the base descriptive prompt for a character profile"""
    profile = CHARACTER_PROFILES.get(profile_key)
    if profile:
        return f"{profile['base_prompt']} {profile['style_hint']}"
    return None

def list_profiles() -> Dict[str, str]:
    """List available character profiles with their names"""
    return {k: v['name'] for k, v in CHARACTER_PROFILES.items()}
