-- Evidence Mode - Seed Data
-- Classical Vedic astrology texts and foundational sources
-- Run this after migration.sql

-- ============================================================================
-- Classical Vedic Texts
-- ============================================================================

INSERT INTO evidence_mode_sources (
    title,
    author,
    source_type,
    description,
    excerpt,
    publication_year,
    language,
    tags,
    keywords,
    credibility_score,
    is_verified,
    is_public
) VALUES
(
    'Brihat Parashara Hora Shastra (BPHS)',
    'Maharishi Parashara',
    'classical_text',
    'The foundational text of Vedic astrology, containing the core principles taught by Maharishi Parashara to his disciples. Covers houses, planets, yogas, dashas, and predictive techniques.',
    'The text covers planetary influences, house significations, yogas, dasha systems, and comprehensive predictive methodologies.',
    -500,
    'sanskrit',
    '["classical", "vedic", "foundational", "yogas", "dashas", "houses"]',
    '["parashara", "bphs", "hora", "shastra", "planets", "houses", "yogas"]',
    0.98,
    TRUE,
    TRUE
),
(
    'Jataka Parijata',
    'Vaidyanatha Dikshita',
    'classical_text',
    'A comprehensive treatise on Vedic astrology written in the 15th century CE. Known for its precise rules on chart interpretation, yogas, and predictive techniques.',
    'Detailed analysis of planetary combinations, yogas, and their effects on various life areas.',
    1450,
    'sanskrit',
    '["classical", "vedic", "yogas", "predictions"]',
    '["jataka", "parijata", "vaidyanatha", "combinations", "effects"]',
    0.95,
    TRUE,
    TRUE
),
(
    'Phaladeepika',
    'Mantreswara',
    'classical_text',
    'A classical text focusing on predictive astrology and interpretation of planetary positions. Written in the 14th century CE, it provides clear rules for chart analysis.',
    'Systematic approach to analyzing planetary strength, yogas, and making predictions about life events.',
    1350,
    'sanskrit',
    '["classical", "predictions", "analysis", "strength"]',
    '["phaladeepika", "mantreswara", "planetary", "strength", "predictions"]',
    0.94,
    TRUE,
    TRUE
),
(
    'Saravali',
    'Kalyana Varma',
    'classical_text',
    'An ancient text covering all aspects of Vedic astrology including planetary effects, yogas, dashas, and transits. One of the most comprehensive classical works.',
    'Extensive coverage of planetary combinations, their effects, and timing of events through dasha systems.',
    800,
    'sanskrit',
    '["classical", "comprehensive", "yogas", "dashas", "transits"]',
    '["saravali", "kalyana", "varma", "planetary", "effects", "dashas"]',
    0.96,
    TRUE,
    TRUE
),
(
    'Uttara Kalamrita',
    'Kalidasa',
    'classical_text',
    'A classical work by the renowned astrologer-poet Kalidasa, focusing on predictive techniques and timing of events. Known for its poetic style and practical insights.',
    'Practical rules for prediction, planetary strengths, and timing methodologies with clear examples.',
    1025,
    'sanskrit',
    '["classical", "predictions", "timing", "practical"]',
    '["uttara", "kalamrita", "kalidasa", "timing", "events"]',
    0.93,
    TRUE,
    TRUE
),
(
    'Brihat Jataka',
    'Varahamihira',
    'classical_text',
    'One of the most authoritative classical texts on Vedic astrology by the legendary Varahamihira. Covers natal astrology, planetary combinations, and predictive principles.',
    'Comprehensive treatment of planetary influences, house significations, and yogas with mathematical precision.',
    505,
    'sanskrit',
    '["classical", "authoritative", "varahamihira", "natal", "yogas"]',
    '["brihat", "jataka", "varahamihira", "natal", "combinations"]',
    0.97,
    TRUE,
    TRUE
),
(
    'Hora Sara',
    'Prithuyasas',
    'classical_text',
    'A classical text dealing with hora or horary astrology and natal chart interpretation. Contains important principles for analyzing planetary positions.',
    'Rules for analyzing planetary positions, aspects, and their effects on different life areas.',
    700,
    'sanskrit',
    '["classical", "hora", "natal", "interpretation"]',
    '["hora", "sara", "prithuyasas", "horary", "aspects"]',
    0.92,
    TRUE,
    TRUE
),
(
    'Laghu Parashari',
    'Varaha Mihira (attributed)',
    'classical_text',
    'A concise version of Parashari principles focusing on essential predictive techniques and planetary combinations.',
    'Simplified yet comprehensive rules for chart analysis and prediction.',
    600,
    'sanskrit',
    '["classical", "parashari", "concise", "essentials"]',
    '["laghu", "parashari", "techniques", "combinations"]',
    0.91,
    TRUE,
    TRUE
);

