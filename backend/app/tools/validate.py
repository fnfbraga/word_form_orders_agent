"""Tool for validating country names."""

import pycountry


# Common country name aliases
COUNTRY_ALIASES = {
    "usa": "United States",
    "us": "United States",
    "u.s.": "United States",
    "u.s.a.": "United States",
    "america": "United States",
    "uk": "United Kingdom",
    "u.k.": "United Kingdom",
    "britain": "United Kingdom",
    "great britain": "United Kingdom",
    "england": "United Kingdom",
    "deutschland": "Germany",
    "holland": "Netherlands",
    "россия": "Russia",
    "中国": "China",
    "日本": "Japan",
    "한국": "Korea, Republic of",
    "south korea": "Korea, Republic of",
    "north korea": "Korea, Democratic People's Republic of",
}


def validate_country(country_name: str) -> dict:
    """
    Validate if the provided string is a valid country name.
    
    Args:
        country_name: The country name to validate
        
    Returns:
        Dictionary with validation result and suggested correction if invalid
    """
    if not country_name or not country_name.strip():
        return {
            "is_valid": False,
            "message": "Country name cannot be empty.",
            "suggestion": None
        }
    
    country_name = country_name.strip()
    normalized = country_name.lower()
    
    # Check aliases first
    if normalized in COUNTRY_ALIASES:
        return {
            "is_valid": True,
            "normalized_name": COUNTRY_ALIASES[normalized],
            "message": f"Valid country: {COUNTRY_ALIASES[normalized]}"
        }
    
    # Try exact match with pycountry
    try:
        country = pycountry.countries.get(name=country_name)
        if country:
            return {
                "is_valid": True,
                "normalized_name": country.name,
                "message": f"Valid country: {country.name}"
            }
    except (KeyError, LookupError):
        pass
    
    # Try fuzzy search
    try:
        results = pycountry.countries.search_fuzzy(country_name)
        if results:
            best_match = results[0]
            # If close enough match, accept it
            if normalized in best_match.name.lower() or best_match.name.lower() in normalized:
                return {
                    "is_valid": True,
                    "normalized_name": best_match.name,
                    "message": f"Valid country: {best_match.name}"
                }
            else:
                return {
                    "is_valid": False,
                    "message": f"'{country_name}' is not a valid country.",
                    "suggestion": best_match.name
                }
    except LookupError:
        pass
    
    # Check if it's an alpha-2 or alpha-3 code
    try:
        country = pycountry.countries.get(alpha_2=country_name.upper())
        if country:
            return {
                "is_valid": True,
                "normalized_name": country.name,
                "message": f"Valid country: {country.name}"
            }
    except (KeyError, LookupError):
        pass
    
    try:
        country = pycountry.countries.get(alpha_3=country_name.upper())
        if country:
            return {
                "is_valid": True,
                "normalized_name": country.name,
                "message": f"Valid country: {country.name}"
            }
    except (KeyError, LookupError):
        pass
    
    # No valid country found
    return {
        "is_valid": False,
        "message": f"'{country_name}' is not a valid country for shipping. Please provide a valid country name.",
        "suggestion": None
    }


