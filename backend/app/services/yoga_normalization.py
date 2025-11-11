"""
Yoga Normalization and Categorization System

This module provides:
1. Canonical name normalization (combines spelling variations)
2. Proper categorization (Major Positive, Major Challenge, Standard, Minor, Subtle)
3. Deduplication logic
4. BPHS-compliant categorization rules

Created: 2025-11-10
Purpose: Fix duplicate yogas and ensure proper categorization
"""

from typing import List, Dict, Set
import re


class YogaNormalizer:
    """
    Normalizes yoga names and categories according to BPHS standards.
    Combines spelling variations and ensures proper categorization.
    """

    # Canonical name mappings (all variations map to one canonical name)
    CANONICAL_NAMES = {
        # Gaja Kesari variations
        "gaja kesari yoga": "Gaja Kesari Yoga",
        "gajakesari yoga": "Gaja Kesari Yoga",
        "gaj kesari yoga": "Gaja Kesari Yoga",
        "gajkesari yoga": "Gaja Kesari Yoga",
        "gaja kesri yoga": "Gaja Kesari Yoga",
        "gajakesri yoga": "Gaja Kesari Yoga",

        # Dhana variations
        "dhan yoga": "Dhana Yoga",
        "dhana yoga": "Dhana Yoga",
        "ripu dhan yoga": "Dhana Yoga (Ripu-Dhan Type)",
        "dhan ripu yoga": "Dhana Yoga (Ripu-Dhan Type)",
        "ripu-dhan yoga": "Dhana Yoga (Ripu-Dhan Type)",
        "dhan-ripu yoga": "Dhana Yoga (Ripu-Dhan Type)",

        # Vaapi variations (Nabhasa type)
        "vaapi yoga": "Vaapi Yoga",
        "vapi yoga": "Vaapi Yoga",
        "wapi yoga": "Vaapi Yoga",
        "vapee yoga": "Vaapi Yoga",

        # Vaapi Dharma Lords type
        "vaapi yoga (dharma lords)": "Vaapi Yoga (Dharma Lords)",
        "vapi yoga (dharma lords)": "Vaapi Yoga (Dharma Lords)",
        "vaapi dharma yoga": "Vaapi Yoga (Dharma Lords)",

        # Parijata variations
        "parijata yoga": "Parijata Yoga",
        "parijat yoga": "Parijata Yoga",
        "parijaata yoga": "Parijata Yoga",

        # Saraswati variations
        "saraswati yoga": "Saraswati Yoga",
        "sarasvati yoga": "Saraswati Yoga",
        "sarswati yoga": "Saraswati Yoga",

        # Viparita Raj Yoga variations
        "vimal yoga": "Vimala Viparita Raj Yoga",
        "vimala yoga": "Vimala Viparita Raj Yoga",
        "vimal viparita raj yoga": "Vimala Viparita Raj Yoga",
        "vimala viparita raj yoga": "Vimala Viparita Raj Yoga",
        "vimal vipreet yoga": "Vimala Viparita Raj Yoga",
        "vimal vipreet raj yoga": "Vimala Viparita Raj Yoga",

        "harsha yoga": "Harsha Viparita Raj Yoga",
        "harsh yoga": "Harsha Viparita Raj Yoga",
        "harsha viparita raj yoga": "Harsha Viparita Raj Yoga",
        "harsh viparita raj yoga": "Harsha Viparita Raj Yoga",
        "harsha vipreet yoga": "Harsha Viparita Raj Yoga",

        "sarala yoga": "Sarala Viparita Raj Yoga",
        "saral yoga": "Sarala Viparita Raj Yoga",
        "sarala viparita raj yoga": "Sarala Viparita Raj Yoga",
        "saral viparita raj yoga": "Sarala Viparita Raj Yoga",
        "sarala vipreet yoga": "Sarala Viparita Raj Yoga",

        # Kala Sarpa variations
        "kaal sarpa yoga": "Kala Sarpa Yoga",
        "kala sarpa yoga": "Kala Sarpa Yoga",
        "kaalsarpa yoga": "Kala Sarpa Yoga",
        "kaal sarp yoga": "Kala Sarpa Yoga",
        "kal sarpa yoga": "Kala Sarpa Yoga",

        # Neecha Bhanga variations
        "neecha bhanga raj yoga": "Neecha Bhanga Raj Yoga",
        "neechabhanga raj yoga": "Neecha Bhanga Raj Yoga",
        "neeche bhanga raj yoga": "Neecha Bhanga Raj Yoga",
        "neech bhang raj yoga": "Neecha Bhanga Raj Yoga",
        "neecha bhanga": "Neecha Bhanga Raj Yoga",

        # Lakshmi variations
        "lakshmi yoga": "Lakshmi Yoga",
        "laxmi yoga": "Lakshmi Yoga",
        "laksmi yoga": "Lakshmi Yoga",

        # Budhaditya variations
        "budhaditya yoga": "Budhaditya Yoga",
        "budh aditya yoga": "Budhaditya Yoga",
        "budha aditya yoga": "Budhaditya Yoga",
        "mercury sun yoga": "Budhaditya Yoga",

        # Chandra Mangala variations
        "chandra mangala yoga": "Chandra Mangala Yoga",
        "chandra mangal yoga": "Chandra Mangala Yoga",
        "chandra-mangala yoga": "Chandra Mangala Yoga",
        "moon mars yoga": "Chandra Mangala Yoga",

        # Guru Mangala variations
        "guru mangala yoga": "Guru Mangala Yoga",
        "guru mangal yoga": "Guru Mangala Yoga",
        "guru-mangala yoga": "Guru Mangala Yoga",
        "jupiter mars yoga": "Guru Mangala Yoga",

        # Pancha Mahapurusha variations
        "hamsa yoga": "Hamsa Yoga",
        "hansa yoga": "Hamsa Yoga",
        "hans yoga": "Hamsa Yoga",

        "malavya yoga": "Malavya Yoga",
        "malavia yoga": "Malavya Yoga",
        "malaviya yoga": "Malavya Yoga",

        "sasha yoga": "Sasha Yoga",
        "shasha yoga": "Sasha Yoga",
        "sasa yoga": "Sasha Yoga",

        "ruchaka yoga": "Ruchaka Yoga",
        "ruchika yoga": "Ruchaka Yoga",
        "ruchak yoga": "Ruchaka Yoga",

        "bhadra yoga": "Bhadra Yoga",
        "bhadra yog": "Bhadra Yoga",

        # Raj Yoga variations
        "raj yoga": "Raj Yoga",
        "raja yoga": "Raj Yoga",
        "rajayoga": "Raj Yoga",

        # Adhi Yoga variations
        "adhi yoga": "Adhi Yoga",
        "adi yoga": "Adhi Yoga",
        "aadhi yoga": "Adhi Yoga",

        # Chamara variations
        "chamara yoga": "Chamara Yoga",
        "chaamara yoga": "Chamara Yoga",
        "chamar yoga": "Chamara Yoga",

        # Parvata variations
        "parvata yoga": "Parvata Yoga",
        "parvat yoga": "Parvata Yoga",

        # Kahala variations
        "kahala yoga": "Kahala Yoga",
        "kahal yoga": "Kahala Yoga",

        # Amala variations
        "amala yoga": "Amala Yoga",
        "amal yoga": "Amala Yoga",
        "amla yoga": "Amala Yoga",

        # Surya yogas
        "vesi yoga": "Vesi Yoga",
        "veshi yoga": "Vesi Yoga",
        "vaisheshika yoga": "Vesi Yoga",

        "vosi yoga": "Vosi Yoga",
        "vashi yoga": "Vosi Yoga",
        "voshi yoga": "Vosi Yoga",

        "ubhayachari yoga": "Ubhayachari Yoga",
        "ubhaya yoga": "Ubhayachari Yoga",
        "obhayachari yoga": "Ubhayachari Yoga",

        # Chandra yogas
        "sunapha yoga": "Sunapha Yoga",
        "sunafa yoga": "Sunapha Yoga",
        "sunaph yoga": "Sunapha Yoga",

        "anapha yoga": "Anapha Yoga",
        "anafa yoga": "Anapha Yoga",
        "anaph yoga": "Anapha Yoga",

        "durudhura yoga": "Durudhura Yoga",
        "dhurdhura yoga": "Durudhura Yoga",
        "durudhara yoga": "Durudhura Yoga",

        "kemadruma yoga": "Kemadruma Yoga",
        "kemdruma yoga": "Kemadruma Yoga",
        "kemadruma dosha": "Kemadruma Yoga",

        # Nabhasa yogas
        "rajju yoga": "Rajju Yoga",
        "raju yoga": "Rajju Yoga",

        "musala yoga": "Musala Yoga",
        "musla yoga": "Musala Yoga",
        "musl yoga": "Musala Yoga",

        "nala yoga": "Nala Yoga",
        "nal yoga": "Nala Yoga",

        "mala yoga": "Mala Yoga",
        "maala yoga": "Mala Yoga",
        "mal yoga": "Mala Yoga",

        "sarpa yoga": "Sarpa Yoga",
        "sarp yoga": "Sarpa Yoga",

        "gada yoga": "Gada Yoga",
        "gadha yoga": "Gada Yoga",
        "gad yoga": "Gada Yoga",

        "shakata yoga": "Shakata Yoga",
        "sakata yoga": "Shakata Yoga",
        "shakta yoga": "Shakata Yoga",
        "shakat yoga": "Shakata Yoga",

        "vihaga yoga": "Vihaga Yoga",
        "vihanga yoga": "Vihaga Yoga",
        "vihag yoga": "Vihaga Yoga",

        "shrinagata yoga": "Shrinagata Yoga",
        "shringata yoga": "Shrinagata Yoga",
        "shringa yoga": "Shrinagata Yoga",

        "hala yoga": "Hala Yoga",
        "hal yoga": "Hala Yoga",

        "vajra yoga": "Vajra Yoga",
        "bajra yoga": "Vajra Yoga",

        "yava yoga": "Yava Yoga",
        "yav yoga": "Yava Yoga",

        "kamala yoga": "Kamala Yoga",
        "kamal yoga": "Kamala Yoga",

        # Dosha yogas
        "grahan yoga": "Grahan Yoga",
        "grahan dosha": "Grahan Yoga",
        "grahana yoga": "Grahan Yoga",

        "chandal yoga": "Chandal Yoga",
        "chandala yoga": "Chandal Yoga",
        "guru rahu yoga": "Chandal Yoga",

        "manglik dosha": "Manglik Dosha",
        "mangal dosha": "Manglik Dosha",
        "kuja dosha": "Manglik Dosha",
        "manglik yoga": "Manglik Dosha",

        "daridra yoga": "Daridra Yoga",
        "daridra dosha": "Daridra Yoga",
        "poverty yoga": "Daridra Yoga",

        # Sanyas yogas
        "sanyas yoga": "Sanyas Yoga",
        "sannyasa yoga": "Sanyas Yoga",
        "sanyasa yoga": "Sanyas Yoga",

        # Kubera variations
        "kubera yoga": "Kubera Yoga",
        "kuber yoga": "Kubera Yoga",
        "kuvera yoga": "Kubera Yoga",

        # Nipuna variations
        "nipuna yoga": "Nipuna Yoga",
        "nipun yoga": "Nipuna Yoga",
    }

    # Category mappings (BPHS-compliant)
    YOGA_CATEGORIES = {
        # MAJOR POSITIVE YOGAS (life-changing positive effects)
        "major_positive": {
            # Pancha Mahapurusha
            "Hamsa Yoga", "Malavya Yoga", "Sasha Yoga", "Ruchaka Yoga", "Bhadra Yoga",

            # Raj Yogas
            "Gaja Kesari Yoga", "Raj Yoga", "Lakshmi Yoga", "Saraswati Yoga",
            "Adhi Yoga", "Neecha Bhanga Raj Yoga", "Dharma Karmadhipati Yoga",
            "Parijata Yoga",  # Lagna lord strong in Kendra/Trikona

            # Viparita Raj Yogas
            "Harsha Viparita Raj Yoga", "Sarala Viparita Raj Yoga", "Vimala Viparita Raj Yoga",

            # Dhana Yogas (MAJOR because wealth-creating)
            "Dhana Yoga", "Dhana Yoga (Ripu-Dhan Type)", "Kubera Yoga", "Vaapi Yoga",
            "Vaapi Yoga (Dharma Lords)",  # 5th-9th lord relationship

            # Wealth combinations
            "Chandra Mangala Yoga", "Guru Mangala Yoga", "Parvata Yoga", "Kahala Yoga",
            "Amala Yoga", "Chamara Yoga",

            # Special major yogas
            "Budhaditya Yoga", "Kalpa Vriksha Yoga", "Akhanda Samrajya Yoga",
        },

        # MAJOR CHALLENGE YOGAS (significant obstacles/malefic effects)
        "major_challenge": {
            # Kemadruma and poverty
            "Kemadruma Yoga", "Daridra Yoga",

            # Doshas
            "Grahan Yoga", "Chandal Yoga", "Manglik Dosha", "Pitra Dosha",
            "Kala Sarpa Yoga",

            # Kala Sarpa types (all major challenges)
            "Ananta Kala Sarpa Yoga", "Kulika Kala Sarpa Yoga", "Vasuki Kala Sarpa Yoga",
            "Shankhapala Kala Sarpa Yoga", "Padma Kala Sarpa Yoga", "Mahapadma Kala Sarpa Yoga",
            "Takshaka Kala Sarpa Yoga", "Karkotak Kala Sarpa Yoga", "Shankhachud Kala Sarpa Yoga",
            "Ghatak Kala Sarpa Yoga", "Vishdhar Kala Sarpa Yoga", "Sheshnag Kala Sarpa Yoga",

            # Arishta yogas
            "Balarishta Yoga", "Kroora Yoga", "Vish Yoga",
        },

        # STANDARD YOGAS (moderate positive or negative effects)
        "standard": {
            # Surya yogas
            "Vesi Yoga", "Vosi Yoga", "Ubhayachari Yoga",

            # Chandra yogas
            "Sunapha Yoga", "Anapha Yoga", "Durudhura Yoga",

            # Nabhasa Ashraya
            "Rajju Yoga", "Musala Yoga", "Nala Yoga", "Mala Yoga",

            # Nabhasa Akriti (most)
            "Gada Yoga", "Shakata Yoga", "Vihaga Yoga", "Shrinagata Yoga",
            "Hala Yoga", "Vajra Yoga", "Yava Yoga", "Kamala Yoga",

            # Planetary combinations
            "Nipuna Yoga", "Shukra Budh Yoga", "Guru Shukra Yoga",

            # Sanyas
            "Sanyas Yoga",
        },

        # MINOR YOGAS (subtle effects on personality/life)
        "minor": {
            # Nabhasa Dala
            "Sarpa Yoga (Nabhasa)",

            # Nabhasa Sankhya
            "Vallaki Yoga", "Dama Yoga", "Pasha Yoga", "Kedara Yoga", "Shula Yoga", "Yuga Yoga",

            # Nitya yogas (27)
            "Vishkambha Yoga", "Preeti Yoga", "Ayushman Yoga", "Saubhagya Yoga",
            "Shobhana Yoga", "Atiganda Yoga", "Sukarma Yoga", "Dhriti Yoga",
            "Shoola Yoga", "Ganda Yoga", "Vriddhi Yoga", "Dhruva Yoga",
            "Vyaghata Yoga", "Harshana Yoga", "Vajra Yoga (Nitya)", "Siddhi Yoga",
            "Vyatipata Yoga", "Variyana Yoga", "Parigha Yoga", "Shiva Yoga",
            "Siddha Yoga", "Sadhya Yoga", "Shubha Yoga", "Shukla Yoga",
            "Brahma Yoga", "Indra Yoga", "Vaidhriti Yoga",
        },

        # SUBTLE INFLUENCES (very minor effects)
        "subtle": {
            # Varga-specific
            "Vargottama Yoga", "Pushkara Navamsa Yoga",

            # Degree-specific
            "Atma Karaka Yoga", "Amatyakaraka Yoga",

            # Minor strength
            "Uccha Yoga", "Swa Graha Yoga", "Moolatrikona Yoga",

            # Rare with subtle effects
            "Amrita Yoga", "Trimsamsa Yoga", "Khavedamsa Yoga",
        },
    }

    def __init__(self):
        """Initialize the normalizer with reverse lookup maps."""
        # Create reverse category lookup
        self.yoga_to_category = {}
        for category, yogas in self.YOGA_CATEGORIES.items():
            for yoga in yogas:
                self.yoga_to_category[yoga.lower()] = category

    def normalize_name(self, yoga_name: str) -> str:
        """
        Normalize a yoga name to its canonical form.

        Args:
            yoga_name: Raw yoga name (any spelling variation)

        Returns:
            Canonical yoga name
        """
        # Convert to lowercase for matching
        name_lower = yoga_name.lower().strip()

        # Remove extra spaces
        name_lower = re.sub(r'\s+', ' ', name_lower)

        # Check if we have a canonical mapping
        if name_lower in self.CANONICAL_NAMES:
            return self.CANONICAL_NAMES[name_lower]

        # If no mapping found, return title-cased original
        return yoga_name.strip()

    def get_category(self, yoga_name: str) -> str:
        """
        Get the proper category for a yoga.

        Args:
            yoga_name: Yoga name (canonical or variation)

        Returns:
            Category: "major_positive", "major_challenge", "standard", "minor", or "subtle"
        """
        # Normalize first
        canonical_name = self.normalize_name(yoga_name)

        # Look up category
        category = self.yoga_to_category.get(canonical_name.lower())

        # Default to standard if not found
        return category if category else "standard"

    def get_importance(self, category: str) -> str:
        """
        Convert category to importance level.

        Args:
            category: Category name

        Returns:
            Importance: "major", "moderate", "minor"
        """
        if category == "major_positive":
            return "major"
        elif category == "major_challenge":
            return "major"
        elif category == "standard":
            return "moderate"
        elif category == "minor":
            return "minor"
        elif category == "subtle":
            return "minor"
        return "moderate"

    def get_impact(self, category: str) -> str:
        """
        Get impact type from category.

        Args:
            category: Category name

        Returns:
            Impact: "positive", "negative", or "neutral"
        """
        if category == "major_positive":
            return "positive"
        elif category == "major_challenge":
            return "negative"
        return "neutral"

    def deduplicate_yogas(self, yogas: List[Dict]) -> List[Dict]:
        """
        Remove duplicate yogas by normalizing names.

        Args:
            yogas: List of yoga dictionaries

        Returns:
            Deduplicated list with canonical names and proper categories
        """
        seen = {}
        deduplicated = []

        for yoga in yogas:
            # Normalize the name
            canonical_name = self.normalize_name(yoga["name"])

            # Check if we've seen this canonical name
            if canonical_name.lower() not in seen:
                # Get proper category
                category = self.get_category(canonical_name)

                # Update yoga dictionary
                yoga["name"] = canonical_name
                yoga["importance"] = self.get_importance(category)
                yoga["impact"] = self.get_impact(category)
                yoga["category_type"] = category  # Add for reporting

                # Mark as seen and add to result
                seen[canonical_name.lower()] = True
                deduplicated.append(yoga)

        return deduplicated

    def generate_deduplication_report(self, original_yogas: List[Dict], deduplicated_yogas: List[Dict]) -> Dict:
        """
        Generate a report showing what was combined.

        Args:
            original_yogas: Original yoga list (with duplicates)
            deduplicated_yogas: Deduplicated yoga list

        Returns:
            Report dictionary with statistics and combined yogas
        """
        # Group original yogas by canonical name
        canonical_groups = {}
        for yoga in original_yogas:
            canonical = self.normalize_name(yoga["name"])
            if canonical not in canonical_groups:
                canonical_groups[canonical] = []
            canonical_groups[canonical].append(yoga["name"])

        # Find which ones were combined (multiple variations)
        combined = {}
        for canonical, variations in canonical_groups.items():
            if len(variations) > 1:
                combined[canonical] = list(set(variations))  # Remove exact duplicates within variations

        # Category counts
        category_counts = {}
        for yoga in deduplicated_yogas:
            cat = yoga.get("category_type", "unknown")
            category_counts[cat] = category_counts.get(cat, 0) + 1

        return {
            "original_count": len(original_yogas),
            "deduplicated_count": len(deduplicated_yogas),
            "removed_duplicates": len(original_yogas) - len(deduplicated_yogas),
            "combined_yogas": combined,
            "category_counts": category_counts,
        }


# Global instance for easy import
normalizer = YogaNormalizer()


# Convenience functions
def normalize_yoga_name(name: str) -> str:
    """Normalize a yoga name to canonical form."""
    return normalizer.normalize_name(name)


def get_yoga_category(name: str) -> str:
    """Get the category for a yoga."""
    return normalizer.get_category(name)


def deduplicate_yogas(yogas: List[Dict]) -> List[Dict]:
    """Remove duplicate yogas and apply proper categorization."""
    return normalizer.deduplicate_yogas(yogas)


def generate_deduplication_report(original: List[Dict], deduplicated: List[Dict]) -> Dict:
    """Generate report showing what was combined."""
    return normalizer.generate_deduplication_report(original, deduplicated)