-- ============================================================================
-- Modern Research and Studies
-- ============================================================================

INSERT INTO evidence_mode_sources (
    title,
    author,
    source_type,
    description,
    url,
    publication_year,
    language,
    tags,
    keywords,
    credibility_score,
    is_verified,
    is_public
) VALUES
(
    'Light on Life: An Introduction to the Astrology of India',
    'Hart de Fouw and Robert Svoboda',
    'modern_study',
    'A comprehensive modern introduction to Vedic astrology by respected scholars, bridging classical wisdom with contemporary understanding.',
    'https://example.com/light-on-life',
    1996,
    'english',
    '["modern", "introduction", "scholarly", "comprehensive"]',
    '["vedic", "astrology", "defouw", "svoboda", "introduction"]',
    0.88,
    TRUE,
    TRUE
),
(
    'Astrology of the Seers',
    'David Frawley (Pandit Vamadeva Shastri)',
    'modern_study',
    'A guide to Vedic astrology by a renowned scholar, explaining classical principles in modern context with practical applications.',
    'https://example.com/astrology-seers',
    2000,
    'english',
    '["modern", "vedic", "practical", "scholarly"]',
    '["frawley", "vamadeva", "vedic", "seers", "principles"]',
    0.90,
    TRUE,
    TRUE
),
(
    'The Art and Science of Vedic Astrology: Volume 1',
    'Richard Fish and Ryan Kurczak',
    'modern_study',
    'A systematic modern approach to learning Vedic astrology, combining traditional knowledge with practical techniques.',
    'https://example.com/art-science-vedic',
    2012,
    'english',
    '["modern", "systematic", "practical", "educational"]',
    '["fish", "kurczak", "vedic", "art", "science", "learning"]',
    0.85,
    TRUE,
    TRUE
);

-- ============================================================================
-- Expert Opinions and Traditional Teachings
-- ============================================================================

INSERT INTO evidence_mode_sources (
    title,
    author,
    source_type,
    description,
    publication_year,
    language,
    tags,
    keywords,
    credibility_score,
    is_verified,
    is_public
) VALUES
(
    'Traditional Parampara Teachings',
    'Various Guru-Shishya Lineages',
    'traditional',
    'Oral traditions and teachings passed down through authentic guru-shishya (teacher-student) lineages in Vedic astrology.',
    NULL,
    'multiple',
    '["traditional", "oral", "lineage", "authentic"]',
    '["parampara", "guru", "shishya", "oral", "tradition"]',
    0.87,
    TRUE,
    TRUE
),
(
    'Parashari Principles: Core Concepts',
    'Traditional Vedic Astrologers',
    'traditional',
    'Core concepts from the Parashari school of astrology as practiced and taught by traditional astrologers.',
    NULL,
    'sanskrit',
    '["traditional", "parashari", "core", "foundational"]',
    '["parashari", "principles", "core", "concepts", "traditional"]',
    0.89,
    TRUE,
    TRUE
);

-- ============================================================================
-- Sample Citations for Common Yogas
-- ============================================================================

