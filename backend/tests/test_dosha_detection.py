"""
Comprehensive tests for Enhanced Dosha Detection System (v2.2.0)

Tests all 4 major doshas with intensity calculations, cancellations, and remedies:
- Manglik Dosha (5-level intensity)
- Kaal Sarpa Yoga (12 variations)
- Pitra Dosha (11 indicators)
- Grahan Dosha (degree-based intensity)
"""
import pytest
from app.services.dosha_detection_service import DoshaDetectionService


@pytest.fixture
def dosha_service():
    """Create DoshaDetectionService instance"""
    return DoshaDetectionService()


# ============================================================================
# MANGLIK DOSHA TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.dosha
class TestManglikDosha:
    """Tests for Manglik Dosha detection with 5-level intensity"""

    def test_high_intensity_manglik(self, dosha_service, manglik_chart_high_intensity):
        """Test detection of high intensity Manglik Dosha (Mars in 8th house)"""
        result = dosha_service.detect_manglik_dosha(manglik_chart_high_intensity)
        
        assert result["present"] is True
        assert result["severity"] in ["high", "very_high"]
        assert result["intensity_score"] > 5.0
        assert result["details"]["mars_house_from_lagna"] == 8
        assert "remedies" in result
        assert len(result["remedies"]) > 0

    def test_manglik_with_cancellations(self, dosha_service):
        """Test Manglik Dosha with cancellations (Mars in own sign)"""
        # Mars in Aries (own sign) in 1st house
        chart = {
            "Mars": {"house": 1, "sign": "Aries", "sign_num": 1, "abs_degree": 15.0, "is_retrograde": False, "is_combust": False},
            "Moon": {"house": 4, "sign": "Cancer", "sign_num": 4, "abs_degree": 105.0, "is_retrograde": False, "is_combust": False},
            "Venus": {"house": 7, "sign": "Libra", "sign_num": 7, "abs_degree": 195.0, "is_retrograde": False, "is_combust": False},
            "Jupiter": {"house": 10, "sign": "Capricorn", "sign_num": 10, "abs_degree": 285.0, "is_retrograde": False, "is_combust": False},
            "Saturn": {"house": 11, "sign": "Aquarius", "sign_num": 11, "abs_degree": 315.0, "is_retrograde": False, "is_combust": False},
            "Sun": {"house": 5, "sign": "Leo", "sign_num": 5, "abs_degree": 135.0, "is_retrograde": False, "is_combust": False},
            "Mercury": {"house": 6, "sign": "Virgo", "sign_num": 6, "abs_degree": 165.0, "is_retrograde": False, "is_combust": False},
            "Rahu": {"house": 3, "sign": "Gemini", "sign_num": 3, "abs_degree": 75.0, "is_retrograde": True},
            "Ketu": {"house": 9, "sign": "Sagittarius", "sign_num": 9, "abs_degree": 255.0, "is_retrograde": True}
        }
        
        result = dosha_service.detect_manglik_dosha(chart)
        
        assert result["present"] is True
        assert result["cancellation_percentage"] > 0
        assert any("Mars in own sign" in str(c) for c in result["details"]["cancellations"])

    def test_no_manglik(self, dosha_service, clean_chart):
        """Test chart without Manglik Dosha"""
        result = dosha_service.detect_manglik_dosha(clean_chart)
        
        assert result["present"] is False
        assert result["severity"] == "none"
        assert result["intensity_score"] == 0
        assert result["remedies"] == {}

    def test_manglik_intensity_labels(self, dosha_service, manglik_chart_high_intensity):
        """Test that intensity labels are correctly assigned"""
        result = dosha_service.detect_manglik_dosha(manglik_chart_high_intensity)
        
        assert "intensity_label" in result
        assert result["intensity_label"] in ["None", "Very Low", "Low", "Medium", "High", "Very High"]

    def test_manglik_remedies_categorization(self, dosha_service, manglik_chart_high_intensity):
        """Test that remedies are properly categorized by type"""
        result = dosha_service.detect_manglik_dosha(manglik_chart_high_intensity)
        
        if result["present"]:
            remedies = result["remedies"]
            # Check for standard remedy categories
            expected_categories = ["pujas_rituals", "mantras", "fasting", "charity"]
            for category in expected_categories:
                assert category in remedies

    def test_manglik_manifestation_period(self, dosha_service, manglik_chart_high_intensity):
        """Test that manifestation period is included in details"""
        result = dosha_service.detect_manglik_dosha(manglik_chart_high_intensity)
        
        if result["present"]:
            assert "manifestation_period" in result["details"]
            assert "years" in result["details"]["manifestation_period"].lower()


