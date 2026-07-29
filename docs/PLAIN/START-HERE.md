# Start Here — the no-jargon version

> For people who are not developers. Everything here is also true in the [main README](../../README.md); this page just says it without the vocabulary.
> If this page ever disagrees with a rule file, the rule file wins.

## What this thing actually is

You are going to ask an AI to build software for you. Left alone, an AI assistant will happily do the wrong thing confidently, forget what it learned yesterday, and tell you it finished when it did not.

This project is the set of rules and safety nets that stops that. You do not read the rules. You do not memorise anything. The AI reads them, and some of them are enforced by the computer rather than by good intentions.

## Before you start

You need two things:

1. **Claude Code installed** and working in your terminal.
2. **A copy of this project** as the folder you are working in.

That is it. You do not need to know git, Python, or what a hook is.

## The first thing to type

Open Claude Code in the project folder and paste this, in your own words:

```
幫我完成專案初始化，交給它做前兩步
```

or, in English:

```
Help me set this project up. Do the first two steps for me.
```

It will ask you a couple of questions about what you are building, then do the setup itself. If a question does not make sense to you, say so — "I don't know what that means" is a perfectly good answer, and it will rephrase rather than push past you.

After setup, just describe what you want built. Plain sentences. No special syntax.

If you would rather be walked through it question by question, type `/guided-start` and describe your goal. Same destination, more hand-holding.

## What happens after you ask for something

Three things, in this order:

1. **It works out how big the job is.** Small and obvious — a typo, a one-line change — it just does it. Anything bigger, it writes you a plan first and waits for you to say yes. It does not start changing things and tell you afterwards.
2. **It does the work**, splitting the job across specialists when that helps.
3. **Something other than the writer checks the work.** The part of the AI that wrote the code is not allowed to be the part that declares it correct. That separation is deliberate — it is the single biggest reason this setup catches its own mistakes.

## How you know it actually worked

Every piece of work ends in the same three lines:

```
✓ Done: [what was actually done]
→ Next: [what happens next]
⚠ Note: [anything you should worry about]
```

The useful part is that each line points at a real file you could open. "Tests pass" on its own is a claim. "Tests pass, output in `state/acceptance/...`" is evidence. If you ever want the evidence in plain language, ask: *"翻成白話給我看"* / *"show me that in plain language."*

## When something goes wrong

Describe what you are seeing, in whatever words you have. Pasting the red error text works fine. You do not need to diagnose anything.

Two things it is built to do instead of guessing:

- **It stops and asks** when your request could reasonably mean two different things, or when the next step is hard to undo.
- **It gives up out loud** when it is stuck. After a fixed number of failed attempts it stops, tells you what it tried, and asks — rather than quietly trying a fourth time on your budget.

## What it will not do without asking you

These are enforced by the computer, not by the AI's good behaviour. It cannot talk its way past them:

- Commit to your main branch
- Force-push over your main branch, or hard-reset it
- Read your secret files — passwords, API keys, `.env`
- Pipe something off the internet straight into your shell
- Delete files outside the job it was given

## Words you will see, in one line each

| Word | What it means |
|---|---|
| **ExecPlan** | A written plan for a big change. You approve it before anything happens. |
| **Plan Mode** | The same idea for a smaller job — a plan shown in chat, waiting on your yes. |
| **Agent** | A specialist the AI hands part of the job to. |
| **Skill** | A saved procedure for a recurring task. |
| **Hook** | An automatic check that runs whether anyone remembered it or not. |
| **Invariant** | A rule that is never negotiable, and that a hook actually enforces. |
| **Acceptance** | Proof the work is done — an actual test run, not an opinion. |
| **Handoff** | The note one part of the AI leaves the next, so nothing is lost between sessions. |
| **Tier pack** | The rulebook, sized to whichever AI model is running. You never touch this. |

## If you want to go one level deeper

- [`claude-md-crib-sheet.md`](claude-md-crib-sheet.md) — one page on how it decides "just do it" versus "write a plan first" (Chinese)
- [Main README](../../README.md) — the full picture, written for developers
- `docs/harness/NEW-PROJECT-VALIDATION.md` — the 30-minute test drive worth doing before you trust it with real work

## The honest part

This setup makes an AI far more reliable at **doing the thing right**. It cannot tell you whether you are asking for **the right thing**. Taste, product judgment, whether users will care — those stay yours. When the AI hits one of those, it is under instruction to hand you options and let you choose, rather than pick and sound confident about it.
