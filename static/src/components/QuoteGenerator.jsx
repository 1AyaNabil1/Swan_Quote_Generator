import React, { useCallback, useEffect, useState } from 'react';
import { navigateHost, shareLink, streamZibbyAi, ZIBBY_COMPED_LINE, ZIBBY_CREDITS_PATH } from '@zibby-run/app-kit';
import { useAvgActionCr, useComped, useCreditBalance } from '@zibby-run/app-kit/react';
import useQuoteHistory from '../hooks/useQuoteHistory';
import { generateQuote, QuoteError } from '../lib/quote';
import { CATEGORIES, QUOTE_ACTION, QUOTE_ESTIMATE_CR } from '../lib/prompt';
import HistoryPanel from './HistoryPanel';
import Select from './Select';
import ShareImage from './ShareImage';
import { useToast } from './Toast';

const MESSAGES = {
  copied: { en: 'Quote copied to clipboard.', ar: 'تم نسخ الاقتباس.' },
  copiedInstead: {
    en: "Sharing isn't supported on this device, so the quote was copied instead.",
    ar: 'المشاركة غير مدعومة على هذا الجهاز، لذا نُسخ الاقتباس بدلًا منها.',
  },
  copyFailed: {
    en: "Couldn't copy the quote. Select it and copy it yourself.",
    ar: 'تعذّر نسخ الاقتباس. حدّده وانسخه يدويًا.',
  },
  unreachable: {
    en: "Couldn't reach Swan. Check your connection and try again.",
    ar: 'تعذّر الوصول إلى Swan. تحقّق من اتصالك وحاول مرة أخرى.',
  },
  // What a failed run says, by QuoteError kind
  input: {
    en: 'Swan writes about a topic in a tone, and does not take instructions. Try another topic or style.',
    ar: 'يكتب Swan عن موضوع بأسلوب ما، ولا يتلقى تعليمات. جرّب موضوعًا أو أسلوبًا آخر.',
  },
  refused: { en: 'The model declined this topic. Try another one.', ar: 'رفض النموذج هذا الموضوع. جرّب موضوعًا آخر.' },
  truncated: {
    en: "The quote ran past Swan's length limit. Try a shorter topic or style.",
    ar: 'تجاوز الاقتباس الطول المسموح. جرّب موضوعًا أو أسلوبًا أقصر.',
  },
  checks: { en: "This answer didn't pass Swan's checks", ar: 'لم يجتز هذا الرد فحوص Swan' },
  checksAgain: {
    en: "The second answer didn't pass either. Try another topic or style.",
    ar: 'لم يجتز الرد الثاني الفحوص أيضًا. جرّب موضوعًا أو أسلوبًا آخر.',
  },
  tryAgain: { en: 'Try again', ar: 'حاول مرة أخرى' },
  credits: { en: "You're out of Zibby credits.", ar: 'نفد رصيدك على Zibby.' },
  topUp: { en: 'Top up', ar: 'اشحن الرصيد' },
  cap: {
    en: 'Swan has spent a lot of credits in a short time. Continue?',
    ar: 'أنفق Swan الكثير من الرصيد في وقت قصير. هل تتابع؟',
  },
  continue: { en: 'Continue', ar: 'تابع' },
  'signed-out': { en: 'Sign in to Zibby to write quotes.', ar: 'سجّل الدخول إلى Zibby لكتابة الاقتباسات.' },
  signIn: { en: 'Sign in', ar: 'تسجيل الدخول' },
  locked: { en: 'Your Zibby account is on hold.', ar: 'حسابك على Zibby موقوف مؤقتًا.' },
  busy: { en: 'Too many quotes at once. Wait a moment and try again.', ar: 'طلبات كثيرة في وقت واحد. انتظر قليلًا وحاول مرة أخرى.' },
  server: { en: 'Something went wrong. Please try again in a moment.', ar: 'حدث خطأ ما. حاول مرة أخرى بعد قليل.' },
  shareFailed: { en: "Couldn't share. Here is the link:", ar: 'تعذّرت المشاركة. هذا هو الرابط:' },
  linkCopied: { en: 'Link copied.', ar: 'تم نسخ الرابط.' },
  offline: {
    en: "You're offline. Swan needs a connection to write quotes.",
    ar: 'أنت غير متصل بالإنترنت. يحتاج Swan إلى اتصال لكتابة الاقتباسات.',
  },
  online: { en: 'Back online.', ar: 'عاد الاتصال بالإنترنت.' },
  imageFailed: { en: "Couldn't create the image.", ar: 'تعذّر إنشاء الصورة.' },
  history: { en: 'Your quotes', ar: 'اقتباساتك' },
  favorite: { en: 'Add to favorites', ar: 'أضف إلى المفضلة' },
  unfavorite: { en: 'Remove from favorites', ar: 'أزل من المفضلة' },
  image: { en: 'Image', ar: 'صورة' },
};

