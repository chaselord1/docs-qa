# Example answers (Ollama end-to-end run)

Run against `LLM_BASE_URL=http://localhost:11434/v1`, `LLM_MODEL=qwen2.5:14b-instruct`,
`EMBED_MODEL=nomic-embed-text`, with the bundled sample docs loaded.

## Q1: Can I get a refund on a bike I already rode?

**Answer:** No, ridden bikes cannot be returned for a refund [returns-and-warranty.md p.1].
However, you can exchange it within 14 days if it doesn't fit [returns-and-warranty.md p.1].

**Top citation:** returns-and-warranty.md p.1 (score 0.70)

## Q2: How much paid time off do full-time employees accrue?

**Answer:** Full-time staff accrue one day of paid time off for every month worked, up to
15 days a year [employee-handbook.pdf p.2].

**Top citation:** employee-handbook.pdf p.2 (score 0.75), the page the answer is actually on.

## Q3: What is the capital of France?

**Answer:** That isn't covered in the documents I have.

**Citations:** none. Best retrieval score (0.37) was below the 0.50 guardrail threshold,
so the model was never called.
