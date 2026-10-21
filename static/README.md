# Swan on Zibby: the frontend

On the `zibby` branch this React app is the whole of Swan. It is built as a static bundle
that [Zibby](https://zibby.run) serves, and every quote is one call through Zibby's
`/api/ai`, paid in the signed-in person's Zibby credits. There is no server, no API key and
no provider SDK in it; the Python app in the repository root is not part of the build.

```bash
npm ci          # from the repository root
npm run dev     # http://localhost:5173, on the kit's mock: no network, no credits
npm test        # Vitest: guardrails, the Zibby flow, the screen
npm run build   # dist/, with dist/zibby-sample.json
```

Zibby builds it the same way: install `npm ci`, build `npm run build`, output `dist`.

## What moved from the server

| Server (`app/`) | Here (`src/lib/`) |
| --- | --- |
| `guardrails/normalize.py`, `injection.py`, `output.py` | `normalize.js`, `injection.js`, `output.js`, rule for rule |
| `api/utils/prompt_builder.py`, the system instruction | `prompt.js`, plus the Anthropic request body |
| `controllers/quote_controller.py` | `quote.js`, on Zibby's rules |

`scripts/guardrail_parity.py` runs the Python guardrails over every string in
`tests/test_guardrails.py` and `evals/cases.jsonl` and writes
`src/lib/parity.fixture.json`; `parity.test.js` checks that the JavaScript says exactly the
same about each one, and CI checks that the fixture is current.

What changed on the way, because a person pays for each call:

- **One press, one call.** The server regenerated a failed answer by itself. Here a failed
  check is shown with its reasons and a "Try again" button that sends the same request
  with those reasons attached, once. An answer cut off at the length limit gets no paid
  retry, since it would be cut off again. A refusal is final.
- **Zibby owns the rest.** Retries, fallbacks, circuit breakers and rate limits are gone;
  credits, the spending cap, sign-in and top-up are Zibby's, reached through the kit.
- **The charge** shown is the run's own terminal frame: "Charged 1 credit.", "Nothing was
  charged.", "Charge unknown" with the request id, or "Comped" for runs on Zibby.
- **The model** is Claude Haiku 4.5 (`src/lib/prompt.js`). Zibby has no Gemini text model
  yet.
- **Nothing leaves the app's frame**: no GitHub link, no share links to X, Facebook or
  WhatsApp. Sharing uses Zibby's own share sheet; copying and the quote images stay.
- **Fonts** (Amiri, Cairo, Crimson Text, Poppins) are bundled from Fontsource instead of
  Google Fonts.

History and favorites stay in this browser's localStorage, as before.

## Notifications

`src/components/Toast.jsx` provides the toasts. The app is wrapped in `<ToastProvider>`;
any component can then call:

```javascript
const toast = useToast();
toast.success('Quote copied to clipboard.');
toast.error(message, { id: 'generate' }); // same id replaces instead of stacking
toast.warning(message, { dir: 'rtl' });   // Arabic text
toast.info(message, { duration: 0 });     // stays until dismissed
toast.error(message, { action: { label: 'Top up', onClick } }); // one button
```

Errors and warnings are announced to screen readers immediately (`role="alert"`), the
others politely. Toasts pause while hovered or focused and close with their button or
Escape.

---

<div align="center">
  <em>Built by AyaNexus 🦢</em>
</div>
