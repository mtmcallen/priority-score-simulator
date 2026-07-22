# CIP-9372: Outreach on These Holidays — Update to Actual Date Only

**Document prepared for:** Implementation Team  
**Source ticket:** CIP-9372 (CipherHealth)  
**Status:** Closed / Done  
**Release:** Evolve v26.24.0 (Release Candidate)  
**Reporter:** Mykela McAllen  
**Assignee:** Gregory Bowman  
**Created:** June 3, 2026  
**Last updated:** July 2, 2026  

---

## Summary

Holidays in the **Outreach on These Holidays** field now reflect only the **actual holiday date**, not the **observed holiday date**. This gives customers more control over which days outreach calls go out.

---

## Background

A prior change (CIP-9068: *Ability to Override Holiday Blockages for Outreach*) partially addressed holiday configuration issues, but Support still had to do significant manual work. The root problem was that actual and observed dates were bundled into a single holiday, which confused customers.

**Important:** The fixes from CIP-9068 should remain in place. This story builds on that work.

### What CIP-9068 Already Fixed

CIP-9068 loosened validation so customers can add a date to **No Outreach on These Dates** even when that date falls within a holiday — as long as that holiday is in the **Outreach on These Holidays** allowlist. For example, if Independence Day is in the allowlist, a customer can add July 4 to **No Outreach on These Dates** to block outreach on the 4th while still allowing it on the 3rd.

---

## What Changed (CIP-9372)

The system now uses **only the actual holiday date** in the holiday list. Observed dates are no longer included as part of the holiday definition.

If outreach needs to be blocked on an observed date, add that date manually in **No Outreach on These Dates**.

---

## Expected Behavior

### 1. Holidays block only the actual date

When a holiday is configured, it applies only to its actual calendar date — not any observed date.

| Holiday | Actual Date |
|---------|-------------|
| Independence Day | July 4 only |
| Juneteenth National Independence Day | June 19 only |
| Veteran's Day | November 11 only |
| Christmas Day | December 25 only |
| Christmas Eve | December 24 only |
| New Year's Day | January 1 only |
| New Year's Eve | December 31 only |

If Independence Day is in **Outreach on These Holidays**, outreach will go out on **7/4 only**. It will not affect any other day (including 7/3).

### 2. Observed dates are not treated as holidays

Observed dates are **not** holidays in the system. They can be added to **No Outreach on These Dates** without validation issues.

For example, to block outreach on **7/3/2026** (the observed date for Independence Day in 2026), add `7/3/2026` to **No Outreach on These Dates**. If you do not add it, outreach proceeds as usual on that date.

---

## Configuration Guide: Independence Day 2026 Example

Independence Day 2026: **actual date = 7/4**, **observed date = 7/3** (Friday).

Use the two fields together:

- **Outreach on These Holidays** — allows outreach on a holiday's actual date
- **No Outreach on These Dates** — blocks outreach on specific dates (including observed dates)

### Scenario 1: Customer wants outreach on BOTH 7/3 and 7/4

**Config actions:**
1. Add **Independence Day** to **Outreach on These Holidays**

No other changes needed. Outreach is allowed on both days.

---

### Scenario 2: Customer does NOT want outreach on 7/3 OR 7/4

**Config actions:**
1. Ensure **Independence Day** is **NOT** in **Outreach on These Holidays**
2. Add **7/3/2026** to **No Outreach on These Dates**

Note: 7/4 is blocked automatically because Independence Day is not in the allowlist. Adding 7/3 to the block list covers the observed date.

---

### Scenario 3: Customer wants outreach on 7/3 but NOT 7/4 *(most common)*

**Config actions:**
1. Ensure **Independence Day** is **NOT** in **Outreach on These Holidays**
2. Ensure **7/3/2026** is **NOT** in **No Outreach on These Dates**

Result: Normal outreach on 7/3; 7/4 is blocked because Independence Day is not in the allowlist.

---

### Scenario 4: Customer wants outreach on 7/4 but NOT 7/3 *(least common)*

**Config actions:**
1. Add **Independence Day** to **Outreach on These Holidays**
2. Add **7/3/2026** to **No Outreach on These Dates**

Result: Outreach allowed on 7/4 (via the holiday allowlist); 7/3 is explicitly blocked.

---

## Static-Date Holidays to Account For

These holidays have fixed calendar dates and are affected by this change:

1. Veteran's Day
2. Juneteenth National Independence Day
3. Independence Day
4. Christmas Day
5. Christmas Eve
6. New Year's Day
7. New Year's Eve

For holidays with **variable dates** (e.g., Thanksgiving, Memorial Day), the same principle applies: only the actual date is in the holiday definition. Use **No Outreach on These Dates** for any observed or adjacent dates as needed.

---

## Production Deployment

Deployed to production on **Tuesday, July 8, 2026** as part of **Evolve 26.24.0**.

---

## Quick Reference

| Customer Goal | Outreach on These Holidays | No Outreach on These Dates |
|---------------|---------------------------|---------------------------|
| Outreach on both actual + observed dates | Add the holiday | Leave observed date out |
| No outreach on actual or observed dates | Remove the holiday | Add observed date |
| Outreach on observed only, not actual | Remove the holiday | Do not block observed date |
| Outreach on actual only, not observed | Add the holiday | Add observed date to block list |

---

## Questions?

Contact **Mykela McAllen** (Product) or **Gregory Bowman** (Engineering) for clarification on specific customer configurations.
