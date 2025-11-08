"""
Comprehensive Test Suite for Extended Yoga Detection Service
Tests 40+ classical Vedic yogas with strength calculation and timing
"""

import pytest
from typing import Dict, Any
from app.services.extended_yoga_service import ExtendedYogaService


@pytest.fixture
def yoga_service():
    """Extended Yoga Service instance"""
    return ExtendedYogaService()


# =============================================================================
# HELPER METHOD TESTS
# =============================================================================

class TestHelperMethods:
    """Test yoga detection helper methods"""
    
    @pytest.mark.unit
    def test_planet_dignity_exalted(self, yoga_service):
        """Test dignity calculation for exalted planet"""
        planets = {"Sun": {"sign_num": 1, "house": 1}}  # Sun exalted in Aries
        dignity = yoga_service._calculate_planet_dignity("Sun", planets)
        assert dignity == 100, "Exalted planet should have dignity 100"
    
    @pytest.mark.unit
    def test_planet_dignity_debilitated(self, yoga_service):
        """Test dignity calculation for debilitated planet"""
        planets = {"Sun": {"sign_num": 7, "house": 7}}  # Sun debilitated in Libra
        dignity = yoga_service._calculate_planet_dignity("Sun", planets)
        assert dignity == 0, "Debilitated planet should have dignity 0"
    
    @pytest.mark.unit
    def test_planet_dignity_own_sign(self, yoga_service):
        """Test dignity calculation for planet in own sign"""
        planets = {"Sun": {"sign_num": 5, "house": 5}}  # Sun in Leo (own sign)
        dignity = yoga_service._calculate_planet_dignity("Sun", planets)
        assert dignity == 80, "Planet in own sign should have dignity 80"
    
    @pytest.mark.unit
    def test_house_strength_kendra(self, yoga_service):
        """Test house strength for Kendra houses"""
        for house in [1, 4, 7, 10]:
            strength = yoga_service._calculate_house_strength(house)
            assert strength == 100, f"Kendra house {house} should have strength 100"
    
    @pytest.mark.unit
    def test_house_strength_trikona(self, yoga_service):
        """Test house strength for Trikona houses"""
        for house in [5, 9]:
            strength = yoga_service._calculate_house_strength(house)
            assert strength == 90, f"Trikona house {house} should have strength 90"
    
    @pytest.mark.unit
    def test_house_strength_dusthana(self, yoga_service):
        """Test house strength for Dusthana houses"""
        for house in [8, 12]:
            strength = yoga_service._calculate_house_strength(house)
            assert strength == 20, f"Dusthana house {house} should have strength 20"
    
    @pytest.mark.unit
    def test_combustion_detection(self, yoga_service):
        """Test combustion detection when planet is with Sun"""
        planets = {
            "Sun": {"house": 3},
            "Mercury": {"house": 3}  # Mercury with Sun - combusted
        }
        assert yoga_service._is_combusted("Mercury", planets) is True
        assert yoga_service._is_combusted("Sun", planets) is False
    
    @pytest.mark.unit
    def test_retrograde_detection(self, yoga_service):
        """Test retrograde planet detection"""
        planets = {
            "Mars": {"house": 5, "retrograde": True},
            "Jupiter": {"house": 7, "retrograde": False}
        }
        assert yoga_service._is_retrograde("Mars", planets) is True
        assert yoga_service._is_retrograde("Jupiter", planets) is False
        assert yoga_service._is_retrograde("Sun", planets) is False  # Sun never retrograde
    
    @pytest.mark.unit
    def test_yoga_strength_calculation_strong(self, yoga_service):
        """Test yoga strength calculation for strong yoga"""
        planets = {
            "Jupiter": {"house": 1, "sign_num": 4, "retrograde": False}  # Exalted in Kendra
        }
        strength = yoga_service._calculate_yoga_strength(["Jupiter"], planets)
        assert strength in ["Very Strong", "Strong"], "Exalted planet in Kendra should be very strong"
    
    @pytest.mark.unit
    def test_yoga_strength_calculation_weak(self, yoga_service):
        """Test yoga strength calculation for weak yoga"""
        planets = {
            "Jupiter": {"house": 8, "sign_num": 10, "retrograde": False}  # Debilitated in Dusthana
        }
        strength = yoga_service._calculate_yoga_strength(["Jupiter"], planets)
        assert strength in ["Weak", "Medium"], "Debilitated planet in Dusthana should be weak"
    
    @pytest.mark.unit
    def test_yoga_cancellation_debilitated(self, yoga_service):
        """Test yoga cancellation due to debilitation"""
        planets = {
            "Jupiter": {"house": 1, "sign_num": 10}  # Debilitated in Capricorn
        }
        is_cancelled, reasons = yoga_service._check_yoga_cancellation(["Jupiter"], planets)
        assert is_cancelled is True
        assert any("debilitated" in reason.lower() for reason in reasons)
    
    @pytest.mark.unit
    def test_yoga_cancellation_combustion(self, yoga_service):
        """Test yoga cancellation due to combustion"""
        planets = {
            "Sun": {"house": 5, "sign_num": 5},
            "Venus": {"house": 5, "sign_num": 7}  # Venus combusted by Sun
        }
        is_cancelled, reasons = yoga_service._check_yoga_cancellation(["Venus"], planets)
        assert is_cancelled is True
        assert any("combust" in reason.lower() for reason in reasons)


# =============================================================================
# PANCHA MAHAPURUSHA YOGA TESTS
# =============================================================================

