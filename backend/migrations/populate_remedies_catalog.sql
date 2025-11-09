-- Seed Data: Populate Remedies Catalog with Vedic Remedies
-- Author: Claude Code
-- Date: 2024-11-09

-- PLANET-BASED REMEDIES

-- Sun (Surya) Remedies
INSERT INTO remedies_catalog (remedy_name, remedy_type, description, detailed_instructions, planet, frequency, best_time, duration_days, difficulty_level, benefits, precautions, cost_estimate, materials_needed, scripture_reference)
VALUES
('Surya Namaskar (Sun Salutation)', 'spiritual_practice', 'Daily Sun Salutation to strengthen Sun in chart',
'Perform 12 rounds of Surya Namaskar facing east at sunrise. Chant Sun mantras with each round.',
'Sun', 'daily', 'sunrise', 40, 'easy',
ARRAY['Strengthens Sun', 'Improves confidence', 'Enhances leadership', 'Boosts vitality'],
ARRAY['Consult doctor if you have back problems', 'Start slowly if beginner'],
'free', ARRAY['Yoga mat', 'Open space'],
'Rig Veda'),

('Surya Mantra Japa', 'mantra', 'Chant Sun mantra 108 times daily',
'Chant "Om Suryaya Namaha" or Gayatri Mantra 108 times at sunrise facing east. Use rudraksha mala for counting.',
'Sun', 'daily', 'sunrise', 40, 'easy',
ARRAY['Strengthens Sun', 'Removes obstacles', 'Improves health', 'Enhances father relationship'],
ARRAY['Maintain pronunciation accuracy', 'Sit in clean place'],
'free', ARRAY['Rudraksha mala (108 beads)'],
'Surya Upanishad'),

('Donate Wheat on Sunday', 'charity', 'Donate wheat to the needy every Sunday',
'Donate wheat, jaggery, or copper items to poor people or temples every Sunday morning.',
'Sun', 'weekly', 'on_specific_days', NULL, 'easy',
ARRAY['Strengthens Sun', 'Removes pitru dosha', 'Brings prosperity'],
ARRAY['Give with pure intention', 'Do not expect anything in return'],
'low', ARRAY['Wheat', 'Jaggery', 'Copper items'],
'Lal Kitab'),

('Ruby Gemstone', 'gemstone', 'Wear ruby gemstone for strong Sun',
'Wear 3-6 carat natural ruby set in gold ring on Sunday morning after energizing with Surya mantra. Wear on ring finger.',
'Sun', 'one_time', 'sunrise', NULL, 'hard',
ARRAY['Powerful Sun strengthening', 'Leadership boost', 'Health improvement'],
ARRAY['Consult astrologer before wearing', 'Ensure natural gemstone', 'Get energized properly'],
'high', ARRAY['Natural ruby', 'Gold ring', 'Pandit for energizing'],
'Garuda Purana');

-- Moon (Chandra) Remedies
INSERT INTO remedies_catalog (remedy_name, remedy_type, description, detailed_instructions, planet, frequency, best_time, duration_days, difficulty_level, benefits, precautions, cost_estimate, materials_needed)
VALUES
('Chandra Mantra Japa', 'mantra', 'Chant Moon mantra for mental peace',
'Chant "Om Chandraya Namaha" or "Om Som Somaya Namaha" 108 times on Monday evening. Face northwest.',
'Moon', 'daily', 'during_rahukaal', 40, 'easy',
ARRAY['Calms mind', 'Improves emotional balance', 'Strengthens mother relationship', 'Better sleep'],
ARRAY['Best done on Mondays and Full Moon days'],
'free', ARRAY['Rudraksha mala', 'White cloth to sit on']),

('Drink Water from Silver Vessel', 'lifestyle', 'Drink water stored in silver vessel',
'Store water overnight in pure silver vessel and drink in morning on empty stomach.',
'Moon', 'daily', 'sunrise', NULL, 'easy',
ARRAY['Strengthens Moon', 'Improves mental clarity', 'Cooling effect on mind'],
ARRAY['Use pure silver', 'Clean vessel regularly'],
'medium', ARRAY['Pure silver vessel']),

