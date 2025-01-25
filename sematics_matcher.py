from difflib import SequenceMatcher
import re
from thefuzz import fuzz
import spacy


class SemanticMatcher:
    def __init__(self):
        # Load English language model for NLP
        self.nlp = spacy.load("en_core_web_sm")

        # Define base patterns we want to match
        self.base_patterns = [
            "free water and electricity",
            "water and electricity included",
            "electricity and water included",
            "water electricity included",
            "utilities included",
            "bills included",
            "all bills included",
            "including utilities",
            "including water electricity",
            "water and electricity are free",
            "free utilities",
        ]

        # Key terms that should be present
        self.key_terms = ["water", "electricity", "utilities", "bills"]
        self.inclusion_terms = ["free", "included", "including", "covered"]

    def preprocess_text(self, text):
        # Convert to lowercase and remove special characters
        text = text.lower()
        text = re.sub(r"[^\w\s]", " ", text)
        return text

    def fuzzy_match(self, text, pattern, threshold=80):
        # Use fuzzy string matching to handle spelling errors
        ratio = fuzz.partial_ratio(text, pattern)
        return ratio >= threshold

    def semantic_similarity(self, text):
        # Process the text with spaCy
        doc = self.nlp(text)

        # Look for semantic relationships between key terms
        for sent in doc.sents:
            # Check if sentence contains our key terms
            has_utility = any(
                term in sent.text.lower() for term in self.key_terms
            )
            has_inclusion = any(
                term in sent.text.lower() for term in self.inclusion_terms
            )

            if has_utility and has_inclusion:
                return True

        return False

    def check_match(self, text):
        text = self.preprocess_text(text)

        # Method 1: Direct pattern matching
        for pattern in self.base_patterns:
            if pattern in text:
                return True, "Direct match"

        # Method 2: Fuzzy matching for spelling errors
        for pattern in self.base_patterns:
            if self.fuzzy_match(text, pattern):
                return True, "Fuzzy match"

        # Method 3: Semantic analysis
        if self.semantic_similarity(text):
            return True, "Semantic match"

        return False, "No match"


# Usage example
def analyze_property_description(description):
    matcher = SemanticMatcher()
    is_match, match_type = matcher.check_match(description)

    return {"has_free_utilities": is_match, "match_type": match_type}


def test_sematics_match():
    # Test cases
    test_descriptions = [
        "Water Electricity and Maintenance are included.",
        "All bills including water & electricity covered in rent",
        "Free utilties provided with the apartment",
        "Wat3r and electrcity included in the price",  # Misspelled
        "Including all utility bills in the rent",
        "All utilities covered",
        "Bills are inclusive",
        "No extra charges for water or electricity",
        "Utilities to be paid by tenant",  # Should not match
        "<title><br>Water Electricity and Maintenance are included.<br><title>",
    ]
    for desc in test_descriptions:
        result = analyze_property_description(desc)
        print(f"\nText: {desc}")
        print(f"Result: {result}")


if __name__ == "__main__":
    test_sematics_match()