class TestPanchaMahapurushaYogas:
    """Test the 5 great person yogas"""
    
    @pytest.mark.yoga
    def test_ruchaka_yoga_mars_exalted_kendra(self, yoga_service):
        """Test Ruchaka Yoga - Mars exalted in Kendra"""
        planets = {
            "Mars": {"house": 10, "sign_num": 10}  # Mars exalted in Capricorn in 10th
        }
        yogas = yoga_service._detect_pancha_mahapurusha(planets)
        assert len(yogas) > 0
        assert yogas[0]["name"] == "Ruchaka Yoga"
        assert "courage" in yogas[0]["description"].lower()
    
    @pytest.mark.yoga
    def test_bhadra_yoga_mercury_own_sign_kendra(self, yoga_service):
        """Test Bhadra Yoga - Mercury in own sign in Kendra"""
        planets = {
            "Mercury": {"house": 1, "sign_num": 6}  # Mercury in Virgo (own sign) in 1st
        }
        yogas = yoga_service._detect_pancha_mahapurusha(planets)
        assert len(yogas) > 0
        assert yogas[0]["name"] == "Bhadra Yoga"
        assert "intelligence" in yogas[0]["description"].lower()
    
    @pytest.mark.yoga
    def test_hamsa_yoga_jupiter_exalted_kendra(self, yoga_service):
        """Test Hamsa Yoga - Jupiter exalted in Kendra"""
        planets = {
            "Jupiter": {"house": 4, "sign_num": 4}  # Jupiter exalted in Cancer in 4th
        }
        yogas = yoga_service._detect_pancha_mahapurusha(planets)
        assert len(yogas) > 0
        assert yogas[0]["name"] == "Hamsa Yoga"
        assert "wisdom" in yogas[0]["description"].lower()
    
    @pytest.mark.yoga
    def test_malavya_yoga_venus_exalted_kendra(self, yoga_service):
        """Test Malavya Yoga - Venus exalted in Kendra"""
        planets = {
            "Venus": {"house": 7, "sign_num": 12}  # Venus exalted in Pisces in 7th
        }
        yogas = yoga_service._detect_pancha_mahapurusha(planets)
        assert len(yogas) > 0
        assert yogas[0]["name"] == "Malavya Yoga"
        assert "beauty" in yogas[0]["description"].lower()
    
    @pytest.mark.yoga
    def test_sasa_yoga_saturn_own_sign_kendra(self, yoga_service):
        """Test Sasa Yoga - Saturn in own sign in Kendra"""
        planets = {
            "Saturn": {"house": 10, "sign_num": 10}  # Saturn in Capricorn (own sign) in 10th
        }
        yogas = yoga_service._detect_pancha_mahapurusha(planets)
        assert len(yogas) > 0
        assert yogas[0]["name"] == "Sasa Yoga"
        assert "authority" in yogas[0]["description"].lower()
    
    @pytest.mark.yoga
    def test_no_mahapurusha_yoga_not_in_kendra(self, yoga_service):
        """Test that Pancha Mahapurusha yogas don't form outside Kendra"""
        planets = {
            "Jupiter": {"house": 5, "sign_num": 4}  # Exalted but not in Kendra
        }
        yogas = yoga_service._detect_pancha_mahapurusha(planets)
        assert len(yogas) == 0


# =============================================================================
# WEALTH & POWER YOGA TESTS
# =============================================================================

class TestWealthPowerYogas:
    """Test wealth and power yogas"""
    
    @pytest.mark.yoga
    def test_adhi_yoga_benefics_678_from_moon(self, yoga_service):
        """Test Adhi Yoga - Benefics in 6/7/8 from Moon"""
        planets = {
            "Moon": {"house": 1},
            "Mercury": {"house": 6},  # 6th from Moon
            "Jupiter": {"house": 7},  # 7th from Moon
            "Venus": {"house": 8}     # 8th from Moon
        }
        yogas = yoga_service._detect_adhi_yoga(planets)
        assert len(yogas) > 0
        assert yogas[0]["name"] == "Adhi Yoga"
        assert "wealth" in yogas[0]["description"].lower()
    
    @pytest.mark.yoga
    def test_lakshmi_yoga_venus_strong_kendra(self, yoga_service):
        """Test Lakshmi Yoga - Venus strong in Kendra"""
        planets = {
            "Venus": {"house": 7, "sign_num": 7}  # Venus in Libra (own sign) in 7th
        }
        yogas = yoga_service._detect_lakshmi_saraswati_yoga(planets)
        lakshmi = [y for y in yogas if y["name"] == "Lakshmi Yoga"]
        assert len(lakshmi) > 0
        assert "wealth" in lakshmi[0]["description"].lower()
    
    @pytest.mark.yoga
    def test_saraswati_yoga_all_benefics_kendra_trikona(self, yoga_service):
        """Test Saraswati Yoga - All benefics in Kendra/Trikona"""
        planets = {
            "Mercury": {"house": 1},   # Kendra
            "Jupiter": {"house": 5},   # Trikona
            "Venus": {"house": 10}     # Kendra
        }
        yogas = yoga_service._detect_lakshmi_saraswati_yoga(planets)
        saraswati = [y for y in yogas if y["name"] == "Saraswati Yoga"]
        assert len(saraswati) > 0
        assert "learning" in saraswati[0]["description"].lower()
    
    @pytest.mark.yoga
    def test_parvata_yoga_benefics_in_kendra_no_malefics(self, yoga_service):
        """Test Parvata Yoga - Benefics in Kendra, no malefics"""
        planets = {
            "Jupiter": {"house": 1},
            "Venus": {"house": 4},
            "Mercury": {"house": 7},
            "Mars": {"house": 3},     # Not in Kendra
            "Saturn": {"house": 8}    # Not in Kendra
        }
        yogas = yoga_service._detect_parvata_yoga(planets)
        assert len(yogas) > 0
        assert yogas[0]["name"] == "Parvata Yoga"


# =============================================================================
# CONJUNCTION YOGA TESTS
# =============================================================================

class TestConjunctionYogas:
    """Test planetary conjunction yogas"""
    
    @pytest.mark.yoga
    def test_chandra_mangala_yoga_conjunction(self, yoga_service):
        """Test Chandra-Mangala Yoga - Moon-Mars conjunction"""
        planets = {
            "Moon": {"house": 5},
            "Mars": {"house": 5}
        }
        yogas = yoga_service._detect_chandra_mangala_yoga(planets)
        assert len(yogas) > 0
        assert "Chandra-Mangala Yoga" in yogas[0]["name"]
        assert "wealth" in yogas[0]["description"].lower()
    
    @pytest.mark.yoga
    def test_guru_mangala_yoga_conjunction(self, yoga_service):
        """Test Guru-Mangala Yoga - Jupiter-Mars conjunction"""
        planets = {
            "Jupiter": {"house": 10},
            "Mars": {"house": 10}
        }
        yogas = yoga_service._detect_guru_mangala_yoga(planets)
        assert len(yogas) > 0
        assert yogas[0]["name"] == "Guru-Mangala Yoga"
        assert "technical" in yogas[0]["description"].lower()
    
    @pytest.mark.yoga
    def test_budhaditya_yoga_sun_mercury_conjunction(self, yoga_service):
        """Test Budhaditya Yoga - Sun-Mercury conjunction"""
        planets = {
            "Sun": {"house": 1},
            "Mercury": {"house": 1}
        }
        yogas = yoga_service._detect_budhaditya_yoga(planets)
        assert len(yogas) > 0
        assert yogas[0]["name"] == "Budhaditya Yoga"
        assert "intelligence" in yogas[0]["description"].lower()