('Pearl Gemstone', 'gemstone', 'Wear pearl for strong Moon',
'Wear 5-7 carat natural pearl set in silver ring on Monday morning. Wear on little finger.',
'Moon', 'one_time', 'sunrise', NULL, 'medium',
ARRAY['Mental peace', 'Emotional stability', 'Better intuition'],
ARRAY['Consult astrologer', 'Ensure natural pearl'],
'medium', ARRAY['Natural pearl', 'Silver ring']),

('Feed White Cow', 'charity', 'Feed white cow on Mondays',
'Feed white cows with green grass or flour balls every Monday.',
'Moon', 'weekly', 'on_specific_days', NULL, 'easy',
ARRAY['Strengthens Moon', 'Mental peace', 'Removes obstacles'],
ARRAY['Be gentle with animals'],
'low', ARRAY['Green grass', 'Flour', 'Jaggery']);

-- Mars (Mangal) Remedies
INSERT INTO remedies_catalog (remedy_name, remedy_type, description, detailed_instructions, planet, dosha, frequency, best_time, duration_days, difficulty_level, benefits, precautions, cost_estimate, materials_needed)
VALUES
('Hanuman Chalisa', 'mantra', 'Recite Hanuman Chalisa for Mars strength',
'Recite Hanuman Chalisa every Tuesday and Saturday. Visit Hanuman temple on Tuesdays.',
'Mars', 'Mangal', 'daily', 'sunrise', 40, 'easy',
ARRAY['Reduces Mangal dosha', 'Increases courage', 'Removes obstacles', 'Protection from enemies'],
ARRAY['Learn correct pronunciation'],
'free', ARRAY['Hanuman Chalisa book']),

('Red Lentil Donation', 'charity', 'Donate red lentils on Tuesdays',
'Donate red lentils (masoor dal), jaggery, or copper to poor people or temples every Tuesday.',
'Mars', 'Mangal', 'weekly', 'on_specific_days', NULL, 'easy',
ARRAY['Reduces Mangal dosha', 'Removes anger', 'Better relationships'],
ARRAY['Give with devotion'],
'low', ARRAY['Red lentils', 'Jaggery', 'Copper items']),

('Red Coral Gemstone', 'gemstone', 'Wear red coral for Mars',
'Wear 5-8 carat natural red coral set in gold/copper ring on Tuesday. Wear on ring finger.',
'Mars', 'Mangal', 'one_time', 'sunrise', NULL, 'medium',
ARRAY['Strengthens Mars', 'Courage', 'Success in competition', 'Reduces Mangal dosha'],
ARRAY['Consult astrologer', 'Not for everyone'],
'medium', ARRAY['Natural red coral', 'Gold or copper ring']),

('Fast on Tuesdays', 'fasting', 'Observe fast on Tuesdays for 21 consecutive weeks',
'Fast from sunrise to sunset on Tuesdays. Eat only once after sunset. No grains, only fruits and milk allowed.',
'Mars', 'Mangal', 'weekly', 'on_specific_days', 147, 'medium',
ARRAY['Powerful Mars remedy', 'Removes Mangal dosha', 'Helps in marriage'],
ARRAY['Consult doctor if health issues', 'Stay hydrated'],
'free', NULL);

-- Mercury (Budh) Remedies
INSERT INTO remedies_catalog (remedy_name, remedy_type, description, detailed_instructions, planet, frequency, best_time, duration_days, difficulty_level, benefits, precautions, cost_estimate, materials_needed)
VALUES
('Budh Mantra Japa', 'mantra', 'Chant Mercury mantra for intelligence',
'Chant "Om Budhaya Namaha" 108 times on Wednesday morning.',
'Mercury', 'daily', 'sunrise', 40, 'easy',
ARRAY['Enhances intelligence', 'Improves communication', 'Better business skills', 'Academic success'],
ARRAY['Maintain regularity'],
'free', ARRAY['Rudraksha mala']),

