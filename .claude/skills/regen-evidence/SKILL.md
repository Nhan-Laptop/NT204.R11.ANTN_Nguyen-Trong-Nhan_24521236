---
name: regen-evidence
description: Regenerate the committed PCAP fixtures and JSONL evidence under TEST/ by running the make_*.py scripts. Overwrites tracked files; run only when explicitly asked.
disable-model-invocation: true
---

This skill overwrites tracked files under `TEST/`. Before running it, tell the user which files will change and wait for confirmation unless they already asked for regeneration explicitly.

Run from the repository root, in this order:

1. `python TEST/baitap1/khac/mandatory_cases/make_test_pcaps.py` — rebuilds the PCAP input and JSONL output of the 12 Bài 1 test-case folders.
2. `python TEST/baitap2/khac/integration/make_evidence.py` — rebuilds the integration evidence JSONL.

Afterwards:

1. Run `git status -- TEST/` and list every changed file.
2. Run the tests (the `run-tests` skill) and confirm each one still prints the output its `readme.md` expects.
3. If any output changed unexpectedly, say so and do not commit. Committing is up to the user.