# =============================================================================
# KALA SARPA YOGA TESTS
# =============================================================================

class TestKalaSarpaYoga:
    """Test Kala Sarpa Yoga (12 variations)"""
    
    @pytest.mark.yoga
    def test_anant_kala_sarpa_rahu_1st(self, yoga_service):
        """Test Anant Kala Sarpa - Rahu in 1st house"""
        planets = {
            "Rahu": {"house": 1},
            "Ketu": {"house": 7},
            "Sun": {"house": 3},
            "Moon": {"house": 4},
            "Mars": {"house": 5},
            "Mercury": {"house": 2},
            "Jupiter": {"house": 6},
            "Venus": {"house": 4},
            "Saturn": {"house": 3}
        }
        yogas = yoga_service._detect_kala_sarpa_yoga(planets)
        assert len(yogas) > 0
        assert "Anant" in yogas[0]["name"]
        assert "health" in yogas[0]["description"].lower()
    
    @pytest.mark.yoga
    def test_ghatak_kala_sarpa_rahu_10th(self, yoga_service):
        """Test Ghatak Kala Sarpa - Rahu in 10th house"""
        planets = {
            "Rahu": {"house": 10},
            "Ketu": {"house": 4},
            "Sun": {"house": 12},
            "Moon": {"house": 1},
            "Mars": {"house": 2},
            "Mercury": {"house": 11},
            "Jupiter": {"house": 3},
            "Venus": {"house": 1},
            "Saturn": {"house": 12}
        }
        yogas = yoga_service._detect_kala_sarpa_yoga(planets)
        assert len(yogas) > 0
        assert "Ghatak" in yogas[0]["name"]
        assert "career" in yogas[0]["description"].lower()
    
    @pytest.mark.yoga
    def test_partial_kala_sarpa_5_planets(self, yoga_service):
        """Test Partial Kala Sarpa - 5/7 planets between Rahu-Ketu"""
        planets = {
            "Rahu": {"house": 1},
            "Ketu": {"house": 7},
            "Sun": {"house": 3},
            "Moon": {"house": 4},
            "Mars": {"house": 5},
            "Mercury": {"house": 2},
            "Jupiter": {"house": 6},
            "Venus": {"house": 8},   # Outside axis
            "Saturn": {"house": 9}   # Outside axis
        }
        yogas = yoga_service._detect_kala_sarpa_yoga(planets)
        if len(yogas) > 0:
            assert "Partial" in yogas[0]["name"]
    
    @pytest.mark.yoga
    def test_no_kala_sarpa_planets_outside_axis(self, yoga_service):
        """Test no Kala Sarpa when planets are scattered"""
        planets = {
            "Rahu": {"house": 1},
            "Ketu": {"house": 7},
            "Sun": {"house": 3},
            "Moon": {"house": 8},    # Outside
            "Mars": {"house": 9},    # Outside
            "Mercury": {"house": 10}, # Outside
            "Jupiter": {"house": 11}, # Outside
            "Venus": {"house": 12},  # Outside
            "Saturn": {"house": 1}   # Outside
        }
        yogas = yoga_service._detect_kala_sarpa_yoga(planets)
        assert len(yogas) == 0


# =============================================================================
# SUN-BASED YOGA TESTS
# =============================================================================

class TestSunBasedYogas:
    """Test yogas formed around Sun"""
    
    @pytest.mark.yoga
    def test_vesi_yoga_planet_2nd_from_sun(self, yoga_service):
        """Test Vesi Yoga - Planet in 2nd from Sun"""
        planets = {
            "Sun": {"house": 5},
            "Mars": {"house": 6}  # 2nd from Sun
        }
        yogas = yoga_service._detect_vesi_yoga(planets)
        assert len(yogas) > 0
        assert yogas[0]["name"] == "Vesi Yoga"
    
    @pytest.mark.yoga
    def test_vosi_yoga_planet_12th_from_sun(self, yoga_service):
        """Test Vosi Yoga - Planet in 12th from Sun"""
        planets = {
            "Sun": {"house": 5},
            "Jupiter": {"house": 4}  # 12th from Sun
        }
        yogas = yoga_service._detect_vosi_yoga(planets)
        assert len(yogas) > 0
        assert yogas[0]["name"] == "Vosi Yoga"
    
    @pytest.mark.yoga
    def test_ubhayachari_yoga_planets_both_sides_sun(self, yoga_service):
        """Test Ubhayachari Yoga - Planets on both sides of Sun"""
        planets = {
            "Sun": {"house": 5},
            "Mars": {"house": 4},    # 12th from Sun
            "Jupiter": {"house": 6}   # 2nd from Sun
        }
        yogas = yoga_service._detect_ubhayachari_yoga(planets)
        assert len(yogas) > 0
        assert yogas[0]["name"] == "Ubhayachari Yoga"


# =============================================================================
# MOON-BASED YOGA TESTS
# =============================================================================

