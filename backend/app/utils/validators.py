import re

def validate_phone(phone: str) -> bool:
    """Validate Indian phone number format."""
    pattern = r'^(\+91|91)?[6-9]\d{9}$'
    return bool(re.match(pattern, phone.replace(' ', '').replace('-', '')))

def validate_email(email: str) -> bool:
    """Basic email validation."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def sanitize_text(text: str) -> str:
    """Remove potentially dangerous HTML/script content."""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Remove script content
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
    return text.strip()

def validate_password_strength(password: str) -> tuple[bool, str]:
    """Validate password meets strength requirements."""
    if len(password) < 8:
        return False, 'Password must be at least 8 characters'
    if not re.search(r'[A-Z]', password):
        return False, 'Password must contain at least one uppercase letter'
    if not re.search(r'[a-z]', password):
        return False, 'Password must contain at least one lowercase letter'
    if not re.search(r'\d', password):
        return False, 'Password must contain at least one digit'
    return True, 'Password is strong'
