# The story

**Goal of this file:** learn how we go from a human need to a well-defined project.

> **Fictional institution.** Université de Val-Lumière, its staff and its graduates do not exist. Every name here is invented.

The story is told in the order things happen in real life: first a request, then meetings with the people who do the work, then the people the information is about, and only at the end, an agreement on what to build. The technical translation (entities, tables, rules) comes after, in [model.md](model.md).



---

## 1. The request (week 1)

The Director of the Alumni Relations Office sends us this message:

> Université de Val-Lumière, a public university in Québec, has awarded degrees to about 60,000 people since it was founded. Our office exists to keep a lasting link with them: we send them news, we invite them to our events, and we call on them when the university needs their experience.
>
> Our information is spread over many files, and it is getting harder every year to know who our graduates are and how to reach them. Recently we made a painful mistake because of it.
>
> We need your help to find a better way of working.

That is all we have at the start: a goal, a feeling that things are not working, and no detailed account yet of the problems or of what is needed.

---

## 2. Meeting the office (weeks 2 and 3)

Before proposing anything, we meet the people who do the work every day. For each one: what they do, and what goes wrong.

### The newsletter manager

**What she does:** sends a newsletter every month to a mailing list of graduates.

**What goes wrong:**
- "About a third of our emails bounce back. I don't know which ones are dead, so I keep sending to them."
- "Some people ask us to stop all contact, but I only manage the newsletter list. The events team keeps its own list, so these people may still receive invitations."
- "When someone calls to say *stop writing to me*, I write it on a sticky note. Sometimes I'm not the one who answers the phone."

### The events coordinator

**What he does:** organises the annual reunion and a few smaller events. Every year he builds a new invitation list by copying the faculties' spreadsheets into one.

**What goes wrong:**
- "The same person shows up two or three times: *Marie-Ève Tremblay*, *Marie Eve Trembley*, *M. Tremblay*. Same person? I guess, I check by hand."
- "Last year we sent a reunion invitation to a graduate who had passed away. His family called us. They were hurt. That must never happen again."
- "I know who registered, more or less. Who actually came? Paper lists at the door. I never enter them anywhere."
- "For the reunion I get help from student volunteers. I give them the whole spreadsheet, home addresses included. I don't like it, but I don't have anything else."

### A faculty secretary (Faculty of Engineering)

**What she does:** keeps her faculty's spreadsheet of graduates: name, program, year. Professors also ask her for graduates who could give a talk in a course, mentor students, sit on a jury or help with grading. These are small paid assignments.

**What goes wrong:**
- "Some graduates did a bachelor's here, then a master's years later, sometimes in another faculty. They are in two spreadsheets, and they receive everything twice."
- "Some changed their name since they graduated. Their diploma is under the old name; their emails come with the new one. I can't always connect them."
- "I never know when an address was last checked. Some lines are twenty years old."
- "For assignments, I search my memory and my old emails. I don't keep track of who applied or who was chosen."

### The privacy officer

Under Québec's law, the head of the university (the rector) is responsible for the protection of personal information, and may delegate this role in writing. At Val-Lumière, the rector delegated it to her.

**What she explains:**
- "We may use personal information only for the purposes the person agreed to. Someone can agree to the newsletter and refuse everything else."
- "Anyone can ask us in writing: *what do you know about me?* We must answer completely, within the legal deadline. They can also ask us to correct what is wrong or incomplete."
- "Deleting is not automatic. We cannot simply erase anything on request: some records must be kept by law, and others must be destroyed once we no longer need them. Each request is checked."
- "Two requests are often confused. *Stop contacting me* is not the same as *remove my information*. The first one we must respect right away; the second one we must examine."
- "Today, nobody knows who asked not to be contacted, for what, or since when. People asked by phone, by email; it was noted in one file and not in the others. We have contacted people who had asked us to stop."
- "Not everyone in the office needs to see everything. A student volunteer does not need home addresses. Someone preparing statistics does not need names."
- "Last year someone asked to be deleted. We removed their lines from a few files, and the next report showed fewer graduates for 2010 than the year before. Totals must not change because someone left."

---

## 3. Asking the graduates (week 3)

The office talks *about* graduates all the time. We also need to hear *from* them. With the office's help, we send a short questionnaire to a group of volunteer graduates, and we interview five of them. The interviews give us first examples of their experience and expectations.

| Graduate | Their situation | What they told us |
|---|---|---|
| **Léa**, computer science 2024 | Her student email stopped working after graduation | "I'd like news and job events, by email only. Just let me update my address easily." |
| **Sophie**, education 2009 | Graduated as *Sophie Gagnon*, now *Sophie Roy* | "Please use my current name. But yes, my diploma is under my old one; I understand you need both." |
| **Robert**, administration 1995 | Asked twice by phone to stop all contact | "And I still got an invitation. I want it respected everywhere. And I'd like to know what you still have about me." |
| **Karim**, bachelor 1998 (science), master 2012 (engineering) | Appears in two faculties | "I get every message twice. It looks like you don't know me." |
| **Nadia**, civil engineering 2003, 20 years in industry | Would like to give back | "I'd gladly give talks or mentor students, paid or not. But I don't want the newsletter, and please ask me only in my field." |

