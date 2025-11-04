"""
Birth Time Rectification Service
Uses event anchors and dasha analysis to narrow down correct birth time
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta, date, time
from app.services.astrology import astrology_service


class RectificationService:
    """
    Service for birth time rectification using event anchors

    Method: Analyzes major life events against dasha periods and transits
    to find the most likely birth time within a given window
    """

    def __init__(self):
        """Initialize rectification service"""
        pass

    def rectify_birth_time(
        self,
        name: str,
        birth_date: date,
        approximate_time: time,
        time_window_minutes: int,
        latitude: float,
        longitude: float,
        timezone_str: str,
        city: str,
        event_anchors: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Rectify birth time using event anchors

        Args:
            name: Person's name
            birth_date: Known birth date
            approximate_time: Approximate birth time (e.g., from memory/documents)
            time_window_minutes: Window of uncertainty (e.g., ±30 minutes)
            latitude: Birth latitude
            longitude: Birth longitude
            timezone_str: Timezone
            city: Birth city
            event_anchors: List of verified life events with dates

        Returns:
            Dictionary with rectified time and confidence score
        """
        print(f"🔍 Starting birth time rectification...")
        print(f"   Approximate time: {approximate_time}")
        print(f"   Time window: ±{time_window_minutes} minutes")
        print(f"   Event anchors: {len(event_anchors)}")

        # Generate candidate times within window
        candidate_times = self._generate_candidate_times(
            approximate_time,
            time_window_minutes,
            interval_minutes=2  # Test every 2 minutes
        )

        print(f"   Testing {len(candidate_times)} candidate times...")

        # Score each candidate time
        scored_candidates = []

        for candidate_time in candidate_times:
            # Calculate chart for this time
            try:
                chart = astrology_service.calculate_birth_chart(
                    name=name,
                    birth_date=birth_date,
                    birth_time=candidate_time,
                    latitude=latitude,
                    longitude=longitude,
                    timezone_str=timezone_str,
                    city=city
                )

                # Score this candidate against event anchors
                score, event_matches = self._score_candidate(
                    chart,
                    birth_date,
                    candidate_time,
                    event_anchors
                )

                scored_candidates.append({
                    "time": candidate_time,
                    "score": score,
                    "chart": chart,
                    "event_matches": event_matches
                })

            except Exception as e:
                print(f"   Error with {candidate_time}: {e}")
                continue

        # Sort by score
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)

        # Get top 3 candidates
        top_candidates = scored_candidates[:3]

        # Calculate confidence
        confidence = self._calculate_confidence(top_candidates, event_anchors)

        print(f"✅ Rectification complete!")
        print(f"   Top candidate: {top_candidates[0]['time']} (score: {top_candidates[0]['score']:.2f})")
        print(f"   Confidence: {confidence}%")

        return {
            "rectified_time": top_candidates[0]['time'].isoformat(),
            "rectified_chart": top_candidates[0]['chart'],
            "confidence": confidence,
            "score": top_candidates[0]['score'],
            "top_candidates": [
                {
                    "time": c['time'].isoformat(),
                    "score": c['score'],
                    "event_matches": c['event_matches']
                }
                for c in top_candidates
            ],
            "event_anchors_used": len(event_anchors),
            "method": "dasha_event_correlation",
            "time_window_tested": time_window_minutes * 2,  # ±window
            "candidates_tested": len(scored_candidates)
        }

    def _generate_candidate_times(
        self,
        approximate_time: time,
        window_minutes: int,
        interval_minutes: int = 2
    ) -> List[time]:
        """Generate list of candidate times within window"""
        candidates = []

        # Convert to datetime for easier manipulation
        base_dt = datetime.combine(date.today(), approximate_time)

        # Start time
        start_dt = base_dt - timedelta(minutes=window_minutes)

        # End time
        end_dt = base_dt + timedelta(minutes=window_minutes)

        # Generate candidates
        current_dt = start_dt
        while current_dt <= end_dt:
            candidates.append(current_dt.time())
            current_dt += timedelta(minutes=interval_minutes)

        return candidates

    def _score_candidate(
        self,
        chart: Dict[str, Any],
        birth_date: date,
        birth_time: time,
        event_anchors: List[Dict[str, Any]]
    ) -> Tuple[float, List[Dict[str, Any]]]:
        """
        Score a candidate time against event anchors

        Returns:
            Tuple of (score, event_matches)
        """
        total_score = 0.0
        event_matches = []

        # Get dashas from chart
        chart_dashas = chart.get('vimshottari_dasha', {}).get('periods', [])

        for anchor in event_anchors:
            event_type = anchor.get('event_type')
            event_date = anchor.get('event_date')
            event_significance = anchor.get('event_significance', 'medium')

            # Find which dasha period this event occurred in
            dasha_at_event = self._find_dasha_at_date(
                chart_dashas,
                birth_date,
                birth_time,
                event_date
            )

            if not dasha_at_event:
                continue

            # Score this event match
            event_score = self._score_event_dasha_match(
                event_type=event_type,
                dasha_planet=dasha_at_event['planet'],
                chart=chart,
                significance=event_significance
            )

            total_score += event_score

            event_matches.append({
                "event_type": event_type,
                "event_date": event_date,
                "dasha_planet": dasha_at_event['planet'],
                "score": event_score,
                "expected_dasha": self._get_expected_dasha_for_event(event_type)
            })

        # Average score
        if event_anchors:
            total_score = total_score / len(event_anchors)

        # Bonus for ascendant in good houses
        asc_sign = chart.get('ascendant', {}).get('sign', '')
        if asc_sign in ['Aries', 'Leo', 'Sagittarius', 'Cancer', 'Pisces']:
            total_score += 0.5  # Slight bonus for benefic ascendants

        return total_score, event_matches

    def _find_dasha_at_date(
        self,
        dasha_periods: List[Dict[str, Any]],
        birth_date: date,
        birth_time: time,
        event_date: str
    ) -> Optional[Dict[str, Any]]:
        """Find which dasha period was active at given date"""
        if not dasha_periods:
            return None

        try:
            # Convert event_date string to date object
            if isinstance(event_date, str):
                event_dt = datetime.fromisoformat(event_date).date()
            else:
                event_dt = event_date

            # Calculate birth datetime
            birth_dt = datetime.combine(birth_date, birth_time)

            # Calculate years from birth to event
            years_since_birth = (event_dt - birth_date).days / 365.25

            # Find active dasha
            cumulative_years = 0.0

            for period in dasha_periods:
                period_years = period.get('duration_years', 0)

                if cumulative_years <= years_since_birth < cumulative_years + period_years:
                    return period

                cumulative_years += period_years

            # If we're past all dasha periods, return the last one
            if dasha_periods:
                return dasha_periods[-1]

        except Exception as e:
            print(f"Error finding dasha at date: {e}")
            return None

        return None

    def _score_event_dasha_match(
        self,
        event_type: str,
        dasha_planet: str,
        chart: Dict[str, Any],
        significance: str
    ) -> float:
        """
        Score how well an event matches the dasha planet

        Args:
            event_type: Type of event (marriage, job_start, etc.)
            dasha_planet: Planet ruling dasha during event
            chart: Birth chart data
            significance: Event significance (very_high, high, medium, low)

        Returns:
            Score from 0 to 10
        """
        score = 0.0

        # Get expected dasha planets for this event type
        expected_dashas = self._get_expected_dasha_for_event(event_type)

        # Base score if dasha matches expected
        if dasha_planet in expected_dashas['primary']:
            score += 8.0
        elif dasha_planet in expected_dashas.get('secondary', []):
            score += 5.0
        else:
            score += 2.0  # Some baseline score

        # Check planet strength in chart
        planet_data = chart.get('planets', {}).get(dasha_planet, {})
        planet_house = planet_data.get('house', 0)
        planet_sign = planet_data.get('sign', '')

        # Bonus for planet in relevant houses
        relevant_houses = self._get_relevant_houses_for_event(event_type)
        if planet_house in relevant_houses:
            score += 2.0

        # Significance multiplier
        significance_multipliers = {
            'very_high': 1.5,
            'high': 1.2,
            'medium': 1.0,
            'low': 0.8
        }

        score *= significance_multipliers.get(significance, 1.0)

        return min(score, 10.0)  # Cap at 10

    def _get_expected_dasha_for_event(self, event_type: str) -> Dict[str, List[str]]:
        """Get expected dasha planets for event type"""
        event_dasha_map = {
            'marriage': {
                'primary': ['Venus', 'Jupiter'],
                'secondary': ['Moon']
            },
            'divorce': {
                'primary': ['Saturn', 'Mars', 'Sun'],
                'secondary': ['Rahu', 'Ketu']
            },
            'job_start': {
                'primary': ['Sun', 'Jupiter', 'Saturn'],
                'secondary': ['Mercury', 'Mars']
            },
            'job_end': {
                'primary': ['Saturn', 'Mars'],
                'secondary': ['Sun']
            },
            'promotion': {
                'primary': ['Jupiter', 'Sun', 'Mercury'],
                'secondary': ['Venus']
            },
            'relocation': {
                'primary': ['Moon', 'Mars', 'Rahu'],
                'secondary': ['Mercury']
            },
            'childbirth': {
                'primary': ['Jupiter', 'Moon'],
                'secondary': ['Venus', 'Sun']
            },
            'parent_death': {
                'primary': ['Saturn', 'Sun', 'Mars'],
                'secondary': ['Rahu']
            },
            'property_purchase': {
                'primary': ['Mars', 'Moon', 'Venus'],
                'secondary': ['Jupiter']
            },
            'business_start': {
                'primary': ['Mercury', 'Jupiter', 'Sun'],
                'secondary': ['Venus', 'Mars']
            },
            'education_start': {
                'primary': ['Mercury', 'Jupiter'],
                'secondary': ['Venus']
            },
            'major_accident': {
                'primary': ['Mars', 'Saturn', 'Rahu'],
                'secondary': ['Sun']
            },
            'surgery': {
                'primary': ['Mars', 'Saturn'],
                'secondary': ['Sun']
            }
        }

        return event_dasha_map.get(event_type, {
            'primary': ['Jupiter'],  # Default to Jupiter
            'secondary': []
        })

    def _get_relevant_houses_for_event(self, event_type: str) -> List[int]:
        """Get relevant houses for event type"""
        event_house_map = {
            'marriage': [7, 8],
            'divorce': [6, 8, 12],
            'job_start': [10, 6],
            'job_end': [6, 8, 12],
            'promotion': [10, 11],
            'relocation': [3, 12],
            'childbirth': [5, 9],
            'parent_death': [4, 9],  # 4th for mother, 9th for father
            'property_purchase': [4, 11],
            'business_start': [10, 11],
            'education_start': [4, 5],
            'major_accident': [6, 8],
            'surgery': [6, 8]
        }

        return event_house_map.get(event_type, [1])  # Default to 1st house

    def _calculate_confidence(
        self,
        top_candidates: List[Dict[str, Any]],
        event_anchors: List[Dict[str, Any]]
    ) -> int:
        """
        Calculate confidence level in rectification

        Factors:
        - Score difference between top candidates
        - Number of event anchors
        - Quality of event anchors

        Returns:
            Confidence percentage (0-100)
        """
        if not top_candidates or not event_anchors:
            return 0

        confidence = 50  # Base confidence

        # Factor 1: Score spread
        if len(top_candidates) >= 2:
            score_diff = top_candidates[0]['score'] - top_candidates[1]['score']
            if score_diff > 2.0:
                confidence += 20  # Clear winner
            elif score_diff > 1.0:
                confidence += 10
            else:
                confidence -= 10  # Too close

        # Factor 2: Number of event anchors
        if len(event_anchors) >= 5:
            confidence += 20
        elif len(event_anchors) >= 3:
            confidence += 10
        elif len(event_anchors) == 1:
            confidence -= 15

        # Factor 3: Top score absolute value
        top_score = top_candidates[0]['score']
        if top_score >= 8.0:
            confidence += 15
        elif top_score >= 6.0:
            confidence += 5
        elif top_score < 4.0:
            confidence -= 10

        # Clamp to 0-100
        return max(0, min(100, confidence))


# Singleton instance
rectification_service = RectificationService()
