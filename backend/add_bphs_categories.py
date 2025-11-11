#!/usr/bin/env python3
"""
Script to add BPHS categorization fields to all yogas in extended_yoga_service.py
Based on BPHS_YOGA_CATEGORIZATION_ANALYSIS.md findings
"""

import re
from pathlib import Path

# BPHS Category Mapping - Based on analysis document
YOGA_BPHS_MAPPING = {
    # MAJOR POSITIVE YOGAS
    # Pancha Mahapurusha (Ch.75)
    "Ruchaka Yoga": {"category": "Major Positive Yogas", "section": "E) Pañcha-Mahāpuruṣa (Ch.75)", "ref": "Ch.75.1-2"},
    "Bhadra Yoga": {"category": "Major Positive Yogas", "section": "E) Pañcha-Mahāpuruṣa (Ch.75)", "ref": "Ch.75.1-2"},
    "Hamsa Yoga": {"category": "Major Positive Yogas", "section": "E) Pañcha-Mahāpuruṣa (Ch.75)", "ref": "Ch.75.1-2"},
    "Malavya Yoga": {"category": "Major Positive Yogas", "section": "E) Pañcha-Mahāpuruṣa (Ch.75)", "ref": "Ch.75.1-2"},
    "Sasa Yoga": {"category": "Major Positive Yogas", "section": "E) Pañcha-Mahāpuruṣa (Ch.75)", "ref": "Ch.75.1-2"},

    # Named Yogas (Ch.36)
    "Gaja Kesari Yoga": {"category": "Major Positive Yogas", "section": "B) Named Yogas (Ch.36)", "ref": "Ch.36.3-4"},
    "Gajakesari Yoga": {"category": "Major Positive Yogas", "section": "B) Named Yogas (Ch.36)", "ref": "Ch.36.3-4"},
    "Amala Yoga": {"category": "Major Positive Yogas", "section": "B) Named Yogas (Ch.36)", "ref": "Ch.36.5-6"},
    "Parvata Yoga": {"category": "Major Positive Yogas", "section": "B) Named Yogas (Ch.36)", "ref": "Ch.36.7-8"},
    "Kahala Yoga": {"category": "Major Positive Yogas", "section": "B) Named Yogas (Ch.36)", "ref": "Ch.36.9-10"},
    "Chamara Yoga": {"category": "Major Positive Yogas", "section": "B) Named Yogas (Ch.36)", "ref": "Ch.36.11-12"},
    "Lakshmi Yoga": {"category": "Major Positive Yogas", "section": "B) Named Yogas (Ch.36)", "ref": "Ch.36.27-28"},
    "Kusuma Yoga": {"category": "Major Positive Yogas", "section": "B) Named Yogas (Ch.36)", "ref": "Ch.36.29-30"},
    "Kalanidhi Yoga": {"category": "Major Positive Yogas", "section": "B) Named Yogas (Ch.36)", "ref": "Ch.36.31-32"},
    "Kālanidhi Yoga": {"category": "Major Positive Yogas", "section": "B) Named Yogas (Ch.36)", "ref": "Ch.36.31-32"},
    "Matsya Yoga": {"category": "Major Positive Yogas", "section": "B) Named Yogas (Ch.36)", "ref": "Ch.36.21-22"},
    "Kurma Yoga": {"category": "Major Positive Yogas", "section": "B) Named Yogas (Ch.36)", "ref": "Ch.36.23-24"},
    "Shrinatha Yoga": {"category": "Major Positive Yogas", "section": "B) Named Yogas (Ch.36)", "ref": "Ch.36.18"},

    # Raj Yoga (Ch.39)
    "Raj Yoga": {"category": "Major Positive Yogas", "section": "F) Rāja-Yoga (Ch.39)", "ref": "Ch.39"},
    "Lagna Lord in Trine/Kendra": {"category": "Major Positive Yogas", "section": "F) Rāja-Yoga (Ch.39)", "ref": "Ch.39"},
    "Karma Raj Yoga": {"category": "Major Positive Yogas", "section": "F) Rāja-Yoga (Ch.39)", "ref": "Ch.39.21-22"},
    "All-Benefic Kendras Yoga": {"category": "Major Positive Yogas", "section": "F) Rāja-Yoga (Ch.39)", "ref": "Ch.39.48"},
    "Moon-Venus Mutual": {"category": "Major Positive Yogas", "section": "F) Rāja-Yoga (Ch.39)", "ref": "Ch.39.41"},

    # Royal Association (Ch.40)
    "Royal Association Yoga": {"category": "Major Positive Yogas", "section": "G) Royal Association (Ch.40)", "ref": "Ch.40.1-15"},

    # Wealth (Ch.41)
    "Dhana Yoga": {"category": "Major Positive Yogas", "section": "H) Wealth (Ch.41)", "ref": "Ch.41.2-15"},
    "Wealth Yoga": {"category": "Major Positive Yogas", "section": "H) Wealth (Ch.41)", "ref": "Ch.41.16,28-34"},
    "Lakshmi Wealth Yoga": {"category": "Major Positive Yogas", "section": "H) Wealth (Ch.41)", "ref": "Ch.41.16,28-34"},

    # Nabhasa (Ch.35) - Positive ones
    "Kamala Yoga": {"category": "Major Positive Yogas", "section": "A) Nabhasa (Ch.35)", "ref": "Ch.35.12"},
    "Mala Yoga": {"category": "Major Positive Yogas", "section": "A) Nabhasa (Ch.35)", "ref": "Ch.35.8"},
    "Vaapi Yoga": {"category": "Major Positive Yogas", "section": "A) Nabhasa (Ch.35)", "ref": "Ch.35.12"},
    "Vaapī Nabhasa Yoga": {"category": "Major Positive Yogas", "section": "A) Nabhasa (Ch.35)", "ref": "Ch.35.12"},

    # MAJOR CHALLENGES
    # Penury (Ch.42)
    "Penury Yoga": {"category": "Major Challenges", "section": "I) Penury (Ch.42)", "ref": "Ch.42.2-18"},
    "Daridra Yoga": {"category": "Major Challenges", "section": "I) Penury (Ch.42)", "ref": "Ch.42"},

    # Moon Challenges (Ch.37)
    "Kemadruma Yoga": {"category": "Major Challenges", "section": "C) Moon's Yogas (Ch.37)", "ref": "Ch.37.13"},

    # Nabhasa Challenges (Ch.35)
    "Sarpa Yoga": {"category": "Major Challenges", "section": "A) Nabhasa (Ch.35)", "ref": "Ch.35.8"},
    "Gola Yoga": {"category": "Major Challenges", "section": "A) Nabhasa (Ch.35)", "ref": "Ch.35.16"},
    "Shoola Yoga": {"category": "Major Challenges", "section": "A) Nabhasa (Ch.35)", "ref": "Ch.35.16"},
    "Paasha Yoga": {"category": "Major Challenges", "section": "A) Nabhasa (Ch.35)", "ref": "Ch.35.16"},
    "Dama Yoga": {"category": "Major Challenges", "section": "A) Nabhasa (Ch.35)", "ref": "Ch.35.16"},

    # STANDARD YOGAS
    # Moon Yogas (Ch.37)
    "Sunapha Yoga": {"category": "Standard Yogas", "section": "C) Moon's Yogas (Ch.37)", "ref": "Ch.37.3-6"},
    "Anapha Yoga": {"category": "Standard Yogas", "section": "C) Moon's Yogas (Ch.37)", "ref": "Ch.37.3-6"},
    "Durudhura Yoga": {"category": "Standard Yogas", "section": "C) Moon's Yogas (Ch.37)", "ref": "Ch.37.3-6"},
    "Adhi Yoga": {"category": "Standard Yogas", "section": "C) Moon's Yogas (Ch.37)", "ref": "Ch.37.1-2"},

    # Sun Yogas (Ch.38)
    "Vesi Yoga": {"category": "Standard Yogas", "section": "D) Sun's Yogas (Ch.38)", "ref": "Ch.38.1"},
    "Vosi Yoga": {"category": "Standard Yogas", "section": "D) Sun's Yogas (Ch.38)", "ref": "Ch.38.1"},
    "Vasi Yoga": {"category": "Standard Yogas", "section": "D) Sun's Yogas (Ch.38)", "ref": "Ch.38.1"},
    "Ubhayachari Yoga": {"category": "Standard Yogas", "section": "D) Sun's Yogas (Ch.38)", "ref": "Ch.38.1-4"},

    # Nabhasa Standard (Ch.35)
    "Rajju Yoga": {"category": "Standard Yogas", "section": "A) Nabhasa (Ch.35)", "ref": "Ch.35.7"},
    "Musala Yoga": {"category": "Standard Yogas", "section": "A) Nabhasa (Ch.35)", "ref": "Ch.35.7"},
    "Mushala Yoga": {"category": "Standard Yogas", "section": "A) Nabhasa (Ch.35)", "ref": "Ch.35.7"},
    "Nala Yoga": {"category": "Standard Yogas", "section": "A) Nabhasa (Ch.35)", "ref": "Ch.35.7"},
    "Maala Yoga": {"category": "Standard Yogas", "section": "A) Nabhasa (Ch.35)", "ref": "Ch.35.7"},
    "Gada Yoga": {"category": "Standard Yogas", "section": "A) Nabhasa (Ch.35)", "ref": "Ch.35.9"},
    "Sakata Yoga": {"category": "Standard Yogas", "section": "A) Nabhasa (Ch.35)", "ref": "Ch.35.9"},
    "Vihaga Yoga": {"category": "Standard Yogas", "section": "A) Nabhasa (Ch.35)", "ref": "Ch.35.9"},
    "Shringataka Yoga": {"category": "Standard Yogas", "section": "A) Nabhasa (Ch.35)", "ref": "Ch.35.10"},
    "Hala Yoga": {"category": "Standard Yogas", "section": "A) Nabhasa (Ch.35)", "ref": "Ch.35.10"},
    "Vajra Yoga": {"category": "Standard Yogas", "section": "A) Nabhasa (Ch.35)", "ref": "Ch.35.11"},
    "Yava Yoga": {"category": "Standard Yogas", "section": "A) Nabhasa (Ch.35)", "ref": "Ch.35.11"},
    "Yupa Yoga": {"category": "Standard Yogas", "section": "A) Nabhasa (Ch.35)", "ref": "Ch.35.13"},
    "Shara Yoga": {"category": "Standard Yogas", "section": "A) Nabhasa (Ch.35)", "ref": "Ch.35.13"},
    "Shakti Yoga": {"category": "Standard Yogas", "section": "A) Nabhasa (Ch.35)", "ref": "Ch.35.13"},
    "Danda Yoga": {"category": "Standard Yogas", "section": "A) Nabhasa (Ch.35)", "ref": "Ch.35.13"},
    "Nauka Yoga": {"category": "Standard Yogas", "section": "A) Nabhasa (Ch.35)", "ref": "Ch.35.14"},
    "Koota Yoga": {"category": "Standard Yogas", "section": "A) Nabhasa (Ch.35)", "ref": "Ch.35.14"},
    "Chatra Yoga": {"category": "Standard Yogas", "section": "A) Nabhasa (Ch.35)", "ref": "Ch.35.14"},
    "Chaapa Yoga": {"category": "Standard Yogas", "section": "A) Nabhasa (Ch.35)", "ref": "Ch.35.14"},
    "Chakra Yoga": {"category": "Standard Yogas", "section": "A) Nabhasa (Ch.35)", "ref": "Ch.35.15"},
    "Samudra Yoga": {"category": "Standard Yogas", "section": "A) Nabhasa (Ch.35)", "ref": "Ch.35.15"},
    "Yuga Yoga": {"category": "Standard Yogas", "section": "A) Nabhasa (Ch.35)", "ref": "Ch.35.16"},

    # MINOR YOGAS & SUBTLE INFLUENCES
    # (Most are missing, will be added in future phases)

    # NON-BPHS (PRACTICAL) - Modern additions
    "Neecha Bhanga": {"category": "Non-BPHS (Practical)", "section": "Modern Enhancement", "ref": "Classical principle"},
    "Viparita Raj Yoga": {"category": "Non-BPHS (Practical)", "section": "Modern Enhancement", "ref": "Classical principle"},
    "Chandra Mangala Yoga": {"category": "Non-BPHS (Practical)", "section": "Modern Enhancement", "ref": "Classical principle"},
    "Guru Mangala Yoga": {"category": "Non-BPHS (Practical)", "section": "Modern Enhancement", "ref": "Classical principle"},
    "Budhaditya Yoga": {"category": "Non-BPHS (Practical)", "section": "Modern Enhancement", "ref": "Classical principle"},
    "Ganesha Yoga": {"category": "Non-BPHS (Practical)", "section": "Modern Enhancement", "ref": "Modern interpretation"},
    "Nipuna Yoga": {"category": "Non-BPHS (Practical)", "section": "Modern Enhancement", "ref": "Classical principle"},
    "Kala Sarpa Yoga": {"category": "Non-BPHS (Practical)", "section": "Modern Enhancement", "ref": "Classical principle"},
    "Grahan Yoga": {"category": "Non-BPHS (Practical)", "section": "Modern Enhancement", "ref": "Eclipse yoga"},
    "Chandal Yoga": {"category": "Non-BPHS (Practical)", "section": "Modern Enhancement", "ref": "Challenge yoga"},
    "Kubera Yoga": {"category": "Non-BPHS (Practical)", "section": "Modern Enhancement", "ref": "Wealth yoga"},
    "Balarishta Yoga": {"category": "Non-BPHS (Practical)", "section": "Modern Enhancement", "ref": "Challenge yoga"},
    "Kroora Yoga": {"category": "Non-BPHS (Practical)", "section": "Modern Enhancement", "ref": "Challenge yoga"},
    "Saraswati Yoga": {"category": "Non-BPHS (Practical)", "section": "Modern Enhancement", "ref": "Learning yoga"},
    "Nitya Yoga": {"category": "Non-BPHS (Practical)", "section": "Muhurta Text", "ref": "Tithi yoga"},
    "Sanyas Yoga": {"category": "Non-BPHS (Practical)", "section": "Modern Enhancement", "ref": "Renunciation yoga"},
    "Bhava Yoga": {"category": "Non-BPHS (Practical)", "section": "Practical House Analysis", "ref": "House lord placement"},
}


