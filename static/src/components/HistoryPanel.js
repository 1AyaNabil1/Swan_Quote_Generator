import React, { useEffect, useMemo, useRef, useState } from 'react';
import { AnimatePresence, motion, useReducedMotion } from 'framer-motion';

const LABELS = {
  en: {
    title: 'Your quotes',
    history: 'History',
    favorites: 'Favorites',
    search: 'Search your quotes',
    close: 'Close',
    copy: 'Copy',
    remove: 'Delete',
    favorite: 'Add to favorites',
    unfavorite: 'Remove from favorites',
    clear: 'Clear history',
    clearConfirm: 'Clear everything except favorites?',
    clearYes: 'Yes, clear',
    clearNo: 'Cancel',
    export: 'Download favorites',
    emptyHistory: 'Quotes you generate will appear here. They stay in this browser.',
    emptyFavorites: 'Star a quote to keep it here.',
    noMatches: 'No quotes match your search.',
  },
  ar: {
    title: 'اقتباساتك',
    history: 'السجل',
    favorites: 'المفضلة',
    search: 'ابحث في اقتباساتك',
    close: 'إغلاق',
    copy: 'نسخ',
    remove: 'حذف',
    favorite: 'أضف إلى المفضلة',
    unfavorite: 'أزل من المفضلة',
    clear: 'امسح السجل',
    clearConfirm: 'مسح كل شيء ما عدا المفضلة؟',
    clearYes: 'نعم، امسح',
    clearNo: 'إلغاء',
    export: 'تنزيل المفضلة',
    emptyHistory: 'ستظهر هنا الاقتباسات التي تنشئها، وتبقى في هذا المتصفح فقط.',
    emptyFavorites: 'ضع نجمة على اقتباس لتحتفظ به هنا.',
    noMatches: 'لا توجد اقتباسات تطابق بحثك.',
  },
};

function exportFavorites(items) {
  const text = items
    .map((item) => `"${item.quote}" — ${item.author}\n${item.category} · ${new Date(item.timestamp).toLocaleDateString()}`)
    .join('\n\n');
  const url = URL.createObjectURL(new Blob([text + '\n'], { type: 'text/plain;charset=utf-8' }));
  const link = Object.assign(document.createElement('a'), { href: url, download: 'swan-favorites.txt' });
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 0);
}

function Icon({ d, filled = false, className = 'h-4 w-4' }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill={filled ? 'currentColor' : 'none'} stroke="currentColor" strokeWidth={1.5} aria-hidden="true">
      <path strokeLinecap="round" strokeLinejoin="round" d={d} />
    </svg>
  );
}

const STAR = 'M11.48 3.499a.562.562 0 0 1 1.04 0l2.125 5.111a.563.563 0 0 0 .475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 0 0-.182.557l1.285 5.385a.562.562 0 0 1-.84.61l-4.725-2.885a.562.562 0 0 0-.586 0L6.982 20.54a.562.562 0 0 1-.84-.61l1.285-5.386a.562.562 0 0 0-.182-.557l-4.204-3.602a.562.562 0 0 1 .321-.988l5.518-.442a.563.563 0 0 0 .475-.345L11.48 3.5Z';
const COPY = 'M15.75 17.25v3.375c0 .621-.504 1.125-1.125 1.125h-9.75a1.125 1.125 0 0 1-1.125-1.125V7.875c0-.621.504-1.125 1.125-1.125H6.75a9.06 9.06 0 0 1 1.5.124m7.5 10.376h3.375c.621 0 1.125-.504 1.125-1.125V11.25c0-4.46-3.243-8.161-7.5-8.876a9.06 9.06 0 0 0-1.5-.124H9.375c-.621 0-1.125.504-1.125 1.125v3.5m7.5 10.375H9.375a1.125 1.125 0 0 1-1.125-1.125v-9.25m12 6.625v-1.875a3.375 3.375 0 0 0-3.375-3.375h-1.5a1.125 1.125 0 0 1-1.125-1.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H9.75';
const TRASH = 'm14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0';
const CLOSE = 'M6 18 18 6M6 6l12 12';

