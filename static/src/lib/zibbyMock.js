/** Canned quotes for `npm run dev`: no network, no credits. */
import { createMockStream } from '@zibby-run/app-kit/mock';
import { QUOTE_ESTIMATE_CR } from './prompt';

const CANNED = {
  en: 'Every small step you take in the dark still counts, because dawn keeps the score of the patient.',
  ar: 'كل خطوة صغيرة تخطوها في العتمة محسوبة، فالفجر لا ينسى من صبروا على الطريق.',
};

export const mockStream = createMockStream({
  cannedAnswer: (request) => (/ONLY in Arabic/.test(request.payload.messages[0].content) ? CANNED.ar : CANNED.en),
  quoteFor: () => QUOTE_ESTIMATE_CR,
});
