"""
Dosha Detection Service
Detects major doshas (afflictions) in Vedic astrology charts
"""

from typing import Dict, Any, List


class DoshaDetectionService:
    """Detect classical Vedic astrology doshas"""

    def detect_all_doshas(
        self,
        d1_planets: Dict[str, Any],
        d1_ascendant: Dict[str, Any],
        d9_planets: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Detect all major doshas in the birth chart

        Args:
            d1_planets: Planets from D1 (Rashi) chart
            d1_ascendant: Ascendant from D1 chart
            d9_planets: Planets from D9 (Navamsa) chart (optional for Manglik)

        Returns:
            List of detected doshas with details
        """
        doshas = []

        # 1. Manglik Dosha (Mars affliction)
        manglik = self.detect_manglik_dosha(d1_planets, d9_planets)
        if manglik["present"]:
            doshas.append(manglik)

        # 2. Kaal Sarpa Dosha (All planets between Rahu-Ketu axis)
        kaal_sarpa = self.detect_kaal_sarpa_dosha(d1_planets)
        if kaal_sarpa["present"]:
            doshas.append(kaal_sarpa)

        # 3. Pitra Dosha (Ancestral affliction)
        pitra = self.detect_pitra_dosha(d1_planets)
        if pitra["present"]:
            doshas.append(pitra)

        # 4. Gandanta Dosha (Junction points between signs/nakshatras)
        gandanta = self.detect_gandanta_dosha(d1_planets, d1_ascendant)
        if gandanta["present"]:
            doshas.append(gandanta)

        # 5. Grahan Dosha (Eclipse dosha - Sun/Moon with Rahu/Ketu)
        grahan = self.detect_grahan_dosha(d1_planets)
        if grahan["present"]:
            doshas.append(grahan)

        # 6. Kemdrum Dosha (Moon isolated)
        kemdrum = self.detect_kemdrum_dosha(d1_planets)
        if kemdrum["present"]:
            doshas.append(kemdrum)

        return doshas if doshas else [{
            "name": "No Major Dosha",
            "present": False,
            "severity": "none",
            "description": "No major doshas detected in the chart",
            "effects": "Chart is relatively free from major afflictions",
            "remedies": []
        }]

    def detect_manglik_dosha(
        self,
        d1_planets: Dict[str, Any],
        d9_planets: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Enhanced Manglik Dosha Detection with 5-level intensity classification

        Analyzes Mars placement from Lagna, Moon, and Venus for comprehensive Manglik analysis.
        Includes sign strength, combustion, aspects, and Navamsa placement for accurate severity.

        Intensity Levels: Very High, High, Medium, Low, Very Low, None
        """
        mars_data = d1_planets.get("Mars", {})
        mars_house_lagna = mars_data.get("house", 0)
        mars_sign_name = mars_data.get("sign", "")
        mars_sign_num = mars_data.get("sign_num", 0)
        mars_is_retrograde = mars_data.get("is_retrograde", False)

        # Get Moon's position to check from Moon
        moon_data = d1_planets.get("Moon", {})
        moon_sign = moon_data.get("sign_num", 0)

        # Get Venus position (some texts also check from Venus)
        venus_data = d1_planets.get("Venus", {})
        venus_sign = venus_data.get("sign_num", 0)

        # Calculate Mars house from Moon and Venus
        mars_house_from_moon = ((mars_sign_num - moon_sign) % 12) + 1
        mars_house_from_venus = ((mars_sign_num - venus_sign) % 12) + 1

        # Manglik houses with intensity weights
        # Very high intensity: 1st (aggression), 8th (accidents/death), 12th (separation)
        # High intensity: 2nd (family discord), 7th (spouse conflicts)
        # Medium intensity: 4th (domestic peace issues)
        house_intensity_weights = {
            1: 4,   # Self, personality, aggression
            2: 3,   # Family, wealth conflicts
            4: 2,   # Domestic peace
            7: 3,   # Spouse, partnership
            8: 5,   # Longevity, accidents, major transformations
            12: 4   # Separation, losses
        }

        # Calculate base intensity score
        intensity_score = 0
        affected_houses = []

        # Check from Lagna
        if mars_house_lagna in house_intensity_weights:
            weight = house_intensity_weights[mars_house_lagna]
            intensity_score += weight
            affected_houses.append(f"{mars_house_lagna}th from Lagna (weight: {weight})")

        # Check from Moon (slightly less weight)
        if mars_house_from_moon in house_intensity_weights:
            weight = house_intensity_weights[mars_house_from_moon] * 0.8
            intensity_score += weight
            affected_houses.append(f"{mars_house_from_moon}th from Moon (weight: {weight:.1f})")

        # Check from Venus (least weight, but still significant)
        if mars_house_from_venus in house_intensity_weights:
            weight = house_intensity_weights[mars_house_from_venus] * 0.5
            intensity_score += weight
            affected_houses.append(f"{mars_house_from_venus}th from Venus (weight: {weight:.1f})")

        is_manglik = intensity_score > 0

        # Strength modifiers
        strength_factors = []

        # Sign strength (own/exalted increases effect, debilitated reduces)
        if mars_sign_name in ["Aries", "Scorpio"]:  # Own sign
            intensity_score *= 1.2
            strength_factors.append("Mars in own sign (Aries/Scorpio) - 20% increase")
        elif mars_sign_name == "Capricorn":  # Exalted
            intensity_score *= 1.3
            strength_factors.append("Mars exalted in Capricorn - 30% increase")
        elif mars_sign_name == "Cancer":  # Debilitated
            intensity_score *= 0.5
            strength_factors.append("Mars debilitated in Cancer - 50% reduction")

        # Retrograde Mars (intensifies effects)
        if mars_is_retrograde:
            intensity_score *= 1.15
            strength_factors.append("Mars retrograde - 15% increase in intensity")

        # Combustion check (if available)
        if mars_data.get("is_combust", False):
            intensity_score *= 0.7
            strength_factors.append("Mars combust - 30% reduction in effect")

        # Check for cancellations (Manglik Dosha Bhanga)
        cancellations = []
        cancellation_reduction = 0

        # 1. Mars in own sign or exalted (partial cancellation)
        if mars_sign_name in ["Aries", "Scorpio", "Capricorn"]:
            cancellations.append({
                "type": "Sign Strength",
                "description": "Mars in own/exalted sign provides strength to handle effects",
                "reduction": 20
            })
            cancellation_reduction += 20

        # 2. Mars in D9 (Navamsa) well-placed
        if d9_planets:
            mars_d9 = d9_planets.get("Mars", {})
            mars_d9_house = mars_d9.get("house", 0)
            mars_d9_sign = mars_d9.get("sign", "")

            if mars_d9_house not in [1, 7, 8, 12]:
                cancellations.append({
                    "type": "Navamsa Placement",
                    "description": f"Mars well-placed in {mars_d9_house}th house of D9",
                    "reduction": 25
                })
                cancellation_reduction += 25

            if mars_d9_sign in ["Aries", "Scorpio", "Capricorn"]:
                cancellations.append({
                    "type": "Navamsa Sign",
                    "description": f"Mars in {mars_d9_sign} in Navamsa (own/exalted)",
                    "reduction": 15
                })
                cancellation_reduction += 15

        # 3. Jupiter/Venus in Kendra (1, 4, 7, 10) - benefic influence
        jupiter_data = d1_planets.get("Jupiter", {})
        if jupiter_data.get("house", 0) in [1, 4, 7, 10]:
            cancellations.append({
                "type": "Benefic Aspect",
                "description": f"Jupiter in {jupiter_data.get('house')}th house (Kendra) provides protection",
                "reduction": 20
            })
            cancellation_reduction += 20

        if venus_data.get("house", 0) in [1, 4, 7, 10]:
            cancellations.append({
                "type": "Benefic Aspect",
                "description": f"Venus in {venus_data.get('house')}th house (Kendra) provides protection",
                "reduction": 15
            })
            cancellation_reduction += 15

        # 4. Age-based natural reduction (after 28 years, effects reduce)
        # Note: This would require birth date calculation in actual implementation
        # Placeholder for now

        # Apply cancellation reduction (cap at 90% reduction)
        cancellation_reduction = min(cancellation_reduction, 90)
        final_intensity = intensity_score * (1 - cancellation_reduction / 100)

        # Determine severity based on final intensity
        if not is_manglik or final_intensity <= 0:
            severity = "none"
            intensity_label = "None"
        elif final_intensity <= 1.5:
            severity = "very_low"
            intensity_label = "Very Low"
        elif final_intensity <= 3.0:
            severity = "low"
            intensity_label = "Low"
        elif final_intensity <= 5.0:
            severity = "medium"
            intensity_label = "Medium"
        elif final_intensity <= 7.0:
            severity = "high"
            intensity_label = "High"
        else:
            severity = "very_high"
            intensity_label = "Very High"

        # Effects based on severity
        effects_by_severity = {
            "none": "No Manglik affliction present",
            "very_low": "Minimal impact. May experience minor delays in marriage (1-2 years) or occasional disagreements. Effects naturally reduce after age 28.",
            "low": "Mild impact. Possible delays in finding suitable match (2-3 years). Minor conflicts in early marriage that resolve with maturity. Consider simple remedies.",
            "medium": "Moderate impact. Marriage delays (3-5 years) or challenges in married life such as frequent disagreements, ego clashes. Remedies recommended before marriage.",
            "high": "Significant impact. Substantial delays (5-7 years), major conflicts with spouse, possible separation if not addressed. Strong remedial measures essential.",
            "very_high": "Severe impact. Very long delays (7+ years), serious marital discord, risk of separation or spouse's health issues. Comprehensive remedial measures and compatibility matching crucial."
        }

        # Age-based manifestation
        manifestation_periods = {
            "very_low": "18-28 years (reduces significantly after 28)",
            "low": "20-30 years (reduces after 28-30)",
            "medium": "22-35 years (partial reduction after 32)",
            "high": "24-40 years (gradual reduction after 35)",
            "very_high": "25-45 years (remedies essential throughout)"
        }

        # Categorized remedies by type and severity
        remedies = self._get_manglik_remedies(severity)

        return {
            "name": "Manglik Dosha",
            "present": is_manglik,
            "severity": severity,
            "intensity_label": intensity_label,
            "intensity_score": round(final_intensity, 2),
            "base_score": round(intensity_score, 2),
            "cancellation_percentage": round(cancellation_reduction, 1),
            "details": {
                "mars_house_from_lagna": mars_house_lagna,
                "mars_house_from_moon": mars_house_from_moon,
                "mars_house_from_venus": mars_house_from_venus,
                "mars_sign": mars_sign_name,
                "mars_retrograde": mars_is_retrograde,
                "affected_houses": affected_houses,
                "strength_factors": strength_factors,
                "cancellations": cancellations,
                "manifestation_period": manifestation_periods.get(severity, "Not applicable")
            },
            "description": (
                f"Mars in {mars_house_lagna}th house from Lagna, "
                f"{mars_house_from_moon}th from Moon, "
                f"{mars_house_from_venus}th from Venus. "
                f"Intensity: {intensity_label} ({final_intensity:.1f}/10)"
            ),
            "effects": effects_by_severity.get(severity, ""),
            "remedies": remedies
        }

    def _get_manglik_remedies(self, severity: str) -> Dict[str, List[str]]:
        """Get categorized remedies based on Manglik Dosha severity"""

        # Base remedies for all severities (except none)
        base_remedies = {
            "pujas_rituals": [
                "Hanuman Chalisa recitation daily (especially Tuesdays)",
                "Visit Hanuman temple on Tuesdays",
                "Mangal Shanti Puja before marriage"
            ],
            "fasting": [
                "Fast on Tuesdays (consume only fruits/milk)",
                "Observe Pradosh Vrat (13th day of lunar fortnight)"
            ],
            "charity": [
                "Donate red lentils (masoor dal) on Tuesdays",
                "Donate red clothes to laborers/workers",
                "Feed monkeys with jaggery and gram on Tuesdays"
            ],
            "mantras": [
                "Om Angarakaya Namaha (108 times daily)",
                "Hanuman Chalisa (1-2 times daily)",
                "Mangal Gayatri Mantra: 'Om Bhumiputraya Vidmahe'"
            ]
        }

        if severity == "none":
            return {}

        # Additional remedies for higher severities
        if severity in ["very_low", "low"]:
            return {
                **base_remedies,
                "gemstones": [
                    "Red Coral (Moonga) - Consult astrologer for suitability",
                    "Wear on Tuesday morning after purification"
                ],
                "lifestyle": [
                    "Maintain patience and understanding in relationships",
                    "Delay marriage until age 28 if possible (natural reduction)",
                    "Ensure compatibility matching (Koot Milan) before marriage"
                ]
            }

        elif severity == "medium":
            return {
                **base_remedies,
                "gemstones": [
                    "Red Coral (Moonga) - 6-7 carats in gold/copper ring",
                    "Wear on ring finger, Tuesday morning after Hanuman puja",
                    "Consult experienced astrologer before wearing"
                ],
                "advanced_pujas": [
                    "Mangal Dosh Nivaran Puja by qualified priest",
                    "Kumbh Vivah (symbolic marriage) before actual marriage",
                    "Navagraha Shanti Puja for planetary peace"
                ],
                "lifestyle": [
                    "Marriage with another Manglik (dosha cancellation)",
                    "Thorough compatibility analysis essential",
                    "Pre-marital counseling recommended",
                    "Strengthen Jupiter and Venus through remedies"
                ]
            }

        else:  # high or very_high
            return {
                **base_remedies,
                "gemstones": [
                    "Red Coral (Moonga) - 7-9 carats, high quality",
                    "Wear in gold ring on ring finger after Mangal puja",
                    "Must consult expert Vedic astrologer",
                    "Consider Pearl (Moon) or Yellow Sapphire (Jupiter) for balance"
                ],
                "advanced_pujas": [
                    "Mangal Dosh Nivaran Maha Puja at sacred temples",
                    "Kumbh Vivah (mandatory before actual marriage)",
                    "Rudrabhishek every Tuesday for 11 weeks",
                    "Navagraha Homa on auspicious day",
                    "Visit Mangalnath Temple (Ujjain) or similar Mars temples"
                ],
                "lifestyle": [
                    "ESSENTIAL: Marriage with another Manglik person",
                    "Comprehensive compatibility matching (Ashtakoot + Manglik)",
                    "Delay marriage until after age 28-30",
                    "Pre-marital counseling and compatibility workshops",
                    "Strengthen benefic planets (Jupiter, Venus, Mercury)",
                    "Avoid marriage during Mars dasha/antardasha if possible"
                ],
                "yantra": [
                    "Mangal Yantra installation at home/workplace",
                    "Hanuman Yantra for protection",
                    "Energize yantras on Tuesday during Mars hora"
                ],
                "special": [
                    "Consult multiple expert astrologers for confirmation",
                    "Consider partnership compatibility counseling",
                    "Perform remedies for minimum 3-6 months before marriage",
                    "Regular spiritual practices for emotional balance"
                ]
            }

        return base_remedies

    def detect_kaal_sarpa_dosha(self, d1_planets: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhanced Kaal Sarpa Dosha Detection with 12 variations and detailed effects

        Analyzes planetary positions relative to Rahu-Ketu axis for comprehensive
        Kaal Sarpa Yoga classification with type-specific effects and remedies.

        Types: Full (7/7 planets), Partial (5-6/7), and intensity levels
        """
        rahu_data = d1_planets.get("Rahu", {})
        ketu_data = d1_planets.get("Ketu", {})

        rahu_house = rahu_data.get("house", 0)
        ketu_house = ketu_data.get("house", 0)

        # Get all planets except Rahu and Ketu
        planets_to_check = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

        # Check if all planets are on one side of Rahu-Ketu axis
        planets_between_rahu_ketu = []
        planets_outside = []

        for planet in planets_to_check:
            planet_house = d1_planets.get(planet, {}).get("house", 0)

            # Check if planet is between Rahu and Ketu
            if rahu_house < ketu_house:
                # Rahu in earlier house, Ketu in later house
                if rahu_house < planet_house < ketu_house:
                    planets_between_rahu_ketu.append(planet)
                else:
                    planets_outside.append(planet)
            else:
                # Rahu in later house, Ketu in earlier house (axis wraps around)
                if planet_house > rahu_house or planet_house < ketu_house:
                    planets_between_rahu_ketu.append(planet)
                else:
                    planets_outside.append(planet)

        # Determine Full vs Partial Kaal Sarpa
        num_planets_hemmed = max(len(planets_between_rahu_ketu), len(planets_outside))
        is_full_kaal_sarpa = num_planets_hemmed == 7
        is_partial_kaal_sarpa = num_planets_hemmed >= 5  # 5-6 planets

        has_kaal_sarpa = is_full_kaal_sarpa or is_partial_kaal_sarpa

        # Determine type based on Rahu's house (12 classical variations)
        kaal_sarpa_type_info = self._get_kaal_sarpa_type_details(rahu_house, ketu_house)

        # Calculate intensity
        intensity_factors = []
        intensity_score = 0

        if has_kaal_sarpa:
            # Base score from number of planets hemmed
            if is_full_kaal_sarpa:
                intensity_score = 10
                intensity_factors.append("Full Kaal Sarpa (7/7 planets) - Maximum intensity")
            elif num_planets_hemmed == 6:
                intensity_score = 7
                intensity_factors.append("Strong Partial Kaal Sarpa (6/7 planets)")
            else:  # 5 planets
                intensity_score = 5
                intensity_factors.append("Mild Partial Kaal Sarpa (5/7 planets)")

            # Check if benefics (Jupiter, Venus, Mercury) are hemmed
            benefics_hemmed = [p for p in ["Jupiter", "Venus", "Mercury"]
                             if p in planets_between_rahu_ketu or p in planets_outside]
            if len(benefics_hemmed) == 3:
                intensity_score *= 1.3
                intensity_factors.append("All benefics hemmed - 30% increase")

            # Check if Sun/Moon are hemmed (luminaries)
            luminaries_hemmed = [p for p in ["Sun", "Moon"]
                               if p in planets_between_rahu_ketu or p in planets_outside]
            if len(luminaries_hemmed) == 2:
                intensity_score *= 1.2
                intensity_factors.append("Both luminaries hemmed - 20% increase")

        # Check for cancellations (Kaal Sarpa Dosha Bhanga)
        cancellations = []
        cancellation_reduction = 0

        if has_kaal_sarpa:
            # 1. Jupiter in Kendra (1, 4, 7, 10)
            jupiter_house = d1_planets.get("Jupiter", {}).get("house", 0)
            if jupiter_house in [1, 4, 7, 10]:
                cancellations.append({
                    "type": "Benefic Protection",
                    "description": f"Jupiter in {jupiter_house}th house (Kendra) reduces effects",
                    "reduction": 30
                })
                cancellation_reduction += 30

            # 2. Venus in Kendra
            venus_house = d1_planets.get("Venus", {}).get("house", 0)
            if venus_house in [1, 4, 7, 10]:
                cancellations.append({
                    "type": "Benefic Protection",
                    "description": f"Venus in {venus_house}th house (Kendra) provides relief",
                    "reduction": 20
                })
                cancellation_reduction += 20

            # 3. Moon in strong position (exalted or own sign)
            moon_sign = d1_planets.get("Moon", {}).get("sign", "")
            if moon_sign in ["Cancer", "Taurus"]:  # Own or exalted
                cancellations.append({
                    "type": "Luminary Strength",
                    "description": f"Moon in {moon_sign} (strong) stabilizes mind",
                    "reduction": 25
                })
                cancellation_reduction += 25

            # 4. Rahu/Ketu in exalted signs (Taurus/Scorpio)
            rahu_sign = rahu_data.get("sign", "")
            if rahu_sign in ["Taurus", "Gemini"]:  # Considered strong
                cancellations.append({
                    "type": "Node Strength",
                    "description": f"Rahu in {rahu_sign} (favorable) reduces malefic effects",
                    "reduction": 15
                })
                cancellation_reduction += 15

        # Apply cancellation reduction (cap at 85%)
        cancellation_reduction = min(cancellation_reduction, 85)
        final_intensity = intensity_score * (1 - cancellation_reduction / 100)

        # Determine severity
        if not has_kaal_sarpa:
            severity = "none"
            intensity_label = "None"
        elif final_intensity <= 3:
            severity = "low"
            intensity_label = "Low"
        elif final_intensity <= 6:
            severity = "medium"
            intensity_label = "Medium"
        elif final_intensity <= 8:
            severity = "high"
            intensity_label = "High"
        else:
            severity = "very_high"
            intensity_label = "Very High"

        # Get type-specific remedies
        remedies = self._get_kaal_sarpa_remedies(
            severity,
            kaal_sarpa_type_info.get("name", "Kaal Sarpa")
        )

        return {
            "name": "Kaal Sarpa Dosha",
            "present": has_kaal_sarpa,
            "severity": severity,
            "intensity_label": intensity_label,
            "intensity_score": round(final_intensity, 2),
            "type": kaal_sarpa_type_info.get("name") if has_kaal_sarpa else None,
            "details": {
                "full_kaal_sarpa": is_full_kaal_sarpa,
                "partial_kaal_sarpa": is_partial_kaal_sarpa and not is_full_kaal_sarpa,
                "planets_hemmed": num_planets_hemmed,
                "rahu_house": rahu_house,
                "ketu_house": ketu_house,
                "planets_between": planets_between_rahu_ketu,
                "planets_outside": planets_outside,
                "intensity_factors": intensity_factors,
                "cancellations": cancellations,
                "cancellation_percentage": round(cancellation_reduction, 1),
                "type_details": kaal_sarpa_type_info
            },
            "description": (
                f"{kaal_sarpa_type_info.get('name')} - "
                f"{'Full' if is_full_kaal_sarpa else 'Partial'} Kaal Sarpa with "
                f"{num_planets_hemmed}/7 planets hemmed between "
                f"Rahu (house {rahu_house}) and Ketu (house {ketu_house}). "
                f"Intensity: {intensity_label} ({final_intensity:.1f}/10)"
                if has_kaal_sarpa else "Planets not hemmed between Rahu-Ketu axis"
            ),
            "effects": kaal_sarpa_type_info.get("effects", "No Kaal Sarpa affliction"),
            "positive_effects": kaal_sarpa_type_info.get("positive_effects", []) if has_kaal_sarpa else [],
            "manifestation_period": kaal_sarpa_type_info.get("manifestation_period", "") if has_kaal_sarpa else "",
            "remedies": remedies
        }

    def _get_kaal_sarpa_type_details(self, rahu_house: int, ketu_house: int) -> Dict[str, Any]:
        """Get detailed information for each of the 12 Kaal Sarpa Yoga types"""

        type_details = {
            1: {
                "name": "Ananta Kaal Sarpa",
                "deity": "Lord Ananta (Vishnu's serpent)",
                "effects": "Challenges in self-confidence, health issues, obstacles in personal development. May face struggles in establishing identity and authority. Possible delays in achieving goals.",
                "positive_effects": [
                    "Strong spiritual inclination after age 42",
                    "Ability to overcome obstacles through perseverance",
                    "Deep philosophical understanding"
                ],
                "life_areas": "Self, personality, health, vitality",
                "manifestation_period": "Most active: 18-42 years, reduces after 42"
            },
            2: {
                "name": "Kulika Kaal Sarpa",
                "deity": "Kulika Naga",
                "effects": "Family conflicts, wealth instability, speech-related problems. Challenges in accumulating and maintaining wealth. Strained family relationships. Possible food-related issues.",
                "positive_effects": [
                    "Excellent communication skills after maturity",
                    "Ability to earn through speech/teaching",
                    "Strong family bonds after resolution"
                ],
                "life_areas": "Wealth, family, speech, food",
                "manifestation_period": "Most active: 22-45 years, stabilizes after 45"
            },
            3: {
                "name": "Vasuki Kaal Sarpa",
                "deity": "Vasuki Naga (King of Serpents)",
                "effects": "Sibling conflicts, courage challenges, communication issues. Problems with neighbors or close relatives. Obstacles in short travels. Lack of support from siblings.",
                "positive_effects": [
                    "Exceptional writing and communication abilities",
                    "Success in media, journalism after struggles",
                    "Strong willpower and courage development"
                ],
                "life_areas": "Siblings, courage, communication, short journeys",
                "manifestation_period": "Most active: 20-40 years"
            },
            4: {
                "name": "Shankhapala Kaal Sarpa",
                "deity": "Shankhapala Naga",
                "effects": "Property disputes, mother's health issues, emotional instability. Challenges in domestic peace. Difficulty acquiring or maintaining property. Lack of mental peace at home.",
                "positive_effects": [
                    "Strong emotional resilience after trials",
                    "Success in real estate after age 35",
                    "Deep maternal devotion"
                ],
                "life_areas": "Mother, property, emotions, domestic peace",
                "manifestation_period": "Most active: 25-50 years"
            },
            5: {
                "name": "Padma Kaal Sarpa",
                "deity": "Padma Naga",
                "effects": "Children-related concerns, intelligence blocks, speculative losses. Delays in having children or challenges with them. Obstacles in education. Losses in speculation/gambling.",
                "positive_effects": [
                    "Exceptional intelligence and creativity after maturity",
                    "Success in research and innovation",
                    "Good relationship with children eventually"
                ],
                "life_areas": "Children, intelligence, education, speculation",
                "manifestation_period": "Most active: 25-45 years"
            },
            6: {
                "name": "Mahapadma Kaal Sarpa",
                "deity": "Mahapadma Naga",
                "effects": "Health problems, enemy troubles, debt issues, legal disputes. Chronic health conditions. Persistent enemies. Financial obligations. Service-related struggles.",
                "positive_effects": [
                    "Excellent problem-solving abilities",
                    "Success in healing professions",
                    "Ability to overcome major obstacles"
                ],
                "life_areas": "Health, enemies, debts, litigation, service",
                "manifestation_period": "Most active: Throughout life, peaks 30-50 years"
            },
            7: {
                "name": "Takshaka Kaal Sarpa",
                "deity": "Takshaka Naga",
                "effects": "Marriage delays, partnership problems, spouse health issues. Serious challenges in married life. Business partnership conflicts. Delays in finding suitable partner.",
                "positive_effects": [
                    "Strong partnership skills after trials",
                    "Deep understanding of relationships",
                    "Success in public relations"
                ],
                "life_areas": "Marriage, partnerships, spouse, contracts",
                "manifestation_period": "Most active: 24-42 years"
            },
            8: {
                "name": "Karkotak Kaal Sarpa",
                "deity": "Karkotak Naga",
                "effects": "Sudden accidents, longevity concerns, inheritance disputes. Unexpected setbacks. Chronic ailments. Challenges with in-laws. Occult interests but with obstacles.",
                "positive_effects": [
                    "Strong interest and success in occult sciences",
                    "Transformational abilities",
                    "Research and investigation skills"
                ],
                "life_areas": "Longevity, accidents, inheritance, transformation",
                "manifestation_period": "Critical periods: 21, 28, 35, 42, 56 years"
            },
            9: {
                "name": "Shankhachud Kaal Sarpa",
                "deity": "Shankhachud Naga",
                "effects": "Father's health/relationship issues, spiritual obstacles, higher education delays. Problems with authority figures. Obstacles in religious pursuits. Foreign travel issues.",
                "positive_effects": [
                    "Strong philosophical and spiritual wisdom",
                    "Success in higher education eventually",
                    "Teaching and mentoring abilities"
                ],
                "life_areas": "Father, religion, higher education, long journeys",
                "manifestation_period": "Most active: 22-48 years"
            },
            10: {
                "name": "Ghatak Kaal Sarpa",
                "deity": "Ghatak Naga (The Destroyer)",
                "effects": "Career instability, professional setbacks, authority conflicts. Frequent job changes. Delays in career success. Problems with superiors. Public image challenges.",
                "positive_effects": [
                    "Exceptional career success after age 42",
                    "Leadership abilities through struggles",
                    "Recognition and fame eventually"
                ],
                "life_areas": "Career, profession, status, authority",
                "manifestation_period": "Most active: 25-42 years, major success after 42"
            },
            11: {
                "name": "Vishdhar Kaal Sarpa",
                "deity": "Vishdhar Naga",
                "effects": "Income fluctuations, unfulfilled desires, social network issues. Unstable income sources. Obstacles in achieving wishes. Elder sibling problems. Inconsistent gains.",
                "positive_effects": [
                    "Multiple income sources after maturity",
                    "Large social network eventually",
                    "Fulfillment of major desires after struggles"
                ],
                "life_areas": "Income, gains, desires, friends, elder siblings",
                "manifestation_period": "Most active: 28-50 years"
            },
            12: {
                "name": "Sheshnag Kaal Sarpa",
                "deity": "Sheshnag (Divine Serpent)",
                "effects": "Expenditure problems, foreign settlement issues, sleep disorders. Excessive or wasteful expenses. Difficulties in foreign lands. Spiritual confusion. Hospitalization possibilities.",
                "positive_effects": [
                    "Strong spiritual liberation potential",
                    "Success in foreign lands eventually",
                    "Charitable inclinations and moksha pursuit"
                ],
                "life_areas": "Losses, expenses, foreign lands, spirituality, moksha",
                "manifestation_period": "Most active: Throughout life, spiritual peak after 48"
            }
        }

        return type_details.get(rahu_house, {
            "name": "Kaal Sarpa Yoga",
            "deity": "Serpent Deities",
            "effects": "General obstacles and transformational challenges in life",
            "positive_effects": ["Spiritual growth through adversity"],
            "life_areas": "Various life areas",
            "manifestation_period": "Throughout life"
        })

    def _get_kaal_sarpa_remedies(self, severity: str, yoga_type: str) -> Dict[str, List[str]]:
        """Get categorized remedies for Kaal Sarpa Yoga based on severity and type"""

        # Base remedies for all severities
        base_remedies = {
            "pujas_rituals": [
                "Kaal Sarpa Dosha Puja on Naga Panchami day (most powerful)",
                "Perform Rahu-Ketu Shanti Puja",
                "Rudrabhishek on Mondays (Lord Shiva worship)",
                "Visit Trimbakeshwar Temple (Maharashtra) or other Kaal Sarpa temples"
            ],
            "mantras": [
                "Maha Mrityunjaya Mantra (108 times daily)",
                "Om Namah Shivaya (throughout the day)",
                "Rahu Mantra: Om Bhram Bhreem Bhroum Sah Rahave Namaha (18000 times in 40 days)",
                "Ketu Mantra: Om Sraam Sreem Sraum Sah Ketave Namaha (18000 times in 40 days)"
            ],
            "charity": [
                "Donate milk to serpent idols/anthills",
                "Feed Brahmins on Naga Panchami",
                "Donate black sesame seeds on Saturdays",
                "Donate to snake rescue organizations"
            ]
        }

        if severity == "none":
            return {}

        if severity in ["low", "medium"]:
            return {
                **base_remedies,
                "yantra": [
                    "Kaal Sarpa Yantra (energize on Naga Panchami)",
                    "Keep in puja room or wear as pendant"
                ],
                "lifestyle": [
                    "Avoid killing serpents or harming reptiles",
                    "Respect serpent imagery and deities",
                    "Practice meditation for mental peace",
                    "Maintain positive attitude during challenges"
                ],
                "worship": [
                    "Worship serpent deities on Tuesdays and Saturdays",
                    "Light oil lamp under peepal tree on Saturdays",
                    "Perform Nag Puja on Naga Panchami annually"
                ]
            }

        else:  # high or very_high
            return {
                **base_remedies,
                "advanced_pujas": [
                    f"Specific {yoga_type} Nivaran Puja by experienced priests",
                    "Navagraha Homa for planetary peace",
                    "Nagabali Puja (for ancestral serpent curses)",
                    "Sarpa Samskara ritual",
                    "108 Rudrabhishek over period of time"
                ],
                "pilgrimage": [
                    "Visit Trimbakeshwar Temple, Nashik (most powerful)",
                    "Kukke Subramanya Temple, Karnataka",
                    "Sri Kalahasti Temple, Andhra Pradesh",
                    "Rameswaram Temple, Tamil Nadu",
                    "Any of the 12 Jyotirlinga temples"
                ],
                "yantra_gemstones": [
                    "Kaal Sarpa Yantra - properly energized and installed",
                    "Gomedh (Hessonite) for Rahu after astrological consultation",
                    "Cat's Eye for Ketu after astrological consultation",
                    "Energize on Rahu/Ketu hora on Saturday"
                ],
                "advanced_mantras": [
                    "Naga Stotram daily",
                    "Kaal Sarpa Dosha Nivaran Stotra",
                    "Shiva Panchakshari Stotra (Om Namah Shivaya elaboration)",
                    "Complete 125,000 Maha Mrityunjaya Mantra japa (with priest guidance)"
                ],
                "special_remedies": [
                    "Energize silver serpent idol and keep at home",
                    "Feed milk to serpent idol every Monday",
                    "Perform Nag Pratishtha (serpent installation) at home",
                    "Participate in Nag Panchami celebrations annually",
                    "Consider Nag Puja every month on Panchami tithi"
                ],
                "lifestyle": [
                    "ESSENTIAL: Never harm serpents or reptiles",
                    "Protect serpent habitats and support conservation",
                    "Regular spiritual practices and meditation",
                    "Develop patience and acceptance of life challenges",
                    "Serve parents and elders with devotion",
                    "Practice non-violence (Ahimsa) in all aspects"
                ],
                "timing": [
                    "Best time for major remedies: Naga Panchami day",
                    "Monthly: Panchami tithi (5th lunar day)",
                    "Weekly: Mondays and Saturdays",
                    "Daily: Rahu Kaal timing for Rahu mantra (avoid starting new ventures)"
                ]
            }

        return base_remedies

    def detect_pitra_dosha(self, d1_planets: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhanced Pitra Dosha Detection (Ancestral Afflictions)

        Comprehensive analysis of ancestral karmic debts through multiple classical indicators:
        - Sun-Rahu-Saturn combinations
        - 5th and 9th house afflictions
        - Moon-Ketu associations
        - Debilitation of significators

        Categorized by intensity and affected life areas
        """
        sun_data = d1_planets.get("Sun", {})
        rahu_data = d1_planets.get("Rahu", {})
        ketu_data = d1_planets.get("Ketu", {})
        saturn_data = d1_planets.get("Saturn", {})
        moon_data = d1_planets.get("Moon", {})
        jupiter_data = d1_planets.get("Jupiter", {})

        sun_house = sun_data.get("house", 0)
        sun_sign = sun_data.get("sign", "")
        rahu_house = rahu_data.get("house", 0)
        ketu_house = ketu_data.get("house", 0)
        saturn_house = saturn_data.get("house", 0)
        moon_house = moon_data.get("house", 0)
        moon_sign = moon_data.get("sign", "")
        jupiter_house = jupiter_data.get("house", 0)
        jupiter_sign = jupiter_data.get("sign", "")

        # Check for indicators with weights
        indicators = []
        intensity_score = 0

        # PRIMARY INDICATORS (Strong - Weight 3-4)

        # 1. Sun-Rahu conjunction (Grahan Yoga on Sun) - Very strong indicator
        if sun_house == rahu_house:
            indicators.append({
                "type": "Primary",
                "indicator": f"Sun-Rahu conjunction in {sun_house}th house",
                "weight": 4,
                "description": "Pitru Dosha from paternal lineage, father-related karma"
            })
            intensity_score += 4

        # 2. Moon-Ketu conjunction - Strong indicator
        if moon_house == ketu_house:
            indicators.append({
                "type": "Primary",
                "indicator": f"Moon-Ketu conjunction in {moon_house}th house",
                "weight": 4,
                "description": "Pitru Dosha from maternal lineage, mother-related karma"
            })
            intensity_score += 4

        # 3. Rahu in 9th house (house of father, ancestors, dharma)
        if rahu_house == 9:
            indicators.append({
                "type": "Primary",
                "indicator": "Rahu in 9th house (father/ancestors)",
                "weight": 3,
                "description": "Obstacles in ancestral blessings, father's health issues"
            })
            intensity_score += 3

        # 4. Ketu in 5th house (house of progeny, purva punya)
        if ketu_house == 5:
            indicators.append({
                "type": "Primary",
                "indicator": "Ketu in 5th house (progeny/past merit)",
                "weight": 3,
                "description": "Children-related issues, depletion of past life merits"
            })
            intensity_score += 3

        # SECONDARY INDICATORS (Medium - Weight 2)

        # 5. Saturn-Rahu conjunction (Shrapit Dosha)
        if saturn_house == rahu_house:
            indicators.append({
                "type": "Secondary",
                "indicator": f"Saturn-Rahu conjunction in {saturn_house}th house (Shrapit Yoga)",
                "weight": 2,
                "description": "Cursed by ancestors, severe karmic debts"
            })
            intensity_score += 2

        # 6. Sun debilitated (Libra)
        if sun_sign == "Libra":
            indicators.append({
                "type": "Secondary",
                "indicator": "Sun debilitated in Libra",
                "weight": 2,
                "description": "Weak father figure, paternal lineage affliction"
            })
            intensity_score += 2

        # 7. Moon debilitated (Scorpio)
        if moon_sign == "Scorpio":
            indicators.append({
                "type": "Secondary",
                "indicator": "Moon debilitated in Scorpio",
                "weight": 2,
                "description": "Maternal lineage affliction, emotional karmic debt"
            })
            intensity_score += 2

        # 8. Jupiter debilitated (Capricorn) - affects progeny and ancestral blessings
        if jupiter_sign == "Capricorn":
            indicators.append({
                "type": "Secondary",
                "indicator": "Jupiter debilitated in Capricorn",
                "weight": 2,
                "description": "Reduced ancestral blessings, children-related challenges"
            })
            intensity_score += 2

        # TERTIARY INDICATORS (Mild - Weight 1)

        # 9. Sun in 9th house (can be afflicted by malefics)
        if sun_house == 9:
            indicators.append({
                "type": "Tertiary",
                "indicator": "Sun in 9th house",
                "weight": 1,
                "description": "Father-related karma, need for ancestral remedies"
            })
            intensity_score += 1

        # 10. Rahu/Ketu in conjunction with Sun or Moon (eclipsed luminaries)
        if sun_house == ketu_house:
            indicators.append({
                "type": "Tertiary",
                "indicator": f"Sun-Ketu conjunction in {sun_house}th house",
                "weight": 1,
                "description": "Paternal side subtle afflictions"
            })
            intensity_score += 1

        if moon_house == rahu_house:
            indicators.append({
                "type": "Tertiary",
                "indicator": f"Moon-Rahu conjunction in {moon_house}th house",
                "weight": 1,
                "description": "Maternal side subtle afflictions"
            })
            intensity_score += 1

        # 11. Multiple planets in 9th or 5th house with Rahu/Ketu
        ninth_house_planets = [p for p, data in d1_planets.items()
                              if data.get("house") == 9 and p not in ["Rahu", "Ketu"]]
        fifth_house_planets = [p for p, data in d1_planets.items()
                             if data.get("house") == 5 and p not in ["Rahu", "Ketu"]]

        if rahu_house == 9 and len(ninth_house_planets) >= 2:
            indicators.append({
                "type": "Tertiary",
                "indicator": "Multiple planets with Rahu in 9th house",
                "weight": 1,
                "description": "Complex ancestral karma"
            })
            intensity_score += 1

        if ketu_house == 5 and len(fifth_house_planets) >= 2:
            indicators.append({
                "type": "Tertiary",
                "indicator": "Multiple planets with Ketu in 5th house",
                "weight": 1,
                "description": "Multiple progeny challenges"
            })
            intensity_score += 1

        has_pitra_dosha = len(indicators) >= 1

        # Calculate severity based on intensity score
        if not has_pitra_dosha:
            severity = "none"
            intensity_label = "None"
        elif intensity_score <= 2:
            severity = "low"
            intensity_label = "Low"
        elif intensity_score <= 4:
            severity = "medium"
            intensity_label = "Medium"
        elif intensity_score <= 7:
            severity = "high"
            intensity_label = "High"
        else:
            severity = "very_high"
            intensity_label = "Very High"

        # Detailed effects by category
        effects_detail = {
            "family_lineage": [],
            "progeny": [],
            "financial": [],
            "health": [],
            "spiritual": []
        }

        if has_pitra_dosha:
            # Add category-specific effects based on indicators
            for indicator in indicators:
                indicator_text = indicator["indicator"]

                # Family/Father effects
                if "Sun" in indicator_text or "9th house" in indicator_text:
                    effects_detail["family_lineage"].append(
                        "Strained relationship with father or paternal figures"
                    )
                    effects_detail["spiritual"].append(
                        "Obstacles in dharma and righteous path"
                    )

                # Mother/Maternal effects
                if "Moon" in indicator_text:
                    effects_detail["family_lineage"].append(
                        "Maternal lineage issues or mother's health concerns"
                    )
                    effects_detail["health"].append(
                        "Mental peace disturbances, anxiety"
                    )

                # Progeny effects
                if "5th house" in indicator_text or "Jupiter" in indicator_text:
                    effects_detail["progeny"].append(
                        "Delays or difficulties in having children"
                    )
                    effects_detail["progeny"].append(
                        "Health issues with existing children"
                    )

                # Financial effects
                if "Saturn" in indicator_text or "Shrapit" in indicator_text:
                    effects_detail["financial"].append(
                        "Sudden financial losses or persistent debts"
                    )
                    effects_detail["financial"].append(
                        "Obstacles in wealth accumulation"
                    )

            # Remove duplicates
            for category in effects_detail:
                effects_detail[category] = list(set(effects_detail[category]))

        # Categorized remedies
        remedies = self._get_pitra_dosha_remedies(severity, intensity_score)

        return {
            "name": "Pitra Dosha",
            "present": has_pitra_dosha,
            "severity": severity,
            "intensity_label": intensity_label,
            "intensity_score": intensity_score,
            "details": {
                "total_indicators": len(indicators),
                "primary_indicators": [i for i in indicators if i["type"] == "Primary"],
                "secondary_indicators": [i for i in indicators if i["type"] == "Secondary"],
                "tertiary_indicators": [i for i in indicators if i["type"] == "Tertiary"],
                "sun_house": sun_house,
                "rahu_house": rahu_house,
                "ketu_house": ketu_house,
                "saturn_house": saturn_house,
                "moon_house": moon_house,
                "jupiter_house": jupiter_house
            },
            "description": (
                f"Pitra Dosha present with {len(indicators)} indicator(s). "
                f"Intensity: {intensity_label} ({intensity_score} points). "
                f"Primary afflictions: {len([i for i in indicators if i['type'] == 'Primary'])}"
                if has_pitra_dosha else "No Pitra Dosha indicators found"
            ),
            "effects": effects_detail if has_pitra_dosha else "No Pitra Dosha affliction",
            "manifestation_areas": {
                "paternal_lineage": any("Sun" in i["indicator"] or "9th" in i["indicator"] for i in indicators),
                "maternal_lineage": any("Moon" in i["indicator"] for i in indicators),
                "progeny_issues": any("5th" in i["indicator"] or "Jupiter" in i["indicator"] for i in indicators),
                "karmic_debts": any("Saturn" in i["indicator"] or "Shrapit" in i["indicator"] for i in indicators)
            } if has_pitra_dosha else {},
            "remedies": remedies
        }

    def _get_pitra_dosha_remedies(self, severity: str, intensity_score: int) -> Dict[str, List[str]]:
        """Get categorized remedies for Pitra Dosha based on severity"""

        # Base remedies for all severities
        base_remedies = {
            "daily_practices": [
                "Feed crows daily (especially mornings)",
                "Offer water to Peepal tree on Saturdays",
                "Light lamp using sesame oil on Saturdays",
                "Recite Pitra Dosha Nivaran Mantra daily"
            ],
            "monthly_rituals": [
                "Perform Tarpan on Amavasya (new moon) days",
                "Feed Brahmins in the name of ancestors",
                "Donate to the needy on your father's birth tithi"
            ],
            "charity": [
                "Donate food to poor and needy",
                "Feed dogs (especially black dogs)",
                "Donate black sesame, black cloth on Saturdays",
                "Support orphanages or old age homes"
            ]
        }

        if severity == "none":
            return {}

        if severity in ["low", "medium"]:
            return {
                **base_remedies,
                "annual_rituals": [
                    "Perform Shraddha during Pitru Paksha (15-day period)",
                    "Observe fast on Amavasya if possible",
                    "Participate in Brahmin Bhojan on ancestor tithis"
                ],
                "spiritual_practices": [
                    "Recite Vishnu Sahasranamam for ancestral peace",
                    "Offer prayers to Lord Shiva for liberation of ancestors",
                    "Plant and maintain Peepal or Banyan tree"
                ],
                "lifestyle": [
                    "Respect elders and parents",
                    "Maintain family photographs and honor ancestors",
                    "Avoid non-vegetarian food on Saturdays and Amavasya",
                    "Practice forgiveness towards family members"
                ]
            }

        else:  # high or very_high
            return {
                **base_remedies,
                "major_rituals": [
                    "ESSENTIAL: Pind Daan at Gaya (Bihar) - Most powerful remedy",
                    "Tripindi Shraddha (for three generations)",
                    "Narayan Bali Puja at Trimbakeshwar",
                    "Perform 16 Monday fasts with Shiva worship",
                    "Kaal Sarp Puja if Rahu-Ketu axis is strong"
                ],
                "pilgrimage": [
                    "Visit Gaya for Pind Daan (mandatory for severe cases)",
                    "Haridwar or Rishikesh for Tarpan rituals",
                    "Trimbakeshwar for Narayan Bali",
                    "Badrinath or Kedarnath for ancestral peace",
                    "Any Jyotirlinga temple for Rudrabhishek"
                ],
                "advanced_pujas": [
                    "Pitra Dosha Nivaran Maha Puja by qualified priests",
                    "Brahma Bali Puja (complete ancestral ritual)",
                    "Navagraha Homa for planetary peace",
                    "Rudrabhishek every Monday for 16 consecutive Mondays",
                    "Organize mass feeding (Anna Daan) in ancestor's name"
                ],
                "mantras": [
                    "Pitra Gayatri Mantra (daily 108 times)",
                    "Maha Mrityunjaya Mantra (108 times daily)",
                    "Vishnu Sahasranamam (weekly)",
                    "Specific mantra for afflicted planet (Sun/Moon/Jupiter)",
                    "Pitru Stotra recitation on Saturdays"
                ],
                "gemstones_yantra": [
                    "Pitra Dosh Nivaran Yantra (energize on Amavasya)",
                    "Ruby for Sun (if Sun-Rahu conjunction) - after consultation",
                    "Pearl for Moon (if Moon-Ketu conjunction) - after consultation",
                    "Yellow Sapphire for Jupiter (if Jupiter debilitated)"
                ],
                "special_remedies": [
                    "Perform Kanya Daan (daughter's marriage support)",
                    "Organize Go Daan (cow donation) in ancestor's name",
                    "Support education of underprivileged children",
                    "Establish water facility (well/handpump) in ancestor's name",
                    "Sponsor Brahmin Bhojan on Pitru Paksha days"
                ],
                "lifestyle_essential": [
                    "ESSENTIAL: Never disrespect parents or elders",
                    "Perform Shraddha without fail during Pitru Paksha",
                    "Avoid meat, alcohol, and negative activities on Amavasya",
                    "Maintain ancestral property and respect family traditions",
                    "Seek forgiveness from anyone wronged by family",
                    "Practice charity and service in the name of ancestors",
                    "Teach children about ancestral values and culture"
                ],
                "timing": [
                    "Best for major remedies: Pitru Paksha (Sep-Oct)",
                    "Monthly: Amavasya (new moon) days",
                    "Weekly: Saturdays for Tarpan and donations",
                    "Annual: Perform on father's death anniversary (tithi)"
                ]
            }

        return base_remedies

    def detect_gandanta_dosha(
        self,
        d1_planets: Dict[str, Any],
        d1_ascendant: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Detect Gandanta Dosha (Junction points between water and fire signs)
        Critical junctions: Pisces-Aries, Cancer-Leo, Scorpio-Sagittarius
        Last 3°20' of water sign to first 3°20' of fire sign
        """
        # Gandanta zones (sign_num, degree_start, degree_end)
        gandanta_zones = [
            (11, 26.666667, 30.0),  # Last 3°20' of Pisces (11)
            (0, 0.0, 3.333333),      # First 3°20' of Aries (0)
            (3, 26.666667, 30.0),    # Last 3°20' of Cancer (3)
            (4, 0.0, 3.333333),      # First 3°20' of Leo (4)
            (7, 26.666667, 30.0),    # Last 3°20' of Scorpio (7)
            (8, 0.0, 3.333333),      # First 3°20' of Sagittarius (8)
        ]

        afflicted_points = []

        # Check Ascendant
        asc_sign = d1_ascendant.get("sign_num", 0)
        asc_degree = d1_ascendant.get("degree", 0)

        for zone_sign, zone_start, zone_end in gandanta_zones:
            if asc_sign == zone_sign and zone_start <= asc_degree <= zone_end:
                afflicted_points.append({
                    "point": "Ascendant",
                    "sign": d1_ascendant.get("sign"),
                    "degree": asc_degree
                })
                break

        # Check Moon (most sensitive to Gandanta)
        moon_data = d1_planets.get("Moon", {})
        moon_sign = moon_data.get("sign_num", 0)
        moon_degree = moon_data.get("degree", 0)

        for zone_sign, zone_start, zone_end in gandanta_zones:
            if moon_sign == zone_sign and zone_start <= moon_degree <= zone_end:
                afflicted_points.append({
                    "point": "Moon",
                    "sign": moon_data.get("sign"),
                    "degree": moon_degree
                })
                break

        has_gandanta = len(afflicted_points) > 0

        # Moon in Gandanta is most critical
        moon_in_gandanta = any(p["point"] == "Moon" for p in afflicted_points)

        return {
            "name": "Gandanta Dosha",
            "present": has_gandanta,
            "severity": "high" if moon_in_gandanta else "medium" if has_gandanta else "none",
            "details": {
                "afflicted_points": afflicted_points,
                "moon_in_gandanta": moon_in_gandanta
            },
            "description": (
                "Critical junction point affliction found in: " +
                ", ".join([f"{p['point']} in {p['sign']} at {p['degree']:.2f}°"
                          for p in afflicted_points])
                if has_gandanta else "No Gandanta affliction"
            ),
            "effects": (
                "May cause initial life struggles, health issues in childhood, "
                "mental anxiety, or transformation through hardship. "
                "Moon in Gandanta can cause emotional turmoil." if has_gandanta
                else "No Gandanta affliction"
            ),
            "remedies": [
                "Perform Gandanta Dosha Shanti Puja",
                "Recite Mahamrityunjaya Mantra 108 times daily",
                "Donate white items on Mondays if Moon is afflicted",
                "Wear Pearl gemstone after consultation",
                "Worship Lord Shiva and Goddess Durga",
                "Perform Rudrabhishek on Mondays",
                "Chant Om Namah Shivaya regularly"
            ] if has_gandanta else []
        }

    def detect_grahan_dosha(self, d1_planets: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhanced Grahan Dosha Detection (Eclipse Afflictions)

        Comprehensive analysis of luminaries eclipsed by shadow planets:
        - Sun-Rahu (Solar Eclipse): Father, ego, authority issues
        - Sun-Ketu: Spiritual confusion, identity crisis
        - Moon-Rahu (Lunar Eclipse): Mental anxiety, mother issues
        - Moon-Ketu: Emotional detachment, meditation

        Intensity based on conjunction degrees, house, and benefic protection
        """
        sun_data = d1_planets.get("Sun", {})
        moon_data = d1_planets.get("Moon", {})
        rahu_data = d1_planets.get("Rahu", {})
        ketu_data = d1_planets.get("Ketu", {})
        jupiter_data = d1_planets.get("Jupiter", {})
        venus_data = d1_planets.get("Venus", {})

        sun_house = sun_data.get("house", 0)
        sun_sign = sun_data.get("sign", "")
        sun_degree = sun_data.get("abs_degree", 0)

        moon_house = moon_data.get("house", 0)
        moon_sign = moon_data.get("sign", "")
        moon_degree = moon_data.get("abs_degree", 0)

        rahu_house = rahu_data.get("house", 0)
        rahu_degree = rahu_data.get("abs_degree", 0)

        ketu_house = ketu_data.get("house", 0)
        ketu_degree = ketu_data.get("abs_degree", 0)

        jupiter_house = jupiter_data.get("house", 0)
        venus_house = venus_data.get("house", 0)

        afflictions = []
        intensity_score = 0

        # Check Sun with Rahu/Ketu (Solar Eclipse Yogas)
        if sun_house == rahu_house:
            # Calculate degree difference for intensity
            degree_diff = abs(sun_degree - rahu_degree) % 360
            if degree_diff > 180:
                degree_diff = 360 - degree_diff

            # Intensity based on closeness
            if degree_diff <= 5:
                weight = 5  # Very close conjunction
                closeness = "Very Close"
            elif degree_diff <= 10:
                weight = 4
                closeness = "Close"
            elif degree_diff <= 15:
                weight = 3
                closeness = "Moderate"
            else:
                weight = 2
                closeness = "Wide"

            afflictions.append({
                "type": "Solar Eclipse (Sun-Rahu)",
                "conjunction": f"Sun-Rahu conjunction in {sun_house}th house ({sun_sign})",
                "degree_difference": round(degree_diff, 2),
                "closeness": closeness,
                "weight": weight,
                "effects": "Father issues, ego problems, authority conflicts, health challenges"
            })
            intensity_score += weight

        if sun_house == ketu_house:
            # Calculate degree difference
            degree_diff = abs(sun_degree - ketu_degree) % 360
            if degree_diff > 180:
                degree_diff = 360 - degree_diff

            if degree_diff <= 5:
                weight = 4
                closeness = "Very Close"
            elif degree_diff <= 10:
                weight = 3
                closeness = "Close"
            elif degree_diff <= 15:
                weight = 2
                closeness = "Moderate"
            else:
                weight = 1.5
                closeness = "Wide"

            afflictions.append({
                "type": "Sun-Ketu Eclipse",
                "conjunction": f"Sun-Ketu conjunction in {sun_house}th house ({sun_sign})",
                "degree_difference": round(degree_diff, 2),
                "closeness": closeness,
                "weight": weight,
                "effects": "Spiritual confusion, identity crisis, separation from father, mystical inclinations"
            })
            intensity_score += weight

        # Check Moon with Rahu/Ketu (Lunar Eclipse Yogas)
        if moon_house == rahu_house:
            # Calculate degree difference
            degree_diff = abs(moon_degree - rahu_degree) % 360
            if degree_diff > 180:
                degree_diff = 360 - degree_diff

            if degree_diff <= 5:
                weight = 5  # Moon-Rahu very serious for mental health
                closeness = "Very Close"
            elif degree_diff <= 10:
                weight = 4
                closeness = "Close"
            elif degree_diff <= 15:
                weight = 3
                closeness = "Moderate"
            else:
                weight = 2
                closeness = "Wide"

            afflictions.append({
                "type": "Lunar Eclipse (Moon-Rahu)",
                "conjunction": f"Moon-Rahu conjunction in {moon_house}th house ({moon_sign})",
                "degree_difference": round(degree_diff, 2),
                "closeness": closeness,
                "weight": weight,
                "effects": "Mental anxiety, emotional instability, mother's health, obsessive thoughts, phobias"
            })
            intensity_score += weight

        if moon_house == ketu_house:
            # Calculate degree difference
            degree_diff = abs(moon_degree - ketu_degree) % 360
            if degree_diff > 180:
                degree_diff = 360 - degree_diff

            if degree_diff <= 5:
                weight = 4
                closeness = "Very Close"
            elif degree_diff <= 10:
                weight = 3
                closeness = "Close"
            elif degree_diff <= 15:
                weight = 2
                closeness = "Moderate"
            else:
                weight = 1.5
                closeness = "Wide"

            afflictions.append({
                "type": "Moon-Ketu Eclipse",
                "conjunction": f"Moon-Ketu conjunction in {moon_house}th house ({moon_sign})",
                "degree_difference": round(degree_diff, 2),
                "closeness": closeness,
                "weight": weight,
                "effects": "Emotional detachment, meditation ability, maternal separation, psychic sensitivity"
            })
            intensity_score += weight

        has_grahan = len(afflictions) > 0

        # Check for remedial factors (Jupiter/Venus protection)
        benefic_protection = []
        reduction_percentage = 0

        if has_grahan:
            # Jupiter in Kendra or aspecting Moon/Sun
            if jupiter_house in [1, 4, 7, 10]:
                benefic_protection.append("Jupiter in Kendra provides wisdom and protection")
                reduction_percentage += 25

            # Venus protection for emotional stability
            if venus_house in [1, 4, 7, 10]:
                benefic_protection.append("Venus in Kendra provides emotional balance")
                reduction_percentage += 15

            # Sun exalted (Aries) or own sign (Leo) - reduces eclipse impact
            if sun_sign in ["Aries", "Leo"]:
                benefic_protection.append(f"Sun in {sun_sign} (strong) reduces eclipse impact")
                reduction_percentage += 20

            # Moon exalted (Taurus) or own sign (Cancer)
            if moon_sign in ["Taurus", "Cancer"]:
                benefic_protection.append(f"Moon in {moon_sign} (strong) provides emotional stability")
                reduction_percentage += 20

        # Apply reduction (cap at 70%)
        reduction_percentage = min(reduction_percentage, 70)
        final_intensity = intensity_score * (1 - reduction_percentage / 100)

        # Determine severity
        if not has_grahan:
            severity = "none"
            intensity_label = "None"
        elif final_intensity <= 2:
            severity = "low"
            intensity_label = "Low"
        elif final_intensity <= 4:
            severity = "medium"
            intensity_label = "Medium"
        elif final_intensity <= 6:
            severity = "high"
            intensity_label = "High"
        else:
            severity = "very_high"
            intensity_label = "Very High"

        # Categorized effects based on affliction types
        effects_detail = {
            "paternal": [],
            "maternal": [],
            "mental_emotional": [],
            "spiritual": [],
            "health": []
        }

        if has_grahan:
            for affliction in afflictions:
                aff_type = affliction["type"]

                if "Sun-Rahu" in aff_type:
                    effects_detail["paternal"].extend([
                        "Strained relationship with father",
                        "Authority and ego conflicts",
                        "Career obstacles from superiors"
                    ])
                    effects_detail["health"].append("Heart or bone-related health issues")

                elif "Sun-Ketu" in aff_type:
                    effects_detail["paternal"].append("Separation or distance from father")
                    effects_detail["spiritual"].extend([
                        "Spiritual confusion or crisis of faith",
                        "Strong mystical inclinations",
                        "Search for identity and purpose"
                    ])

                elif "Moon-Rahu" in aff_type:
                    effects_detail["maternal"].extend([
                        "Mother's health concerns",
                        "Emotional dependency on mother"
                    ])
                    effects_detail["mental_emotional"].extend([
                        "Mental anxiety and restlessness",
                        "Obsessive thoughts or phobias",
                        "Emotional instability and mood swings",
                        "Sleep disturbances"
                    ])
                    effects_detail["health"].append("Digestive issues, water retention")

                elif "Moon-Ketu" in aff_type:
                    effects_detail["maternal"].append("Emotional detachment from mother")
                    effects_detail["mental_emotional"].extend([
                        "Emotional numbness or detachment",
                        "Difficulty expressing emotions"
                    ])
                    effects_detail["spiritual"].extend([
                        "Strong meditation and spiritual abilities",
                        "Psychic sensitivity",
                        "Interest in occult sciences"
                    ])

            # Remove duplicates
            for category in effects_detail:
                effects_detail[category] = list(set(effects_detail[category]))

        # Get categorized remedies
        remedies = self._get_grahan_dosha_remedies(severity, afflictions)

        return {
            "name": "Grahan Dosha",
            "present": has_grahan,
            "severity": severity,
            "intensity_label": intensity_label,
            "intensity_score": round(final_intensity, 2),
            "base_score": round(intensity_score, 2),
            "reduction_percentage": round(reduction_percentage, 1),
            "details": {
                "total_afflictions": len(afflictions),
                "afflictions": afflictions,
                "benefic_protection": benefic_protection,
                "sun_house": sun_house,
                "moon_house": moon_house,
                "rahu_house": rahu_house,
                "ketu_house": ketu_house
            },
            "description": (
                f"Grahan Dosha present with {len(afflictions)} eclipse affliction(s). "
                f"Intensity: {intensity_label} ({final_intensity:.1f} points). "
                f"{'Benefic protection: ' + str(reduction_percentage) + '%' if benefic_protection else ''}"
                if has_grahan else "No Grahan Dosha"
            ),
            "effects": effects_detail if has_grahan else "No Grahan Dosha affliction",
            "remedies": remedies
        }

    def _get_grahan_dosha_remedies(self, severity: str, afflictions: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Get categorized remedies for Grahan Dosha based on severity and affliction types"""

        # Determine which luminaries are afflicted
        sun_afflicted = any("Sun" in aff["type"] for aff in afflictions)
        moon_afflicted = any("Moon" in aff["type"] for aff in afflictions)
        rahu_involved = any("Rahu" in aff["type"] for aff in afflictions)
        ketu_involved = any("Ketu" in aff["type"] for aff in afflictions)

        # Base remedies for all severities
        base_remedies = {
            "daily_practices": [],
            "mantras": [],
            "eclipse_rituals": [
                "IMPORTANT: Donate during eclipses (solar or lunar)",
                "Avoid eating during eclipse period",
                "Take bath after eclipse ends",
                "Chant mantras during eclipse time"
            ]
        }

        # Add luminary-specific daily practices
        if sun_afflicted:
            base_remedies["daily_practices"].extend([
                "Offer water to Sun at sunrise (Surya Arghya)",
                "Recite Aditya Hridayam on Sundays"
            ])
            base_remedies["mantras"].append("Surya Mantra: Om Suryaya Namaha (108 times)")

        if moon_afflicted:
            base_remedies["daily_practices"].extend([
                "Offer water to Moon on Monday evenings",
                "Donate white items on Mondays"
            ])
            base_remedies["mantras"].append("Chandra Mantra: Om Chandraya Namaha (108 times)")

        if rahu_involved:
            base_remedies["mantras"].append("Rahu Mantra: Om Rahave Namaha (108 times)")

        if ketu_involved:
            base_remedies["mantras"].append("Ketu Mantra: Om Ketave Namaha (108 times)")

        if severity == "none":
            return {}

        if severity in ["low", "medium"]:
            return {
                **base_remedies,
                "pujas": [
                    "Grahan Dosha Nivaran Puja on eclipse days",
                    "Rudrabhishek on Mondays for Ketu afflictions",
                    "Vishnu puja for overall protection"
                ],
                "charity": [
                    "Donate during eclipses: rice, ghee, sugar if Moon afflicted",
                    "Donate wheat, jaggery, copper if Sun afflicted",
                    "Feed Brahmins on eclipse days",
                    "Donate to orphanages or elderly"
                ],
                "gemstones": [
                    "Ruby for Sun affliction (after consultation)" if sun_afflicted else None,
                    "Pearl for Moon affliction (after consultation)" if moon_afflicted else None,
                    "Hessonite for Rahu (after consultation)" if rahu_involved else None,
                    "Cat's Eye for Ketu (after consultation)" if ketu_involved else None
                ],
                "lifestyle": [
                    "Respect parents and elders",
                    "Practice meditation for mental peace" if moon_afflicted else None,
                    "Develop self-confidence" if sun_afflicted else None,
                    "Regular yoga and pranayama"
                ]
            }

        else:  # high or very_high
            return {
                **base_remedies,
                "major_pujas": [
                    "Grahan Dosha Nivaran Maha Puja by experienced priest",
                    "Surya Grahan Shanti Puja (if Sun afflicted)",
                    "Chandra Grahan Shanti Puja (if Moon afflicted)",
                    "Navagraha Homa for complete planetary peace",
                    "Rahu-Ketu Shanti Puja on Saturdays"
                ],
                "advanced_mantras": [
                    "Aditya Hridayam (daily if Sun afflicted)",
                    "Chandra Stotram (daily if Moon afflicted)",
                    "Maha Mrityunjaya Mantra (108 times daily) - Essential",
                    "Complete 18,000 Rahu mantra in 40 days (if Rahu involved)",
                    "Complete 18,000 Ketu mantra in 40 days (if Ketu involved)",
                    "Durga Saptashati path monthly"
                ],
                "pilgrimage": [
                    "Visit Surya temples (Konark, Modhera) if Sun afflicted",
                    "Visit Chandra temples if Moon afflicted",
                    "Trimbakeshwar or Kalahasti for Rahu-Ketu",
                    "Perform rituals at sacred rivers during eclipse"
                ],
                "advanced_charity": [
                    "ESSENTIAL: Major donations during eclipses",
                    "Anna Daan (mass feeding) on eclipse day",
                    "Go Daan (cow donation) in parent's name",
                    "Sponsor education for underprivileged",
                    "Donate silver if Moon afflicted, gold/copper if Sun afflicted"
                ],
                "yantra_gemstones": [
                    "Surya Yantra if Sun afflicted (energize on Sunday)",
                    "Chandra Yantra if Moon afflicted (energize on Monday)",
                    "Rahu Yantra if Rahu involved (energize on Saturday)",
                    "Ruby (Sun) or Pearl (Moon) - High quality, after expert consultation",
                    "Hessonite (Rahu) or Cat's Eye (Ketu) - After verification"
                ],
                "special_remedies": [
                    "108 Rudrabhishek if Ketu involved",
                    "16 Monday fasts with Shiva worship if Moon afflicted",
                    "12 Sunday fasts if Sun afflicted",
                    "Establish Shiva Lingam at home for Ketu",
                    "Daily offering to parents' photos (father if Sun, mother if Moon)"
                ],
                "mental_health": [
                    "ESSENTIAL for Moon afflictions: Regular meditation",
                    "Psychiatric counseling if severe anxiety",
                    "Yoga Nidra for sleep issues",
                    "Breathing exercises (Anulom Vilom, Bhramari)",
                    "Maintain regular sleep schedule",
                    "Avoid stimulants (caffeine, etc.) if Moon afflicted"
                ] if moon_afflicted else [],
                "timing": [
                    "Best for major remedies: During eclipses",
                    "Sunday worship and fasting if Sun afflicted",
                    "Monday worship and fasting if Moon afflicted",
                    "Saturday for Rahu-Ketu remedies",
                    "Amavasya (new moon) for overall Grahan remedies"
                ]
            }

        # Filter out None values
        for key in base_remedies:
            if isinstance(base_remedies[key], list):
                base_remedies[key] = [r for r in base_remedies[key] if r is not None]

        return base_remedies

    def detect_kemdrum_dosha(self, d1_planets: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect Kemdrum Dosha (Moon isolated - no planets in 2nd and 12th from Moon)
        """
        moon_data = d1_planets.get("Moon", {})
        moon_house = moon_data.get("house", 0)

        # Calculate 2nd and 12th houses from Moon
        house_before_moon = (moon_house - 2) % 12 + 1
        house_after_moon = (moon_house % 12) + 1

        # Check if any planet (except Rahu/Ketu) in these houses
        planets_to_check = ["Sun", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

        planets_before = []
        planets_after = []

        for planet in planets_to_check:
            planet_house = d1_planets.get(planet, {}).get("house", 0)
            if planet_house == house_before_moon:
                planets_before.append(planet)
            if planet_house == house_after_moon:
                planets_after.append(planet)

        has_kemdrum = (len(planets_before) == 0 and len(planets_after) == 0)

        # Check for cancellations
        cancellations = []

        # Jupiter or Venus in Kendra from Lagna cancels
        jupiter_house = d1_planets.get("Jupiter", {}).get("house", 0)
        venus_house = d1_planets.get("Venus", {}).get("house", 0)

        if jupiter_house in [1, 4, 7, 10]:
            cancellations.append("Jupiter in Kendra from Lagna")
        if venus_house in [1, 4, 7, 10]:
            cancellations.append("Venus in Kendra from Lagna")

        effective_kemdrum = has_kemdrum and len(cancellations) == 0

        return {
            "name": "Kemdrum Dosha",
            "present": effective_kemdrum,
            "severity": "medium" if effective_kemdrum else "none",
            "details": {
                "moon_house": moon_house,
                "house_before_moon": house_before_moon,
                "house_after_moon": house_after_moon,
                "planets_before": planets_before,
                "planets_after": planets_after,
                "cancellations": cancellations
            },
            "description": (
                f"Moon isolated in house {moon_house} with no planets in houses "
                f"{house_before_moon} and {house_after_moon}"
                if effective_kemdrum else "Moon not isolated"
            ),
            "effects": (
                "May cause poverty, lack of support, mental depression, or loss of comforts. "
                "However, cancellations can reduce severity." if effective_kemdrum
                else "No Kemdrum affliction"
            ),
            "remedies": [
                "Worship Lord Shiva and fast on Mondays",
                "Wear Pearl gemstone after consultation",
                "Donate white items on Mondays",
                "Recite Chandra (Moon) mantra 108 times daily",
                "Perform Chandra Graha Shanti Puja",
                "Keep fast on Purnima (Full Moon)",
                "Drink water from silver vessel"
            ] if effective_kemdrum else []
        }


# Singleton instance
dosha_detection_service = DoshaDetectionService()
