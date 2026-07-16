# Wake Protocol — Step-by-Step Initialization

Run this at the start of every FTN session when the Human Director says "Wake Protocol" or "Good morning".

## 1. File Check
```bash
read_file(path="/hermes/profiles/zeon7/leads_inbox.md")
```
- Note the date of the last entry (if any)
- Count existing leads

## 2. Time Check
- Current date: use system date (YYYY-MM-DD)
- Identify today's signal from Seven Signals Calendar
- Calculate 6-day window: `start_date = current_date - 6 days`

## 3. Catch-Up Logic
**IF** the inbox has no leads with trigger dates within the 6-day window for today's signal:
- Run Tavily search for today's theme (see theme keywords below)
- Generate Story Lead Cards (see story-lead-template.md)
- Append to `leads_inbox.md` using write_file or patch

**ELSE** (leads exist for current window):
- Report existing leads to Human Director
- Ask for editorial steer

## 4. Theme Keywords by Signal

| Signal | Search Keywords (Tavily) |
|--------|-------------------------|
| The Signal Still Comes Through (Mon) | "community resilience UK", "mutual aid UK", "grassroots recovery UK", "personal story resilience" |
| Through the Static (Tue) | "investigation UK", "FOIA UK", "data journalism UK", "corporate accountability UK", "government failure UK" |
| Out From the Noise (Wed) | "personal essay UK", "first person narrative UK", "my story UK", "A moment that changed me", "life changing moment UK" |
| 404: Hope Not Found (Thu) | "institutional failure UK", "public service collapse UK", "NHS crisis", "council bankruptcy UK", "system failure UK" |
| The Maddest Stuff They Did This Week (Fri) | "absurd UK politics", "satire UK", "bizarre policy UK", "government waste UK", "political gaffe UK" |
| Everything's Fine (Sat) | "performative normalcy UK", "cost of living UK", "pretending everything fine UK", "ironic normalcy UK" |
| The Last Warm Place (Sun) | "community memory UK", "local history UK", "neighbourhood stories UK", "tender community UK", "mutual aid story UK" |

## 5. Report to Human Director
Format:
```
Good morning, Merrill. Systems are online.

**Wake Protocol Report — [DATE]**

**Inbox Status**: [X leads total, Y fresh today]

**Today's Signal**: [Signal**: [Day] — "[Signal Name]" ([Theme]). [6-day window dates].

**New Leads**: [count] — [one-line summary each]

Ready for your editorial steer.
```