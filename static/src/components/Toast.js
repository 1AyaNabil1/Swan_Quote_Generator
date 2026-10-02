/**
 * Notifications ("toasts") for Swan.
 *
 * Wrap the app in <ToastProvider>, then in any component:
 *
 *   const toast = useToast();
 *   toast.success('Quote copied to clipboard.');
 *   toast.error(message);
 *   toast.warning(message, { id: 'rate-limit' });  // replaces an earlier toast with this id
 *   toast.info(message, { duration: 0 });           // 0 stays until dismissed
 *   toast.dismiss(id);
 *
 * Options: `id` (a toast with the same id is replaced instead of stacked), `duration`
 * in ms (defaults per type below), `dir` ('rtl' for Arabic text).
 *
 * Toasts stack top-right (top-center on mobile), never block the page, pause while
 * hovered or focused, and close with their button or Escape. Errors and warnings are
 * announced to screen readers straight away, the rest politely.
 */
import React, { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from 'react';
import { AnimatePresence, motion, useReducedMotion } from 'framer-motion';

const DURATIONS = { success: 3000, info: 4000, warning: 5000, error: 6000 };
const MAX_TOASTS = 4;

// Heroicons (MIT), outline
const ICONS = {
  success: 'M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z',
  info: 'm11.25 11.25.041-.02a.75.75 0 0 1 1.063.852l-.708 2.836a.75.75 0 0 0 1.063.853l.041-.021M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9-3.75h.008v.008H12V8.25Z',
  warning: 'M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z',
  error: 'm9.75 9.75 4.5 4.5m0-4.5-4.5 4.5M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z',
};

const COLORS = {
  success: 'text-emerald-300',
  info: 'text-purple-light',
  warning: 'text-amber-300',
  error: 'text-rose-300',
};

const ToastContext = createContext(null);

export function useToast() {
  const toast = useContext(ToastContext);
  if (!toast) throw new Error('useToast must be used inside <ToastProvider>');
  return toast;
}

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);
  const counter = useRef(0);

  const dismiss = useCallback((id) => {
    setToasts((list) => list.filter((t) => t.id !== id));
  }, []);

  const show = useCallback((type, message, options = {}) => {
    counter.current += 1;
    const toast = {
      key: counter.current, // a fresh key, so a replaced toast animates and restarts its timer
      id: options.id ?? `toast-${counter.current}`,
      type,
      message,
      duration: options.duration ?? DURATIONS[type],
      dir: options.dir,
    };
    setToasts((list) => [...list.filter((t) => t.id !== toast.id), toast].slice(-MAX_TOASTS));
    return toast.id;
  }, []);

  const api = useMemo(() => ({
    success: (message, options) => show('success', message, options),
    info: (message, options) => show('info', message, options),
    warning: (message, options) => show('warning', message, options),
    error: (message, options) => show('error', message, options),
    dismiss,
  }), [show, dismiss]);

  return (
    <ToastContext.Provider value={api}>
      {children}
      <section
        aria-label="Notifications"
        aria-live="polite"
        className="pointer-events-none fixed inset-x-0 top-0 z-50 flex flex-col items-center gap-2 p-4 md:items-end md:p-6"
      >
        <AnimatePresence initial={false}>
          {toasts.map((toast) => (
            <Toast key={toast.key} toast={toast} onDismiss={dismiss} />
          ))}
        </AnimatePresence>
      </section>
    </ToastContext.Provider>
  );
}

function Toast({ toast, onDismiss }) {
  const reduceMotion = useReducedMotion();
  const [paused, setPaused] = useState(false);
  const timeLeft = useRef(toast.duration);

  useEffect(() => {
    if (paused || !toast.duration) return undefined;
    const started = Date.now();
    const timer = setTimeout(() => onDismiss(toast.id), timeLeft.current);
    return () => {
      clearTimeout(timer);
      timeLeft.current -= Date.now() - started;
    };
  }, [paused, toast.id, toast.duration, onDismiss]);

  const urgent = toast.type === 'error' || toast.type === 'warning';
  const motionProps = reduceMotion
    ? { initial: { opacity: 0 }, animate: { opacity: 1 }, exit: { opacity: 0 } }
    : {
        initial: { opacity: 0, y: -12, scale: 0.98 },
        animate: { opacity: 1, y: 0, scale: 1 },
        exit: { opacity: 0, scale: 0.96, transition: { duration: 0.15 } },
      };

  return (
    <motion.div
      layout={!reduceMotion}
      {...motionProps}
      transition={{ duration: 0.2, ease: 'easeOut' }}
      role={urgent ? 'alert' : 'status'}
      dir={toast.dir}
      onMouseEnter={() => setPaused(true)}
      onMouseLeave={() => setPaused(false)}
      onFocus={() => setPaused(true)}
      onBlur={() => setPaused(false)}
      onKeyDown={(e) => e.key === 'Escape' && onDismiss(toast.id)}
      className="pointer-events-auto flex w-full max-w-sm items-start gap-3 rounded-xl border border-purple-primary/30 bg-black/80 px-4 py-3 text-sm font-light text-white/90 shadow-lg shadow-purple-primary/20 backdrop-blur-md"
      style={{ fontFamily: toast.dir === 'rtl' ? "'Cairo', sans-serif" : "'Poppins', 'Inter', sans-serif" }}
    >
      <svg
        className={`mt-0.5 h-5 w-5 flex-shrink-0 ${COLORS[toast.type]}`}
        fill="none"
        stroke="currentColor"
        strokeWidth={1.5}
        viewBox="0 0 24 24"
        aria-hidden="true"
      >
        <path strokeLinecap="round" strokeLinejoin="round" d={ICONS[toast.type]} />
      </svg>
      <p className="flex-1 leading-relaxed">{toast.message}</p>
      <button
        type="button"
        onClick={() => onDismiss(toast.id)}
        aria-label="Dismiss notification"
        className="-m-1 rounded-md p-1 text-white/50 hover:text-white focus:outline-none focus-visible:ring-2 focus-visible:ring-purple-light"
      >
        <svg className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24" aria-hidden="true">
          <path strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12" />
        </svg>
      </button>
    </motion.div>
  );
}