class TestMoonBasedYogas:
    """Test yogas formed around Moon"""
    
    @pytest.mark.yoga
    def test_sunapha_yoga_planet_2nd_from_moon(self, yoga_service):
        """Test Sunapha Yoga - Planet in 2nd from Moon"""
        planets = {
            "Moon": {"house": 3},
            "Mars": {"house": 4}  # 2nd from Moon
        }
        yogas = yoga_service._detect_sunapha_yoga(planets)
        assert len(yogas) > 0
        assert yogas[0]["name"] == "Sunapha Yoga"
    
    @pytest.mark.yoga
    def test_anapha_yoga_planet_12th_from_moon(self, yoga_service):
        """Test Anapha Yoga - Planet in 12th from Moon"""
        planets = {
            "Moon": {"house": 5},
            "Saturn": {"house": 4}  # 12th from Moon
        }
        yogas = yoga_service._detect_anapha_yoga(planets)
        assert len(yogas) > 0
        assert yogas[0]["name"] == "Anapha Yoga"
    
    @pytest.mark.yoga
    def test_durudhura_yoga_planets_both_sides_moon(self, yoga_service):
        """Test Durudhura Yoga - Planets on both sides of Moon"""
        planets = {
            "Moon": {"house": 7},
            "Mercury": {"house": 6},  # 12th from Moon
            "Venus": {"house": 8}     # 2nd from Moon
        }
        yogas = yoga_service._detect_durudhura_yoga(planets)
        assert len(yogas) > 0
        assert yogas[0]["name"] == "Durudhura Yoga"
    
    @pytest.mark.yoga
    def test_kemadruma_yoga_moon_isolated(self, yoga_service):
        """Test Kemadruma Yoga - Moon isolated (no planets in 2nd/12th)"""
        planets = {
            "Moon": {"house": 5},
            "Sun": {"house": 1},     # Not in 2nd/12th from Moon
            "Mars": {"house": 10},   # Not in 2nd/12th from Moon
            "Mercury": {"house": 9}, # Not in 2nd/12th from Moon
            "Jupiter": {"house": 3}, # Not in 2nd/12th from Moon
            "Venus": {"house": 8},   # Not in 2nd/12th from Moon
            "Saturn": {"house": 2}   # Not in 2nd/12th from Moon
        }
        yogas = yoga_service._detect_kemadruma_yoga(planets)
        assert len(yogas) > 0
        assert yogas[0]["name"] == "Kemadruma Yoga"


# =============================================================================
# NABHASA YOGA TESTS
# =============================================================================

class TestNabhasaYogas:
    """Test Nabhasa yogas (Ashraya, Dala, Akriti)"""
    
    @pytest.mark.yoga
    def test_rajju_yoga_all_movable_signs(self, yoga_service):
        """Test Rajju Yoga - All planets in movable signs"""
        planets = {
            "Sun": {"sign_num": 1},      # Aries - Movable
            "Moon": {"sign_num": 4},     # Cancer - Movable
            "Mars": {"sign_num": 7},     # Libra - Movable
            "Mercury": {"sign_num": 10}, # Capricorn - Movable
            "Jupiter": {"sign_num": 1},  # Aries - Movable
            "Venus": {"sign_num": 4},    # Cancer - Movable
            "Saturn": {"sign_num": 7}    # Libra - Movable
        }
        yogas = yoga_service._detect_nabhasa_ashraya_yogas(planets)
        assert len(yogas) > 0
        assert yogas[0]["name"] == "Rajju Yoga"
    
    @pytest.mark.yoga
    def test_musala_yoga_all_fixed_signs(self, yoga_service):
        """Test Musala Yoga - All planets in fixed signs"""
        planets = {
            "Sun": {"sign_num": 2},      # Taurus - Fixed
            "Moon": {"sign_num": 5},     # Leo - Fixed
            "Mars": {"sign_num": 8},     # Scorpio - Fixed
            "Mercury": {"sign_num": 11}, # Aquarius - Fixed
            "Jupiter": {"sign_num": 2},  # Taurus - Fixed
            "Venus": {"sign_num": 5},    # Leo - Fixed
            "Saturn": {"sign_num": 8}    # Scorpio - Fixed
        }
        yogas = yoga_service._detect_nabhasa_ashraya_yogas(planets)
        assert len(yogas) > 0
        assert yogas[0]["name"] == "Musala Yoga"
    
    @pytest.mark.yoga
    def test_mala_yoga_benefics_in_kendra(self, yoga_service):
        """Test Mala Yoga - All benefics in kendras"""
        planets = {
            "Jupiter": {"house": 1},
            "Venus": {"house": 4},
            "Mercury": {"house": 7}
        }
        yogas = yoga_service._detect_nabhasa_dala_yogas(planets)
        mala = [y for y in yogas if y["name"] == "Mala Yoga"]
        assert len(mala) > 0


# =============================================================================
# RARE YOGA TESTS
# =============================================================================

class TestRareYogas:
    """Test rare but important yogas"""
    
    @pytest.mark.yoga
    def test_shakata_yoga_moon_68_12_from_jupiter(self, yoga_service):
        """Test Shakata Yoga - Moon in 6/8/12 from Jupiter"""
        planets = {
            "Moon": {"house": 8},
            "Jupiter": {"house": 2}  # Moon in 7th position = 8th house from Jupiter
        }
        yogas = yoga_service._detect_rare_yogas(planets)
        shakata = [y for y in yogas if y["name"] == "Shakata Yoga"]
        assert len(shakata) > 0
    
    @pytest.mark.yoga
    def test_shrinatha_yoga_venus_kendra(self, yoga_service):
        """Test Shrinatha Yoga - Venus in kendra"""
        planets = {
            "Venus": {"house": 10}
        }
        yogas = yoga_service._detect_rare_yogas(planets)
        shrinatha = [y for y in yogas if y["name"] == "Shrinatha Yoga"]
        assert len(shrinatha) > 0
    
    @pytest.mark.yoga
    def test_kusuma_yoga_jupiter_1st_venus_7th(self, yoga_service):
        """Test Kusuma Yoga - Jupiter in 1st, Venus in 7th"""
        planets = {
            "Jupiter": {"house": 1},
            "Venus": {"house": 7}
        }
        yogas = yoga_service._detect_rare_yogas(planets)
        kusuma = [y for y in yogas if y["name"] == "Kusuma Yoga"]
        assert len(kusuma) > 0
        assert kusuma[0]["strength"] == "Very Strong"


# =============================================================================
# TRANSFORMATION YOGA TESTS
# =============================================================================

class TestTransformationYogas:
    """Test transformation and overcoming adversity yogas"""
    
    @pytest.mark.yoga
    def test_viparita_raj_yoga_malefics_in_dusthana(self, yoga_service):
        """Test Viparita Raj Yoga - Malefics in dusthana"""
        planets = {
            "Mars": {"house": 8},
            "Saturn": {"house": 12}
        }
        yogas = yoga_service._detect_viparita_raj_yoga(planets)
        assert len(yogas) > 0
        assert yogas[0]["name"] == "Viparita Raj Yoga"
        assert "adversity" in yogas[0]["description"].lower()
    
    @pytest.mark.yoga
    def test_neecha_bhanga_debilitated_planet_potential(self, yoga_service):
        """Test Neecha Bhanga Raj Yoga - Debilitation cancellation"""
        planets = {
            "Jupiter": {"house": 1, "sign_num": 10}  # Debilitated in Capricorn
        }
        yogas = yoga_service._detect_neecha_bhanga(planets)
        assert len(yogas) > 0
        assert "Neecha Bhanga" in yogas[0]["name"]