('Donate Green Items', 'charity', 'Donate green items on Wednesdays',
'Donate green vegetables, green cloth, or educational materials on Wednesdays.',
'Mercury', 'weekly', 'on_specific_days', NULL, 'easy',
ARRAY['Strengthens Mercury', 'Improves communication', 'Better relationships'],
ARRAY['Give with good intention'],
'low', ARRAY['Green vegetables', 'Green cloth', 'Books']),

('Emerald Gemstone', 'gemstone', 'Wear emerald for Mercury',
'Wear 3-6 carat natural emerald set in gold ring on Wednesday. Wear on little finger.',
'Mercury', 'one_time', 'sunrise', NULL, 'hard',
ARRAY['Mental clarity', 'Communication skills', 'Business success'],
ARRAY['Expensive', 'Consult astrologer', 'Ensure natural stone'],
'high', ARRAY['Natural emerald', 'Gold ring']),

('Worship Lord Vishnu', 'puja', 'Worship Lord Vishnu on Wednesdays',
'Visit Vishnu temple or perform Vishnu puja at home every Wednesday.',
'Mercury', 'weekly', 'on_specific_days', NULL, 'easy',
ARRAY['Strengthens Mercury', 'Mental peace', 'Prosperity'],
ARRAY['Learn puja vidhi properly'],
'low', ARRAY['Flowers', 'Incense', 'Tulsi leaves']);

-- Jupiter (Guru) Remedies
INSERT INTO remedies_catalog (remedy_name, remedy_type, description, detailed_instructions, planet, frequency, best_time, duration_days, difficulty_level, benefits, precautions, cost_estimate, materials_needed)
VALUES
('Guru Mantra Japa', 'mantra', 'Chant Jupiter mantra for wisdom',
'Chant "Om Gurave Namaha" or "Om Brihaspataye Namaha" 108 times on Thursday morning.',
'Jupiter', 'daily', 'sunrise', 40, 'easy',
ARRAY['Enhances wisdom', 'Spiritual growth', 'Good luck', 'Children blessings'],
ARRAY['Face northeast while chanting'],
'free', ARRAY['Rudraksha mala', 'Yellow cloth']),

('Donate Yellow Items', 'charity', 'Donate yellow items on Thursdays',
'Donate turmeric, yellow cloth, gram dal, or gold to Brahmins or temples on Thursdays.',
'Jupiter', 'weekly', 'on_specific_days', NULL, 'easy',
ARRAY['Strengthens Jupiter', 'Financial prosperity', 'Good fortune'],
ARRAY['Donate in morning hours'],
'low', ARRAY['Turmeric', 'Yellow cloth', 'Gram dal']),

('Yellow Sapphire Gemstone', 'gemstone', 'Wear yellow sapphire for Jupiter',
'Wear 3-6 carat natural yellow sapphire set in gold ring on Thursday. Wear on index finger.',
'Jupiter', 'one_time', 'sunrise', NULL, 'hard',
ARRAY['Prosperity', 'Wisdom', 'Marriage', 'Children'],
ARRAY['One of the most beneficial stones', 'Expensive', 'Consult astrologer'],
'high', ARRAY['Natural yellow sapphire', 'Gold ring']),

('Worship Banana Tree', 'ritual', 'Worship banana tree on Thursdays',
'Offer water and yellow flowers to banana tree every Thursday.',
'Jupiter', 'weekly', 'on_specific_days', NULL, 'easy',
ARRAY['Strengthens Jupiter', 'Family happiness', 'Children blessings'],
ARRAY['Be respectful to nature'],
'free', ARRAY['Water', 'Yellow flowers']);

