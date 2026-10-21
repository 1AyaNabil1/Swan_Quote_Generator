/**
 * One press, one quote: the browser port of quote_controller.py, on Zibby's rules.
 *
 * 1. scan the topic and style for prompt injection (nothing is sent, nothing is charged)
 * 2. build the prompt
 * 3. one call through Zibby's /api/ai, paid in the signed-in person's credits
 * 4. check the answer: language, length, format, instruction leaks, refusals
 *
 * The server regenerated a failed answer by itself. On Zibby a press pays for one
 * call, so a failed answer is reported with its reasons instead, and the person may
 * press once more to send the same request with those reasons attached (`hint`).
 * An answer cut off at the length limit is never offered a paid repair: it would be
 * cut off the same way again.
 */
import { publishBalance, streamZibbyAi, ZibbyAiError } from '@zibby-run/app-kit';
import { scanRequest } from './injection';
import { checkQuote, cleanQuote } from './output';
import { buildQuotePayload, QUOTE_ACTION, QUOTE_MODEL, SYSTEM_INSTRUCTION } from './prompt';

export class QuoteError extends Error {
  /**
   * kind: input · refused · truncated · checks (the one that may be repaired) ·
   * credits · cap · signed-out · locked · busy · network · aborted · server
   */
  constructor(kind, { charge = null, requestId = null, checks = [], hint = '', cause } = {}) {
    super(kind, cause === undefined ? undefined : { cause });
    this.name = 'QuoteError';
    this.kind = kind;
    this.charge = charge;
    this.requestId = requestId ?? charge?.requestId ?? null;
    this.checks = checks;
    this.hint = hint;
  }
}

function fromZibby(error) {
  if (error?.name === 'AbortError') return new QuoteError('aborted', { cause: error });
  if (!(error instanceof ZibbyAiError)) return new QuoteError('network', { cause: error });
  const opts = { requestId: error.requestId ?? null, cause: error };
  switch (error.code) {
    case 'insufficient_credits':
      return new QuoteError('credits', opts);
    case 'session_cap_reached':
      return new QuoteError('cap', opts);
    case 'unauthenticated':
      return new QuoteError('signed-out', opts);
    case 'locked':
      return new QuoteError('locked', opts);
    case 'rate_limited':
      return new QuoteError('busy', opts);
    case 'network':
      return new QuoteError('network', opts);
    default:
      return new QuoteError('server', opts);
  }
}

/** What the run cost. Only the terminal frame matches Zibby's ledger (CONTRACT §2). */
function chargeOf(result) {
  return {
    known: result.chargeKnown,
    credits: result.terminal?.charged_cr ?? 0,
    comped: result.terminal?.comped === true,
    requestId: result.requestId ?? null,
  };
}

/**
 * Resolves with {quote, charge}; rejects with a QuoteError. A run that completed but
 * failed a check carries its charge, so the person sees what it cost.
 */
export async function generateQuote(request, { stream = streamZibbyAi, hint = '', capAck = false, signal } = {}) {
  const finding = scanRequest({ topic: request.topic, style: request.style });
  if (finding) throw new QuoteError('input', { checks: [finding.field] });

  let result;
  try {
    result = await stream(
      { action: QUOTE_ACTION, provider: 'anthropic', model: QUOTE_MODEL, payload: buildQuotePayload(request, { hint }) },
      { ...(signal ? { signal } : {}), ...(capAck ? { capAck: true } : {}) },
    );
  } catch (error) {
    throw fromZibby(error);
  }
  const charge = chargeOf(result);
  if (result.terminal) publishBalance(result.terminal.balance_cr);

  // The model said no, in a stop reason or in words. That is final: asking again
  // would be asking until it says yes.
  if (result.stopReason === 'refusal') throw new QuoteError('refused', { charge });
  const quote = cleanQuote(result.text);
  const finishReason = result.stopReason === 'max_tokens' ? 'max_tokens' : 'stop';
  const violations = checkQuote(quote, {
    language: request.language,
    length: request.length,
    finishReason,
    instructions: SYSTEM_INSTRUCTION,
  });
  const checks = violations.map((v) => v.check);
  if (checks.includes('refusal')) throw new QuoteError('refused', { charge });
  if (checks.includes('truncated')) throw new QuoteError('truncated', { charge, checks });
  if (violations.length > 0) {
    const hints = [...new Set(violations.map((v) => v.hint))].join(' ');
    throw new QuoteError('checks', { charge, checks, hint: ` Your previous answer was rejected. ${hints}` });
  }
  return { quote, charge };
}