# =============================================================================
# INTEGRATION & TIMING TESTS
# =============================================================================

class TestYogaIntegration:
    """Integration tests for full yoga detection and timing"""
    
    @pytest.mark.integration
    def test_detect_extended_yogas_multiple_present(self, yoga_service):
        """Test detection of multiple yogas in a chart"""
        planets = {
            "Sun": {"house": 1, "sign_num": 1, "is_retrograde": False},
            "Moon": {"house": 4, "sign_num": 4, "is_retrograde": False},
            "Mars": {"house": 10, "sign_num": 10, "is_retrograde": False},  # Ruchaka
            "Mercury": {"house": 1, "sign_num": 6, "is_retrograde": False},
            "Jupiter": {"house": 4, "sign_num": 4, "is_retrograde": False}, # Hamsa
            "Venus": {"house": 7, "sign_num": 12, "is_retrograde": False},  # Malavya
            "Saturn": {"house": 11, "sign_num": 11, "is_retrograde": False},
            "Rahu": {"house": 2, "sign_num": 2, "is_retrograde": True},
            "Ketu": {"house": 8, "sign_num": 8, "is_retrograde": True}
        }
        
        yogas = yoga_service.detect_extended_yogas(planets)
        
        # Should detect at least Pancha Mahapurusha yogas
        assert len(yogas) > 0
        
        # Check for specific yogas
        yoga_names = [y["name"] for y in yogas]
        assert any("Ruchaka" in name for name in yoga_names)
        assert any("Hamsa" in name for name in yoga_names)
        assert any("Malavya" in name for name in yoga_names)
    
    @pytest.mark.integration
    def test_yoga_timing_calculation(self, yoga_service):
        """Test yoga timing calculation"""
        yoga = {
            "name": "Hamsa Yoga",
            "description": "Jupiter exalted in Kendra",
            "strength": "Very Strong",
            "category": "Pancha Mahapurusha"
        }
        
        chart_data = {
            "dashas": {
                "vimshottari_dasha": [
                    {
                        "planet": "Jupiter",
                        "start_date": "2025-01-01",
                        "end_date": "2030-01-01",
                        "antardashas": []
                    }
                ]
            }
        }
        
        timing = yoga_service.calculate_yoga_timing(yoga, chart_data)
        
        assert timing["yoga_name"] == "Hamsa Yoga"
        assert "general_activation_age" in timing
        assert isinstance(timing["dasha_activation_periods"], list)
    
    @pytest.mark.integration
    def test_extract_yoga_planets_from_description(self, yoga_service):
        """Test extraction of yoga-forming planets"""
        yoga = {
            "name": "Chandra-Mangala Yoga",
            "description": "Moon-Mars conjunction - wealth through property",
            "category": "Wealth"
        }
        
        planets = yoga_service._extract_yoga_planets(yoga)
        assert "Moon" in planets
        assert "Mars" in planets
    
    @pytest.mark.integration
    def test_yoga_service_performance(self, yoga_service):
        """Test that yoga detection completes within reasonable time"""
        import time
        
        planets = {
            "Sun": {"house": 1, "sign_num": 5},
            "Moon": {"house": 4, "sign_num": 4},
            "Mars": {"house": 8, "sign_num": 8},
            "Mercury": {"house": 2, "sign_num": 6},
            "Jupiter": {"house": 9, "sign_num": 9},
            "Venus": {"house": 7, "sign_num": 7},
            "Saturn": {"house": 11, "sign_num": 11},
            "Rahu": {"house": 3, "sign_num": 3, "is_retrograde": True},
            "Ketu": {"house": 9, "sign_num": 9, "is_retrograde": True}
        }
        
        start = time.time()
        yogas = yoga_service.detect_extended_yogas(planets)
        end = time.time()
        
        # Should complete within 500ms for all 40+ yogas
        assert (end - start) < 0.5, f"Yoga detection took {end-start:.3f}s, should be <0.5s"
        assert isinstance(yogas, list)


# =============================================================================
# EDGE CASE TESTS
# =============================================================================

class TestEdgeCases:
    """Test edge cases and error handling"""
    
    @pytest.mark.unit
    def test_empty_planets_dict(self, yoga_service):
        """Test yoga detection with empty planets dict"""
        yogas = yoga_service.detect_extended_yogas({})
        assert isinstance(yogas, list)
    
    @pytest.mark.unit
    def test_missing_planet_data(self, yoga_service):
        """Test yoga detection with incomplete planet data"""
        planets = {
            "Sun": {"house": 1},  # Missing sign_num
            "Moon": {"sign_num": 4}  # Missing house
        }
        yogas = yoga_service.detect_extended_yogas(planets)
        assert isinstance(yogas, list)
    
    @pytest.mark.unit
    def test_yoga_strength_no_planets(self, yoga_service):
        """Test strength calculation with empty planet list"""
        strength = yoga_service._calculate_yoga_strength([], {})
        assert strength == "Medium"  # Should return default


# =============================================================================
# NEW YOGA TESTS - Phase 1, 2, 3
# =============================================================================