-- Raj Yoga Citation
INSERT INTO evidence_mode_citations (
    source_id,
    insight_type,
    insight_text,
    insight_reference,
    confidence_level,
    confidence_score,
    relevance_score,
    context,
    reasoning,
    is_active
)
SELECT
    id,
    'yoga',
    'Raj Yoga is formed when lords of Kendra (1st, 4th, 7th, 10th) and Trikona (1st, 5th, 9th) houses combine or aspect each other',
    'raj_yoga_definition',
    'very_high',
    0.95,
    0.98,
    '{"yoga_type": "raj_yoga", "houses": ["kendra", "trikona"], "effect": "power_and_authority"}',
    'Classical definition from BPHS Chapter 41, widely accepted across all schools of Vedic astrology',
    TRUE
FROM evidence_mode_sources
WHERE title = 'Brihat Parashara Hora Shastra (BPHS)'
LIMIT 1;

-- Dhana Yoga Citation
INSERT INTO evidence_mode_citations (
    source_id,
    insight_type,
    insight_text,
    insight_reference,
    confidence_level,
    confidence_score,
    relevance_score,
    context,
    reasoning,
    is_active
)
SELECT
    id,
    'yoga',
    'Dhana Yoga (wealth yoga) is formed when lords of 2nd, 5th, 9th, or 11th houses combine or aspect each other',
    'dhana_yoga_definition',
    'high',
    0.92,
    0.95,
    '{"yoga_type": "dhana_yoga", "houses": [2, 5, 9, 11], "effect": "wealth_prosperity"}',
    'Traditional definition found in multiple classical texts including Phaladeepika',
    TRUE
FROM evidence_mode_sources
WHERE title = 'Phaladeepika'
LIMIT 1;

-- Gaja Kesari Yoga Citation
INSERT INTO evidence_mode_citations (
    source_id,
    insight_type,
    insight_text,
    insight_reference,
    confidence_level,
    confidence_score,
    relevance_score,
    context,
    reasoning,
    is_active
)
SELECT
    id,
    'yoga',
    'Gaja Kesari Yoga is formed when Jupiter is in a kendra (angular house) from the Moon, bestowing intelligence, wisdom, and prosperity',
    'gaja_kesari_yoga',
    'very_high',
    0.96,
    0.97,
    '{"yoga_type": "gaja_kesari", "planets": ["jupiter", "moon"], "position": "kendra", "effects": ["intelligence", "wisdom", "prosperity"]}',
    'One of the most celebrated yogas, mentioned in Brihat Jataka and extensively described in classical literature',
    TRUE
FROM evidence_mode_sources
WHERE title = 'Brihat Jataka'
LIMIT 1;

-- Mars in 10th House Citation
INSERT INTO evidence_mode_citations (
    source_id,
    insight_type,
    insight_text,
    insight_reference,
    confidence_level,
    confidence_score,
    relevance_score,
    context,
    reasoning,
    is_active
)
SELECT
    id,
    'planet_position',
    'Mars in the 10th house gives strong career drive, leadership abilities, and success through courage and determination',
    'mars_10th_house',
    'high',
    0.88,
    0.90,
    '{"planet": "mars", "house": 10, "effects": ["career_drive", "leadership", "courage"]}',
    'Classical interpretation from BPHS Chapter 26 on planetary effects in houses',
    TRUE
FROM evidence_mode_sources
WHERE title = 'Brihat Parashara Hora Shastra (BPHS)'
LIMIT 1;

-- ============================================================================
-- Statistics
-- ============================================================================

-- Display summary
DO $$
DECLARE
    source_count INTEGER;
    citation_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO source_count FROM evidence_mode_sources;
    SELECT COUNT(*) INTO citation_count FROM evidence_mode_citations;

    RAISE NOTICE '========================================';
    RAISE NOTICE 'Evidence Mode Seed Data Complete';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Sources Added: %', source_count;
    RAISE NOTICE 'Citations Added: %', citation_count;
    RAISE NOTICE '========================================';
END $$;