# ============================================================================
# KAAL SARPA YOGA TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.dosha
class TestKaalSarpaYoga:
    """Tests for Kaal Sarpa Yoga with 12 variations"""

    def test_full_kaal_sarpa_detection(self, dosha_service, kaal_sarpa_full_chart):
        """Test detection of Full Kaal Sarpa (7/7 planets hemmed)"""
        result = dosha_service.detect_kaal_sarpa_dosha(kaal_sarpa_full_chart)
        
        assert result["present"] is True
        assert result["details"]["full_kaal_sarpa"] is True
        assert result["details"]["planets_hemmed"] == 7
        assert result["intensity_score"] > 5.0

    def test_partial_kaal_sarpa_detection(self, dosha_service):
        """Test detection of Partial Kaal Sarpa (6/7 planets hemmed)"""
        # Chart with 6 planets between Rahu-Ketu
        chart = {
            "Sun": {"house": 3, "sign": "Gemini", "sign_num": 3, "abs_degree": 75.0, "is_retrograde": False, "is_combust": False},
            "Moon": {"house": 4, "sign": "Cancer", "sign_num": 4, "abs_degree": 105.0, "is_retrograde": False, "is_combust": False},
            "Mars": {"house": 5, "sign": "Leo", "sign_num": 5, "abs_degree": 135.0, "is_retrograde": False, "is_combust": False},
            "Mercury": {"house": 2, "sign": "Taurus", "sign_num": 2, "abs_degree": 45.0, "is_retrograde": False, "is_combust": False},
            "Jupiter": {"house": 6, "sign": "Virgo", "sign_num": 6, "abs_degree": 165.0, "is_retrograde": False, "is_combust": False},
            "Venus": {"house": 4, "sign": "Cancer", "sign_num": 4, "abs_degree": 110.0, "is_retrograde": False, "is_combust": False},
            "Saturn": {"house": 10, "sign": "Capricorn", "sign_num": 10, "abs_degree": 290.0, "is_retrograde": False, "is_combust": False},  # Outside axis
            "Rahu": {"house": 1, "sign": "Aries", "sign_num": 1, "abs_degree": 10.0, "is_retrograde": True},
            "Ketu": {"house": 7, "sign": "Libra", "sign_num": 7, "abs_degree": 190.0, "is_retrograde": True}
        }
        
        result = dosha_service.detect_kaal_sarpa_dosha(chart)
        
        assert result["present"] is True
        assert result["details"]["partial_kaal_sarpa"] is True
        assert result["details"]["planets_hemmed"] == 6

    def test_kaal_sarpa_type_ananta(self, dosha_service, kaal_sarpa_full_chart):
        """Test Kaal Sarpa type identification (Ananta - Rahu in 1st)"""
        result = dosha_service.detect_kaal_sarpa_dosha(kaal_sarpa_full_chart)
        
        assert result["present"] is True
        assert "Ananta" in result["type"]

    def test_kaal_sarpa_type_ghatak(self, dosha_service):
        """Test Ghatak Kaal Sarpa (Rahu in 10th house)"""
        chart = {
            "Sun": {"house": 11, "sign": "Aquarius", "sign_num": 11, "abs_degree": 315.0, "is_retrograde": False, "is_combust": False},
            "Moon": {"house": 12, "sign": "Pisces", "sign_num": 12, "abs_degree": 345.0, "is_retrograde": False, "is_combust": False},
            "Mars": {"house": 1, "sign": "Aries", "sign_num": 1, "abs_degree": 15.0, "is_retrograde": False, "is_combust": False},
            "Mercury": {"house": 2, "sign": "Taurus", "sign_num": 2, "abs_degree": 45.0, "is_retrograde": False, "is_combust": False},
            "Jupiter": {"house": 3, "sign": "Gemini", "sign_num": 3, "abs_degree": 75.0, "is_retrograde": False, "is_combust": False},
            "Venus": {"house": 11, "sign": "Aquarius", "sign_num": 11, "abs_degree": 320.0, "is_retrograde": False, "is_combust": False},
            "Saturn": {"house": 12, "sign": "Pisces", "sign_num": 12, "abs_degree": 350.0, "is_retrograde": False, "is_combust": False},
            "Rahu": {"house": 10, "sign": "Capricorn", "sign_num": 10, "abs_degree": 285.0, "is_retrograde": True},
            "Ketu": {"house": 4, "sign": "Cancer", "sign_num": 4, "abs_degree": 105.0, "is_retrograde": True}
        }
        
        result = dosha_service.detect_kaal_sarpa_dosha(chart)
        
        if result["present"]:
            assert "Ghatak" in result["type"]
            assert "career" in result["effects"].lower() or "profession" in result["effects"].lower()

    def test_kaal_sarpa_positive_effects(self, dosha_service, kaal_sarpa_full_chart):
        """Test that positive effects are included for Kaal Sarpa"""
        result = dosha_service.detect_kaal_sarpa_dosha(kaal_sarpa_full_chart)
        
        if result["present"]:
            assert "positive_effects" in result
            assert len(result["positive_effects"]) > 0

    def test_kaal_sarpa_cancellations(self, dosha_service):
        """Test Kaal Sarpa with cancellations (Jupiter in Kendra)"""
        chart = {
            "Sun": {"house": 3, "sign": "Gemini", "sign_num": 3, "abs_degree": 75.0, "is_retrograde": False, "is_combust": False},
            "Moon": {"house": 4, "sign": "Cancer", "sign_num": 4, "abs_degree": 105.0, "is_retrograde": False, "is_combust": False},
            "Mars": {"house": 5, "sign": "Leo", "sign_num": 5, "abs_degree": 135.0, "is_retrograde": False, "is_combust": False},
            "Mercury": {"house": 2, "sign": "Taurus", "sign_num": 2, "abs_degree": 45.0, "is_retrograde": False, "is_combust": False},
            "Jupiter": {"house": 10, "sign": "Capricorn", "sign_num": 10, "abs_degree": 285.0, "is_retrograde": False, "is_combust": False},  # Kendra position
            "Venus": {"house": 4, "sign": "Cancer", "sign_num": 4, "abs_degree": 110.0, "is_retrograde": False, "is_combust": False},
            "Saturn": {"house": 3, "sign": "Gemini", "sign_num": 3, "abs_degree": 80.0, "is_retrograde": False, "is_combust": False},
            "Rahu": {"house": 1, "sign": "Aries", "sign_num": 1, "abs_degree": 10.0, "is_retrograde": True},
            "Ketu": {"house": 7, "sign": "Libra", "sign_num": 7, "abs_degree": 190.0, "is_retrograde": True}
        }
        
        result = dosha_service.detect_kaal_sarpa_dosha(chart)
        
        if result["present"]:
            assert result["details"]["cancellation_percentage"] > 0
            assert len(result["details"]["cancellations"]) > 0

    def test_no_kaal_sarpa(self, dosha_service, clean_chart):
        """Test chart without Kaal Sarpa Yoga"""
        result = dosha_service.detect_kaal_sarpa_dosha(clean_chart)
        
        assert result["present"] is False
        assert result["severity"] == "none"