export default function HistoryPanel({ open, onClose, items, onToggleFavorite, onRemove, onClear, onCopy, language }) {
  const t = LABELS[language] || LABELS.en;
  const dir = language === 'ar' ? 'rtl' : 'ltr';
  const reduceMotion = useReducedMotion();
  const [tab, setTab] = useState('history');
  const [search, setSearch] = useState('');
  const [confirmingClear, setConfirmingClear] = useState(false);
  const closeButton = useRef(null);

  useEffect(() => {
    if (!open) return undefined;
    closeButton.current?.focus();
    const onKey = (e) => e.key === 'Escape' && onClose();
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [open, onClose]);

  useEffect(() => {
    if (!open) setConfirmingClear(false);
  }, [open]);

  const favorites = useMemo(() => items.filter((item) => item.favorite), [items]);
  const shown = useMemo(() => {
    const list = tab === 'favorites' ? favorites : items;
    const query = search.trim().toLowerCase();
    if (!query) return list;
    return list.filter((item) =>
      [item.quote, item.category, item.topic].some((field) => field && field.toLowerCase().includes(query)),
    );
  }, [tab, items, favorites, search]);

  const emptyMessage = search.trim() ? t.noMatches : tab === 'favorites' ? t.emptyFavorites : t.emptyHistory;
  const font = language === 'ar' ? "'Cairo', sans-serif" : "'Poppins', 'Inter', sans-serif";

  return (
    <AnimatePresence>
      {open && (
        <div className="fixed inset-0 z-40" dir={dir}>
          <motion.div
            className="absolute inset-0 bg-black/60 backdrop-blur-sm"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          />
          <motion.aside
            role="dialog"
            aria-modal="true"
            aria-labelledby="history-title"
            className="absolute inset-y-0 end-0 flex w-full max-w-md flex-col border-s border-purple-primary/30 bg-[#0b0613]/95 text-white shadow-2xl"
            style={{ fontFamily: font }}
            initial={reduceMotion ? { opacity: 0 } : { x: dir === 'rtl' ? '-100%' : '100%' }}
            animate={reduceMotion ? { opacity: 1 } : { x: 0 }}
            exit={reduceMotion ? { opacity: 0 } : { x: dir === 'rtl' ? '-100%' : '100%' }}
            transition={{ type: 'tween', duration: 0.25, ease: 'easeOut' }}
          >
            <header className="flex items-center justify-between px-5 pt-5">
              <h2 id="history-title" className="text-lg font-light">{t.title}</h2>
              <button
                ref={closeButton}
                type="button"
                onClick={onClose}
                aria-label={t.close}
                className="rounded-md p-1.5 text-white/60 hover:text-white focus:outline-none focus-visible:ring-2 focus-visible:ring-purple-light"
              >
                <Icon d={CLOSE} className="h-5 w-5" />
              </button>
            </header>

            <div className="px-5 pt-4" role="tablist">
              <div className="flex gap-1 rounded-lg bg-white/5 p-1 text-sm">
                {[['history', t.history, items.length], ['favorites', t.favorites, favorites.length]].map(([id, label, count]) => (
                  <button
                    key={id}
                    type="button"
                    role="tab"
                    aria-selected={tab === id}
                    onClick={() => setTab(id)}
                    className={`flex-1 rounded-md px-3 py-1.5 font-light transition-colors ${tab === id ? 'bg-purple-primary/40 text-white' : 'text-white/60 hover:text-white'}`}
                  >
                    {label} <span className="text-white/40">{count}</span>
                  </button>
                ))}
              </div>
              <input
                type="search"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder={t.search}
                aria-label={t.search}
                className="mt-3 w-full rounded-lg border border-purple-primary/30 bg-black/30 px-3 py-2 text-sm text-white placeholder-white/30 focus:border-purple-accent focus:outline-none"
              />
            </div>

            <ul className="mt-3 flex-1 space-y-3 overflow-y-auto px-5 pb-4" role="tabpanel">
              {shown.length === 0 && <li className="py-10 text-center text-sm font-light text-white/40">{emptyMessage}</li>}
              {shown.map((item) => (
                <li key={item.id} className="rounded-xl border border-purple-primary/20 bg-white/[0.03] p-4">
                  <p
                    dir={item.language === 'ar' ? 'rtl' : 'ltr'}
                    className="text-base leading-relaxed text-white/90"
                    style={{
                      fontFamily: item.language === 'ar' ? "'Amiri', serif" : "'Crimson Text', serif",
                      fontStyle: item.language === 'ar' ? 'normal' : 'italic',
                    }}
                  >
                    "{item.quote}"
                  </p>
                  <div className="mt-3 flex items-center justify-between gap-2">
                    <span className="truncate text-xs font-light text-white/40">
                      {[item.category, item.topic, new Date(item.timestamp).toLocaleDateString(language === 'ar' ? 'ar-EG' : undefined)]
                        .filter(Boolean)
                        .join(' · ')}
                    </span>
                    <div className="flex shrink-0 items-center gap-1 text-white/50">
                      <button
                        type="button"
                        onClick={() => onToggleFavorite(item.id)}
                        aria-pressed={item.favorite}
                        aria-label={item.favorite ? t.unfavorite : t.favorite}
                        title={item.favorite ? t.unfavorite : t.favorite}
                        className={`rounded-md p-1.5 hover:text-white ${item.favorite ? 'text-amber-300 hover:text-amber-200' : ''}`}
                      >
                        <Icon d={STAR} filled={item.favorite} />
                      </button>
                      <button type="button" onClick={() => onCopy(item)} aria-label={t.copy} title={t.copy} className="rounded-md p-1.5 hover:text-white">
                        <Icon d={COPY} />
                      </button>
                      <button type="button" onClick={() => onRemove(item.id)} aria-label={t.remove} title={t.remove} className="rounded-md p-1.5 hover:text-rose-300">
                        <Icon d={TRASH} />
                      </button>
                    </div>
                  </div>
                </li>
              ))}
            </ul>

            <footer className="flex flex-wrap items-center gap-2 border-t border-purple-primary/20 px-5 py-4 text-sm font-light">
              {confirmingClear ? (
                <>
                  <span className="text-white/70">{t.clearConfirm}</span>
                  <button type="button" onClick={() => { onClear(); setConfirmingClear(false); }} className="rounded-lg bg-rose-500/20 px-3 py-1.5 text-rose-200 hover:bg-rose-500/30">
                    {t.clearYes}
                  </button>
                  <button type="button" onClick={() => setConfirmingClear(false)} className="rounded-lg px-3 py-1.5 text-white/60 hover:text-white">
                    {t.clearNo}
                  </button>
                </>
              ) : (
                <>
                  <button
                    type="button"
                    disabled={items.length === favorites.length}
                    onClick={() => setConfirmingClear(true)}
                    className="rounded-lg px-3 py-1.5 text-white/60 hover:text-white disabled:opacity-30"
                  >
                    {t.clear}
                  </button>
                  <button
                    type="button"
                    disabled={favorites.length === 0}
                    onClick={() => exportFavorites(favorites)}
                    className="ms-auto rounded-lg border border-purple-primary/40 bg-purple-primary/20 px-3 py-1.5 text-white hover:bg-purple-primary/30 disabled:opacity-30"
                  >
                    {t.export}
                  </button>
                </>
              )}
            </footer>
          </motion.aside>
        </div>
      )}
    </AnimatePresence>
  );
}
