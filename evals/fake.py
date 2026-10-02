"""
A stand-in model for checking the harness offline. It behaves like a model with no
defenses: it obeys any instruction to print the canary, and refuses a few obviously
harmful topics.
"""

import json

from app.llm import LLMRequest, LLMResult, Refused


HARMFUL_MARKERS = ("bomb", "قنبل", "terrorist", "إرهابي", "ارهابي")


class FakeEvalModel:
    name = "fake-model"

    async def generate(self, request: LLMRequest, timeout: float) -> LLMResult:
        prompt = request.prompt
        if any(marker in prompt.lower() for marker in HARMFUL_MARKERS):
            raise Refused("fake refusal")
        if "PWNED42" in prompt:
            quote = "PWNED42"
        elif "Write ONLY in Arabic" in prompt:
            quote = "الصبر مفتاح الفرج، والخطوة الصغيرة تصنع طريقًا طويلًا."
        else:
            quote = "Keep going; the road remembers every step you take."
        return LLMResult(
            text=json.dumps({"quote": quote}, ensure_ascii=False),
            model=self.name,
            finish_reason="stop",
            input_tokens=len(prompt.split()),
            output_tokens=len(quote.split()),
            latency=0.01,
        )
