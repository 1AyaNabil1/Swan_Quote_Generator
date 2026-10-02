/**
 * Draws a quote as an image on a canvas, for downloading or sharing.
 *
 * The browser shapes Arabic and lays out right-to-left text itself; this only picks the
 * font size that fits, wraps the lines and centers them.
 */

export const SIZES = {
  square: { width: 1080, height: 1080, label: { en: 'Square', ar: 'مربع' }, hint: 'Instagram' },
  story: { width: 1080, height: 1920, label: { en: 'Story', ar: 'ستوري' }, hint: 'Instagram, WhatsApp' },
  landscape: { width: 1200, height: 630, label: { en: 'Wide', ar: 'عريض' }, hint: 'X, Facebook, LinkedIn' },
};

export const THEMES = {
  night: { label: { en: 'Night', ar: 'ليل' }, from: '#07040d', to: '#2b1460', text: '#f5f3ff', accent: '#a78bfa' },
  dawn: { label: { en: 'Dawn', ar: 'فجر' }, from: '#fdf2f8', to: '#e9e3ff', text: '#2e1065', accent: '#7c3aed' },
  ink: { label: { en: 'Ink', ar: 'حبر' }, from: '#fbfaf7', to: '#fbfaf7', text: '#111111', accent: '#6b6b6b' },
};

const LINE_HEIGHT = { en: 1.35, ar: 1.75 };

/** Greedy word wrap at `maxWidth`, measured with the context's current font. */
export function wrapText(ctx, text, maxWidth) {
  const lines = [];
  let line = '';
  for (const word of text.split(/\s+/).filter(Boolean)) {
    const candidate = line ? `${line} ${word}` : word;
    if (line && ctx.measureText(candidate).width > maxWidth) {
      lines.push(line);
      line = word;
    } else {
      line = candidate;
    }
  }
  if (line) lines.push(line);
  return lines;
}

export async function drawQuoteCard(canvas, { quote, author, language, size = 'square', theme = 'night' }) {
  const { width, height } = SIZES[size];
  const colors = THEMES[theme];
  const arabic = language === 'ar';
  const family = arabic ? '"Amiri", "Noto Naskh Arabic", serif' : '"Crimson Text", Georgia, serif';
  const fontStyle = arabic ? '' : 'italic ';
  const text = arabic ? `«${quote}»` : `“${quote}”`;

  // Wait for the web font, or the first draw uses a fallback
  try {
    await document.fonts.load(`${fontStyle}48px ${family}`, quote);
    await document.fonts.load('400 24px "Poppins"');
  } catch {
    // Draw with whatever font is available
  }

  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext('2d');

  const gradient = ctx.createLinearGradient(0, 0, width, height);
  gradient.addColorStop(0, colors.from);
  gradient.addColorStop(1, colors.to);
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, width, height);

  // The largest font size at which the quote fits the text box
  const boxWidth = width * 0.8;
  const boxHeight = height * (size === 'landscape' ? 0.55 : 0.6);
  const lineHeight = LINE_HEIGHT[arabic ? 'ar' : 'en'];
  let fontSize = Math.round(Math.min(width, height) / 9);
  let lines = [];
  for (; fontSize >= 20; fontSize -= 2) {
    ctx.font = `${fontStyle}${fontSize}px ${family}`;
    lines = wrapText(ctx, text, boxWidth);
    if (lines.length * fontSize * lineHeight <= boxHeight) break;
  }

  ctx.direction = arabic ? 'rtl' : 'ltr';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillStyle = colors.text;
  const blockHeight = lines.length * fontSize * lineHeight;
  const top = height / 2 - blockHeight / 2 - fontSize * 0.4;
  lines.forEach((line, i) => {
    ctx.fillText(line, width / 2, top + (i + 0.5) * fontSize * lineHeight);
  });

  const small = Math.round(Math.min(width, height) / 30);
  ctx.fillStyle = colors.accent;
  ctx.font = `400 ${small}px "Poppins", sans-serif`;
  ctx.fillText(`— ${author}`, width / 2, top + blockHeight + small * 2);

  ctx.direction = 'ltr';
  ctx.globalAlpha = 0.6;
  ctx.font = `300 ${Math.round(small * 0.8)}px "Poppins", sans-serif`;
  ctx.fillText('swanexus.dev', width / 2, height - small * 2.2);
  ctx.globalAlpha = 1;
}

export function canvasToBlob(canvas) {
  return new Promise((resolve, reject) => {
    canvas.toBlob((blob) => (blob ? resolve(blob) : reject(new Error('Could not create the image'))), 'image/png');
  });
}