// Why an answer failed, in a few words, by check
const CHECK_REASONS = {
  language: { en: 'wrong language', ar: 'لغة غير مطلوبة' },
  length: { en: 'wrong length', ar: 'طول غير مناسب' },
  format: { en: 'extra text around the quote', ar: 'نص زائد حول الاقتباس' },
  leak: { en: 'it repeated its instructions', ar: 'كرّر تعليماته' },
  empty: { en: 'it was empty', ar: 'كان فارغًا' },
};

/** The only charge figure allowed is the run's own terminal frame (Zibby CONTRACT §2). */
function chargeLine(charge, language) {
  if (!charge) return null;
  if (charge.comped) return ZIBBY_COMPED_LINE;
  const ar = language === 'ar';
  if (!charge.known) {
    const id = charge.requestId ?? 'none';
    return ar ? `التكلفة غير معروفة (رقم الطلب ${id}).` : `Charge unknown (request id ${id}).`;
  }
  if (charge.credits === 0) return ar ? 'لم يُخصم شيء.' : 'Nothing was charged.';
  return ar
    ? `خُصم ${charge.credits} من رصيدك.`
    : `Charged ${charge.credits} credit${charge.credits === 1 ? '' : 's'}.`;
}

/** `stream` is Zibby's /api/ai client; tests hand in their own. */
const QuoteGenerator = ({ stream = streamZibbyAi }) => {
  const history = useQuoteHistory();
  // Start from the last quote in this browser's history, if there is one
  const [last] = useState(() => history.items[0]);
  const [quote, setQuote] = useState(last?.quote ?? '');
  const [author, setAuthor] = useState(last?.author ?? '');
  const [category, setCategory] = useState('motivation');
  const [topic, setTopic] = useState('');
  const [style, setStyle] = useState('');
  const [language, setLanguage] = useState('en');
  const [quoteLanguage, setQuoteLanguage] = useState(last?.language ?? 'en'); // what the shown quote is written in
  const [loading, setLoading] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [showImage, setShowImage] = useState(false);
  const [currentId, setCurrentId] = useState(last?.id ?? null); // the shown quote's history entry
  const [charge, setCharge] = useState(null); // what the last run cost
  const balance = useCreditBalance();
  const comped = useComped();
  const liveEstimate = useAvgActionCr(QUOTE_ACTION);
  const estimate = comped ? null : `~${liveEstimate === null ? QUOTE_ESTIMATE_CR : Math.max(1, Math.round(liveEstimate))} cr`;
  const current = history.items.find((item) => item.id === currentId);
  // Stable, so the dialogs' effects (focus, Escape) don't rerun on every render
  const closeHistory = useCallback(() => setShowHistory(false), []);
  const closeImage = useCallback(() => setShowImage(false), []);
  const toast = useToast();
  const dir = language === 'ar' ? 'rtl' : 'ltr';

  const categories = CATEGORIES;

  useEffect(() => {
    const options = { id: 'network', dir: language === 'ar' ? 'rtl' : 'ltr' };
    const goneOffline = () => toast.error(MESSAGES.offline[language], { ...options, duration: 0 });
    const backOnline = () => toast.success(MESSAGES.online[language], options);
    window.addEventListener('offline', goneOffline);
    window.addEventListener('online', backOnline);
    return () => {
      window.removeEventListener('offline', goneOffline);
      window.removeEventListener('online', backOnline);
    };
  }, [toast, language]);

  /**
   * One press, one run. `repair` is the request that just failed Swan's checks and the
   * checks' own words, for the one repair the person may ask for; `capAck` resends a
   * run Zibby paused at the spending cap, byte for byte.
   */
  const handleGenerateQuote = async ({ repair = null, capAck = false } = {}) => {
    const request = repair?.request ?? {
      category,
      length: 'medium',
      language,
      // Only include topic and style if they have values
      ...(topic.trim() ? { topic: topic.trim() } : {}),
      ...(style.trim() ? { style: style.trim() } : {}),
    };
    const hint = repair?.hint ?? '';
    const words = (key) => MESSAGES[key][request.language];
    const options = { id: 'generate', dir: request.language === 'ar' ? 'rtl' : 'ltr' };
    setLoading(true);
    toast.dismiss('generate');
    try {
      const result = await generateQuote(request, { stream, hint, capAck });
      setQuote(result.quote);
      setAuthor('Swan');
      setQuoteLanguage(request.language);
      setCharge(result.charge);
      setCurrentId(history.add({
        quote: result.quote,
        author: 'Swan',
        category: request.category,
        language: request.language,
        topic: request.topic,
        timestamp: new Date().toISOString(),
      }));
    } catch (error) {
      // The last quote stays on screen; the problem is shown as a notification
      if (!(error instanceof QuoteError)) throw error;
      setCharge(error.charge);
      const again = (next) => () => handleGenerateQuote(next);
      if (error.kind === 'checks' && !repair) {
        const reasons = error.checks.map((check) => CHECK_REASONS[check]?.[request.language]).filter(Boolean);
        toast.warning(`${words('checks')}${reasons.length ? `: ${reasons.join(', ')}` : ''}.`, {
          ...options,
          duration: 0,
          action: {
            label: `${words('tryAgain')}${estimate ? ` (${estimate})` : ''}`,
            onClick: again({ repair: { request, hint: error.hint } }),
          },
        });
      } else if (error.kind === 'checks') {
        toast.error(words('checksAgain'), options);
      } else if (error.kind === 'cap') {
        toast.warning(words('cap'), {
          ...options,
          duration: 0,
          action: { label: words('continue'), onClick: again({ repair, capAck: true }) },
        });
      } else if (error.kind === 'credits') {
        toast.error(words('credits'), {
          ...options,
          duration: 0,
          action: { label: words('topUp'), onClick: () => navigateHost(ZIBBY_CREDITS_PATH) },
        });
      } else if (error.kind === 'signed-out') {
        toast.error(words('signed-out'), {
          ...options,
          duration: 0,
          action: { label: words('signIn'), onClick: () => navigateHost('/users/log-in') },
        });
      } else if (error.kind === 'network') {
        toast.error(MESSAGES.unreachable[request.language], options);
      } else if (error.kind !== 'aborted') {
        toast.error(words(MESSAGES[error.kind] ? error.kind : 'server'), options);
      }
    } finally {
      setLoading(false);
    }
  };

  const copyQuote = async (copiedMessage, item = { quote, author }) => {
    try {
      await navigator.clipboard.writeText(`"${item.quote}" - ${item.author}`);
      toast.success(copiedMessage[language], { dir });
    } catch (err) {
      toast.error(MESSAGES.copyFailed[language], { dir });
    }
  };

  const handleCopyQuote = () => {
    if (quote) copyQuote(MESSAGES.copied);
  };

  // Zibby shares the app's public page: no link may leave the app's frame.
  const handleShareQuote = async () => {
    if (!quote) return;
    const text = `"${quote}" - ${author}`;
    const result = await shareLink({ text: [...text].slice(0, 280).join(''), title: 'Swan' });
    if (result.outcome === 'copied') toast.success(MESSAGES.linkCopied[language], { dir });
    else if ((result.outcome === 'failed' || result.outcome === 'url') && result.url) {
      toast.info(`${MESSAGES.shareFailed[language]} ${result.url}`, { dir, duration: 0 });
    }
  };

  // Also shown when a charged answer failed the checks and no quote is on screen yet.
  const line = chargeLine(charge, language);
  const chargeNote = line && (
    <p className="mt-3 text-xs font-light text-white/40" role="status" style={{ fontFamily: "'Poppins', 'Inter', sans-serif" }}>
      {line}
    </p>
  );

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <header className="flex items-center justify-between px-4 md:px-8 py-4 md:py-6">
        <button
          type="button"
          onClick={() => setShowHistory(true)}
          className="flex items-center gap-2 rounded-lg px-2 py-1.5 text-sm font-light text-white/60 transition-colors hover:text-white"
          style={{ fontFamily: language === 'ar' ? "'Cairo', sans-serif" : "'Poppins', 'Inter', sans-serif" }}
        >
          <svg className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5} aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
          </svg>
          {MESSAGES.history[language]}
          {history.items.length > 0 && <span className="text-white/40">{history.items.length}</span>}
        </button>
        <span
          className="rounded-full border border-purple-primary/40 px-3 py-1 text-xs font-light text-white/70"
          style={{ fontFamily: "'Poppins', 'Inter', sans-serif" }}
          title={comped ? 'Your runs are on Zibby' : 'Your Zibby credits'}
        >
          {comped ? 'Comped' : balance === null ? '—' : `${balance.toLocaleString('en-US')} cr`}
        </span>
      </header>

      {/* Hero Section - Center */}
      <div className="flex-shrink-0 text-center px-4 md:px-8 pb-4 md:pb-8 pt-2">
        <div className="flex flex-col items-center space-y-1 md:space-y-3">
          <h1 className="text-5xl md:text-7xl lg:text-8xl font-normal text-white tracking-tight" style={{ fontFamily: "'Courier New', 'Courier', monospace", fontWeight: 400 }}>
            Swan
          </h1>
          <p className="text-white/60 text-sm md:text-base lg:text-lg max-w-xl font-light tracking-wide px-4" style={{ fontFamily: "'Courier New', 'Courier', monospace" }}>
            Because sometimes, the right words can light the stars inside you
          </p>
        </div>
      </div>

      {/* Mobile-First Layout - Scrollable on mobile, Two columns on desktop */}
      <div className="flex-1 px-4 md:px-8 pb-4 md:pb-8 overflow-y-auto md:overflow-hidden">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 md:gap-8 h-full">
          {/* Quote Display - More compact on mobile */}
          <div className="flex items-center justify-center order-2 lg:order-1">
            <div className="w-full max-w-2xl border border-purple-primary/20 rounded-xl md:rounded-2xl p-4 md:p-8 lg:p-12 min-h-[180px] md:min-h-[280px] flex items-center justify-center bg-gradient-to-br from-purple-primary/20 via-purple-accent/10 to-transparent backdrop-blur-sm">
              {quote ? (
                <div className="space-y-3 md:space-y-6 w-full" dir={quoteLanguage === 'ar' ? 'rtl' : 'ltr'}>
                  <div
                    className="text-lg md:text-2xl lg:text-3xl font-serif text-white/90 leading-relaxed"
                    style={{
                      fontFamily: quoteLanguage === 'ar' ? "'Amiri', 'Georgia', serif" : "'Crimson Text', 'Georgia', serif",
                      fontStyle: quoteLanguage === 'ar' ? 'normal' : 'italic',
                      lineHeight: quoteLanguage === 'ar' ? '2' : '1.6'
                    }}
                  >
                    "{quote}"
                  </div>
                  {author && (
                    <div
                      className="text-sm md:text-base text-purple-light/80 font-light"
                      style={{
                        textAlign: quoteLanguage === 'ar' ? 'left' : 'right',
                        fontFamily: quoteLanguage === 'ar' ? "'Cairo', sans-serif" : "'Poppins', 'Inter', sans-serif"
                      }}
                    >
                      — {author}
                    </div>
                  )}
                  <div className="mt-3 md:mt-6 flex flex-wrap gap-2 md:gap-3">
                    {current && (
                      <button
                        type="button"
                        onClick={() => history.toggleFavorite(current.id)}
                        aria-pressed={current.favorite}
                        aria-label={(current.favorite ? MESSAGES.unfavorite : MESSAGES.favorite)[language]}
                        title={(current.favorite ? MESSAGES.unfavorite : MESSAGES.favorite)[language]}
                        className={`px-2.5 py-2 bg-purple-primary/20 hover:bg-purple-primary/30 border border-purple-primary/40 rounded-lg transition-all ${current.favorite ? 'text-amber-300' : 'text-white/70'}`}
                      >
                        <svg className="h-4 w-4" viewBox="0 0 24 24" fill={current.favorite ? 'currentColor' : 'none'} stroke="currentColor" strokeWidth={1.5} aria-hidden="true">
                          <path strokeLinecap="round" strokeLinejoin="round" d="M11.48 3.499a.562.562 0 0 1 1.04 0l2.125 5.111a.563.563 0 0 0 .475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 0 0-.182.557l1.285 5.385a.562.562 0 0 1-.84.61l-4.725-2.885a.562.562 0 0 0-.586 0L6.982 20.54a.562.562 0 0 1-.84-.61l1.285-5.386a.562.562 0 0 0-.182-.557l-4.204-3.602a.562.562 0 0 1 .321-.988l5.518-.442a.563.563 0 0 0 .475-.345L11.48 3.5Z" />
                        </svg>
                      </button>
                    )}
                    <button
                      onClick={handleCopyQuote}
                      className="px-4 md:px-5 py-2 bg-purple-primary/20 hover:bg-purple-primary/30 border border-purple-primary/40 rounded-lg text-white text-xs md:text-sm font-light transition-all"
                      style={{ fontFamily: language === 'ar' ? "'Cairo', sans-serif" : "'Poppins', 'Inter', sans-serif" }}
                    >
                      {language === 'ar' ? 'نسخ الاقتباس' : 'Copy Quote'}
                    </button>
                    <button
                      type="button"
                      onClick={() => setShowImage(true)}
                      className="px-4 md:px-5 py-2 bg-purple-primary/20 hover:bg-purple-primary/30 border border-purple-primary/40 rounded-lg text-white text-xs md:text-sm font-light transition-all"
                      style={{ fontFamily: language === 'ar' ? "'Cairo', sans-serif" : "'Poppins', 'Inter', sans-serif" }}
                    >
                      {MESSAGES.image[language]}
                    </button>
                    <button
                      type="button"
                      onClick={handleShareQuote}
                      className="px-4 md:px-5 py-2 bg-purple-primary/20 hover:bg-purple-primary/30 border border-purple-primary/40 rounded-lg text-white text-xs md:text-sm font-light transition-all"
                      style={{ fontFamily: language === 'ar' ? "'Cairo', sans-serif" : "'Poppins', 'Inter', sans-serif" }}
                    >
                      {language === 'ar' ? 'مشاركة الاقتباس' : 'Share Quote'}
                    </button>
                  </div>
                  {chargeNote}
                </div>
              ) : (
                <div className="text-center" dir={language === 'ar' ? 'rtl' : 'ltr'}>
                  <p
                    className="text-base md:text-xl text-white/30 font-light"
                    style={{
                      fontFamily: language === 'ar' ? "'Amiri', 'Georgia', serif" : "'Crimson Text', 'Georgia', serif",
                      fontStyle: language === 'ar' ? 'normal' : 'italic'
                    }}
                  >
                    {language === 'ar' ? 'سيظهر اقتباسك هنا...' : 'Your quote will appear here...'}
                  </p>
                  {chargeNote}
                </div>
              )}
            </div>
          </div>

          {/* Controls - Show first on mobile for better UX */}
          <div className="flex items-start md:items-center justify-center order-1 lg:order-2">
            <div className="w-full max-w-md space-y-3 md:space-y-5" style={{ fontFamily: "'Poppins', 'Inter', sans-serif" }}>
              <Select
                id="category"
                label="Category"
                value={category}
                onChange={setCategory}
                options={categories.map((cat) => ({ value: cat, label: cat.charAt(0).toUpperCase() + cat.slice(1) }))}
                font="'Poppins', 'Inter', sans-serif"
              />

              <Select
                id="language"
                label="Language"
                value={language}
                onChange={setLanguage}
                options={[
                  { value: 'en', label: 'English' },
                  { value: 'ar', label: 'العربية (Arabic)' },
                ]}
                font="'Poppins', 'Inter', sans-serif"
              />

              <div>
                <label htmlFor="topic" className="block text-white/70 font-light mb-1.5 md:mb-2 text-xs md:text-sm">
                  Topic (optional)
                </label>
                <input
                  id="topic"
                  type="text"
                  autoComplete="off"
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  placeholder="e.g., perseverance, courage..."
                  className="w-full px-3 md:px-4 py-2 md:py-2.5 bg-black/30 border border-purple-primary/30 rounded-lg text-white text-sm placeholder-white/30 focus:outline-none focus:border-purple-accent transition-all"
                  style={{ fontFamily: "'Poppins', 'Inter', sans-serif" }}
                />
              </div>

              <div>
                <label htmlFor="style" className="block text-white/70 font-light mb-1.5 md:mb-2 text-xs md:text-sm">
                  Style (optional)
                </label>
                <input
                  id="style"
                  type="text"
                  autoComplete="off"
                  value={style}
                  onChange={(e) => setStyle(e.target.value)}
                  placeholder="e.g., Shakespeare, modern..."
                  className="w-full px-3 md:px-4 py-2 md:py-2.5 bg-black/30 border border-purple-primary/30 rounded-lg text-white text-sm placeholder-white/30 focus:outline-none focus:border-purple-accent transition-all"
                  style={{ fontFamily: "'Poppins', 'Inter', sans-serif" }}
                />
              </div>

              <button
                onClick={() => handleGenerateQuote()}
                disabled={loading}
                className="w-full px-6 py-2.5 md:py-3 bg-gradient-to-r from-purple-primary via-purple-accent to-purple-primary hover:from-purple-accent hover:via-purple-light hover:to-purple-accent rounded-full text-white text-sm font-medium shadow-lg shadow-purple-primary/30 hover:shadow-purple-light/70 hover:shadow-2xl hover:scale-[1.02] transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed mt-4 md:mt-6"
                style={{ fontFamily: "'Poppins', 'Inter', sans-serif" }}
              >
                {loading ? 'Generating...' : 'Generate Quote'}
                {!loading && estimate && <span className="ml-2 text-xs font-light text-white/70">{estimate}</span>}
              </button>
            </div>
          </div>
        </div>
      </div>

      <HistoryPanel
        open={showHistory}
        onClose={closeHistory}
        items={history.items}
        onToggleFavorite={history.toggleFavorite}
        onRemove={history.remove}
        onClear={history.clearHistory}
        onCopy={(item) => copyQuote(MESSAGES.copied, item)}
        language={language}
      />
      <ShareImage
        open={showImage}
        onClose={closeImage}
        quote={quote}
        author={author}
        quoteLanguage={quoteLanguage}
        language={language}
        onDone={(result) => result === 'failed' && toast.error(MESSAGES.imageFailed[language], { dir })}
      />

      <p className="sr-only" aria-live="polite">
        {quote && `${quote} — ${author}`}
      </p>

      {/* Footer - Smaller on mobile */}
      <footer className="text-center pb-4 md:pb-6 flex-shrink-0">
        {/* On Zibby no link may leave the app's frame, so the credit stays plain text. */}
        <p className="text-white/60 text-xs md:text-sm font-light" style={{ fontFamily: "'Poppins', 'Inter', sans-serif" }}>
          Built by <span className="text-purple-light font-medium">AyaNexus</span> 🦢
        </p>
      </footer>
    </div >
  );
};

export default QuoteGenerator;
