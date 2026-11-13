# 4 · Rolling it out in a company

My setup is one person, one laptop, one number. A company is a different problem. Here is how I would do it, in order.

## Decide first

**1. Whose WhatsApp?**

| Option | Good | Watch out |
|---|---|---|
| Each person links their own number on their own laptop | Simple. Everyone sees only their own chats. This is my setup, copied. | Personal and work chats are mixed on most phones. The allowlist becomes essential. |
| One shared company number (reception, concierge line) on one always-on machine | One place for all client conversations. | That machine holds everything. One owner, locked room or locked-down Mac mini, and decide who may ask Claude about it. |
| WhatsApp Business app numbers | Works the same way; it is still a linked device. | Same unofficial-client caveat. |

Start with option one, for two or three people. Do not start with the shared number.

**2. What may Claude read, and what happens to it?**
Write the allowlist tiers down as a company rule, not per person: which client chats are in, that personal chats are out, what never gets copied (money details, health, IDs).

**3. Who can send?**
My answer: nobody's Claude. Drafts only. Decide it once and deny the send tools in the shared settings file.

**4. Are you allowed to?**
This is processing of personal data of clients and third parties. Depending on where you and your clients are (GDPR in the EU, PDPO in Hong Kong, PDPA in Singapore, PDPA in Taiwan), you may need to update your privacy notice, have a legal basis, and sign a data processing agreement with your AI provider. Check which Claude plan you are on: on the Team and Enterprise plans and the API, Anthropic does not train on your data by default. Ask your lawyer before you roll out to client-facing staff. I am not one.

## Then pilot

1. **Week 1 — one person.** The most technical one. Install (steps 1–2), lock sending (step 1.6), write the allowlist. Use it daily: "what did X and I agree", "who am I not answering".
2. **Week 2 — three people.** They install from this repo with the first person helping. Note every place they get stuck and fix the guide.
3. **Week 3 — decide.** Is it saving time? Did anything leak where it should not? Then either roll out or stop.

## What each person needs

- A laptop with disk encryption on, that is theirs alone.
- Claude Desktop (or Claude Code) on a company plan.
- 30 minutes with someone who has done it.
- The company allowlist rules and the shared settings file with the send tools denied.

## Who keeps it running

Somebody has to own it. The jobs are small but real:

- Update the software about once a month (`git pull`, rebuild, restart). WhatsApp sometimes raises the minimum version and old builds stop pairing.
- Help people re-scan the QR code when a device is logged out.
- Offboarding: when someone leaves, log their linked device out from their phone and wipe `whatsapp-bridge/store/` and the backups on the laptop.
- Review the allowlist every quarter.

## Where this stops being the right tool

- You want Claude to **answer clients automatically** → official WhatsApp Business Platform with a proper bot, consent and templates.
- You need **one searchable archive for the whole company** with access control and audit → a shared inbox product built on the official API.
- You need **compliance-grade retention** → not this.

This setup is a personal assistant that can read your chats. Used as that, it is excellent.