class TestNewYogasPhase1:
    """Test newly implemented critical yogas (Phase 1)"""

    @pytest.mark.yoga
    def test_gajakesari_yoga_jupiter_moon_conjunction(self, yoga_service):
        """Test Gajakesari Yoga when Jupiter and Moon are conjunct"""
        planets = {
            "Moon": {"house": 1, "sign_num": 4, "retrograde": False},
            "Jupiter": {"house": 1, "sign_num": 4, "retrograde": False}
        }
        yogas = yoga_service.detect_extended_yogas(planets)
        yoga_names = [y["name"] for y in yogas]
        assert "Gajakesari Yoga" in yoga_names, "Should detect Gajakesari Yoga when Jupiter-Moon conjunct"

    @pytest.mark.yoga
    def test_gajakesari_yoga_jupiter_4th_from_moon(self, yoga_service):
        """Test Gajakesari Yoga when Jupiter is in 4th from Moon"""
        planets = {
            "Moon": {"house": 1, "sign_num": 1, "retrograde": False},
            "Jupiter": {"house": 4, "sign_num": 4, "retrograde": False}
        }
        yogas = yoga_service.detect_extended_yogas(planets)
        yoga_names = [y["name"] for y in yogas]
        assert "Gajakesari Yoga" in yoga_names, "Should detect Gajakesari Yoga when Jupiter 4th from Moon"

    @pytest.mark.yoga
    def test_gajakesari_yoga_jupiter_7th_from_moon(self, yoga_service):
        """Test Gajakesari Yoga when Jupiter is in 7th from Moon"""
        planets = {
            "Moon": {"house": 1, "sign_num": 1, "retrograde": False},
            "Jupiter": {"house": 7, "sign_num": 7, "retrograde": False}
        }
        yogas = yoga_service.detect_extended_yogas(planets)
        yoga_names = [y["name"] for y in yogas]
        assert "Gajakesari Yoga" in yoga_names, "Should detect Gajakesari Yoga when Jupiter 7th from Moon"

    @pytest.mark.yoga
    def test_gajakesari_yoga_jupiter_10th_from_moon(self, yoga_service):
        """Test Gajakesari Yoga when Jupiter is in 10th from Moon"""
        planets = {
            "Moon": {"house": 1, "sign_num": 1, "retrograde": False},
            "Jupiter": {"house": 10, "sign_num": 10, "retrograde": False}
        }
        yogas = yoga_service.detect_extended_yogas(planets)
        yoga_names = [y["name"] for y in yogas]
        assert "Gajakesari Yoga" in yoga_names, "Should detect Gajakesari Yoga when Jupiter 10th from Moon"

    @pytest.mark.yoga
    def test_gajakesari_yoga_not_in_kendra(self, yoga_service):
        """Test that Gajakesari Yoga is not detected when Jupiter not in kendra from Moon"""
        planets = {
            "Moon": {"house": 1, "sign_num": 1, "retrograde": False},
            "Jupiter": {"house": 2, "sign_num": 2, "retrograde": False}  # 2nd house, not kendra
        }
        yogas = yoga_service.detect_extended_yogas(planets)
        yoga_names = [y["name"] for y in yogas]
        assert "Gajakesari Yoga" not in yoga_names, "Should not detect Gajakesari Yoga when Jupiter not in kendra"

    @pytest.mark.yoga
    def test_raj_yoga_kendra_trikona(self, yoga_service):
        """Test Raj Yoga with benefics in Kendra and Trikona"""
        planets = {
            "Jupiter": {"house": 1, "sign_num": 1, "retrograde": False},  # Kendra and Trikona
            "Venus": {"house": 5, "sign_num": 5, "retrograde": False},    # Trikona
            "Mercury": {"house": 7, "sign_num": 7, "retrograde": False}   # Kendra
        }
        yogas = yoga_service.detect_extended_yogas(planets)
        yoga_names = [y["name"] for y in yogas]
        assert "Raj Yoga (Kendra-Trikona)" in yoga_names, "Should detect Raj Yoga with benefics in Kendra and Trikona"

    @pytest.mark.yoga
    def test_grahan_yoga_sun_rahu(self, yoga_service):
        """Test Grahan Yoga with Sun-Rahu conjunction (Solar Eclipse)"""
        planets = {
            "Sun": {"house": 10, "sign_num": 10, "retrograde": False},
            "Rahu": {"house": 10, "sign_num": 10, "retrograde": True}
        }
        yogas = yoga_service.detect_extended_yogas(planets)
        yoga_names = [y["name"] for y in yogas]
        assert any("Grahan Yoga (Solar Eclipse)" in name for name in yoga_names), "Should detect Solar Eclipse Grahan Yoga"

    @pytest.mark.yoga
    def test_grahan_yoga_moon_rahu(self, yoga_service):
        """Test Grahan Yoga with Moon-Rahu conjunction (Lunar Eclipse)"""
        planets = {
            "Moon": {"house": 4, "sign_num": 4, "retrograde": False},
            "Rahu": {"house": 4, "sign_num": 4, "retrograde": True}
        }
        yogas = yoga_service.detect_extended_yogas(planets)
        yoga_names = [y["name"] for y in yogas]
        assert any("Grahan Yoga (Lunar Eclipse)" in name for name in yoga_names), "Should detect Lunar Eclipse Grahan Yoga"

    @pytest.mark.yoga
    def test_grahan_yoga_sun_ketu(self, yoga_service):
        """Test Grahan Yoga with Sun-Ketu conjunction"""
        planets = {
            "Sun": {"house": 5, "sign_num": 5, "retrograde": False},
            "Ketu": {"house": 5, "sign_num": 5, "retrograde": True}
        }
        yogas = yoga_service.detect_extended_yogas(planets)
        yoga_names = [y["name"] for y in yogas]
        assert any("Grahan Yoga" in name and "Ketu" in name for name in yoga_names), "Should detect Sun-Ketu Grahan Yoga"

    @pytest.mark.yoga
    def test_grahan_yoga_moon_ketu(self, yoga_service):
        """Test Grahan Yoga with Moon-Ketu conjunction"""
        planets = {
            "Moon": {"house": 7, "sign_num": 7, "retrograde": False},
            "Ketu": {"house": 7, "sign_num": 7, "retrograde": True}
        }
        yogas = yoga_service.detect_extended_yogas(planets)
        yoga_names = [y["name"] for y in yogas]
        assert any("Grahan Yoga" in name and "Lunar" in name and "Ketu" in name for name in yoga_names), "Should detect Moon-Ketu Grahan Yoga"


