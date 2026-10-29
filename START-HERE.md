# START HERE

Answer these questions before you work the arc42 chapters. They are the same for every system.

Anyone can answer any of them: the business owner, the security contact, or the architect. The answers are a first draft. They pre-fill the arc42 chapters and the control questions listed under each one, and get sharpened there.

sh-14 picks the overlay. Together with the impact level from sh-12, it tells you which package to use. sh-18 turns on the privacy overlay, which every package already includes.

<!-- charter:start-here id="sh-01" -->
## sh-01  (P-8)

What business capability is this system going to primarily support?

**Pre-fills:** PM-11 (organization-level, kept for the SSP export)

**arc42 chapter:** 1

**Answer:**


<!-- /charter:start-here -->

<!-- charter:start-here id="sh-02" -->
## sh-02  (P-9)

Who has a stake in this system: who owns it, builds it, runs it, uses it, approves it, and eventually retires it, and what does each need?

**Pre-fills:** PL-2 question 4

**arc42 chapter:** 1

**Answer:**


<!-- /charter:start-here -->

<!-- charter:start-here id="sh-03" -->
## sh-03  (P-10)

What does this system need to protect: its data, software, hardware, and facilities, and the people and business capability that depend on it?

**Pre-fills:** CM-8

**arc42 chapter:** 5, 7

**Answer:**


<!-- /charter:start-here -->

<!-- charter:start-here id="sh-04" -->
## sh-04  (P-11)

Where does this system start and stop: what's inside it, and what sits outside but connects to it?

**Pre-fills:** CA-3, SC-7

**arc42 chapter:** 3

**Answer:**


<!-- /charter:start-here -->

<!-- charter:start-here id="sh-05" -->
## sh-05  (P-12)

What kinds of information does this system handle, such as customer records, financial data, health data, or system logs?

**Pre-fills:** RA-2, PL-2 question 1

**arc42 chapter:** 1

**Answer:**


<!-- /charter:start-here -->

## Rating each kind of information

Ask sh-15, sh-16, and sh-17 once for each kind of information named in sh-05. The harm is to the organization's operations, its assets, or individuals. The answers follow the FIPS 199 definitions:

- **Limited** is low: a limited adverse effect.
- **Serious** is moderate: a serious adverse effect.
- **Severe** is high: a severe or catastrophic adverse effect.

To work out the proposed rating:

1. A leak (sh-15) rates confidentiality, a change (sh-16) rates integrity, and an outage (sh-17) rates availability.
2. For each of the three, take the highest answer across all kinds of information.
3. The overall level is the highest of the three. That is the proposed rating sh-12 confirms.

<!-- charter:start-here id="sh-15" -->
## sh-15  (C-2)

How bad would it be if this information leaked to the wrong people: limited, serious, or severe?

Answer once for each kind of information named in sh-05.

**Pre-fills:** RA-2

**arc42 chapter:** 1

**Answer:**


<!-- /charter:start-here -->

<!-- charter:start-here id="sh-16" -->
## sh-16  (C-2)

How bad would it be if this information were changed or corrupted without anyone noticing: limited, serious, or severe?

Answer once for each kind of information named in sh-05.

**Pre-fills:** RA-2

**arc42 chapter:** 1

**Answer:**


<!-- /charter:start-here -->

<!-- charter:start-here id="sh-17" -->
## sh-17  (C-2)

How bad would it be if this information or the system using it were unavailable for a day: limited, serious, or severe?

Answer once for each kind of information named in sh-05.

**Pre-fills:** RA-2

**arc42 chapter:** 1

**Answer:**


<!-- /charter:start-here -->

<!-- charter:start-here id="sh-06" -->
## sh-06  (P-13)

For each kind of information, where does it come from, where does it go, who touches it along the way, and when is it deleted?

**Pre-fills:** CM-13, SI-12

**arc42 chapter:** 6

**Answer:**


<!-- /charter:start-here -->

<!-- charter:start-here id="sh-07" -->
## sh-07  (P-14)

What could go wrong with this system: who might attack or misuse it, what weak spots worry you, and how bad would the damage be?

**Pre-fills:** RA-3

**arc42 chapter:** 11

**Answer:**


<!-- /charter:start-here -->

<!-- charter:start-here id="sh-08" -->
## sh-08  (P-15)

What security and privacy rules does this system have to meet, such as laws, regulations, contracts, customer promises, or company policy?

**Pre-fills:** PL-2 question 2, PT-2

**arc42 chapter:** 2

**Answer:**


<!-- /charter:start-here -->

<!-- charter:start-here id="sh-09" -->
## sh-09  (P-16)

Where does this system fit among the organization's other systems: what does it rely on, share with, or replace?

**Pre-fills:** PM-7 (organization-level, kept for the SSP export), PL-8

**arc42 chapter:** 4

**Answer:**


<!-- /charter:start-here -->

<!-- charter:start-here id="sh-10" -->
## sh-10  (P-17)

Of those security and privacy rules, which does this system handle itself, and which come from shared platforms, cloud providers, or company-wide services?

**Pre-fills:** PL-9, PM-1 (organization-level, kept for the SSP export)

**arc42 chapter:** 8

**Answer:**


<!-- /charter:start-here -->

<!-- charter:start-here id="sh-11" -->
## sh-11  (P-18)

Where is this system registered in the organization's system inventory, and who's listed as its owner?

**Pre-fills:** PM-5 (organization-level, kept for the SSP export)

**arc42 chapter:** 1

**Answer:**


<!-- /charter:start-here -->

<!-- charter:start-here id="sh-12" -->
## sh-12  (C-2)

What final impact level, low, moderate, or high, applies to confidentiality, integrity, and availability, and why does any differ from the proposed rating?

The proposed rating comes from sh-15 to sh-17. See "Rating each kind of information" above.

**Pre-fills:** RA-2

**arc42 chapter:** 1

**Answer:**


<!-- /charter:start-here -->

<!-- charter:start-here id="sh-13" -->
## sh-13  (C-3)

Who approved this system's impact rating, and when?

**Pre-fills:** RA-2

**arc42 chapter:** 1

**Answer:**


<!-- /charter:start-here -->

<!-- charter:start-here id="sh-14" -->
## sh-14  (Select)

Which kind of system is this: an AI system, an OT system, or neither?

**Pre-fills:** (picks overlay)

**arc42 chapter:** 1

**Answer:**


<!-- /charter:start-here -->

<!-- charter:start-here id="sh-18" -->
## sh-18  (Select)

Which kinds of personal information does this system handle, if any?

Any answer except none turns on the privacy overlay.

**Pre-fills:** (adds privacy overlay)

**arc42 chapter:** 1

**Answer:**


<!-- /charter:start-here -->