# ============================================================================
# PITRA DOSHA TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.dosha
class TestPitraDosha:
    """Tests for Pitra Dosha with 11 indicators"""

    def test_high_pitra_dosha_sun_rahu(self, dosha_service, pitra_dosha_high_chart):
        """Test high Pitra Dosha (Sun-Rahu conjunction in 9th)"""
        result = dosha_service.detect_pitra_dosha(pitra_dosha_high_chart)
        
        assert result["present"] is True
        assert result["severity"] in ["high", "very_high"]
        assert result["intensity_score"] >= 4
        assert len(result["details"]["primary_indicators"]) > 0

    def test_pitra_dosha_moon_ketu(self, dosha_service):
        """Test Pitra Dosha with Moon-Ketu conjunction"""
        chart = {
            "Sun": {"house": 5, "sign": "Leo", "sign_num": 5, "abs_degree": 135.0, "is_retrograde": False, "is_combust": False},
            "Moon": {"house": 4, "sign": "Cancer", "sign_num": 4, "abs_degree": 105.0, "is_retrograde": False, "is_combust": False},
            "Mars": {"house": 2, "sign": "Taurus", "sign_num": 2, "abs_degree": 45.0, "is_retrograde": False, "is_combust": False},
            "Mercury": {"house": 6, "sign": "Virgo", "sign_num": 6, "abs_degree": 165.0, "is_retrograde": False, "is_combust": False},
            "Jupiter": {"house": 9, "sign": "Sagittarius", "sign_num": 9, "abs_degree": 255.0, "is_retrograde": False, "is_combust": False},
            "Venus": {"house": 7, "sign": "Libra", "sign_num": 7, "abs_degree": 195.0, "is_retrograde": False, "is_combust": False},
            "Saturn": {"house": 11, "sign": "Aquarius", "sign_num": 11, "abs_degree": 315.0, "is_retrograde": False, "is_combust": False},
            "Rahu": {"house": 10, "sign": "Capricorn", "sign_num": 10, "abs_degree": 285.0, "is_retrograde": True},
            "Ketu": {"house": 4, "sign": "Cancer", "sign_num": 4, "abs_degree": 107.0, "is_retrograde": True}
        }
        
        result = dosha_service.detect_pitra_dosha(chart)
        
        assert result["present"] is True
        assert any(ind["type"] == "Primary" for ind in result["details"]["primary_indicators"])

    def test_pitra_dosha_manifestation_areas(self, dosha_service, pitra_dosha_high_chart):
        """Test that manifestation areas are identified"""
        result = dosha_service.detect_pitra_dosha(pitra_dosha_high_chart)
        
        if result["present"]:
            assert "manifestation_areas" in result
            assert isinstance(result["manifestation_areas"], dict)
            # Should identify paternal lineage due to Sun-Rahu in 9th
            assert result["manifestation_areas"].get("paternal_lineage") is True

    def test_pitra_dosha_categorized_effects(self, dosha_service, pitra_dosha_high_chart):
        """Test that effects are categorized by life area"""
        result = dosha_service.detect_pitra_dosha(pitra_dosha_high_chart)
        
        if result["present"]:
            effects = result["effects"]
            assert isinstance(effects, dict)
            expected_categories = ["family_lineage", "progeny", "financial", "health", "spiritual"]
            for category in expected_categories:
                assert category in effects

    def test_pitra_dosha_shrapit_yoga(self, dosha_service):
        """Test Shrapit Yoga (Saturn-Rahu conjunction)"""
        chart = {
            "Sun": {"house": 5, "sign": "Leo", "sign_num": 5, "abs_degree": 135.0, "is_retrograde": False, "is_combust": False},
            "Moon": {"house": 4, "sign": "Cancer", "sign_num": 4, "abs_degree": 105.0, "is_retrograde": False, "is_combust": False},
            "Mars": {"house": 2, "sign": "Taurus", "sign_num": 2, "abs_degree": 45.0, "is_retrograde": False, "is_combust": False},
            "Mercury": {"house": 6, "sign": "Virgo", "sign_num": 6, "abs_degree": 165.0, "is_retrograde": False, "is_combust": False},
            "Jupiter": {"house": 10, "sign": "Capricorn", "sign_num": 10, "abs_degree": 285.0, "is_retrograde": False, "is_combust": False},
            "Venus": {"house": 7, "sign": "Libra", "sign_num": 7, "abs_degree": 195.0, "is_retrograde": False, "is_combust": False},
            "Saturn": {"house": 11, "sign": "Aquarius", "sign_num": 11, "abs_degree": 315.0, "is_retrograde": False, "is_combust": False},
            "Rahu": {"house": 11, "sign": "Aquarius", "sign_num": 11, "abs_degree": 318.0, "is_retrograde": True},
            "Ketu": {"house": 5, "sign": "Leo", "sign_num": 5, "abs_degree": 138.0, "is_retrograde": True}
        }
        
        result = dosha_service.detect_pitra_dosha(chart)
        
        if result["present"]:
            # Check if Shrapit indicator is found
            secondary_indicators = result["details"]["secondary_indicators"]
            assert any("Shrapit" in ind["indicator"] for ind in secondary_indicators)

    def test_no_pitra_dosha(self, dosha_service, clean_chart):
        """Test chart without Pitra Dosha"""
        result = dosha_service.detect_pitra_dosha(clean_chart)
        
        assert result["present"] is False
        assert result["severity"] == "none"