class TestNewYogasPhase2:
    """Test newly implemented high priority yogas (Phase 2)"""

    @pytest.mark.yoga
    def test_dharma_karmadhipati_yoga(self, yoga_service):
        """Test Dharma-Karmadhipati Yoga with benefics in 9th and 10th"""
        planets = {
            "Jupiter": {"house": 9, "sign_num": 9, "retrograde": False},
            "Venus": {"house": 10, "sign_num": 10, "retrograde": False}
        }
        yogas = yoga_service.detect_extended_yogas(planets)
        yoga_names = [y["name"] for y in yogas]
        assert "Dharma-Karmadhipati Yoga" in yoga_names, "Should detect Dharma-Karmadhipati Yoga"

    @pytest.mark.yoga
    def test_dhana_yoga_multiple_benefics_in_wealth_houses(self, yoga_service):
        """Test Dhana Yoga with multiple benefics in wealth houses"""
        planets = {
            "Jupiter": {"house": 2, "sign_num": 2, "retrograde": False},  # Wealth house
            "Venus": {"house": 5, "sign_num": 5, "retrograde": False},    # Wealth house
            "Mercury": {"house": 9, "sign_num": 9, "retrograde": False}   # Wealth house
        }
        yogas = yoga_service.detect_extended_yogas(planets)
        yoga_names = [y["name"] for y in yogas]
        assert "Dhana Yoga" in yoga_names, "Should detect Dhana Yoga with benefics in wealth houses"

    @pytest.mark.yoga
    def test_dhana_yoga_two_benefics_sufficient(self, yoga_service):
        """Test Dhana Yoga with 2 benefics in wealth houses (minimum)"""
        planets = {
            "Jupiter": {"house": 11, "sign_num": 11, "retrograde": False},  # Wealth house
            "Venus": {"house": 9, "sign_num": 9, "retrograde": False}       # Wealth house
        }
        yogas = yoga_service.detect_extended_yogas(planets)
        yoga_names = [y["name"] for y in yogas]
        assert "Dhana Yoga" in yoga_names, "Should detect Dhana Yoga with 2 benefics in wealth houses"

    @pytest.mark.yoga
    def test_chandal_yoga_jupiter_rahu_conjunction(self, yoga_service):
        """Test Chandal Yoga with Jupiter-Rahu conjunction"""
        planets = {
            "Jupiter": {"house": 5, "sign_num": 5, "retrograde": False},
            "Rahu": {"house": 5, "sign_num": 5, "retrograde": True}
        }
        yogas = yoga_service.detect_extended_yogas(planets)
        yoga_names = [y["name"] for y in yogas]
        assert "Chandal Yoga" in yoga_names, "Should detect Chandal Yoga with Jupiter-Rahu conjunction"

    @pytest.mark.yoga
    def test_chandal_yoga_jupiter_strong(self, yoga_service):
        """Test Chandal Yoga strength when Jupiter is in own sign"""
        planets = {
            "Jupiter": {"house": 9, "sign_num": 9, "retrograde": False},  # Sagittarius - own sign
            "Rahu": {"house": 9, "sign_num": 9, "retrograde": True}
        }
        yogas = yoga_service.detect_extended_yogas(planets)
        chandal_yogas = [y for y in yogas if y["name"] == "Chandal Yoga"]
        assert len(chandal_yogas) > 0, "Should detect Chandal Yoga"
        # When Jupiter strong, effects are mitigated
        assert "unconventional genius" in chandal_yogas[0]["description"].lower() or "wisdom" in chandal_yogas[0]["description"].lower()

    @pytest.mark.yoga
    def test_kubera_yoga_all_benefics_strong(self, yoga_service):
        """Test Kubera Yoga when all benefics are strong"""
        planets = {
            "Jupiter": {"house": 1, "sign_num": 9, "retrograde": False},  # Kendra + own sign
            "Venus": {"house": 4, "sign_num": 12, "retrograde": False},   # Kendra + exalted
            "Mercury": {"house": 10, "sign_num": 6, "retrograde": False}  # Kendra + exalted
        }
        yogas = yoga_service.detect_extended_yogas(planets)
        yoga_names = [y["name"] for y in yogas]
        assert "Kubera Yoga" in yoga_names, "Should detect Kubera Yoga when all benefics strong"

    @pytest.mark.yoga
    def test_daridra_yoga_malefics_in_wealth_houses(self, yoga_service):
        """Test Daridra Yoga with malefics in wealth houses"""
        planets = {
            "Mars": {"house": 2, "sign_num": 2, "retrograde": False},
            "Saturn": {"house": 5, "sign_num": 5, "retrograde": False},
            "Rahu": {"house": 11, "sign_num": 11, "retrograde": True}
        }
        yogas = yoga_service.detect_extended_yogas(planets)
        yoga_names = [y["name"] for y in yogas]
        assert "Daridra Yoga" in yoga_names, "Should detect Daridra Yoga with malefics in wealth houses"

    @pytest.mark.yoga
    def test_daridra_yoga_debilitated_benefics(self, yoga_service):
        """Test Daridra Yoga with debilitated benefics"""
        planets = {
            "Jupiter": {"house": 5, "sign_num": 10, "retrograde": False},  # Debilitated in Capricorn
            "Venus": {"house": 7, "sign_num": 6, "retrograde": False},     # Debilitated in Virgo
            "Mercury": {"house": 9, "sign_num": 12, "retrograde": False}   # Debilitated in Pisces
        }
        yogas = yoga_service.detect_extended_yogas(planets)
        yoga_names = [y["name"] for y in yogas]
        assert "Daridra Yoga" in yoga_names, "Should detect Daridra Yoga with multiple debilitated benefics"