-- Venus (Shukra) Remedies
INSERT INTO remedies_catalog (remedy_name, remedy_type, description, detailed_instructions, planet, frequency, best_time, duration_days, difficulty_level, benefits, precautions, cost_estimate, materials_needed)
VALUES
('Shukra Mantra Japa', 'mantra', 'Chant Venus mantra for luxury and love',
'Chant "Om Shukraya Namaha" 108 times on Friday morning.',
'Venus', 'daily', 'sunrise', 40, 'easy',
ARRAY['Enhances beauty', 'Attracts love', 'Luxury', 'Artistic talents'],
ARRAY['Best results on Fridays'],
'free', ARRAY['Rudraksha mala', 'White flowers']),

('Donate White Items', 'charity', 'Donate white items on Fridays',
'Donate white rice, milk, sugar, white cloth, or silver to women or temples on Fridays.',
'Venus', 'weekly', 'on_specific_days', NULL, 'easy',
ARRAY['Strengthens Venus', 'Marital harmony', 'Beauty', 'Comforts'],
ARRAY['Respect women while donating'],
'low', ARRAY['White rice', 'Milk', 'Sugar', 'White cloth']),

('Diamond Gemstone', 'gemstone', 'Wear diamond for Venus',
'Wear 1-2 carat natural diamond set in platinum/silver ring on Friday. Wear on middle finger.',
'Venus', 'one_time', 'sunrise', NULL, 'hard',
ARRAY['Luxury', 'Beauty', 'Marital bliss', 'Artistic success'],
ARRAY['Very expensive', 'Consult astrologer', 'Alternative: White sapphire'],
'high', ARRAY['Natural diamond', 'Platinum or silver ring']),

('Worship Goddess Lakshmi', 'puja', 'Worship Lakshmi on Fridays',
'Perform Lakshmi puja at home or visit Lakshmi temple every Friday evening.',
'Venus', 'weekly', 'on_specific_days', NULL, 'easy',
ARRAY['Wealth', 'Beauty', 'Marital happiness', 'Comforts'],
ARRAY['Keep home clean', 'Light ghee lamp'],
'low', ARRAY['Lotus flowers', 'Ghee lamp', 'Incense']);

-- Saturn (Shani) Remedies
INSERT INTO remedies_catalog (remedy_name, remedy_type, description, detailed_instructions, planet, frequency, best_time, duration_days, difficulty_level, benefits, precautions, cost_estimate, materials_needed)
VALUES
('Shani Mantra Japa', 'mantra', 'Chant Saturn mantra for obstacles removal',
'Chant "Om Shanaischaraya Namaha" 108 times on Saturday morning.',
'Saturn', 'daily', 'sunrise', 40, 'easy',
ARRAY['Reduces Saturn malefic effects', 'Removes obstacles', 'Patience', 'Discipline'],
ARRAY['Very important to maintain regularity'],
'free', ARRAY['Rudraksha mala', 'Black cloth']),

('Donate Black Items', 'charity', 'Donate black items and serve poor on Saturdays',
'Donate black sesame, black cloth, iron items, or mustard oil to poor people every Saturday.',
'Saturn', 'weekly', 'on_specific_days', NULL, 'easy',
ARRAY['Reduces Shani dosha', 'Removes suffering', 'Better fortune'],
ARRAY['Serve with compassion', 'Help elderly and disabled'],
'low', ARRAY['Black sesame', 'Black cloth', 'Mustard oil', 'Iron items']),

('Blue Sapphire Gemstone', 'gemstone', 'Wear blue sapphire (Neelam) for Saturn',
'Wear 5-7 carat natural blue sapphire set in silver/iron ring on Saturday. Wear on middle finger. TRIAL PERIOD: Keep near pillow for 3 days first.',
'Saturn', 'one_time', 'during_rahukaal', NULL, 'hard',
ARRAY['Powerful effects', 'Quick results', 'Removes obstacles'],
ARRAY['MOST IMPORTANT: Do 3-day trial first', 'Can give negative results if unsuitable', 'Must consult expert astrologer', 'Remove immediately if bad dreams/events occur'],
'high', ARRAY['Natural blue sapphire', 'Silver or iron ring']),

