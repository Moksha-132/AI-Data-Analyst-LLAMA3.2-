import re

def parse_insight_markdown(markdown_text):
    """
    Parses the new Professional Insight format.
    Structure:
    ## INSIGHT TITLE: ...
    OBSERVATION: ...
    ROOT CAUSE: ...
    IMPACT: ...
    RECOMMENDATION: ...
    CONFIDENCE: ...
    """
    if not markdown_text:
        return {}
    
    # Split by '## ' to get sections
    sections = re.split(r'^##\s+', markdown_text, flags=re.MULTILINE)
    
    parsed = {}
    for section in sections:
        if not section.strip():
            continue
        
        # Split into Title and Content (first line is title)
        parts = section.split('\n', 1)
        title = parts[0].strip()
        details = parts[1].strip() if len(parts) > 1 else ""
        
        # Clean up title (remove numbering like "1. ")
        clean_title = re.sub(r'^\d+\.\s*', '', title)
        
        # Extract fields using Regex (more flexible for new/old formats)
        obs = re.search(r'(?:Observation|OBSERVATION):\s*(.*?)(?=\n[\w\(\) ]+:|$)', details, re.DOTALL | re.IGNORECASE)
        root = re.search(r'(?:Root Cause \(Why\)|ROOT CAUSE):\s*(.*?)(?=\n[\w\(\) ]+:|$)', details, re.DOTALL | re.IGNORECASE)
        imp = re.search(r'(?:Business Impact|IMPACT):\s*(.*?)(?=\n[\w\(\) ]+:|$)', details, re.DOTALL | re.IGNORECASE)
        rec = re.search(r'(?:Recommendation|RECOMMENDATION):\s*(.*?)(?=\n[\w\(\) ]+:|$)', details, re.DOTALL | re.IGNORECASE)
        conf = re.search(r'(?:Confidence|CONFIDENCE):\s*(\w+)', details, re.IGNORECASE)
        
        # Fallback logic: If no tags found, put all content into Observation
        obs_val = obs.group(1).strip() if obs else ""
        if not obs_val and details and not any([root, imp, rec]):
            obs_val = details

        parsed[clean_title] = {
            "content": details,
            "observation": obs_val,
            "root_cause": root.group(1).strip() if root else "",
            "impact": imp.group(1).strip() if imp else "",
            "recommendation": rec.group(1).strip() if rec else "",
            "confidence": conf.group(1).strip() if conf else "Medium",
            "evidence": None
        }
        
    return parsed