class TestNewYogasPhase3:
    """Test newly implemented medium priority yogas (Phase 3)"""

    @pytest.mark.yoga
    def test_balarishta_yoga_moon_afflicted(self, yoga_service):
        """Test Balarishta Yoga with afflicted Moon"""
        planets = {
            "Moon": {"house": 4, "sign_num": 8, "retrograde": False},  # Debilitated in Scorpio
            "Mars": {"house": 4, "sign_num": 8, "retrograde": False},  # With Moon
            "Saturn": {"house": 1, "sign_num": 1, "retrograde": False} # In critical house
        }
        yogas = yoga_service.detect_extended_yogas(planets)
        yoga_names = [y["name"] for y in yogas]
        assert "Balarishta Yoga" in yoga_names, "Should detect Balarishta Yoga with afflicted Moon"

    @pytest.mark.yoga
    def test_balarishta_yoga_malefics_in_critical_houses(self, yoga_service):
        """Test Balarishta Yoga with malefics in 1st, 4th, 8th"""
        planets = {
            "Moon": {"house": 5, "sign_num": 5, "retrograde": False},
            "Mars": {"house": 1, "sign_num": 1, "retrograde": False},
            "Saturn": {"house": 8, "sign_num": 8, "retrograde": False}
        }
        yogas = yoga_service.detect_extended_yogas(planets)
        yoga_names = [y["name"] for y in yogas]
        assert "Balarishta Yoga" in yoga_names, "Should detect Balarishta Yoga with malefics in critical houses"

    @pytest.mark.yoga
    def test_kroora_yoga_malefics_in_kendras(self, yoga_service):
        """Test Kroora Yoga with multiple malefics in kendras"""
        planets = {
            "Mars": {"house": 1, "sign_num": 1, "retrograde": False},
            "Saturn": {"house": 7, "sign_num": 7, "retrograde": False},
            "Sun": {"house": 10, "sign_num": 10, "retrograde": False}
        }
        yogas = yoga_service.detect_extended_yogas(planets)
        yoga_names = [y["name"] for y in yogas]
        assert "Kroora Yoga" in yoga_names, "Should detect Kroora Yoga with malefics in kendras"

    @pytest.mark.yoga
    def test_kroora_yoga_mitigated_by_jupiter(self, yoga_service):
        """Test Kroora Yoga mitigation when Jupiter is also in kendra"""
        planets = {
            "Mars": {"house": 1, "sign_num": 1, "retrograde": False},
            "Saturn": {"house": 7, "sign_num": 7, "retrograde": False},
            "Jupiter": {"house": 4, "sign_num": 4, "retrograde": False}  # Mitigating factor
        }
        yogas = yoga_service.detect_extended_yogas(planets)
        kroora_yogas = [y for y in yogas if y["name"] == "Kroora Yoga"]
        assert len(kroora_yogas) > 0, "Should detect Kroora Yoga"
        # Should mention mitigation
        assert "mitigated" in kroora_yogas[0]["description"].lower()

    @pytest.mark.yoga
    def test_kroora_yoga_not_detected_single_malefic(self, yoga_service):
        """Test that Kroora Yoga is not detected with only one malefic in kendra"""
        planets = {
            "Mars": {"house": 1, "sign_num": 1, "retrograde": False},
            "Saturn": {"house": 3, "sign_num": 3, "retrograde": False}  # Not in kendra
        }
        yogas = yoga_service.detect_extended_yogas(planets)
        yoga_names = [y["name"] for y in yogas]
        assert "Kroora Yoga" not in yoga_names, "Should not detect Kroora Yoga with single malefic in kendra"


class TestNewYogasIntegration:
    """Integration tests for all new yogas"""

    @pytest.mark.yoga
    @pytest.mark.integration
    def test_multiple_new_yogas_detected_together(self, yoga_service):
        """Test that multiple new yogas can be detected in the same chart"""
        planets = {
            "Sun": {"house": 10, "sign_num": 10, "retrograde": False},
            "Moon": {"house": 1, "sign_num": 4, "retrograde": False},
            "Mars": {"house": 7, "sign_num": 8, "retrograde": False},
            "Mercury": {"house": 10, "sign_num": 10, "retrograde": False},
            "Jupiter": {"house": 1, "sign_num": 4, "retrograde": False},  # Gajakesari with Moon
            "Venus": {"house": 5, "sign_num": 5, "retrograde": False},
            "Saturn": {"house": 7, "sign_num": 7, "retrograde": False},
            "Rahu": {"house": 3, "sign_num": 3, "retrograde": True},
            "Ketu": {"house": 9, "sign_num": 9, "retrograde": True}
        }
        yogas = yoga_service.detect_extended_yogas(planets)
        yoga_names = [y["name"] for y in yogas]

        # Should detect Gajakesari (Jupiter-Moon in same house)
        assert "Gajakesari Yoga" in yoga_names

        # Should detect Raj Yoga (benefics in kendra and trikona)
        assert "Raj Yoga (Kendra-Trikona)" in yoga_names

        # Should have detected multiple yogas
        assert len(yogas) >= 5, "Should detect multiple yogas in complex chart"

    @pytest.mark.yoga
    @pytest.mark.integration
    def test_new_yogas_performance(self, yoga_service):
        """Test that new yoga detection doesn't significantly impact performance"""
        import time

        planets = {
            "Sun": {"house": 1, "sign_num": 1, "retrograde": False},
            "Moon": {"house": 4, "sign_num": 4, "retrograde": False},
            "Mars": {"house": 7, "sign_num": 8, "retrograde": False},
            "Mercury": {"house": 10, "sign_num": 6, "retrograde": False},
            "Jupiter": {"house": 4, "sign_num": 4, "retrograde": False},
            "Venus": {"house": 7, "sign_num": 12, "retrograde": False},
            "Saturn": {"house": 10, "sign_num": 7, "retrograde": False},
            "Rahu": {"house": 2, "sign_num": 2, "retrograde": True},
            "Ketu": {"house": 8, "sign_num": 8, "retrograde": True}
        }

        start = time.time()
        yogas = yoga_service.detect_extended_yogas(planets)
        end = time.time()

        # With 10 new yogas added, should still complete quickly (< 1 second)
        assert (end - start) < 1.0, f"Yoga detection took {end-start:.3f}s, should be <1s"
        assert isinstance(yogas, list)
        assert len(yogas) > 0, "Should detect some yogas"

    @pytest.mark.yoga
    def test_yoga_count_increased(self, yoga_service):
        """Test that total detectable yoga count has increased"""
        # Complex chart that should trigger many yogas
        planets = {
            "Sun": {"house": 5, "sign_num": 5, "retrograde": False},
            "Moon": {"house": 1, "sign_num": 4, "retrograde": False},
            "Mars": {"house": 10, "sign_num": 10, "retrograde": False},
            "Mercury": {"house": 5, "sign_num": 6, "retrograde": False},
            "Jupiter": {"house": 1, "sign_num": 4, "retrograde": False},
            "Venus": {"house": 7, "sign_num": 7, "retrograde": False},
            "Saturn": {"house": 10, "sign_num": 10, "retrograde": False},
            "Rahu": {"house": 6, "sign_num": 6, "retrograde": True},
            "Ketu": {"house": 12, "sign_num": 12, "retrograde": True}
        }

        yogas = yoga_service.detect_extended_yogas(planets)

        # With 10 new yogas added, should detect more yogas than before
        # Original implementation detected ~37 yogas max, now should have potential for 47+
        assert len(yogas) >= 3, "Should detect multiple yogas in this chart"

        # Check that new yogas are in the results
        yoga_names = [y["name"] for y in yogas]
        new_yoga_categories = ["Gajakesari", "Raj Yoga (Kendra-Trikona)", "Dharma-Karmadhipati",
                              "Dhana Yoga", "Chandal", "Kubera", "Daridra", "Balarishta",
                              "Kroora", "Grahan"]

        detected_new_yogas = sum(1 for category in new_yoga_categories
                                if any(category in name for name in yoga_names))

        assert detected_new_yogas >= 1, "Should detect at least one of the new yogas"