('Serve Crows', 'charity', 'Feed crows on Saturdays',
'Feed crows with rice balls or leftover food every Saturday morning. Consider crows as ancestors.',
'Saturn', 'weekly', 'on_specific_days', NULL, 'easy',
ARRAY['Reduces Saturn affliction', 'Ancestral blessings', 'Removes pitru dosha'],
ARRAY['Feed with respect'],
'free', ARRAY['Rice', 'Leftover food']),

('Hanuman Worship for Shani', 'ritual', 'Worship Hanuman for Saturn protection',
'Visit Hanuman temple on Saturdays. Apply sindoor to Hanuman idol. Recite Hanuman Chalisa.',
'Saturn', 'weekly', 'on_specific_days', NULL, 'easy',
ARRAY['Protection from Saturn', 'Reduces obstacles', 'Mental strength'],
ARRAY['Maintain faith'],
'free', ARRAY['Sindoor', 'Flowers']);

-- Rahu Remedies
INSERT INTO remedies_catalog (remedy_name, remedy_type, description, detailed_instructions, planet, dosha, frequency, best_time, duration_days, difficulty_level, benefits, precautions, cost_estimate, materials_needed)
VALUES
('Rahu Mantra Japa', 'mantra', 'Chant Rahu mantra for Rahu dosha',
'Chant "Om Rahave Namaha" or "Om Bhram Bhreem Bhraum Sah Rahave Namaha" 108 times daily.',
'Rahu', 'Kaal Sarp', 'daily', 'during_rahukaal', 40, 'medium',
ARRAY['Reduces Rahu dosha', 'Removes confusion', 'Mental clarity', 'Success in competition'],
ARRAY['Chant during Rahukaal for best results'],
'free', ARRAY['Rudraksha mala']),

('Donate Dark Blue Items', 'charity', 'Donate to poor and serve lepers',
'Donate blankets, warm clothes, or food to poor people, lepers, and orphans on Saturdays.',
'Rahu', 'Kaal Sarp', 'weekly', 'on_specific_days', NULL, 'easy',
ARRAY['Reduces Rahu affliction', 'Good karma', 'Removes obstacles'],
ARRAY['Serve with compassion', 'No ego while giving'],
'low', ARRAY['Blankets', 'Warm clothes', 'Food']),

('Hessonite Garnet (Gomed)', 'gemstone', 'Wear Gomed for Rahu',
'Wear 5-8 carat natural hessonite garnet set in silver ring on Saturday. Wear on middle finger.',
'Rahu', 'Kaal Sarp', 'one_time', 'during_rahukaal', NULL, 'medium',
ARRAY['Calms Rahu', 'Mental peace', 'Success', 'Removes confusion'],
ARRAY['Consult astrologer', 'Ensure natural stone'],
'medium', ARRAY['Natural gomed', 'Silver ring']),

('Donate Coconut', 'ritual', 'Donate coconut in flowing water',
'Offer a coconut to flowing water (river/sea) on Saturdays or Amavasya.',
'Rahu', 'Kaal Sarp', 'monthly', 'on_specific_days', NULL, 'easy',
ARRAY['Reduces Kaal Sarp dosha', 'Mental peace'],
ARRAY['Do with proper intention'],
'low', ARRAY['Coconut']);

-- Ketu Remedies
INSERT INTO remedies_catalog (remedy_name, remedy_type, description, detailed_instructions, planet, frequency, best_time, duration_days, difficulty_level, benefits, precautions, cost_estimate, materials_needed)
VALUES
('Ketu Mantra Japa', 'mantra', 'Chant Ketu mantra for spiritual growth',
'Chant "Om Ketave Namaha" or "Om Stram Streem Straum Sah Ketave Namaha" 108 times daily.',
'Ketu', 'daily', 'sunrise', 40, 'medium',
ARRAY['Spiritual growth', 'Removes obstacles', 'Clarity', 'Detachment'],
ARRAY['Best for spiritual seekers'],
'free', ARRAY['Rudraksha mala']),