**What these first conversations suggest:**
- They want to **choose what they receive and how** (email only, no phone), separately for each kind of message.
- They want to **update their own information** easily, without a website for now: an email to the office must be enough.
- They want to **be recognised as one person**, even with two degrees or a new name.
- They want their **"no" to be respected everywhere**, and to **know what is kept** about them.

Five interviews are a starting point, not the opinion of 60,000 graduates. What we did not ask, or could not settle, goes into the [open questions](#7-open-questions-before-modelling).

---

## 4. What we agreed to build (week 4)

From these meetings, we wrote a summary. The Director read it, corrected it and approved it.

**One reliable place, shared by the whole office, to:**

1. **Keep in touch** — know who our graduates are, what they studied, in which faculty, in which year, and how to reach them today.
2. **Organise the annual reunion and other events** — invite the right people, record who registered, and record who actually came.
3. **Offer paid assignments** — find graduates who agreed to be asked, in the right field, and keep track of who applied and who was chosen.
4. **Respect each person's wishes** — for each kind of contact separately: newsletter, events, assignments. Someone may ask us to stop contacting them, or ask us to remove their information.
5. **Trust our information** — know how good it is, and see it improve month after month.

**Who uses it:**
- The office staff: newsletter, events, faculty secretaries, the privacy officer.
- Student volunteers, for events only, with limited access.
- The person preparing statistics, without names.

**Who does not use it (for now): the graduates themselves.** When a graduate asks to see or correct their information, to stop being contacted, or to have their information removed, they write to the office, and **the staff use the tool to answer completely**.

---

## 5. Rules and limits (week 4)

**What we must respect**
- **The law.** Collect, use, share and keep personal information only as the law allows, and ask for the person’s consent wherever it is required (for example, for the newsletter or for assignments). Tell a person everything we hold about them, within the legal deadline, and correct what is wrong or incomplete. Examine each removal request against what the law requires us to keep or to destroy.
- **"Stop" is immediate.** This is the office’s own rule: a request to stop contacting someone is respected right away, everywhere, and stays respected even when the person reappears in next year's faculty spreadsheet.
- **Confidentiality.** Each person in the office sees only what their work needs.
- **Removing without breaking history.** When information about a person is removed, everything that identifies them goes, but the totals we have agreed to keep (for example, how many people graduated in 2010) stay the same. *How* to do it is decided later, in the model.

*The law is simplified here for a fictional story; this is not legal advice.*

**What we do not build now**
- No website or mobile application for the graduates.
- No donations or fundraising.
- No social network, chat feature or built-in messaging platform. Newsletters and invitations continue through the office's existing channels.

These may come later. Today, we want a solid foundation.

---

## 6. How we will know it works

Today, each of these questions takes days, or cannot be answered at all. With the new tool, the answers must be right, and fast: about a minute for the questions about our information (1 to 7, and 10). Questions 8 and 9 are requests from a person: they must be handled completely, with a trace, within the legal deadline and our own shorter target.

1. How many graduates do we have, by faculty and by year?
2. How many of them can we actually reach today?
3. Whom can we invite to this year's reunion: reachable, alive, and who agreed to receive invitations?
4. Which engineering graduates agreed to be asked for paid assignments?
5. When was this person's contact information last checked?
6. Who asked not to be contacted, for what, and since when?
7. How many people appear more than once in our records, and which ones?
8. A graduate asks: "What do you know about me?" Can we answer completely?
9. A graduate asks us to remove their information. Can we do what is allowed, and prove it, without changing our statistics?
10. Month after month: is our information getting better or worse?

---

## 7. Open questions before modelling

Some answers are still missing. We take these questions back to the Director, the privacy officer and the staff concerned. Some need a business or policy decision; others will be settled by the modelling. We record each decision before finalising the model.

- **Counting:** when we say "graduates", do we count people or degrees? Karim is one person with two degrees, in two faculties. Do we need both totals?
- **Two entries, one person?** How do we decide that two entries are the same person, and who confirms it?
- **Several emails or phones:** which one do we use first?
- **Names:** we show the current name; who may see the former names?
- **Death:** who informs us that a graduate has died, and what do we keep afterwards?
- **Reachable:** what makes a graduate "reachable today", how often do we check contact information, and what counts as "checked"?
- **"Stop contacting me":** to respect it, we must remember that the person asked, or they may come back with next year's faculty spreadsheet. What is the minimum we keep?
- **Removal:** what exactly do we remove, what do we keep for the totals, and what trace proves the removal was done without identifying the person again?
- **Existing systems:** which spreadsheets and mailing lists does the new tool replace, and which ones remain? If some remain, how do we make sure that a "stop", a correction or a request for information is applied to them too?
- **Sending:** does the new tool send the emails itself, or does it prepare the list of people allowed to receive them, for the office's existing mailing system?
- **Assignments:** what do we record about who applied and who was chosen? Is the payment handled by another service? Do we also track unpaid help, as Nadia offers, or is that for later?
