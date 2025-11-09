"""
Chart Vectorization Service
Encodes birth charts into vector embeddings for similarity search
"""

from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ChartVectorizationService:
    """
    Service for encoding birth charts into 384-dimensional vectors
    Uses feature engineering + dimensionality reduction
    """

    def __init__(self):
        # Feature dimensions
        self.ZODIAC_DIM = 12
        self.PLANET_DIM = 9
        self.HOUSE_DIM = 12
        self.YOGA_DIM = 50  # Top 50 yogas
        self.DASHA_DIM = 9
        self.PHASE_DIM = 10

        # Total raw features: ~100 dimensions
        # After embedding: 384 dimensions

        # Zodiac signs mapping
        self.zodiac_map = {
            "Aries": 0, "Taurus": 1, "Gemini": 2, "Cancer": 3,
            "Leo": 4, "Virgo": 5, "Libra": 6, "Scorpio": 7,
            "Sagittarius": 8, "Capricorn": 9, "Aquarius": 10, "Pisces": 11
        }

        # Planet mapping
        self.planet_map = {
            "Sun": 0, "Moon": 1, "Mars": 2, "Mercury": 3,
            "Jupiter": 4, "Venus": 5, "Saturn": 6, "Rahu": 7, "Ketu": 8
        }

        # Common yogas (top 50)
        self.yoga_map = {
            "GajaKesari": 0, "Hamsa": 1, "Malavya": 2, "Ruchaka": 3, "Bhadra": 4,
            "Shasha": 5, "Budhaditya": 6, "Neecha Bhanga": 7, "Raj Yoga": 8,
            "Dhana Yoga": 9, "Viparita Raja": 10, "Sunapha": 11, "Anapha": 12,
            "Durudhara": 13, "Adhi Yoga": 14, "Vesi": 15, "Vosi": 16,
            "Ubhayachari": 17, "Parivartana": 18, "Kahal": 19,
            # Add more as needed...
        }

        # Life stages
        self.life_stage_map = {
            "0-10": 0, "10-20": 1, "20-30": 2, "30-40": 3,
            "40-50": 4, "50-60": 5, "60-70": 6, "70-80": 7, "80+": 8
        }

        # Saturn phases
        self.saturn_phase_map = {
            "Normal": 0,
            "Sade Sati Phase 1": 1,
            "Sade Sati Phase 2": 2,
            "Sade Sati Phase 3": 3,
            "Ashtama Shani": 4,
            "Dhaiya (2.5 years)": 5
        }

    def encode_chart(self, chart_data: Dict[str, Any], profile_data: Optional[Dict[str, Any]] = None) -> Tuple[List[float], Dict[str, Any]]:
        """
        Encode birth chart into 384-dimensional vector

        Args:
            chart_data: Birth chart calculations
            profile_data: Optional profile metadata (age, gender, location)

        Returns:
            Tuple of (vector, metadata)
        """
        try:
            # Extract features
            features = []
            metadata = {}

            # 1. Sun Sign (12-dim one-hot)
            sun_sign = chart_data.get("sun_sign", "Aries")
            metadata["sun_sign"] = sun_sign
            sun_vector = self._one_hot_encode(sun_sign, self.zodiac_map, self.ZODIAC_DIM)
            features.extend(sun_vector)

            # 2. Moon Sign (12-dim one-hot)
            moon_sign = chart_data.get("moon_sign", "Aries")
            metadata["moon_sign"] = moon_sign
            moon_vector = self._one_hot_encode(moon_sign, self.zodiac_map, self.ZODIAC_DIM)
            features.extend(moon_vector)

            # 3. Ascendant (12-dim one-hot)
            ascendant = chart_data.get("ascendant", "Aries")
            metadata["ascendant"] = ascendant
            asc_vector = self._one_hot_encode(ascendant, self.zodiac_map, self.ZODIAC_DIM)
            features.extend(asc_vector)

            # 4. Dominant Planets (from Shadbala - 9-dim weighted)
            dominant_planets = self._extract_dominant_planets(chart_data)
            metadata["dominant_planets"] = dominant_planets[:3]  # Top 3
            planet_vector = self._encode_dominant_planets(dominant_planets)
            features.extend(planet_vector)

            # 5. Major Yogas (multi-hot encoding - 50-dim)
            yogas = chart_data.get("yogas", [])
            metadata["major_yogas"] = [y.get("name") for y in yogas if y.get("strength", 0) > 0.5][:5]
            yoga_vector = self._encode_yogas(yogas)
            features.extend(yoga_vector)

            # 6. Current Dasha (9-dim one-hot for MD, 9-dim for AD)
            dasha = chart_data.get("current_dasha", {})
            md = dasha.get("mahadasha_lord", "Sun")
            ad = dasha.get("antardasha_lord", "Sun")
            metadata["current_dasha_md"] = md
            metadata["current_dasha_ad"] = ad
            md_vector = self._one_hot_encode(md, self.planet_map, self.PLANET_DIM)
            ad_vector = self._one_hot_encode(ad, self.planet_map, self.PLANET_DIM)
            features.extend(md_vector)
            features.extend(ad_vector)

            # 7. Saturn Phase (6-dim one-hot)
            saturn_phase = self._determine_saturn_phase(chart_data)
            metadata["saturn_phase"] = saturn_phase
            saturn_vector = self._one_hot_encode(saturn_phase, self.saturn_phase_map, 6)
            features.extend(saturn_vector)

            # 8. Life Stage (from profile age - 9-dim one-hot)
            life_stage = self._determine_life_stage(profile_data)
            metadata["life_stage"] = life_stage
            stage_vector = self._one_hot_encode(life_stage, self.life_stage_map, 9)
            features.extend(stage_vector)

            # 9. Gender (2-dim: male=1,0 / female=0,1 / other=0.5,0.5)
            gender = profile_data.get("gender", "other") if profile_data else "other"
            metadata["gender"] = gender
            gender_vector = self._encode_gender(gender)
            features.extend(gender_vector)

            # 10. Location Region (simplified - 5 regions: North, South, East, West, Central India)
            location_region = self._determine_region(profile_data)
            metadata["location_region"] = location_region
            region_vector = self._one_hot_encode(location_region,
                {"North": 0, "South": 1, "East": 2, "West": 3, "Central": 4, "Other": 5}, 6)
            features.extend(region_vector)

            # 11. House Strengths (12-dim - from Ashtakavarga or Shadbala)
            house_strengths = self._extract_house_strengths(chart_data)
            features.extend(house_strengths)

            # 12. Planetary Dignities (9-dim - exalted=1, own=0.75, friend=0.5, neutral=0.25, enemy=0, debilitated=-0.5)
            dignities = self._extract_planetary_dignities(chart_data)
            features.extend(dignities)

            # Current raw features: ~150 dimensions
            # Pad or reduce to exactly 384 dimensions

            # Pad with zeros to reach 384 dimensions
            while len(features) < 384:
                features.append(0.0)

            # Truncate if exceeded
            features = features[:384]

            # Normalize to unit vector (for cosine similarity)
            features = self._normalize_vector(features)

            logger.info(f"Encoded chart to {len(features)}-dim vector with metadata: {list(metadata.keys())}")

            return features, metadata

        except Exception as e:
            logger.error(f"Failed to encode chart: {str(e)}")
            # Return zero vector on error
            return [0.0] * 384, {}

    def _one_hot_encode(self, value: str, mapping: Dict[str, int], dim: int) -> List[float]:
        """Create one-hot encoded vector"""
        vector = [0.0] * dim
        if value in mapping:
            vector[mapping[value]] = 1.0
        return vector

    def _extract_dominant_planets(self, chart_data: Dict[str, Any]) -> List[Tuple[str, float]]:
        """Extract dominant planets from Shadbala scores"""
        shadbala = chart_data.get("shadbala", {})
        if not shadbala:
            return []

        # Get planet strengths
        planet_strengths = []
        for planet, score in shadbala.items():
            if isinstance(score, (int, float)):
                planet_strengths.append((planet, score))

        # Sort by strength descending
        planet_strengths.sort(key=lambda x: x[1], reverse=True)
        return planet_strengths

    def _encode_dominant_planets(self, dominant_planets: List[Tuple[str, float]]) -> List[float]:
        """Encode dominant planets as weighted vector"""
        vector = [0.0] * self.PLANET_DIM

        for planet, strength in dominant_planets[:3]:  # Top 3
            if planet in self.planet_map:
                idx = self.planet_map[planet]
                # Normalize strength to 0-1 range (Shadbala is typically 0-10)
                normalized_strength = min(strength / 10.0, 1.0)
                vector[idx] = normalized_strength

        return vector

    def _encode_yogas(self, yogas: List[Dict[str, Any]]) -> List[float]:
        """Multi-hot encoding of yogas"""
        vector = [0.0] * 50  # Top 50 yogas

        for yoga in yogas:
            yoga_name = yoga.get("name", "")
            if yoga_name in self.yoga_map:
                idx = self.yoga_map[yoga_name]
                strength = yoga.get("strength", 0.5)
                vector[idx] = strength

        return vector

    def _determine_saturn_phase(self, chart_data: Dict[str, Any]) -> str:
        """Determine Saturn transit phase"""
        sade_sati = chart_data.get("sade_sati", {})

        if sade_sati.get("in_sade_sati", False):
            phase = sade_sati.get("phase", 1)
            return f"Sade Sati Phase {phase}"

        if sade_sati.get("in_ashtama_shani", False):
            return "Ashtama Shani"

        return "Normal"

    def _determine_life_stage(self, profile_data: Optional[Dict[str, Any]]) -> str:
        """Determine life stage from age"""
        if not profile_data:
            return "30-40"  # Default

        birth_date = profile_data.get("birth_date")
        if not birth_date:
            return "30-40"

        # Calculate age
        if isinstance(birth_date, str):
            from datetime import datetime
            birth_date = datetime.fromisoformat(birth_date.replace("Z", "+00:00")).date()

        age = (datetime.now().date() - birth_date).days // 365

        if age < 10:
            return "0-10"
        elif age < 20:
            return "10-20"
        elif age < 30:
            return "20-30"
        elif age < 40:
            return "30-40"
        elif age < 50:
            return "40-50"
        elif age < 60:
            return "50-60"
        elif age < 70:
            return "60-70"
        elif age < 80:
            return "70-80"
        else:
            return "80+"

    def _encode_gender(self, gender: str) -> List[float]:
        """Encode gender as 2-dim vector"""
        gender_lower = gender.lower()
        if gender_lower in ["male", "m"]:
            return [1.0, 0.0]
        elif gender_lower in ["female", "f"]:
            return [0.0, 1.0]
        else:
            return [0.5, 0.5]  # Non-binary/other

    def _determine_region(self, profile_data: Optional[Dict[str, Any]]) -> str:
        """Determine region from location"""
        if not profile_data:
            return "Other"

        location = profile_data.get("birth_place", "").lower()

        # Simple heuristics (can be improved with geocoding)
        north_states = ["delhi", "punjab", "haryana", "uttarakhand", "himachal", "jammu", "kashmir"]
        south_states = ["karnataka", "tamil nadu", "kerala", "andhra", "telangana"]
        east_states = ["west bengal", "odisha", "bihar", "jharkhand", "assam"]
        west_states = ["maharashtra", "gujarat", "rajasthan", "goa"]
        central_states = ["madhya pradesh", "chhattisgarh"]

        for state in north_states:
            if state in location:
                return "North"

        for state in south_states:
            if state in location:
                return "South"

        for state in east_states:
            if state in location:
                return "East"

        for state in west_states:
            if state in location:
                return "West"

        for state in central_states:
            if state in location:
                return "Central"

        return "Other"

    def _extract_house_strengths(self, chart_data: Dict[str, Any]) -> List[float]:
        """Extract house strengths from Ashtakavarga"""
        ashtakavarga = chart_data.get("ashtakavarga", {})
        sarva = ashtakavarga.get("sarva_ashtakavarga", {})

        strengths = [0.0] * 12

        if sarva:
            for house_num in range(1, 13):
                bindus = sarva.get(f"house_{house_num}", 0)
                # Normalize bindus (typically 0-50 range) to 0-1
                strengths[house_num - 1] = min(bindus / 50.0, 1.0)

        return strengths

    def _extract_planetary_dignities(self, chart_data: Dict[str, Any]) -> List[float]:
        """Extract planetary dignity scores"""
        planets = chart_data.get("planets", [])

        dignities = [0.0] * 9  # 9 planets

        dignity_scores = {
            "exalted": 1.0,
            "own": 0.75,
            "friend": 0.5,
            "neutral": 0.25,
            "enemy": 0.0,
            "debilitated": -0.5
        }

        for planet in planets:
            planet_name = planet.get("name")
            if planet_name not in self.planet_map:
                continue

            idx = self.planet_map[planet_name]
            dignity = planet.get("dignity", "neutral").lower()
            dignities[idx] = dignity_scores.get(dignity, 0.25)

        return dignities

    def _normalize_vector(self, vector: List[float]) -> List[float]:
        """Normalize to unit vector for cosine similarity"""
        norm = np.linalg.norm(vector)
        if norm == 0:
            return vector
        return (np.array(vector) / norm).tolist()

    def calculate_similarity(self, vector1: List[float], vector2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors
        Returns: 0.0 to 1.0 (1.0 = identical, 0.0 = completely different)
        """
        # Cosine similarity
        dot_product = np.dot(vector1, vector2)
        norm1 = np.linalg.norm(vector1)
        norm2 = np.linalg.norm(vector2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        similarity = dot_product / (norm1 * norm2)

        # Convert to 0-1 range (cosine similarity is -1 to 1)
        return (similarity + 1) / 2

    def extract_shared_features(
        self,
        metadata1: Dict[str, Any],
        metadata2: Dict[str, Any]
    ) -> List[str]:
        """
        Extract shared features between two charts
        Explains why they are similar
        """
        shared = []

        # Check exact matches
        if metadata1.get("sun_sign") == metadata2.get("sun_sign"):
            shared.append(f"Same Sun sign ({metadata1['sun_sign']})")

        if metadata1.get("moon_sign") == metadata2.get("moon_sign"):
            shared.append(f"Same Moon sign ({metadata1['moon_sign']})")

        if metadata1.get("ascendant") == metadata2.get("ascendant"):
            shared.append(f"Same Ascendant ({metadata1['ascendant']})")

        # Check dominant planet overlap
        planets1 = set(metadata1.get("dominant_planets", []))
        planets2 = set(metadata2.get("dominant_planets", []))
        common_planets = planets1 & planets2
        if common_planets:
            shared.append(f"Shared dominant planets: {', '.join(common_planets)}")

        # Check yoga overlap
        yogas1 = set(metadata1.get("major_yogas", []))
        yogas2 = set(metadata2.get("major_yogas", []))
        common_yogas = yogas1 & yogas2
        if common_yogas:
            shared.append(f"Shared yogas: {', '.join(list(common_yogas)[:3])}")

        # Check dasha match
        if metadata1.get("current_dasha_md") == metadata2.get("current_dasha_md"):
            shared.append(f"Both in {metadata1['current_dasha_md']} Mahadasha")

        # Check Saturn phase
        if metadata1.get("saturn_phase") == metadata2.get("saturn_phase"):
            phase = metadata1["saturn_phase"]
            if phase != "Normal":
                shared.append(f"Both experiencing {phase}")

        # Check life stage
        if metadata1.get("life_stage") == metadata2.get("life_stage"):
            shared.append(f"Same life stage ({metadata1['life_stage']} years)")

        return shared