('Donate Gray/Multi-color Items', 'charity', 'Donate blankets and help street dogs',
'Donate blankets to poor, feed street dogs, and help old-age homes.',
'Ketu', 'weekly', 'on_specific_days', NULL, 'easy',
ARRAY['Reduces Ketu affliction', 'Good karma', 'Spiritual merit'],
ARRAY['Serve animals with love'],
'low', ARRAY['Blankets', 'Dog food']),

('Cat''s Eye Gemstone', 'gemstone', 'Wear Cat''s Eye (Lehsunia) for Ketu',
'Wear 5-7 carat natural cat''s eye set in silver ring on Thursday. Wear on middle finger. Do trial period.',
'Ketu', 'one_time', 'sunrise', NULL, 'hard',
ARRAY['Spiritual progress', 'Intuition', 'Protection'],
ARRAY['Do 3-day trial', 'Consult astrologer', 'Can give strong effects'],
'medium', ARRAY['Natural cat''s eye', 'Silver ring']),

('Worship Lord Ganesha', 'puja', 'Daily Ganesha worship for Ketu',
'Worship Lord Ganesha daily. Offer durva grass and modak.',
'Ketu', 'daily', 'morning', NULL, 'easy',
ARRAY['Removes obstacles', 'Spiritual growth', 'Wisdom'],
ARRAY['Maintain devotion'],
'free', ARRAY['Durva grass', 'Flowers', 'Modak']);

-- DOSHA-SPECIFIC REMEDIES

-- Mangal Dosha Remedies
INSERT INTO remedies_catalog (remedy_name, remedy_type, description, detailed_instructions, dosha, frequency, best_time, duration_days, difficulty_level, benefits, precautions, cost_estimate, materials_needed)
VALUES
('Kumbh Vivah (Pot Marriage)', 'ritual', 'Symbolic marriage with pot to nullify Mangal dosha',
'Perform Kumbh Vivah ritual where person symbolically marries a pot (kumbh) before actual marriage. Must be done by qualified pandit.',
'Mangal', 'one_time', 'on_specific_days', NULL, 'medium',
ARRAY['Nullifies Mangal dosha', 'Removes marriage obstacles', 'Traditional remedy'],
ARRAY['Must be done by expert pandit', 'Complete ritual properly'],
'medium', ARRAY['Kumbh (pot)', 'Pandit fees', 'Puja materials']),

('Mangal Bhat Puja', 'puja', 'Special puja for Mangal dosha',
'Perform Mangal Bhat puja at home or temple. Feed married women (Suvasinis). Do on Tuesdays.',
'Mangal', 'monthly', 'on_specific_days', NULL, 'medium',
ARRAY['Reduces Mangal dosha', 'Marriage harmony', 'Family peace'],
ARRAY['Respect married women'],
'medium', ARRAY['Puja materials', 'Food for women']);

-- Kaal Sarp Dosha Remedies
INSERT INTO remedies_catalog (remedy_name, remedy_type, description, detailed_instructions, dosha, frequency, best_time, difficulty_days, difficulty_level, benefits, precautions, cost_estimate, materials_needed)
VALUES
('Kaal Sarp Puja at Trimbakeshwar', 'puja', 'Special Kaal Sarp dosha puja at sacred temple',
'Visit Trimbakeshwar temple (near Nashik) and perform Kaal Sarp puja by authorized pandits. Can be done once in lifetime or annually.',
'Kaal Sarp', 'one_time', NULL, NULL, 'hard',
ARRAY['Powerful remedy for Kaal Sarp dosha', 'Removes major obstacles', 'Peace of mind'],
ARRAY['Plan trip to Trimbakeshwar', 'Costs involved for travel and puja', 'Book pandit in advance'],
'high', ARRAY['Travel to Trimbakeshwar', 'Pandit fees', 'Puja materials']),

