import { MAX_ITEMS, trim } from './useQuoteHistory';

const items = (n, favoriteEvery = 0) =>
  Array.from({ length: n }, (_, i) => ({ id: String(i), favorite: favoriteEvery > 0 && i % favoriteEvery === 0 }));

test('keeps at most MAX_ITEMS non-favorites, newest first', () => {
  const kept = trim(items(MAX_ITEMS + 20));
  expect(kept).toHaveLength(MAX_ITEMS);
  expect(kept[0].id).toBe('0');
});

test('favorites are kept past the limit', () => {
  const all = items(MAX_ITEMS + 50, 10);
  const kept = trim(all);
  const favorites = all.filter((item) => item.favorite);
  expect(favorites.every((fav) => kept.includes(fav))).toBe(true);
  expect(kept.filter((item) => !item.favorite)).toHaveLength(MAX_ITEMS);
});