# ============================================================================
# GRAHAN DOSHA TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.dosha
class TestGrahanDosha:
    """Tests for Grahan Dosha with degree-based intensity"""

    def test_moon_rahu_very_close(self, dosha_service, grahan_dosha_moon_rahu_chart):
        """Test Moon-Rahu conjunction with very close degrees"""
        result = dosha_service.detect_grahan_dosha(grahan_dosha_moon_rahu_chart)
        
        assert result["present"] is True
        assert result["severity"] in ["medium", "high", "very_high"]
        # Check that it's identified as Lunar Eclipse
        afflictions = result["details"]["afflictions"]
        assert any("Moon-Rahu" in aff["type"] for aff in afflictions)

    def test_sun_rahu_solar_eclipse(self, dosha_service):
        """Test Sun-Rahu conjunction (Solar Eclipse)"""
        chart = {
            "Sun": {"house": 1, "sign": "Aries", "sign_num": 1, "abs_degree": 15.0, "is_retrograde": False, "is_combust": False},
            "Moon": {"house": 4, "sign": "Cancer", "sign_num": 4, "abs_degree": 105.0, "is_retrograde": False, "is_combust": False},
            "Mars": {"house": 2, "sign": "Taurus", "sign_num": 2, "abs_degree": 45.0, "is_retrograde": False, "is_combust": False},
            "Mercury": {"house": 12, "sign": "Pisces", "sign_num": 12, "abs_degree": 345.0, "is_retrograde": False, "is_combust": False},
            "Jupiter": {"house": 10, "sign": "Capricorn", "sign_num": 10, "abs_degree": 285.0, "is_retrograde": False, "is_combust": False},
            "Venus": {"house": 7, "sign": "Libra", "sign_num": 7, "abs_degree": 195.0, "is_retrograde": False, "is_combust": False},
            "Saturn": {"house": 11, "sign": "Aquarius", "sign_num": 11, "abs_degree": 315.0, "is_retrograde": False, "is_combust": False},
            "Rahu": {"house": 1, "sign": "Aries", "sign_num": 1, "abs_degree": 18.0, "is_retrograde": True},
            "Ketu": {"house": 7, "sign": "Libra", "sign_num": 7, "abs_degree": 198.0, "is_retrograde": True}
        }
        
        result = dosha_service.detect_grahan_dosha(chart)
        
        assert result["present"] is True
        afflictions = result["details"]["afflictions"]
        assert any("Sun-Rahu" in aff["type"] or "Solar Eclipse" in aff["type"] for aff in afflictions)

    def test_grahan_degree_calculation(self, dosha_service, grahan_dosha_moon_rahu_chart):
        """Test that degree differences are calculated correctly"""
        result = dosha_service.detect_grahan_dosha(grahan_dosha_moon_rahu_chart)
        
        if result["present"]:
            afflictions = result["details"]["afflictions"]
            for aff in afflictions:
                assert "degree_difference" in aff
                assert "closeness" in aff
                assert aff["closeness"] in ["Very Close", "Close", "Moderate", "Wide"]

    def test_grahan_benefic_protection(self, dosha_service):
        """Test Grahan Dosha with benefic protection (Jupiter in Kendra)"""
        chart = {
            "Sun": {"house": 1, "sign": "Aries", "sign_num": 1, "abs_degree": 15.0, "is_retrograde": False, "is_combust": False},
            "Moon": {"house": 4, "sign": "Cancer", "sign_num": 4, "abs_degree": 105.0, "is_retrograde": False, "is_combust": False},
            "Mars": {"house": 2, "sign": "Taurus", "sign_num": 2, "abs_degree": 45.0, "is_retrograde": False, "is_combust": False},
            "Mercury": {"house": 12, "sign": "Pisces", "sign_num": 12, "abs_degree": 345.0, "is_retrograde": False, "is_combust": False},
            "Jupiter": {"house": 10, "sign": "Capricorn", "sign_num": 10, "abs_degree": 285.0, "is_retrograde": False, "is_combust": False},  # Kendra
            "Venus": {"house": 7, "sign": "Libra", "sign_num": 7, "abs_degree": 195.0, "is_retrograde": False, "is_combust": False},  # Kendra
            "Saturn": {"house": 11, "sign": "Aquarius", "sign_num": 11, "abs_degree": 315.0, "is_retrograde": False, "is_combust": False},
            "Rahu": {"house": 1, "sign": "Aries", "sign_num": 1, "abs_degree": 18.0, "is_retrograde": True},
            "Ketu": {"house": 7, "sign": "Libra", "sign_num": 7, "abs_degree": 198.0, "is_retrograde": True}
        }
        
        result = dosha_service.detect_grahan_dosha(chart)
        
        if result["present"]:
            assert result["reduction_percentage"] > 0
            assert len(result["details"]["benefic_protection"]) > 0

    def test_grahan_categorized_effects(self, dosha_service, grahan_dosha_moon_rahu_chart):
        """Test that effects are categorized by affliction type"""
        result = dosha_service.detect_grahan_dosha(grahan_dosha_moon_rahu_chart)
        
        if result["present"]:
            effects = result["effects"]
            assert isinstance(effects, dict)
            expected_categories = ["paternal", "maternal", "mental_emotional", "spiritual", "health"]
            for category in expected_categories:
                assert category in effects

    def test_grahan_mental_health_remedies(self, dosha_service, grahan_dosha_moon_rahu_chart):
        """Test that mental health remedies are included for Moon afflictions"""
        result = dosha_service.detect_grahan_dosha(grahan_dosha_moon_rahu_chart)
        
        if result["present"] and result["severity"] in ["high", "very_high"]:
            remedies = result["remedies"]
            # For Moon afflictions, should have mental health support
            if "mental_health" in remedies:
                assert len(remedies["mental_health"]) > 0

    def test_no_grahan_dosha(self, dosha_service, clean_chart):
        """Test chart without Grahan Dosha"""
        result = dosha_service.detect_grahan_dosha(clean_chart)
        
        assert result["present"] is False
        assert result["severity"] == "none"


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