('Sarpa Samskara (Naga Pratishtha)', 'ritual', 'Snake worship ritual for Kaal Sarp dosha',
'Perform snake worship at Naga temples or under Peepal tree on Naga Panchami.',
'Kaal Sarp', 'yearly', 'on_specific_days', NULL, 'medium',
ARRAY['Reduces Kaal Sarp effects', 'Removes serpent curse', 'Family harmony'],
ARRAY['Do on Naga Panchami for best results'],
'low', ARRAY['Milk', 'Flowers', 'Snake idols']);

-- Pitra Dosha Remedies
INSERT INTO remedies_catalog (remedy_name, remedy_type, description, detailed_instructions, dosha, frequency, best_time, duration_days, difficulty_level, benefits, precautions, cost_estimate, materials_needed)
VALUES
('Pitru Paksha Shraddha', 'ritual', 'Annual ancestral rites during Pitru Paksha',
'Perform Shraddha (ancestral rites) during Pitru Paksha (15 days before Diwali). Feed Brahmins and poor.',
'Pitra', 'yearly', 'on_specific_days', NULL, 'medium',
ARRAY['Removes Pitra dosha', 'Ancestral blessings', 'Family prosperity', 'Children blessings'],
ARRAY['Must be done annually', 'Maintain faith'],
'medium', ARRAY['Pandit fees', 'Food for Brahmins', 'Puja materials']),

('Tripindi Shraddha', 'ritual', 'Special ritual for Pitra dosha removal',
'Perform Tripindi Shraddha at holy places like Gaya, Trimbakeshwar, or Haridwar. Done once in lifetime.',
'Pitra', 'one_time', NULL, NULL, 'hard',
ARRAY['Powerful Pitra dosha remedy', 'Removes ancestral curse', 'Family happiness'],
ARRAY['Expensive', 'Requires travel', 'Must be done properly'],
'high', ARRAY['Travel costs', 'Pandit fees', 'Puja materials']);

-- GENERAL SPIRITUAL PRACTICES

INSERT INTO remedies_catalog (remedy_name, remedy_type, description, detailed_instructions, frequency, best_time, duration_days, difficulty_level, benefits, precautions, cost_estimate, materials_needed)
VALUES
('Gayatri Mantra Japa', 'mantra', 'Universal mantra for all-round benefits',
'Chant Gayatri Mantra 108 times daily at sunrise. Face east. "Om Bhur Bhuva Swaha..."',
'daily', 'sunrise', NULL, 'easy',
ARRAY['Spiritual growth', 'Mental clarity', 'Protection', 'Overall well-being'],
ARRAY['Sacred mantra - maintain purity', 'Can be chanted by all'],
'free', ARRAY['Rudraksha mala', 'Clean place']),

('Mahamrityunjaya Mantra', 'mantra', 'Powerful healing and protection mantra',
'Chant Mahamrityunjaya Mantra 108 times daily. "Om Tryambakam Yajamahe..."',
'daily', 'morning', 40, 'medium',
ARRAY['Healing', 'Protection from death', 'Removes diseases', 'Longevity'],
ARRAY['Very powerful mantra', 'Learn proper pronunciation'],
'free', ARRAY['Rudraksha mala']),

('Rudrabhishek', 'puja', 'Lord Shiva abhishek on Mondays',
'Perform Rudrabhishek (Shiva abhishek) with milk, water, honey, curd, and ghee on Mondays.',
'weekly', 'on_specific_days', NULL, 'medium',
ARRAY['Removes all doshas', 'Shiva blessings', 'Overall prosperity'],
ARRAY['Maintain purity', 'Can be done at home or temple'],
'low', ARRAY['Milk', 'Honey', 'Curd', 'Ghee', 'Bilva leaves']),

('Meditation', 'meditation', 'Daily meditation for mental peace',
'Sit in quiet place, close eyes, focus on breath for 20 minutes daily.',
'daily', 'sunrise', NULL, 'easy',
ARRAY['Mental peace', 'Clarity', 'Spiritual growth', 'Stress relief'],
ARRAY['Start with 10 minutes', 'Gradually increase'],
'free', ARRAY['Quiet place', 'Meditation cushion (optional)']);

-- Mark all as active
UPDATE remedies_catalog SET is_active = true;
