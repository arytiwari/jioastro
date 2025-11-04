# Planet Display in Birth Charts

All three chart visualization styles (North Indian, South Indian, and Western) now display planets with their symbols and retrograde indicators.

## Planet Symbols Used

| Planet | Symbol | Unicode | Description |
|--------|--------|---------|-------------|
| Sun | ☉ | U+2609 | Solar symbol |
| Moon | ☽ | U+263D | Lunar crescent |
| Mars | ♂ | U+2642 | Mars/Male symbol |
| Mercury | ☿ | U+263F | Mercury/Caduceus |
| Jupiter | ♃ | U+2643 | Jupiter symbol |
| Venus | ♀ | U+2640 | Venus/Female symbol |
| Saturn | ♄ | U+2644 | Saturn symbol |
| Rahu | ☊ | U+260A | Ascending Node |
| Ketu | ☋ | U+260B | Descending Node |

## Chart Display Styles

### 1. North Indian Chart (Diamond Layout)

**Features:**
- Traditional diamond-shaped layout
- House 1 at the top (ascendant position varies by sign)
- 12 houses in diamond arrangement
- **Planet Display:**
  - Planets shown as symbols in their respective houses
  - Multiple planets in a house are stacked vertically
  - Retrograde planets marked with 'ʀ' in red color
  - House numbers shown prominently
  - Sign abbreviations (ARI, TAU, GEM, etc.)

**Example Display in a House:**
```
House: 5
Sign: LEO
Planets: ☉ ♀ ☿ʀ
```

### 2. South Indian Chart (Square Layout)

**Features:**
- Square grid layout with fixed zodiac sign positions
- Signs remain in same positions, houses rotate with ascendant
- 12 sections showing zodiac glyphs
- **Planet Display:**
  - Planets appear in their zodiac sign sections
  - House numbers shown as "H1", "H2", etc.
  - Sign glyphs (♈, ♉, ♊, etc.) with abbreviations
  - Retrograde planets in red with 'ʀ' marker
  - Color coding for special houses:
    - Purple: Ascendant (H1)
    - Amber: Kendra houses (H1, H4, H7, H10)
    - Blue: Trikona houses (H5, H9)

**Example Display:**
```
H5
♌ LE
☉ ♀ ☿ʀ
```

### 3. Western Circular Chart

**Features:**
- Circular wheel layout
- Traditional Western appearance with Vedic data
- Ascendant at 9 o'clock position (180°)
- Houses proceed counter-clockwise
- **Planet Display:**
  - Planets shown as symbols on inner ring
  - Positioned at exact degrees on the wheel
  - Each planet in a white circle
  - Retrograde planets have red circle outline
  - Zodiac glyphs on outer ring
  - House numbers in middle ring

**Visual Layout:**
```
Outer ring: Zodiac signs (♈♉♊...)
Middle ring: House numbers (1-12)
Inner ring: Planet symbols with exact positions
Center: "Vedic Birth Chart" + Ascendant
```

## Retrograde Indication

All three chart styles indicate retrograde planets:
- **Visual marker**: 'ʀ' superscript after planet symbol
- **Color**: Red or darker color for retrograde planets
- **Western chart**: Red circle outline around planet

Example: ☿ʀ (Mercury retrograde)

## Data Structure

Charts receive planet data in this format:
```typescript
{
  sign: "Leo",
  sign_num: 4,
  degree: 15.234567,
  longitude: 135.234567,
  house: 5,
  retrograde: false,
  nakshatra: {
    name: "Magha",
    pada: 2
  }
}
```

## Implementation Details

### Planet Grouping

- **North Indian**: Groups planets by house number
- **South Indian**: Groups planets by zodiac sign number
- **Western**: Positions planets by exact degree on circular wheel

### Spacing and Layout

- **North Indian**: Vertical stacking with calculated line spacing (3.8% of chart size)
- **South Indian**: Vertical stacking with 20px spacing
- **Western**: Positioned at exact degrees with 180px radius from center

## Viewing Charts

To view planets in charts:

1. Navigate to any birth chart page
2. Use the chart selector buttons at the top:
   - **North Indian** - Traditional diamond style
   - **South Indian** - Square grid style
   - **Western Style** - Circular wheel
3. All three styles display the same planetary data
4. Switch between styles to see different presentations

## Chart Types Supported

Planets display in all chart types:
- **D1 (Rashi)**: Birth chart
- **D9 (Navamsa)**: Divisional chart for marriage/dharma
- **Moon Chart (Chandra Kundali)**: Chart from Moon's perspective

Each chart type shows planets in their respective positions for that chart division.

## Accessibility

- All charts include proper ARIA labels
- Symbols use standard Unicode characters
- High contrast colors for readability
- Text alternatives provided in legends
