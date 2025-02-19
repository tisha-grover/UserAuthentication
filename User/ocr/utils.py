import re

PREDEFINED_DATA = {
    "colleges": ["CHITKARA UNIVERSITY", "XYZ Institute", "LMN College"],
    "courses": ["MCA", "Mechanical Engineering", "Business Administration"]
}

def process_extracted_text(text):
    """Extract numbers (length >= 10) and match college & course from predefined data."""
    
    # Extract numbers with length >= 10
    numbers = re.findall(r'\b\d{10,}\b', text)

    # Extract college name and course if present in predefined data
    college_name = None
    course_name = None

    for college in PREDEFINED_DATA["colleges"]:
        if college.lower() in text.lower():
            college_name = college
            break  # Stop searching after finding first match

    for course in PREDEFINED_DATA["courses"]:
        if course.lower() in text.lower():
            course_name = course
            break  # Stop searching after finding first match

    return {
        "numbers": numbers,
        "college": college_name,
        "course": course_name
    }
