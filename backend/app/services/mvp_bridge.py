"""
MVP Bridge Layer
Wraps existing astrology services into standardized format for AI Engine
Implements caching by canonical hash
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, date, time
import hashlib
import json
from app.services.astrology import astrology_service
from app.services.supabase_service import supabase_service


class MVPBridge:
    """Bridge layer between existing MVP and AI Engine"""

    def __init__(self):
        """Initialize MVP Bridge"""
        self.astrology = astrology_service
        self.db = supabase_service

    def generate_canonical_hash(self, input_params: Dict[str, Any]) -> str:
        """
        Generate canonical hash for caching
        Hash is based on immutable birth data: dob, tob, lat, lon

        Args:
            input_params: Dict with dob, tob, latitude, longitude

        Returns:
            SHA-256 hash as hex string
        """
        # Extract only immutable params that affect chart
        canonical_keys = ["dob", "tob", "latitude", "longitude"]
        canonical_data = {k: input_params.get(k) for k in canonical_keys if input_params.get(k)}

        # Sort keys for consistency
        canonical_json = json.dumps(canonical_data, sort_keys=True)

        # Generate SHA-256 hash
        hash_obj = hashlib.sha256(canonical_json.encode())
        return hash_obj.hexdigest()

    async def get_charts(
        self,
        name: str,
        dob: str,  # "YYYY-MM-DD"
        tob: str,  # "HH:MM"
        city_id: Optional[str] = None,
        country_code: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        timezone_str: str = "Asia/Kolkata",
        city: str = "Unknown",
        user_id: Optional[str] = None,
        chart_types: List[str] = None
    ) -> Dict[str, Any]:
        """
        Get all charts (D1, D9, Moon) with caching

        Args:
            name: Person's name
            dob: Date of birth (YYYY-MM-DD)
            tob: Time of birth (HH:MM)
            city_id: Optional city ID from dropdown
            country_code: Optional country code
            latitude: Birth latitude
            longitude: Birth longitude
            timezone_str: Timezone (default: Asia/Kolkata)
            city: City name
            user_id: Optional user ID for caching
            chart_types: List of chart types to calculate ['D1', 'D9', 'Moon']

        Returns:
            {
                charts: {rasi, navamsa?, moon?},
                dashas: {maha, antar?},
                transits: {...},
                basics: {strengths?, yogas?, notes?},
                meta: {tz, lat, lon, engine_version, canonical_hash}
            }
        """
        if chart_types is None:
            chart_types = ['D1', 'D9', 'Moon']

        # Parse date and time
        birth_date = datetime.strptime(dob, "%Y-%m-%d").date()
        birth_time = datetime.strptime(tob, "%H:%M").time()

        # Generate canonical hash for caching
        input_params = {
            "dob": dob,
            "tob": tob,
            "latitude": latitude,
            "longitude": longitude
        }
        canonical_hash = self.generate_canonical_hash(input_params)

        # Check cache if user_id provided
        cached_result = None
        if user_id:
            cached_result = await self._check_cache(user_id, canonical_hash)
            if cached_result:
                return cached_result

        # Calculate charts using existing services
        charts = {}

        # D1 (Rashi) - Birth chart
        if 'D1' in chart_types:
            charts['rasi'] = self.astrology.calculate_birth_chart(
                name=name,
                birth_date=birth_date,
                birth_time=birth_time,
                latitude=latitude,
                longitude=longitude,
                timezone_str=timezone_str,
                city=city
            )

        # D9 (Navamsa)
        if 'D9' in chart_types:
            charts['navamsa'] = self.astrology.calculate_navamsa_chart(
                name=name,
                birth_date=birth_date,
                birth_time=birth_time,
                latitude=latitude,
                longitude=longitude,
                timezone_str=timezone_str,
                city=city
            )

        # Moon Chart (Chandra Kundali)
        if 'Moon' in chart_types:
            charts['moon'] = self.astrology.calculate_moon_chart(
                name=name,
                birth_date=birth_date,
                birth_time=birth_time,
                latitude=latitude,
                longitude=longitude,
                timezone_str=timezone_str,
                city=city
            )

        # Extract dashas from D1 chart
        dashas = {}
        if 'rasi' in charts and charts['rasi'].get('dasha'):
            dashas = {
                'maha': charts['rasi']['dasha'].get('current_mahadasha'),
                'antar': charts['rasi']['dasha'].get('current_antardasha'),
                'all_mahadashas': charts['rasi']['dasha'].get('mahadasha_sequence', [])
            }

        # Get current transits (calculate from current date)
        transits = self._calculate_transits(latitude, longitude, timezone_str)

        # Extract basic info
        basics = {}
        if 'rasi' in charts:
            basics = {
                'ascendant': charts['rasi'].get('ascendant'),
                'moon_sign': charts['rasi']['planets'].get('Moon', {}).get('sign'),
                'sun_sign': charts['rasi']['planets'].get('Sun', {}).get('sign'),
                'yogas': charts['rasi'].get('yogas', []),
                'strengths': self._analyze_strengths(charts['rasi'])
            }

        # Metadata
        meta = {
            'tz': timezone_str,
            'lat': latitude,
            'lon': longitude,
            'city': city,
            'engine_version': '1.0.0-mvp',
            'canonical_hash': canonical_hash,
            'calculation_method': 'Swiss Ephemeris with Lahiri Ayanamsa',
            'calculated_at': datetime.utcnow().isoformat()
        }

        result = {
            'charts': charts,
            'dashas': dashas,
            'transits': transits,
            'basics': basics,
            'meta': meta
        }

        # Cache result if user_id provided
        if user_id:
            await self._cache_result(user_id, canonical_hash, result)

        return result

    def _calculate_transits(
        self,
        latitude: float,
        longitude: float,
        timezone_str: str
    ) -> Dict[str, Any]:
        """
        Calculate current transits

        Args:
            latitude: Location latitude
            longitude: Location longitude
            timezone_str: Timezone

        Returns:
            Dict of current planetary positions
        """
        now = datetime.now()
        current_date = now.date()
        current_time = now.time()

        # Calculate transit chart (same as birth chart but for current moment)
        transit_chart = self.astrology.calculate_birth_chart(
            name="Transits",
            birth_date=current_date,
            birth_time=current_time,
            latitude=latitude,
            longitude=longitude,
            timezone_str=timezone_str,
            city="Current Location"
        )

        return {
            'planets': transit_chart.get('planets', {}),
            'calculated_at': now.isoformat()
        }

    def _analyze_strengths(self, rasi_chart: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze planetary strengths

        Args:
            rasi_chart: D1 chart data

        Returns:
            Dict of strength metrics
        """
        planets = rasi_chart.get('planets', {})
        strengths = {}

        for planet_name, planet_data in planets.items():
            # Basic strength indicators
            strength = {
                'retrograde': planet_data.get('retrograde', False),
                'house': planet_data.get('house'),
                'sign': planet_data.get('sign'),
                'nakshatra': planet_data.get('nakshatra', {}).get('name') if planet_data.get('nakshatra') else None
            }

            # Determine if exalted/debilitated (simplified)
            exaltation_signs = {
                'Sun': 'Aries',
                'Moon': 'Taurus',
                'Mars': 'Capricorn',
                'Mercury': 'Virgo',
                'Jupiter': 'Cancer',
                'Venus': 'Pisces',
                'Saturn': 'Libra'
            }

            debilitation_signs = {
                'Sun': 'Libra',
                'Moon': 'Scorpio',
                'Mars': 'Cancer',
                'Mercury': 'Pisces',
                'Jupiter': 'Capricorn',
                'Venus': 'Virgo',
                'Saturn': 'Aries'
            }

            if planet_name in exaltation_signs:
                strength['exalted'] = planet_data.get('sign') == exaltation_signs[planet_name]
                strength['debilitated'] = planet_data.get('sign') == debilitation_signs[planet_name]

            strengths[planet_name] = strength

        return strengths

    async def _check_cache(
        self,
        user_id: str,
        canonical_hash: str
    ) -> Optional[Dict[str, Any]]:
        """
        Check if result is cached

        Args:
            user_id: User ID
            canonical_hash: Canonical hash

        Returns:
            Cached result or None
        """
        try:
            # Query reading_sessions table
            response = self.db.client.table("reading_sessions")\
                .select("charts, dashas, transits, input_params")\
                .eq("user_id", user_id)\
                .eq("canonical_hash", canonical_hash)\
                .gte("expires_at", datetime.utcnow().isoformat())\
                .execute()

            if response.data and len(response.data) > 0:
                session = response.data[0]
                return {
                    'charts': session.get('charts'),
                    'dashas': session.get('dashas'),
                    'transits': session.get('transits'),
                    'meta': session.get('input_params'),  # Map input_params to meta for API consistency
                    'cached': True
                }

        except Exception as e:
            print(f"Cache check error: {str(e)}")

        return None

    async def _cache_result(
        self,
        user_id: str,
        canonical_hash: str,
        result: Dict[str, Any]
    ) -> None:
        """
        Cache result for future use

        Args:
            user_id: User ID
            canonical_hash: Canonical hash
            result: Result to cache
        """
        try:
            # Store in reading_sessions table
            cache_data = {
                'user_id': user_id,
                'canonical_hash': canonical_hash,
                'input_params': result.get('meta'),
                'charts': result.get('charts'),
                'dashas': result.get('dashas'),
                'transits': result.get('transits'),
                'reading_type': 'full',  # Use 'full' instead of 'mvp_bridge' to match schema constraint
                'confidence_score': 1.0  # MVP calculations are deterministic
            }

            self.db.client.table("reading_sessions").insert(cache_data).execute()

        except Exception as e:
            print(f"Cache write error: {str(e)}")


# Singleton instance
mvp_bridge = MVPBridge()
