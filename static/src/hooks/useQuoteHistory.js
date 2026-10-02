/**
 * Quote history and favorites, kept in this browser's localStorage.
 *
 * Nothing leaves the browser. Storage can be unavailable (private windows, blocked site
 * data), in which case history works for the session and is simply not saved.
 */
import { useCallback, useEffect, useState } from 'react';

const KEY = 'swan.history.v1';
export const MAX_ITEMS = 100; // favorites are kept even past the limit

function load() {
  try {
    const items = JSON.parse(window.localStorage.getItem(KEY) || '[]');
    return Array.isArray(items) ? items : [];
  } catch {
    return [];
  }
}

function save(items) {
  try {
    window.localStorage.setItem(KEY, JSON.stringify(items));
  } catch {
    // Full or blocked: keep going without saving
  }
}

/** Newest first, at most MAX_ITEMS that are not favorites. */
export function trim(items) {
  let others = 0;
  return items.filter((item) => item.favorite || ++others <= MAX_ITEMS);
}

export default function useQuoteHistory() {
  const [items, setItems] = useState(load);

  const update = useCallback((change) => {
    setItems((current) => {
      const next = trim(change(current));
      save(next);
      return next;
    });
  }, []);

  // Another tab changed the history
  useEffect(() => {
    const onStorage = (event) => event.key === KEY && setItems(load());
    window.addEventListener('storage', onStorage);
    return () => window.removeEventListener('storage', onStorage);
  }, []);

  const add = useCallback((quote) => {
    const item = {
      id: `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`,
      favorite: false,
      ...quote,
    };
    update((current) => [item, ...current]);
    return item.id;
  }, [update]);

  const toggleFavorite = useCallback((id) => {
    update((current) => current.map((item) => (item.id === id ? { ...item, favorite: !item.favorite } : item)));
  }, [update]);

  const remove = useCallback((id) => {
    update((current) => current.filter((item) => item.id !== id));
  }, [update]);

  const clearHistory = useCallback(() => {
    update((current) => current.filter((item) => item.favorite));
  }, [update]);

  return { items, add, toggleFavorite, remove, clearHistory };
}