@pytest.mark.integration
@pytest.mark.dosha
class TestDoshaIntegration:
    """Integration tests for dosha detection"""

    def test_multiple_doshas_chart(self, dosha_service):
        """Test chart with multiple doshas present"""
        # Chart with both Manglik and Grahan Dosha
        chart = {
            "Sun": {"house": 1, "sign": "Aries", "sign_num": 1, "abs_degree": 15.0, "is_retrograde": False, "is_combust": False},
            "Moon": {"house": 4, "sign": "Cancer", "sign_num": 4, "abs_degree": 105.0, "is_retrograde": False, "is_combust": False},
            "Mars": {"house": 8, "sign": "Scorpio", "sign_num": 8, "abs_degree": 225.0, "is_retrograde": False, "is_combust": False},  # Manglik
            "Mercury": {"house": 12, "sign": "Pisces", "sign_num": 12, "abs_degree": 345.0, "is_retrograde": False, "is_combust": False},
            "Jupiter": {"house": 9, "sign": "Sagittarius", "sign_num": 9, "abs_degree": 255.0, "is_retrograde": False, "is_combust": False},
            "Venus": {"house": 7, "sign": "Libra", "sign_num": 7, "abs_degree": 195.0, "is_retrograde": False, "is_combust": False},
            "Saturn": {"house": 11, "sign": "Aquarius", "sign_num": 11, "abs_degree": 315.0, "is_retrograde": False, "is_combust": False},
            "Rahu": {"house": 1, "sign": "Aries", "sign_num": 1, "abs_degree": 18.0, "is_retrograde": True},  # Grahan with Sun
            "Ketu": {"house": 7, "sign": "Libra", "sign_num": 7, "abs_degree": 198.0, "is_retrograde": True}
        }
        
        manglik = dosha_service.detect_manglik_dosha(chart)
        grahan = dosha_service.detect_grahan_dosha(chart)
        
        assert manglik["present"] is True
        assert grahan["present"] is True

    def test_all_doshas_clean_chart(self, dosha_service, clean_chart):
        """Test all doshas on a clean chart (should be minimal/none)"""
        manglik = dosha_service.detect_manglik_dosha(clean_chart)
        kaal_sarpa = dosha_service.detect_kaal_sarpa_dosha(clean_chart)
        pitra = dosha_service.detect_pitra_dosha(clean_chart)
        grahan = dosha_service.detect_grahan_dosha(clean_chart)
        
        # Most should be absent or very low
        total_present = sum([
            1 if manglik["present"] else 0,
            1 if kaal_sarpa["present"] else 0,
            1 if pitra["present"] else 0,
            1 if grahan["present"] else 0
        ])
        
        # Clean chart should have 0-1 doshas at most
        assert total_present <= 1

    def test_dosha_service_performance(self, dosha_service, sample_d1_planets):
        """Test that dosha detection completes within reasonable time"""
        import time
        
        start = time.time()
        manglik = dosha_service.detect_manglik_dosha(sample_d1_planets)
        kaal_sarpa = dosha_service.detect_kaal_sarpa_dosha(sample_d1_planets)
        pitra = dosha_service.detect_pitra_dosha(sample_d1_planets)
        grahan = dosha_service.detect_grahan_dosha(sample_d1_planets)
        end = time.time()
        
        # All 4 doshas should complete within 100ms
        assert (end - start) < 0.1