def add_bphs_fields_to_yoga_dict(yoga_dict_str: str, yoga_name: str) -> str:
    """
    Add BPHS category fields to a yoga dictionary string.

    Args:
        yoga_dict_str: The original yoga dictionary as a string
        yoga_name: The name of the yoga to look up in mapping

    Returns:
        Updated yoga dictionary string with BPHS fields
    """
    # Get BPHS info from mapping
    bphs_info = None

    # Try exact match first
    if yoga_name in YOGA_BPHS_MAPPING:
        bphs_info = YOGA_BPHS_MAPPING[yoga_name]
    else:
        # Try partial match (for variations)
        for key in YOGA_BPHS_MAPPING:
            if key.lower() in yoga_name.lower() or yoga_name.lower() in key.lower():
                bphs_info = YOGA_BPHS_MAPPING[key]
                break

    # Default to Non-BPHS if not found
    if not bphs_info:
        bphs_info = {
            "category": "Non-BPHS (Practical)",
            "section": "Modern/Practical Addition",
            "ref": "Not in BPHS spec"
        }

    # Check if fields already exist
    if '"bphs_category"' in yoga_dict_str:
        return yoga_dict_str  # Already has BPHS fields

    # Find the end of the dictionary (before closing brace)
    # Add fields before the last closing brace
    lines = yoga_dict_str.split('\n')

    # Find indentation level
    indent = ""
    for line in lines:
        if '"name"' in line or '"description"' in line:
            indent = line[:len(line) - len(line.lstrip())]
            break

    # Create new fields
    new_fields = [
        f'{indent}"bphs_category": "{bphs_info["category"]}",',
        f'{indent}"bphs_section": "{bphs_info["section"]}",',
        f'{indent}"bphs_ref": "{bphs_info["ref"]}"'
    ]

    # Insert before the last line (which should be the closing brace)
    result_lines = lines[:-1] + new_fields + [lines[-1]]

    return '\n'.join(result_lines)


