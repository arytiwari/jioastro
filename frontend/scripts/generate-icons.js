const { Resvg } = require('@resvg/resvg-js');
const fs = require('fs');
const path = require('path');

const sizes = [192, 384, 512];
const svgPath = path.join(__dirname, '../public/icon.svg');
const publicDir = path.join(__dirname, '../public');

// Read SVG file
const svgContent = fs.readFileSync(svgPath, 'utf-8');

console.log('Converting SVG to PNG icons...');

sizes.forEach(size => {
  try {
    // Create Resvg instance with specific size
    const resvg = new Resvg(svgContent, {
      fitTo: {
        mode: 'width',
        value: size,
      },
    });

    // Render to PNG
    const pngData = resvg.render();
    const pngBuffer = pngData.asPng();

    // Save PNG file
    const outputPath = path.join(publicDir, `icon-${size}x${size}.png`);
    fs.writeFileSync(outputPath, pngBuffer);

    console.log(`✅ Generated icon-${size}x${size}.png`);
  } catch (error) {
    console.error(`❌ Failed to generate icon-${size}x${size}.png:`, error.message);
  }
});

console.log('Icon generation complete!');
