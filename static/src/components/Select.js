/**
 * A dropdown in Swan's theme. The browser's own <select> list can't be styled, so this
 * is a listbox that behaves like one: click or Enter/Space/arrows to open, arrows,
 * Home/End or typing a letter to move, Enter/Space to pick, Escape or Tab to close.
 */
import React, { useEffect, useRef, useState } from 'react';
import { AnimatePresence, motion, useReducedMotion } from 'framer-motion';

export default function Select({ id, label, value, options, onChange, font }) {
  const [open, setOpen] = useState(false);
  const [active, setActive] = useState(0);
  const root = useRef(null);
  const button = useRef(null);
  const list = useRef(null);
  const typed = useRef({ text: '', at: 0 });
  const reduceMotion = useReducedMotion();
  const selectedIndex = Math.max(0, options.findIndex((o) => o.value === value));
  const selected = options[selectedIndex];

  const openList = (index = selectedIndex) => {
    setActive(index);
    setOpen(true);
  };

  const choose = (index) => {
    onChange(options[index].value);
    setOpen(false);
    button.current?.focus();
  };

  // Focus the list when it opens, and close it on a click outside
  useEffect(() => {
    if (!open) return undefined;
    list.current?.focus();
    const onPointer = (e) => root.current && !root.current.contains(e.target) && setOpen(false);
    document.addEventListener('mousedown', onPointer);
    document.addEventListener('touchstart', onPointer);
    return () => {
      document.removeEventListener('mousedown', onPointer);
      document.removeEventListener('touchstart', onPointer);
    };
  }, [open]);

  // Keep the active option in view
  useEffect(() => {
    if (open) list.current?.querySelector(`[data-index="${active}"]`)?.scrollIntoView({ block: 'nearest' });
  }, [open, active]);

  const onButtonKey = (e) => {
    if (['ArrowDown', 'ArrowUp', 'Enter', ' '].includes(e.key)) {
      e.preventDefault();
      openList();
    }
  };

  const onListKey = (e) => {
    const last = options.length - 1;
    const moves = {
      ArrowDown: () => setActive((i) => Math.min(last, i + 1)),
      ArrowUp: () => setActive((i) => Math.max(0, i - 1)),
      Home: () => setActive(0),
      End: () => setActive(last),
      Enter: () => choose(active),
      ' ': () => choose(active),
      Escape: () => {
        setOpen(false);
        button.current?.focus();
      },
    };
    if (moves[e.key]) {
      e.preventDefault();
      moves[e.key]();
    } else if (e.key === 'Tab') {
      setOpen(false);
    } else if (e.key.length === 1) {
      // Type-ahead: jump to the first option starting with what was typed
      const now = Date.now();
      typed.current = { text: (now - typed.current.at < 700 ? typed.current.text : '') + e.key.toLowerCase(), at: now };
      const match = options.findIndex((o) => o.label.toLowerCase().startsWith(typed.current.text));
      if (match >= 0) setActive(match);
    }
  };

  const chevron = (
    <svg
      className={`h-4 w-4 flex-shrink-0 text-purple-light transition-transform duration-200 ${open ? 'rotate-180' : ''}`}
      viewBox="0 0 20 20"
      fill="none"
      stroke="currentColor"
      strokeWidth={2}
      aria-hidden="true"
    >
      <path strokeLinecap="round" strokeLinejoin="round" d="M6 8l4 4 4-4" />
    </svg>
  );

  return (
    <div ref={root} className="relative" style={{ fontFamily: font }}>
      <span id={`${id}-label`} className="mb-1.5 block text-xs font-light text-white/70 md:mb-2 md:text-sm">
        {label}
      </span>
      <button
        ref={button}
        id={id}
        type="button"
        aria-haspopup="listbox"
        aria-expanded={open}
        aria-controls={`${id}-listbox`}
        aria-labelledby={`${id}-label ${id}`}
        onClick={() => (open ? setOpen(false) : openList())}
        onKeyDown={onButtonKey}
        className={`flex w-full items-center justify-between gap-2 rounded-lg border bg-black/30 px-3 py-2 text-start text-sm text-white transition-colors focus:outline-none md:px-4 md:py-2.5 ${open ? 'border-purple-accent' : 'border-purple-primary/30 hover:border-purple-primary/60 focus-visible:border-purple-accent'}`}
      >
        <span className="truncate">{selected?.label}</span>
        {chevron}
      </button>
      <AnimatePresence>
        {open && (
          <motion.ul
            ref={list}
            id={`${id}-listbox`}
            role="listbox"
            tabIndex={-1}
            aria-labelledby={`${id}-label`}
            aria-activedescendant={`${id}-option-${active}`}
            onKeyDown={onListKey}
            initial={reduceMotion ? { opacity: 0 } : { opacity: 0, y: -6 }}
            animate={reduceMotion ? { opacity: 1 } : { opacity: 1, y: 0 }}
            exit={reduceMotion ? { opacity: 0 } : { opacity: 0, y: -6 }}
            transition={{ duration: 0.15, ease: 'easeOut' }}
            className="absolute z-30 mt-2 max-h-[min(23.5rem,60vh)] w-full overflow-y-auto rounded-xl border border-purple-primary/40 bg-[#0b0613]/95 py-1.5 shadow-xl shadow-purple-primary/20 backdrop-blur-md focus:outline-none"
          >
            {options.map((option, index) => {
              const isSelected = option.value === value;
              return (
                <li
                  key={option.value}
                  id={`${id}-option-${index}`}
                  data-index={index}
                  role="option"
                  aria-selected={isSelected}
                  onMouseEnter={() => setActive(index)}
                  onMouseDown={(e) => e.preventDefault()} // keep focus in the list
                  onClick={() => choose(index)}
                  className={`mx-1.5 flex cursor-pointer items-center justify-between gap-3 rounded-lg px-3 py-2 text-sm font-light transition-colors ${index === active ? 'bg-purple-primary/30 text-white' : 'text-white/75'} ${isSelected ? 'text-purple-light' : ''}`}
                >
                  <span>{option.label}</span>
                  {isSelected && (
                    <svg className="h-4 w-4 text-purple-light" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                      <path fillRule="evenodd" d="M16.704 4.153a.75.75 0 0 1 .143 1.052l-8 10.5a.75.75 0 0 1-1.127.075l-4.5-4.5a.75.75 0 0 1 1.06-1.06l3.894 3.893 7.48-9.817a.75.75 0 0 1 1.05-.143Z" clipRule="evenodd" />
                    </svg>
                  )}
                </li>
              );
            })}
          </motion.ul>
        )}
      </AnimatePresence>
    </div>
  );
}