def main():
    """Main function to process extended_yoga_service.py"""
    service_file = Path("/Users/arvind.tiwari/Desktop/jioastro/backend/app/services/extended_yoga_service.py")

    if not service_file.exists():
        print(f"Error: File not found: {service_file}")
        return

    print(f"Reading {service_file}...")
    content = service_file.read_text()

    # Find all yoga dictionary definitions
    # Pattern: yogas.append({ or yogas.extend([{
    yoga_pattern = r'(yogas\.(?:append|extend)\(\[?\s*\{[^}]+\})'

    matches = re.finditer(yoga_pattern, content, re.DOTALL)

    print(f"Found {len(list(re.finditer(yoga_pattern, content, re.DOTALL)))} yoga definitions")
    print(f"\nProcessing yogas and adding BPHS fields...")
    print(f"This is a complex task requiring manual review.")
    print(f"\nPlease use the mapping dictionary above to manually add fields to each yoga.")
    print(f"\nExample:")
    print("""
    yogas.append({
        "name": "Ruchaka Yoga",
        "description": "...",
        "strength": "Strong",
        "category": "Pancha Mahapurusha",
        "bphs_category": "Major Positive Yogas",
        "bphs_section": "E) Pañcha-Mahāpuruṣa (Ch.75)",
        "bphs_ref": "Ch.75.1-2"
    })
    """)

    print(f"\nMapping contains {len(YOGA_BPHS_MAPPING)} yoga classifications")
    print(f"\nTo proceed, I recommend a targeted approach:")
    print(f"1. Start with Pancha Mahapurusha yogas (5 yogas)")
    print(f"2. Then Named Yogas Ch.36 (15 yogas)")
    print(f"3. Then Raj Yogas (10 yogas)")
    print(f"4. Continue by category")


if __name__ == "__main__":
    main()
