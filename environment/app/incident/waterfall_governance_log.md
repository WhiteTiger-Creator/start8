# Structured Finance Payment Waterfall — Governance Review Log
Deal governance archive for the 2026 distribution periods (2026-Q1 through 2026-Q2).

## Executive Summary
How the distribution engine is *meant* to behave — the reconciliation of the period's collections, the order of the payment steps, the accrual and rounding of each due, the two coverage tests and what a breach of each one diverts, defers or withholds, the carryforward of every shortfall, the caps on the diversion and on the residual, and the admission, ordering and capacity cap of the payment register — was settled incrementally by the deal governance board, and those decisions live in the review entries below rather than in any single summary. Several stages deliberately DEVIATE from a plain top-to-bottom cascade: a breached coverage test moves a later step and inserts one of its own, one test is measured after the step above it has already paid, the rounding direction is fixed independently for each accrual leg, and the register is a materiality schedule rather than an execution trace. The February draft proposals were revisited during the 2026-05 governance review and several were reversed, and the reconciliation rules were revisited again in 2026-06; where a draft or an interim conflicts with a later decision, the later dated decision governs. `/app/docs/report_spec.json` is the output contract only.

## Governance Review Archive
Routine entries are context only. #WF-ticketed proposal and decision quotes are the authoritative record for engine behaviour.

### Review entry 4000 — servicer collections desk
Desk lead logged a routine observation for the servicer collections desk during distribution review window 4000. Remittance tiles for the period lagged during the servicer file refresh; attributed to report caching, not the engine.
Reviewers should reconcile behaviour questions against #WF governance decisions rather than desk chatter.

### Review entry 4001 — cash manager
Desk lead logged a routine observation for the cash manager during distribution review window 4001. Obligor concentration audit sampled cross-border accounts; no engine-relevant findings for this lane.
Thread archived; see the #WF decision entries for anything affecting engine behaviour.

