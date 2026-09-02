import re
from typing import Dict, List, Optional

class TextExtractor:
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        entities = {
            'affected_groups': [],
            'locations': [],
            'infrastructure': [],
            'urgency_indicators': [],
            'quantities': []
        }
        
        # Affected groups
        group_patterns = [r'\bwomen\b', r'\bchildren\b', r'\bfarmers\b', r'\bstudents\b', r'\bvillagers\b', r'\bfamilies\b', r'\bpeople\b']
        for pattern in group_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                entities['affected_groups'].extend(list(set(m.lower() for m in matches)))
                
        # Locations (Capitalized words, simplified)
        loc_matches = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        entities['locations'] = list(set(loc_matches))
        
        # Infrastructure
        infra_patterns = [r'\bhandpump\b', r'\bschool building\b', r'\bbridge\b', r'\broad\b', r'\bhospital\b', r'\bpipeline\b']
        for pattern in infra_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                entities['infrastructure'].extend(list(set(m.lower() for m in matches)))
                
        # Urgency indicators
        urgency_patterns = [r'\burgent\b', r'\bemergency\b', r'\bcritical\b', r'\bimmediate\b', r'\bsevere\b']
        for pattern in urgency_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                entities['urgency_indicators'].extend(list(set(m.lower() for m in matches)))
                
        # Quantities
        qty_matches = re.findall(r'\b\d+\s+(?:families|villages|people|households|students)\b', text, re.IGNORECASE)
        entities['quantities'] = list(set(qty_matches))
        
        return entities

    def estimate_affected_population(self, text: str) -> Optional[int]:
        total = 0
        found = False
        
        patterns = {
            r'(\d+)\s+families': 5,
            r'(\d+)\s+people': 1,
            r'(\d+)\s+villagers': 1,
            r'(\d+)\s+households': 5,
            r'(\d+)\s+villages': 500,
            r'(\d+)\s+students': 1
        }
        
        for pattern, multiplier in patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                total += int(match) * multiplier
                found = True
                
        return total if found else None

    def count_urgency_indicators(self, text: str) -> int:
        urgency_patterns = [r'\burgent\b', r'\bemergency\b', r'\bcritical\b', r'\bimmediate\b', r'\bsevere\b']
        count = 0
        for pattern in urgency_patterns:
            count += len(re.findall(pattern, text, re.IGNORECASE))
        return count

text_extractor = TextExtractor()
