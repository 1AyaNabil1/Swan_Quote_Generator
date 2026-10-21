import React, { useEffect, useRef, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { SIZES, THEMES, canvasToBlob, drawQuoteCard } from '../utils/quoteCard';

const LABELS = {
  en: { title: 'Quote image', size: 'Size', theme: 'Theme', download: 'Download PNG', share: 'Share', close: 'Close', preview: 'Preview of the quote image' },
  ar: { title: 'صورة الاقتباس', size: 'المقاس', theme: 'الشكل', download: 'تنزيل الصورة', share: 'مشاركة', close: 'إغلاق', preview: 'معاينة صورة الاقتباس' },
};

function Choice({ options, value, onChange, language }) {
  return (
    <div className="flex flex-wrap gap-2">
      {Object.entries(options).map(([id, option]) => (
        <button
          key={id}
          type="button"
          aria-pressed={value === id}
          onClick={() => onChange(id)}
          title={option.hint}
          className={`rounded-lg border px-3 py-1.5 text-sm font-light transition-colors ${value === id ? 'border-purple-light bg-purple-primary/40 text-white' : 'border-purple-primary/30 text-white/60 hover:text-white'}`}
        >
          {option.label[language] || option.label.en}
        </button>
      ))}
    </div>
  );
}

export default function ShareImage({ open, onClose, quote, author, quoteLanguage, language, onDone }) {
  const t = LABELS[language] || LABELS.en;
  const canvas = useRef(null);
  const [size, setSize] = useState('square');
  const [theme, setTheme] = useState('night');
  const [busy, setBusy] = useState(false);
  const canShareFiles = typeof navigator !== 'undefined' && typeof navigator.canShare === 'function';

  useEffect(() => {
    if (open && canvas.current) {
      drawQuoteCard(canvas.current, { quote, author, language: quoteLanguage, size, theme });
    }
  }, [open, quote, author, quoteLanguage, size, theme]);

  useEffect(() => {
    if (!open) return undefined;
    const onKey = (e) => e.key === 'Escape' && onClose();
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [open, onClose]);

  const fileName = `swan-quote-${size}.png`;

  const download = async () => {
    setBusy(true);
    try {
      const url = URL.createObjectURL(await canvasToBlob(canvas.current));
      Object.assign(document.createElement('a'), { href: url, download: fileName }).click();
      setTimeout(() => URL.revokeObjectURL(url), 0);
      onDone?.('downloaded');
    } catch {
      onDone?.('failed');
    } finally {
      setBusy(false);
    }
  };

  const share = async () => {
    setBusy(true);
    try {
      const file = new File([await canvasToBlob(canvas.current)], fileName, { type: 'image/png' });
      if (!navigator.canShare({ files: [file] })) return download();
      await navigator.share({ files: [file], title: 'Swan' });
    } catch (err) {
      if (err?.name !== 'AbortError') onDone?.('failed');
    } finally {
      setBusy(false);
    }
  };

  const font = language === 'ar' ? "'Cairo', sans-serif" : "'Poppins', 'Inter', sans-serif";

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          className="fixed inset-0 z-40 flex items-center justify-center bg-black/70 p-4 backdrop-blur-sm"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
          dir={language === 'ar' ? 'rtl' : 'ltr'}
        >
          <motion.div
            role="dialog"
            aria-modal="true"
            aria-labelledby="share-image-title"
            className="flex max-h-full w-full max-w-lg flex-col gap-4 overflow-y-auto rounded-2xl border border-purple-primary/30 bg-[#0b0613] p-5 text-white shadow-2xl"
            style={{ fontFamily: font }}
            initial={{ scale: 0.97, y: 8 }}
            animate={{ scale: 1, y: 0 }}
            exit={{ scale: 0.97, y: 8 }}
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between">
              <h2 id="share-image-title" className="text-lg font-light">{t.title}</h2>
              <button type="button" onClick={onClose} aria-label={t.close} className="rounded-md p-1.5 text-white/60 hover:text-white" autoFocus>
                <svg className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5} aria-hidden="true">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="flex justify-center rounded-xl bg-black/40 p-3">
              <canvas ref={canvas} role="img" aria-label={t.preview} className="max-h-[45vh] w-auto max-w-full rounded-lg shadow-lg" />
            </div>
            <div className="space-y-2">
              <p className="text-xs font-light text-white/50">{t.size}</p>
              <Choice options={SIZES} value={size} onChange={setSize} language={language} />
            </div>
            <div className="space-y-2">
              <p className="text-xs font-light text-white/50">{t.theme}</p>
              <Choice options={THEMES} value={theme} onChange={setTheme} language={language} />
            </div>
            <div className="flex gap-2 pt-1">
              <button
                type="button"
                onClick={download}
                disabled={busy}
                className="flex-1 rounded-full bg-gradient-to-r from-purple-primary via-purple-accent to-purple-primary px-4 py-2.5 text-sm font-medium disabled:opacity-50"
              >
                {t.download}
              </button>
              {canShareFiles && (
                <button
                  type="button"
                  onClick={share}
                  disabled={busy}
                  className="rounded-full border border-purple-primary/40 px-4 py-2.5 text-sm font-light hover:bg-purple-primary/20 disabled:opacity-50"
                >
                  {t.share}
                </button>
              )}
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