### Review entry 4002 — trustee reporting desk
Desk lead logged a routine observation for the trustee reporting desk during distribution review window 4002. Synthetic remittance injection verified statement delivery to the noteholder distribution list.
> **Distribution draft proposal (2026-02-06 - #WF-4004)** Anders: the distribution order is fees, then every tranche's interest by seniority regardless of class, then every tranche's principal by seniority, then the residual; the coverage tests are reported for information only and never divert cash or move a step *(Superseded — reversed in the 2026-05 governance review.)*
Historical spreadsheet distributions remain archived and non-authoritative for the engine acceptance.

### Review entry 4003 — rating surveillance
Desk lead logged a routine observation for the rating surveillance during distribution review window 4003. Noise review: repeated servicer lines traced to a duplicated batch upload, suppressed at the source.
No engine semantics changed in this entry; parameters remain as approved by the governance board.

### Review entry 4004 — deal administration
Desk lead logged a routine observation for the deal administration during distribution review window 4004. Quarterly access recertification touched this lane; no engine-relevant configuration changed.
Reviewers should reconcile behaviour questions against #WF governance decisions rather than desk chatter.

### Review entry 4005 — collateral analytics
Desk lead logged a routine observation for the collateral analytics during distribution review window 4005. Capacity review noted rising line-item volume; thresholds unchanged outside the governance process.
Thread archived; see the #WF decision entries for anything affecting engine behaviour.

### Review entry 4006 — paying agent
Desk lead logged a routine observation for the paying agent during distribution review window 4006. Custodian reconciliation drill completed; settlement acknowledgment stayed within the governance window.
> **Distribution draft proposal (2026-02-07 - #WF-4006)** Anders: interest accrues on an actual/365 basis - balance_minor * coupon_bps * period_days // 3650000 - and every accrual in the deal, the basis leg of a fee included, rounds down *(Superseded — reversed in the 2026-05 governance review.)*
Historical spreadsheet distributions remain archived and non-authoritative for the engine acceptance.

### Review entry 4007 — servicer collections desk
Desk lead logged a routine observation for the servicer collections desk during distribution review window 4007. Change board reviewed stale exception approvals; owners pinged before the next distribution cycle.
No engine semantics changed in this entry; parameters remain as approved by the governance board.

### Review entry 4008 — cash manager
Desk lead logged a routine observation for the cash manager during distribution review window 4008. Vendor ticket on remittance retries closed; delivery within contractual budget.
Reviewers should reconcile behaviour questions against #WF governance decisions rather than desk chatter.

### Review entry 4009 — trustee reporting desk
Desk lead logged a routine observation for the trustee reporting desk during distribution review window 4009. Waterfall rehearsal against the prior period ran clean; no changes to engine parameters were approved.
> **Distribution draft proposal (2026-02-08 - #WF-4008)** Rosa: the senior principal step shares the cash in hand pro rata across the senior tranches in proportion to their principal due *(Superseded — reversed in the 2026-05 governance review.)*
Thread archived; see the #WF decision entries for anything affecting engine behaviour.

### Review entry 4010 — rating surveillance
Desk lead logged a routine observation for the rating surveillance during distribution review window 4010. Remittance tiles for the period lagged during the servicer file refresh; attributed to report caching, not the engine.
Historical spreadsheet distributions remain archived and non-authoritative for the engine acceptance.

### Review entry 4011 — deal administration
Desk lead logged a routine observation for the deal administration during distribution review window 4011. Obligor concentration audit sampled cross-border accounts; no engine-relevant findings for this lane.
No engine semantics changed in this entry; parameters remain as approved by the governance board.

### Review entry 4012 — collateral analytics
Desk lead logged a routine observation for the collateral analytics during distribution review window 4012. Synthetic remittance injection verified statement delivery to the noteholder distribution list.
Reviewers should reconcile behaviour questions against #WF governance decisions rather than desk chatter.

### Review entry 4013 — paying agent
Desk lead logged a routine observation for the paying agent during distribution review window 4013. Noise review: repeated servicer lines traced to a duplicated batch upload, suppressed at the source.
Thread archived; see the #WF decision entries for anything affecting engine behaviour.

### Review entry 4014 — servicer collections desk
Desk lead logged a routine observation for the servicer collections desk during distribution review window 4014. Quarterly access recertification touched this lane; no engine-relevant configuration changed.
> **Distribution draft proposal (2026-02-09 - #WF-4010)** Rosa: an unpaid amount carries forward at face value; nothing in this waterfall compounds *(Superseded — reversed in the 2026-05 governance review.)*
Historical spreadsheet distributions remain archived and non-authoritative for the engine acceptance.

### Review entry 4015 — cash manager
Desk lead logged a routine observation for the cash manager during distribution review window 4015. Capacity review noted rising line-item volume; thresholds unchanged outside the governance process.
No engine semantics changed in this entry; parameters remain as approved by the governance board.

### Review entry 4016 — trustee reporting desk
Desk lead logged a routine observation for the trustee reporting desk during distribution review window 4016. Custodian reconciliation drill completed; settlement acknowledgment stayed within the governance window.
Reviewers should reconcile behaviour questions against #WF governance decisions rather than desk chatter.

### Review entry 4017 — rating surveillance
Desk lead logged a routine observation for the rating surveillance during distribution review window 4017. Change board reviewed stale exception approvals; owners pinged before the next distribution cycle.
Thread archived; see the #WF decision entries for anything affecting engine behaviour.

### Review entry 4018 — deal administration
Desk lead logged a routine observation for the deal administration during distribution review window 4018. Vendor ticket on remittance retries closed; delivery within contractual budget.
> **Distribution draft proposal (2026-02-10 - #WF-4012)** Anders: the payment register lists the executed steps in execution order *(Superseded — reversed in the 2026-05 governance review.)*
Historical spreadsheet distributions remain archived and non-authoritative for the engine acceptance.

### Review entry 4019 — collateral analytics
Desk lead logged a routine observation for the collateral analytics during distribution review window 4019. Waterfall rehearsal against the prior period ran clean; no changes to engine parameters were approved.
No engine semantics changed in this entry; parameters remain as approved by the governance board.

### Review entry 4020 — paying agent
Desk lead logged a routine observation for the paying agent during distribution review window 4020. Remittance tiles for the period lagged during the servicer file refresh; attributed to report caching, not the engine.
Reviewers should reconcile behaviour questions against #WF governance decisions rather than desk chatter.

### Review entry 4021 — servicer collections desk
Desk lead logged a routine observation for the servicer collections desk during distribution review window 4021. Obligor concentration audit sampled cross-border accounts; no engine-relevant findings for this lane.
> **Distribution draft proposal (2026-02-11 - #WF-4018)** Anders: the residual step sweeps every remaining unit of cash to the residual payee; there is no cap and nothing is left unapplied *(Superseded — reversed in the 2026-05 governance review.)*
Thread archived; see the #WF decision entries for anything affecting engine behaviour.

### Review entry 4022 — cash manager
Desk lead logged a routine observation for the cash manager during distribution review window 4022. Synthetic remittance injection verified statement delivery to the noteholder distribution list.
Historical spreadsheet distributions remain archived and non-authoritative for the engine acceptance.

### Review entry 4023 — trustee reporting desk
Desk lead logged a routine observation for the trustee reporting desk during distribution review window 4023. Noise review: repeated servicer lines traced to a duplicated batch upload, suppressed at the source.
No engine semantics changed in this entry; parameters remain as approved by the governance board.

### Review entry 4024 — rating surveillance
Desk lead logged a routine observation for the rating surveillance during distribution review window 4024. Quarterly access recertification touched this lane; no engine-relevant configuration changed.
Reviewers should reconcile behaviour questions against #WF governance decisions rather than desk chatter.

### Review entry 4025 — deal administration
Desk lead logged a routine observation for the deal administration during distribution review window 4025. Capacity review noted rising line-item volume; thresholds unchanged outside the governance process.
> **Distribution draft proposal (2026-02-12 - #WF-4020)** Rosa: a coverage ratio is total collections measured against the whole note stack, quoted in basis points *(Superseded — reversed in the 2026-05 governance review.)*
Thread archived; see the #WF decision entries for anything affecting engine behaviour.

### Review entry 4026 — collateral analytics
Desk lead logged a routine observation for the collateral analytics during distribution review window 4026. Custodian reconciliation drill completed; settlement acknowledgment stayed within the governance window.
Historical spreadsheet distributions remain archived and non-authoritative for the engine acceptance.

### Review entry 4027 — paying agent
Desk lead logged a routine observation for the paying agent during distribution review window 4027. Change board reviewed stale exception approvals; owners pinged before the next distribution cycle.
No engine semantics changed in this entry; parameters remain as approved by the governance board.

### Review entry 4028 — servicer collections desk
Desk lead logged a routine observation for the servicer collections desk during distribution review window 4028. Vendor ticket on remittance retries closed; delivery within contractual budget.
> **Distribution draft proposal (2026-02-13 - #WF-4040)** Rosa: every executed step is registered, the residual step included *(Superseded — reversed in the 2026-05 governance review.)*
Reviewers should reconcile behaviour questions against #WF governance decisions rather than desk chatter.

### Review entry 4029 — cash manager
Desk lead logged a routine observation for the cash manager during distribution review window 4029. Waterfall rehearsal against the prior period ran clean; no changes to engine parameters were approved.
Thread archived; see the #WF decision entries for anything affecting engine behaviour.

### Review entry 4030 — trustee reporting desk
Desk lead logged a routine observation for the trustee reporting desk during distribution review window 4030. Remittance tiles for the period lagged during the servicer file refresh; attributed to report caching, not the engine.
Historical spreadsheet distributions remain archived and non-authoritative for the engine acceptance.

### Review entry 4031 — rating surveillance
Desk lead logged a routine observation for the rating surveillance during distribution review window 4031. Obligor concentration audit sampled cross-border accounts; no engine-relevant findings for this lane.
No engine semantics changed in this entry; parameters remain as approved by the governance board.

### Review entry 4032 — deal administration
Desk lead logged a routine observation for the deal administration during distribution review window 4032. Synthetic remittance injection verified statement delivery to the noteholder distribution list.
> **Distribution draft proposal (2026-02-14 - #WF-4044)** Anders: collections normalisation draft: the servicer reports every line already in settlement minor units, so the unit and currency tags on a line are informational; a reversal is carried as its own negative line appended to the settled set *(Superseded — reversed in the 2026-06 governance review.)*
Reviewers should reconcile behaviour questions against #WF governance decisions rather than desk chatter.

### Review entry 4033 — collateral analytics
Desk lead logged a routine observation for the collateral analytics during distribution review window 4033. Noise review: repeated servicer lines traced to a duplicated batch upload, suppressed at the source.
Thread archived; see the #WF decision entries for anything affecting engine behaviour.

### Review entry 4034 — paying agent
Desk lead logged a routine observation for the paying agent during distribution review window 4034. Quarterly access recertification touched this lane; no engine-relevant configuration changed.
Historical spreadsheet distributions remain archived and non-authoritative for the engine acceptance.

### Review entry 4035 — servicer collections desk
Desk lead logged a routine observation for the servicer collections desk during distribution review window 4035. Capacity review noted rising line-item volume; thresholds unchanged outside the governance process.
> **Governance decision (2026-03-05 - #WF-4109)** Rosa: the overcollateralisation test is evaluated on opening balances, before the senior principal step applies any cash *(Revised — see the 2026-05 governance review.)*
No engine semantics changed in this entry; parameters remain as approved by the governance board.

### Review entry 4036 — cash manager
Desk lead logged a routine observation for the cash manager during distribution review window 4036. Custodian reconciliation drill completed; settlement acknowledgment stayed within the governance window.
Reviewers should reconcile behaviour questions against #WF governance decisions rather than desk chatter.

### Review entry 4037 — trustee reporting desk
Desk lead logged a routine observation for the trustee reporting desk during distribution review window 4037. Change board reviewed stale exception approvals; owners pinged before the next distribution cycle.
Thread archived; see the #WF decision entries for anything affecting engine behaviour.

### Review entry 4038 — rating surveillance
Desk lead logged a routine observation for the rating surveillance during distribution review window 4038. Vendor ticket on remittance retries closed; delivery within contractual budget.
Historical spreadsheet distributions remain archived and non-authoritative for the engine acceptance.

### Review entry 4039 — deal administration
Desk lead logged a routine observation for the deal administration during distribution review window 4039. Waterfall rehearsal against the prior period ran clean; no changes to engine parameters were approved.
No engine semantics changed in this entry; parameters remain as approved by the governance board.

### Review entry 4040 — collateral analytics
Desk lead logged a routine observation for the collateral analytics during distribution review window 4040. Remittance tiles for the period lagged during the servicer file refresh; attributed to report caching, not the engine.
> **Governance decision (2026-03-06 - #WF-4115)** Priya: trigger effects interim: a breached interest coverage test simply skips the subordinate interest steps for the period and diverts nothing; a breached overcollateralisation test skips the subordinate principal steps *(Revised — see the 2026-05 governance review.)*
Reviewers should reconcile behaviour questions against #WF governance decisions rather than desk chatter.

### Review entry 4041 — paying agent
Desk lead logged a routine observation for the paying agent during distribution review window 4041. Obligor concentration audit sampled cross-border accounts; no engine-relevant findings for this lane.
Thread archived; see the #WF decision entries for anything affecting engine behaviour.

### Review entry 4042 — servicer collections desk
Desk lead logged a routine observation for the servicer collections desk during distribution review window 4042. Synthetic remittance injection verified statement delivery to the noteholder distribution list.
Historical spreadsheet distributions remain archived and non-authoritative for the engine acceptance.

### Review entry 4043 — cash manager
Desk lead logged a routine observation for the cash manager during distribution review window 4043. Noise review: repeated servicer lines traced to a duplicated batch upload, suppressed at the source.
> **Governance decision (2026-03-07 - #WF-4124)** Priya: baseline interim: the deferred subordinate interest cap is 1800000 minor units and the residual cap is 2750000 minor units *(Revised — see the 2026-05 governance review.)*
No engine semantics changed in this entry; parameters remain as approved by the governance board.

### Review entry 4044 — trustee reporting desk
Desk lead logged a routine observation for the trustee reporting desk during distribution review window 4044. Quarterly access recertification touched this lane; no engine-relevant configuration changed.
Reviewers should reconcile behaviour questions against #WF governance decisions rather than desk chatter.

### Review entry 4045 — rating surveillance
Desk lead logged a routine observation for the rating surveillance during distribution review window 4045. Capacity review noted rising line-item volume; thresholds unchanged outside the governance process.
Thread archived; see the #WF decision entries for anything affecting engine behaviour.

### Review entry 4046 — deal administration
Desk lead logged a routine observation for the deal administration during distribution review window 4046. Custodian reconciliation drill completed; settlement acknowledgment stayed within the governance window.
Historical spreadsheet distributions remain archived and non-authoritative for the engine acceptance.

### Review entry 4047 — collateral analytics
Desk lead logged a routine observation for the collateral analytics during distribution review window 4047. Change board reviewed stale exception approvals; owners pinged before the next distribution cycle.
> **Governance decision (2026-03-08 - #WF-4048)** Yusuf: the three max_* summary fields are maxima over every executed step *(Revised — see the 2026-05 governance review.)*
No engine semantics changed in this entry; parameters remain as approved by the governance board.

### Review entry 4048 — paying agent
Desk lead logged a routine observation for the paying agent during distribution review window 4048. Vendor ticket on remittance retries closed; delivery within contractual budget.
Reviewers should reconcile behaviour questions against #WF governance decisions rather than desk chatter.

### Review entry 4049 — servicer collections desk
Desk lead logged a routine observation for the servicer collections desk during distribution review window 4049. Waterfall rehearsal against the prior period ran clean; no changes to engine parameters were approved.
Thread archived; see the #WF decision entries for anything affecting engine behaviour.

### Review entry 4050 — cash manager
Desk lead logged a routine observation for the cash manager during distribution review window 4050. Remittance tiles for the period lagged during the servicer file refresh; attributed to report caching, not the engine.
> **Governance decision (2026-05-02 - #WF-4101)** Yusuf: settled-collections canonicalization: item_id has its internal whitespace collapsed; category and obligor go through str(...).strip().lower() (empty -> 'unknown'); amount_minor is coerced with int(str(value).strip()), else int(float(...)), else 0, and an item whose amount_minor is not strictly positive is dropped before anything else; the engine reads the `items` array and recomputes the category subtotals from it rather than trusting the file's own totals block; items are taken in category ascending then item_id ascending order
Historical spreadsheet distributions remain archived and non-authoritative for the engine acceptance.

### Review entry 4051 — trustee reporting desk
Desk lead logged a routine observation for the trustee reporting desk during distribution review window 4051. Obligor concentration audit sampled cross-border accounts; no engine-relevant findings for this lane.
> **Governance decision (2026-03-09 - #WF-4009)** Priya: collections reconciliation interim: a foreign-currency line converts by DIVIDING its reported amount by the quoted rate; a reversal larger than the line it names leaves a negative item in the settled set; an item whose category the control totals do not name still settles at face value *(Revised — see the 2026-06 governance review.)*
No engine semantics changed in this entry; parameters remain as approved by the governance board.

### Review entry 4052 — rating surveillance
Desk lead logged a routine observation for the rating surveillance during distribution review window 4052. Synthetic remittance injection verified statement delivery to the noteholder distribution list.
Reviewers should reconcile behaviour questions against #WF governance decisions rather than desk chatter.

### Review entry 4053 — deal administration
Desk lead logged a routine observation for the deal administration during distribution review window 4053. Noise review: repeated servicer lines traced to a duplicated batch upload, suppressed at the source.
Thread archived; see the #WF decision entries for anything affecting engine behaviour.

### Review entry 4054 — collateral analytics
Desk lead logged a routine observation for the collateral analytics during distribution review window 4054. Quarterly access recertification touched this lane; no engine-relevant configuration changed.
> **Governance decision (2026-05-03 - #WF-4102)** Yusuf: tranche register normalization: tranche_id via str(...).strip().upper(); class via str(...).strip().lower(); every numeric field coerced to int; a row whose coupon_bps falls outside 1..3000 is discarded; a row whose balance_minor and both carryforward fields are all non-positive is a redeemed tranche and is discarded; duplicate tranche_id rows collapse to the one with the GREATEST balance_minor; survivors are ordered by seniority ascending then tranche_id ascending. A tranche whose class is `subordinate` is a subordinate tranche and every other class is senior
Historical spreadsheet distributions remain archived and non-authoritative for the engine acceptance.

### Review entry 4055 — paying agent
Desk lead logged a routine observation for the paying agent during distribution review window 4055. Capacity review noted rising line-item volume; thresholds unchanged outside the governance process.
No engine semantics changed in this entry; parameters remain as approved by the governance board.

### Review entry 4056 — servicer collections desk
Desk lead logged a routine observation for the servicer collections desk during distribution review window 4056. Custodian reconciliation drill completed; settlement acknowledgment stayed within the governance window.
Reviewers should reconcile behaviour questions against #WF governance decisions rather than desk chatter.

### Review entry 4057 — cash manager
Desk lead logged a routine observation for the cash manager during distribution review window 4057. Change board reviewed stale exception approvals; owners pinged before the next distribution cycle.
Thread archived; see the #WF decision entries for anything affecting engine behaviour.

### Review entry 4058 — trustee reporting desk
Desk lead logged a routine observation for the trustee reporting desk during distribution review window 4058. Vendor ticket on remittance retries closed; delivery within contractual budget.
> **Governance decision (2026-05-03 - #WF-4108)** Lena: principal allocation, final, superseding #WF-4008: the senior principal step is SEQUENTIAL, not pro rata. Walk the senior tranches in seniority ascending order and give each the smaller of its principal due and the cash still in hand before moving to the next, so a lower-ranking senior tranche receives nothing until the tranche above it has taken its full due. Each payment reduces that tranche's balance immediately, and the same sequential rule governs the subordinate principal steps
Historical spreadsheet distributions remain archived and non-authoritative for the engine acceptance.

### Review entry 4059 — rating surveillance
Desk lead logged a routine observation for the rating surveillance during distribution review window 4059. Waterfall rehearsal against the prior period ran clean; no changes to engine parameters were approved.
No engine semantics changed in this entry; parameters remain as approved by the governance board.

### Review entry 4060 — deal administration
Desk lead logged a routine observation for the deal administration during distribution review window 4060. Remittance tiles for the period lagged during the servicer file refresh; attributed to report caching, not the engine.
Reviewers should reconcile behaviour questions against #WF governance decisions rather than desk chatter.

### Review entry 4061 — collateral analytics
Desk lead logged a routine observation for the collateral analytics during distribution review window 4061. Obligor concentration audit sampled cross-border accounts; no engine-relevant findings for this lane.
Thread archived; see the #WF decision entries for anything affecting engine behaviour.

### Review entry 4062 — paying agent
Desk lead logged a routine observation for the paying agent during distribution review window 4062. Synthetic remittance injection verified statement delivery to the noteholder distribution list.
> **Governance decision (2026-05-04 - #WF-4104)** Lena: the distribution order, final; this supersedes #WF-4004. Available funds are the sum of the settled item amounts and they cascade through the steps in this order: (1) the deal fees in fee_id ascending order; (2) senior interest, seniority ascending; (3) subordinate interest, seniority ascending, but only while the interest coverage test holds; (4) senior principal, seniority ascending; (5) a diverted turbo redemption, only when the interest coverage test is breached; (6) subordinate principal, seniority ascending; (7) the deferred subordinate interest steps, which run HERE rather than in position 3 when and only when the interest coverage test is breached; (8) the residual step. Each step takes the smaller of what it is owed and the cash still in hand, and the balance of its due is its shortfall. Both coverage tests are evaluated exactly once per period, at the points named in #WF-4110 and #WF-4116
Historical spreadsheet distributions remain archived and non-authoritative for the engine acceptance.

### Review entry 4063 — servicer collections desk
Desk lead logged a routine observation for the servicer collections desk during distribution review window 4063. Noise review: repeated servicer lines traced to a duplicated batch upload, suppressed at the source.
No engine semantics changed in this entry; parameters remain as approved by the governance board.

### Review entry 4064 — cash manager
Desk lead logged a routine observation for the cash manager during distribution review window 4064. Quarterly access recertification touched this lane; no engine-relevant configuration changed.
Reviewers should reconcile behaviour questions against #WF governance decisions rather than desk chatter.

### Review entry 4065 — trustee reporting desk
Desk lead logged a routine observation for the trustee reporting desk during distribution review window 4065. Capacity review noted rising line-item volume; thresholds unchanged outside the governance process.
Thread archived; see the #WF decision entries for anything affecting engine behaviour.

### Review entry 4066 — rating surveillance
Desk lead logged a routine observation for the rating surveillance during distribution review window 4066. Custodian reconciliation drill completed; settlement acknowledgment stayed within the governance window.
> **Governance decision (2026-05-04 - #WF-4106)** Lena: accrual, final, superseding #WF-4006. A period's interest accrues on a 30/360 basis. For a senior tranche senior_accrual_base = balance_minor * coupon_bps * period_days and the accrual is senior_accrual_base // 3600000; for a subordinate tranche the same product sub_accrual_base = balance_minor * coupon_bps * period_days accrues as ceil(sub_accrual_base / 3600000). The two directions differ by class and are not uniform. A tranche's interest due is its accrual plus its interest_carryforward_minor; its principal due is min(scheduled_principal_minor + principal_carryforward_minor, balance_minor). A fee's due is flat_minor plus ceil(servicing_fee_base / 10000) where servicing_fee_base = pool_balance_minor * basis_bps. In integer arithmetic ceil(x/n) is -(-x // n). ROUNDING: senior_accrual_base // 3600000 = FLOOR. ROUNDING: sub_accrual_base // 3600000 = CEIL. ROUNDING: servicing_fee_base // 10000 = CEIL
Historical spreadsheet distributions remain archived and non-authoritative for the engine acceptance.

### Review entry 4067 — deal administration
Desk lead logged a routine observation for the deal administration during distribution review window 4067. Change board reviewed stale exception approvals; owners pinged before the next distribution cycle.
No engine semantics changed in this entry; parameters remain as approved by the governance board.

### Review entry 4068 — collateral analytics
Desk lead logged a routine observation for the collateral analytics during distribution review window 4068. Vendor ticket on remittance retries closed; delivery within contractual budget.
Reviewers should reconcile behaviour questions against #WF governance decisions rather than desk chatter.

### Review entry 4069 — paying agent
Desk lead logged a routine observation for the paying agent during distribution review window 4069. Waterfall rehearsal against the prior period ran clean; no changes to engine parameters were approved.
Thread archived; see the #WF decision entries for anything affecting engine behaviour.

### Review entry 4070 — servicer collections desk
Desk lead logged a routine observation for the servicer collections desk during distribution review window 4070. Remittance tiles for the period lagged during the servicer file refresh; attributed to report caching, not the engine.
> **Governance decision (2026-05-05 - #WF-4110)** Marek: interest coverage test, final, superseding #WF-4020. interest_eligible is the sum of the settled category subtotals for the categories `recovery` and `scheduled_interest` and for no other category. ic_bps = interest_eligible * 10000 // senior_interest_due, where senior_interest_due is the sum of the senior tranches' interest due. The test is breached when ic_bps is strictly below the resolved ic_trigger_bps; when senior_interest_due is zero, ic_bps is 0 and the test is not breached. It is measured from the settled collections and the dues alone, so no payment made earlier in the cascade moves it. ROUNDING: ic_bps = FLOOR
Historical spreadsheet distributions remain archived and non-authoritative for the engine acceptance.

### Review entry 4071 — cash manager
Desk lead logged a routine observation for the cash manager during distribution review window 4071. Obligor concentration audit sampled cross-border accounts; no engine-relevant findings for this lane.
No engine semantics changed in this entry; parameters remain as approved by the governance board.

### Review entry 4072 — trustee reporting desk
Desk lead logged a routine observation for the trustee reporting desk during distribution review window 4072. Synthetic remittance injection verified statement delivery to the noteholder distribution list.
Reviewers should reconcile behaviour questions against #WF governance decisions rather than desk chatter.

### Review entry 4073 — rating surveillance
Desk lead logged a routine observation for the rating surveillance during distribution review window 4073. Noise review: repeated servicer lines traced to a duplicated batch upload, suppressed at the source.
Thread archived; see the #WF decision entries for anything affecting engine behaviour.

### Review entry 4074 — deal administration
Desk lead logged a routine observation for the deal administration during distribution review window 4074. Quarterly access recertification touched this lane; no engine-relevant configuration changed.
> **Governance decision (2026-05-05 - #WF-4112)** Marek: breached interest coverage, final, superseding #WF-4115 on effect. Two things happen and both are required. First, the subordinate interest steps do not run in position 3: they are DEFERRED to run after the subordinate principal steps, and a deferred step pays at most the resolved deferred_sub_cap_minor however much cash is in hand - the tranche's full interest due remains its due, so the capped balance is a shortfall. Second, immediately after the senior principal steps a turbo redemption diverts cash to the senior notes: the diversion budget is the smaller of the cash in hand and the resolved divert_cap_minor, and it is applied to the senior tranches in seniority ascending order, each taking the smaller of the budget still unspent and its own remaining balance and reducing that balance by what it takes. A tranche allocated nothing emits no step, and a turbo step's due equals its allocation so it never carries a shortfall. Diverted steps carry the trigger flag `ic_diverted` and the deferred subordinate interest steps carry `ic_deferred`
Historical spreadsheet distributions remain archived and non-authoritative for the engine acceptance.

### Review entry 4075 — collateral analytics
Desk lead logged a routine observation for the collateral analytics during distribution review window 4075. Capacity review noted rising line-item volume; thresholds unchanged outside the governance process.
No engine semantics changed in this entry; parameters remain as approved by the governance board.

### Review entry 4076 — paying agent
Desk lead logged a routine observation for the paying agent during distribution review window 4076. Custodian reconciliation drill completed; settlement acknowledgment stayed within the governance window.
Reviewers should reconcile behaviour questions against #WF governance decisions rather than desk chatter.

### Review entry 4077 — servicer collections desk
Desk lead logged a routine observation for the servicer collections desk during distribution review window 4077. Change board reviewed stale exception approvals; owners pinged before the next distribution cycle.
Thread archived; see the #WF decision entries for anything affecting engine behaviour.

### Review entry 4078 — cash manager
Desk lead logged a routine observation for the cash manager during distribution review window 4078. Vendor ticket on remittance retries closed; delivery within contractual budget.
> **Governance decision (2026-05-06 - #WF-4116)** Yusuf: overcollateralisation test, final; this supersedes the #WF-4109 interim on timing. The test is evaluated AFTER the senior principal steps and after any turbo redemption, on post-payment figures and not on opening balances: pool_balance_after = pool_balance_minor less every unit of principal paid so far in the period, senior principal and turbo alike; senior_balance_after = the sum of the senior tranches' balances as they stand after those steps; oc_bps = pool_balance_after * 10000 // senior_balance_after. The test is breached when oc_bps is strictly below the resolved oc_trigger_bps; when senior_balance_after is zero, oc_bps is 0 and the test is not breached. On a deleveraging period the pre-payment reading gives a different verdict, and that reading is wrong. ROUNDING: oc_bps = FLOOR
Historical spreadsheet distributions remain archived and non-authoritative for the engine acceptance.

### Review entry 4079 — trustee reporting desk
Desk lead logged a routine observation for the trustee reporting desk during distribution review window 4079. Waterfall rehearsal against the prior period ran clean; no changes to engine parameters were approved.
No engine semantics changed in this entry; parameters remain as approved by the governance board.

### Review entry 4080 — rating surveillance
Desk lead logged a routine observation for the rating surveillance during distribution review window 4080. Remittance tiles for the period lagged during the servicer file refresh; attributed to report caching, not the engine.
Reviewers should reconcile behaviour questions against #WF governance decisions rather than desk chatter.

### Review entry 4081 — deal administration
Desk lead logged a routine observation for the deal administration during distribution review window 4081. Obligor concentration audit sampled cross-border accounts; no engine-relevant findings for this lane.
Thread archived; see the #WF decision entries for anything affecting engine behaviour.

### Review entry 4082 — collateral analytics
Desk lead logged a routine observation for the collateral analytics during distribution review window 4082. Synthetic remittance injection verified statement delivery to the noteholder distribution list.
> **Governance decision (2026-05-08 - #WF-4118)** Priya: breached overcollateralisation, final. When the test is breached the subordinate principal steps still execute but may pay NOTHING: each keeps its full principal due, pays zero, carries the whole due as its shortfall and takes the trigger flag `oc_skipped`. The residual step of the same period is capped at zero and takes the trigger flag `oc_capped`. When the test holds, the subordinate principal steps pay normally and neither flag is set
Historical spreadsheet distributions remain archived and non-authoritative for the engine acceptance.

### Review entry 4083 — paying agent
Desk lead logged a routine observation for the paying agent during distribution review window 4083. Noise review: repeated servicer lines traced to a duplicated batch upload, suppressed at the source.
No engine semantics changed in this entry; parameters remain as approved by the governance board.

### Review entry 4084 — servicer collections desk
Desk lead logged a routine observation for the servicer collections desk during distribution review window 4084. Quarterly access recertification touched this lane; no engine-relevant configuration changed.
Reviewers should reconcile behaviour questions against #WF governance decisions rather than desk chatter.

### Review entry 4085 — cash manager
Desk lead logged a routine observation for the cash manager during distribution review window 4085. Capacity review noted rising line-item volume; thresholds unchanged outside the governance process.
Thread archived; see the #WF decision entries for anything affecting engine behaviour.

### Review entry 4086 — trustee reporting desk
Desk lead logged a routine observation for the trustee reporting desk during distribution review window 4086. Custodian reconciliation drill completed; settlement acknowledgment stayed within the governance window.
> **Governance decision (2026-05-07 - #WF-4120)** Lena: carryforward accrual, final, superseding #WF-4010. A step with no shortfall carries nothing forward. Unpaid INTEREST compounds: for a senior interest step senior_carry_interest = shortfall_minor * coupon_bps and carryforward_out_minor = shortfall_minor + ceil(senior_carry_interest / 10000); for a subordinate interest step sub_carry_interest = shortfall_minor * (coupon_bps + the resolved sub_penalty_bps for that tranche) and carryforward_out_minor = shortfall_minor + sub_carry_interest // 10000. Unpaid PRINCIPAL and unpaid fees do not compound: carryforward_out_minor is exactly the shortfall. The two interest legs round in opposite directions and each direction is fixed here independently of the other. ROUNDING: senior_carry_interest // 10000 = CEIL. ROUNDING: sub_carry_interest // 10000 = FLOOR
Historical spreadsheet distributions remain archived and non-authoritative for the engine acceptance.

### Review entry 4087 — rating surveillance
Desk lead logged a routine observation for the rating surveillance during distribution review window 4087. Change board reviewed stale exception approvals; owners pinged before the next distribution cycle.
No engine semantics changed in this entry; parameters remain as approved by the governance board.

### Review entry 4088 — deal administration
Desk lead logged a routine observation for the deal administration during distribution review window 4088. Vendor ticket on remittance retries closed; delivery within contractual budget.
Reviewers should reconcile behaviour questions against #WF governance decisions rather than desk chatter.

### Review entry 4089 — collateral analytics
Desk lead logged a routine observation for the collateral analytics during distribution review window 4089. Waterfall rehearsal against the prior period ran clean; no changes to engine parameters were approved.
Thread archived; see the #WF decision entries for anything affecting engine behaviour.

### Review entry 4090 — paying agent
Desk lead logged a routine observation for the paying agent during distribution review window 4090. Remittance tiles for the period lagged during the servicer file refresh; attributed to report caching, not the engine.
> **Governance decision (2026-05-09 - #WF-4140)** Marek: register admission, final, superseding #WF-4040. The residual step is never registered; every other step kind may be. A step is registered iff its paid_minor is at least the resolved register_min_minor for its payee OR its shortfall_minor is at least the resolved register_shortfall_min_minor for its payee, both inclusive. A fee step's payee is its fee_id, which no tranche override names, so a fee resolves the default layer
Historical spreadsheet distributions remain archived and non-authoritative for the engine acceptance.

### Review entry 4091 — servicer collections desk
Desk lead logged a routine observation for the servicer collections desk during distribution review window 4091. Obligor concentration audit sampled cross-border accounts; no engine-relevant findings for this lane.
No engine semantics changed in this entry; parameters remain as approved by the governance board.

### Review entry 4092 — cash manager
Desk lead logged a routine observation for the cash manager during distribution review window 4092. Synthetic remittance injection verified statement delivery to the noteholder distribution list.
Reviewers should reconcile behaviour questions against #WF governance decisions rather than desk chatter.

### Review entry 4093 — trustee reporting desk
Desk lead logged a routine observation for the trustee reporting desk during distribution review window 4093. Noise review: repeated servicer lines traced to a duplicated batch upload, suppressed at the source.
Thread archived; see the #WF decision entries for anything affecting engine behaviour.

### Review entry 4094 — rating surveillance
Desk lead logged a routine observation for the rating surveillance during distribution review window 4094. Quarterly access recertification touched this lane; no engine-relevant configuration changed.
> **Governance decision (2026-05-10 - #WF-4145)** Yusuf: register ordering, final, superseding #WF-4012, strictly in sequence: shortfall_minor descending; then paid_minor descending; then due_minor descending; then step_kind ascending; then payee_id ascending; then step_index ascending. The register is a materiality schedule and deliberately does not follow execution order
Historical spreadsheet distributions remain archived and non-authoritative for the engine acceptance.

### Review entry 4095 — deal administration
Desk lead logged a routine observation for the deal administration during distribution review window 4095. Capacity review noted rising line-item volume; thresholds unchanged outside the governance process.
No engine semantics changed in this entry; parameters remain as approved by the governance board.

### Review entry 4096 — collateral analytics
Desk lead logged a routine observation for the collateral analytics during distribution review window 4096. Custodian reconciliation drill completed; settlement acknowledgment stayed within the governance window.
Reviewers should reconcile behaviour questions against #WF governance decisions rather than desk chatter.

### Review entry 4097 — paying agent
Desk lead logged a routine observation for the paying agent during distribution review window 4097. Change board reviewed stale exception approvals; owners pinged before the next distribution cycle.
Thread archived; see the #WF decision entries for anything affecting engine behaviour.

### Review entry 4098 — servicer collections desk
Desk lead logged a routine observation for the servicer collections desk during distribution review window 4098. Vendor ticket on remittance retries closed; delivery within contractual budget.
> **Governance decision (2026-05-24 - #WF-4146)** Marek: payee capacity cap: at most TWO register rows per payee. The cap is a FINAL pass over the fully ordered register, not applied during admission and not per payee before ordering: admit every eligible step, apply the #WF-4145 ordering, then walk the ordered register from the top keeping the first two rows of each payee and discarding the rest. Which rows survive depends on the global order, so a payee's third-ranked step is dropped even where it outranks a retained row of another payee. Discarded rows contribute to no register-derived summary field
Historical spreadsheet distributions remain archived and non-authoritative for the engine acceptance.

### Review entry 4099 — cash manager
Desk lead logged a routine observation for the cash manager during distribution review window 4099. Waterfall rehearsal against the prior period ran clean; no changes to engine parameters were approved.
No engine semantics changed in this entry; parameters remain as approved by the governance board.

### Review entry 4100 — trustee reporting desk
Desk lead logged a routine observation for the trustee reporting desk during distribution review window 4100. Remittance tiles for the period lagged during the servicer file refresh; attributed to report caching, not the engine.
Reviewers should reconcile behaviour questions against #WF governance decisions rather than desk chatter.

### Review entry 4101 — rating surveillance
Desk lead logged a routine observation for the rating surveillance during distribution review window 4101. Obligor concentration audit sampled cross-border accounts; no engine-relevant findings for this lane.
Thread archived; see the #WF decision entries for anything affecting engine behaviour.

### Review entry 4102 — deal administration
Desk lead logged a routine observation for the deal administration during distribution review window 4102. Synthetic remittance injection verified statement delivery to the noteholder distribution list.
> **Governance decision (2026-05-10 - #WF-4148)** Yusuf: summary aggregation domains, final, revising #WF-4048: max_paid_minor and max_shortfall_minor are maxima over the FINAL registered rows only, using 0 when the register is empty. Only max_carryforward_out_minor is taken over EVERY executed step, using 0 when there are no steps. step_kind_counts counts EVERY executed step, registered or not, and always enumerates all seven kinds
Historical spreadsheet distributions remain archived and non-authoritative for the engine acceptance.

### Review entry 4103 — collateral analytics
Desk lead logged a routine observation for the collateral analytics during distribution review window 4103. Noise review: repeated servicer lines traced to a duplicated batch upload, suppressed at the source.
No engine semantics changed in this entry; parameters remain as approved by the governance board.

### Review entry 4104 — paying agent
Desk lead logged a routine observation for the paying agent during distribution review window 4104. Quarterly access recertification touched this lane; no engine-relevant configuration changed.
Reviewers should reconcile behaviour questions against #WF governance decisions rather than desk chatter.

### Review entry 4105 — servicer collections desk
Desk lead logged a routine observation for the servicer collections desk during distribution review window 4105. Capacity review noted rising line-item volume; thresholds unchanged outside the governance process.
Thread archived; see the #WF decision entries for anything affecting engine behaviour.

### Review entry 4106 — cash manager
Desk lead logged a routine observation for the cash manager during distribution review window 4106. Custodian reconciliation drill completed; settlement acknowledgment stayed within the governance window.
> **Governance decision (2026-05-18 - #WF-4150)** Priya: policy baseline (read from /app/data/waterfall_policy.json at that fixed absolute path; --input never relocates it). Any field the policy file omits keeps its baseline: ic_trigger_bps = 30340; oc_trigger_bps = 12000; divert_cap_minor = 22680000000; residual_cap_minor = 11340000000; deferred_sub_cap_minor = 6804000000; register_min_minor = 189000000; register_shortfall_min_minor = 7560; sub_penalty_bps = 200. These baselines revise the interim figures quoted in #WF-4124
Historical spreadsheet distributions remain archived and non-authoritative for the engine acceptance.

### Review entry 4107 — trustee reporting desk
Desk lead logged a routine observation for the trustee reporting desk during distribution review window 4107. Change board reviewed stale exception approvals; owners pinged before the next distribution cycle.
No engine semantics changed in this entry; parameters remain as approved by the governance board.

### Review entry 4108 — rating surveillance
Desk lead logged a routine observation for the rating surveillance during distribution review window 4108. Vendor ticket on remittance retries closed; delivery within contractual budget.
Reviewers should reconcile behaviour questions against #WF governance decisions rather than desk chatter.

### Review entry 4109 — deal administration
Desk lead logged a routine observation for the deal administration during distribution review window 4109. Waterfall rehearsal against the prior period ran clean; no changes to engine parameters were approved.
Thread archived; see the #WF decision entries for anything affecting engine behaviour.

### Review entry 4110 — collateral analytics
Desk lead logged a routine observation for the collateral analytics during distribution review window 4110. Remittance tiles for the period lagged during the servicer file refresh; attributed to report caching, not the engine.
> **Governance decision (2026-05-18 - #WF-4152)** Priya: policy resolution, per payee, in three layers: start from the #WF-4150 baseline; overlay every field the policy file's `default` object supplies (it need not be complete - an omitted field keeps its baseline); then overlay every field that payee's entry in `tranche_overrides` supplies (an override names only the fields it changes and inherits the rest). Coerce every policy value to int. The deal-level knobs - ic_trigger_bps, oc_trigger_bps, divert_cap_minor, residual_cap_minor and deferred_sub_cap_minor - are taken from the resolved `default` layer and are never read from a tranche override
Historical spreadsheet distributions remain archived and non-authoritative for the engine acceptance.

### Review entry 4111 — paying agent
Desk lead logged a routine observation for the paying agent during distribution review window 4111. Obligor concentration audit sampled cross-border accounts; no engine-relevant findings for this lane.
No engine semantics changed in this entry; parameters remain as approved by the governance board.

### Review entry 4112 — servicer collections desk
Desk lead logged a routine observation for the servicer collections desk during distribution review window 4112. Synthetic remittance injection verified statement delivery to the noteholder distribution list.
Reviewers should reconcile behaviour questions against #WF governance decisions rather than desk chatter.

### Review entry 4113 — cash manager
Desk lead logged a routine observation for the cash manager during distribution review window 4113. Noise review: repeated servicer lines traced to a duplicated batch upload, suppressed at the source.
Thread archived; see the #WF decision entries for anything affecting engine behaviour.

### Review entry 4114 — trustee reporting desk
Desk lead logged a routine observation for the trustee reporting desk during distribution review window 4114. Quarterly access recertification touched this lane; no engine-relevant configuration changed.
> **Governance decision (2026-05-28 - #WF-4160)** Yusuf: residual step, final, superseding #WF-4018: the residual step pays the smaller of the cash still in hand and the resolved residual_cap_minor to the residual payee named in the tranche terms, so its due equals what it pays and it never carries a shortfall. Whatever is still in hand once it finishes is reported as unapplied_funds_minor and retained in the collection account rather than swept
Historical spreadsheet distributions remain archived and non-authoritative for the engine acceptance.

### Review entry 4115 — rating surveillance
Desk lead logged a routine observation for the rating surveillance during distribution review window 4115. Capacity review noted rising line-item volume; thresholds unchanged outside the governance process.
No engine semantics changed in this entry; parameters remain as approved by the governance board.

### Review entry 4116 — deal administration
Desk lead logged a routine observation for the deal administration during distribution review window 4116. Custodian reconciliation drill completed; settlement acknowledgment stayed within the governance window.
Reviewers should reconcile behaviour questions against #WF governance decisions rather than desk chatter.

### Review entry 4117 — collateral analytics
Desk lead logged a routine observation for the collateral analytics during distribution review window 4117. Change board reviewed stale exception approvals; owners pinged before the next distribution cycle.
Thread archived; see the #WF decision entries for anything affecting engine behaviour.

### Review entry 4118 — paying agent
Desk lead logged a routine observation for the paying agent during distribution review window 4118. Vendor ticket on remittance retries closed; delivery within contractual budget.
Historical spreadsheet distributions remain archived and non-authoritative for the engine acceptance.

### Review entry 4119 — servicer collections desk
Desk lead logged a routine observation for the servicer collections desk during distribution review window 4119. Waterfall rehearsal against the prior period ran clean; no changes to engine parameters were approved.
No engine semantics changed in this entry; parameters remain as approved by the governance board.

### Review entry 4120 — cash manager
Desk lead logged a routine observation for the cash manager during distribution review window 4120. Remittance tiles for the period lagged during the servicer file refresh; attributed to report caching, not the engine.
Reviewers should reconcile behaviour questions against #WF governance decisions rather than desk chatter.

### Review entry 4121 — trustee reporting desk
Desk lead logged a routine observation for the trustee reporting desk during distribution review window 4121. Obligor concentration audit sampled cross-border accounts; no engine-relevant findings for this lane.
Thread archived; see the #WF decision entries for anything affecting engine behaviour.

### Review entry 4122 — rating surveillance
Desk lead logged a routine observation for the rating surveillance during distribution review window 4122. Synthetic remittance injection verified statement delivery to the noteholder distribution list.
> **Governance decision (2026-06-02 - #WF-4170)** Lena: authoritative collections reconciliation, final - this supersedes the #WF-4044 draft, revises the #WF-4009 interim, and it runs BEFORE any distribution. `/app/data/settled_collections.json` ships holding the servicer's unreconciled draft and is not authoritative; it must be rebuilt from `/app/data/collections.json` and `/app/data/control_totals.json`. Normalise every line of the raw file to settlement minor units in this order. A line whose `unit` is `minor` is already in the minor units of its own currency; a line whose `unit` is `major` is a whole-currency amount and is scaled by exactly one hundred, its two decimal places read as minor units - the unit and currency tags govern and are not informational, revising #WF-4044. Then, where the line's `currency` differs from the control file's `settlement_currency`, MULTIPLY by that currency's rate in `fx_rates_bps` and floor: fx_converted = amount * rate_bps and the settled amount is fx_converted // 10000. Dividing by the rate, as the #WF-4009 interim had it, is the wrong direction. Next apply the reversals: an entry whose `entry_type` is `reversal` names in `reverses` the line it reverses, and its normalised amount is SUBTRACTED from that line's normalised amount, floored at zero; the reversal contributes no line of its own, revising #WF-4044, and a reversal naming a line the file does not carry contributes nothing at all. A line reduced to zero, and any line that is not strictly positive, drops out. Then drop every remaining line whose `category` the control file's `category_totals_minor` does not name: that category is not settled this period and its collections are not available to the waterfall, revising #WF-4009. Order the survivors by category ascending then item_id ascending, carrying exactly item_id, category, obligor and amount_minor, and write them under `items` alongside the `period`, the `settlement_currency` and a `category_totals_minor` block keyed by the surviving categories in ascending order. The reconciled per-category totals MUST equal the control file's `category_totals_minor` exactly; a set that does not tie has been normalised wrongly, and every step of the cascade below it is wrong. ROUNDING: fx_converted // 10000 = FLOOR
Historical spreadsheet distributions remain archived and non-authoritative for the engine acceptance.

### Review entry 4123 — deal administration
Desk lead logged a routine observation for the deal administration during distribution review window 4123. Noise review: repeated servicer lines traced to a duplicated batch upload, suppressed at the source.
No engine semantics changed in this entry; parameters remain as approved by the governance board.

### Review entry 4124 — collateral analytics
Desk lead logged a routine observation for the collateral analytics during distribution review window 4124. Quarterly access recertification touched this lane; no engine-relevant configuration changed.
Reviewers should reconcile behaviour questions against #WF governance decisions rather than desk chatter.

### Review entry 4125 — paying agent
Desk lead logged a routine observation for the paying agent during distribution review window 4125. Capacity review noted rising line-item volume; thresholds unchanged outside the governance process.
Thread archived; see the #WF decision entries for anything affecting engine behaviour.

### Review entry 4126 — servicer collections desk
Desk lead logged a routine observation for the servicer collections desk during distribution review window 4126. Custodian reconciliation drill completed; settlement acknowledgment stayed within the governance window.
Historical spreadsheet distributions remain archived and non-authoritative for the engine acceptance.

### Review entry 4127 — cash manager
Desk lead logged a routine observation for the cash manager during distribution review window 4127. Change board reviewed stale exception approvals; owners pinged before the next distribution cycle.
No engine semantics changed in this entry; parameters remain as approved by the governance board.


> **Governance decision (2026-06-04 - #WF-7172)** Lena: obligor concentration cap, final. Before anything is distributed, total the settled collections of each obligor and take each obligor's share of the settled pool as floor(obligor_total x 10000 / pool_total) basis points. An obligor whose share exceeds the resolved concentration_cap_bps contributes only up to its allowance, floor(cap_bps x pool_total / 10000); everything above that is EXCLUDED from the distributable pool and never reaches a tranche. Shares are measured ONCE against the pool before any exclusion and are NOT recomputed after it, so removing an obligor's excess never lifts another obligor over the cap. The summary carries excluded_concentration_minor as the total excluded and max_obligor_concentration_bps as the largest share measured. This settles the #WF-7120 draft, which capped per category rather than per obligor
