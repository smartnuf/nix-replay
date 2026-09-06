# Evidence change workflow

This workflow translates the D2 evidence rules into repeatable checks for
source, claim, and derived-research changes. It supplements the approved
research plan; it does not change project authority or advance a gate.

The repository is the durable record. A conversation, review summary, or
successful automated check is evidence about the work, not a substitute for
the records affected by it.

## Plan, specify, execute, review

### 1. Plan the impact surface

Before editing, identify the question being answered and the records and views
that may be affected. Search for every changed source or claim ID across the
repository. Include indirect consequences: a new qualification can affect a
claim, chronology entry, credit statement, concept note, and intended media
use even when their wording does not cite the changed record directly.

Classify the proposed work as one or more of:

- source registration or reassessment;
- claim addition, replacement, retirement, or reassessment;
- chronology or people-map change;
- architectural, ecosystem, or boundary analysis;
- experiment specification or result;
- rights or intended-use assessment; or
- derived synthesis or other narrative prose.

Stop for a decision if the change reveals a material contradiction, unsafe
experiment, unresolved rights dependency, or premise that would reopen an
approved gate.

### 2. Specify the change

State the bounded question, expected records, affected derived views, and
checks that will show the change is complete. For an experiment, use the
pre-execution fields and safety rules in the research plan.

Allocate stable IDs without reusing retired or superseded identifiers:

- `S####` for a source;
- `C####` for a fact or attributed report;
- `H####` for an inference or hypothesis; and
- `J####` for a project judgement.

Specify version, date, platform, and configuration boundaries wherever they
affect a technical observation. Decide which questions require semantic review
rather than trying to encode them as mechanical rules.

Allocate a new ID when a source's bibliographic identity or a claim's
proposition, kind, or report attribution changes. Reassessment may change the
non-identity fields documented in the evidence-record schema.

### 3. Execute in dependency order

Register or update sources first, claims second, and derived views last. Carry
scope, version, attribution, uncertainty, and material caveats forward rather
than repairing only the most visible prose.

Run the source-impact, claim-impact, derived-view, people-and-credit, rights,
and boundary checks below wherever they apply. Retain experiment
specifications, observations, and results even when a hypothesis is not
supported.

### 4. Review the exact result

Run the structural validator, its tests, and the pre-review checks. Then review
the matters that automation deliberately cannot decide: source adequacy,
source-to-claim scope fit, causal attribution, contribution ranking, and
whether a proposition is properly an inference, hypothesis, or judgement.

Record the exact commit reviewed and the validation commands and results.
Later changes invalidate convergence until the new head is checked. A clean
review means only that the specified change converged; it does not approve a
series, script, production decision, publication action, or project gate.

## Source-impact checklist

When adding, changing, superseding, or retiring a source:

- record its stable ID, bibliographic identity, source class, version or
  revision, access date, authority, scope, limitations, and stable location;
- record rights status and intended use independently of permission to read,
  cite, or quote briefly;
- identify every claim that cites it and reassess support, contrary evidence,
  confidence, scope, status, and caveats;
- do not add an evidence link to a retired source; retain existing links only
  for provenance and reassess them as part of retirement;
- distinguish what the source establishes about its own date from what it can
  establish about current behaviour;
- check the chronology for dates, precedence, influence, and turning points;
- check the people map for roles, names, institutions, and time-bounded credit;
- check concept and ecosystem notes for mechanisms or boundaries that depend
  on it;
- check derived prose for statements whose support or qualification changes;
  and
- check whether any proposed quotation, image, diagram, or redistributed
  material needs a separate rights record or assessment.
- retain retired and superseded records in the register; record their lifecycle
  state, reason, and replacement where applicable rather than deleting them.

## Claim-impact checklist

When adding, changing, superseding, or retiring a claim:

- express one checkable proposition and use the ID prefix matching its kind;
- ensure each evidence record exists and says whether it supports, contradicts,
  or merely motivates the proposition;
- compare the whole proposition with each source's recorded scope and actual
  locator; a structurally valid reference is not proof of scope fit;
- carry applicable version, date, platform, and configuration limits in the
  claim scope or caveats;
- attribute reports without silently adopting the reported proposition as
  fact;
- record material contrary evidence, ambiguity, confidence, and unresolved
  tests;
- keep absence claims open until the stated ecosystem search boundary has been
  examined;
- find every use of the claim ID and update chronology, people, concepts,
  ecosystem notes, experiments, and synthesis as needed; and
- retire displaced records in place without deleting or reusing their IDs.

## Derived-view checklist

Chronologies, people maps, concept notes, ecosystem maps, experiment reports,
and research synthesis are derived views of the registers and retained
evidence. For each material statement:

- cite a registered claim ID so its classification, scope, evidence, and
  caveats remain inspectable;
- use a source ID alone only for non-material bibliographic signposting or an
  explicitly identified open research lead, not to bypass claim
  classification;
- preserve whether the underlying record is a fact, attributed report,
  inference, hypothesis, or judgement in the surrounding wording;
- do not broaden a statement beyond the registered claim;
- carry consequential qualifications close enough to travel with the claim;
- keep historical evidence separate from present, versioned behaviour; and
- update or remove the view when a supporting claim is contested, retired, or
  narrowed.

## People-and-credit checklist

- Record the evidenced role, time period, and source; do not turn an old role
  into a present one.
- Distinguish publication authorship, software authorship, maintenance,
  governance, documentation, support, and community work.
- Do not infer sole invention or contribution rank from the earliest source
  found or from publication order.
- Express rankings, evaluations, and editorial selections as registered
  project judgements with their criteria and limitations.
- Preserve name forms used by sources while checking current self-description
  before any portrayal or separately authorised contact.

## Rights-impact checklist

- Keep a source's rights status distinct from the project's intended use.
- Reassess rights when intended use changes, even if the source does not.
- Record origin, licence, attribution, and permitted use before reusing
  external photographs, audio, artwork, diagrams, or substantial text.
- Treat generated media as illustrative unless its subject matter is
  separately evidenced.
- Escalate licence selections, third-party rights decisions, and publication
  under the human-reserved authority boundary.

## Boundary-analysis checklist

For each technical or process boundary, identify all five layers rather than
using "the system" or "reproducible" without a subject:

1. **Durable descriptions and objects:** declared inputs, specifications,
   derivations, immutable objects, metadata, or other retained records.
2. **Execution:** the evaluator, builder, activation process, human action, or
   external service that interprets or acts on a description.
3. **Realised results:** outputs and observations actually produced, including
   their identity and provenance.
4. **Selected state:** the profile, generation, release, decision, or other
   result currently chosen for use.
5. **Contingent live state:** mutable data, processes, traffic, hardware,
   credentials, failures, and externally owned conditions.

At every layer, record the controlling mechanism, owner or authority, claimed
guarantee, version and platform boundary, failure modes, observations, and
recovery path. State explicitly where responsibility passes to another tool,
person, convention, or service.

## Pre-review checklist

- Run `python3 tools/validate_evidence.py --baseline-ref <review-base>`.
- Run `python3 -m unittest discover -s tests -v`.
- Run `git diff --check` against the proposed review base.
- Inspect all changed source and claim IDs and search for their dependants.
- Confirm that derived material statements use claim IDs and preserve their
  classification and caveats.
- Review source adequacy, claim scope fit, historical/current separation,
  causal language, people credit, and rights implications manually.
- Confirm that experiments stayed within their specified safety and host
  mutation boundaries.
- Record the exact commit and command results in the pull request.
- State explicitly that the change leaves project gates unchanged, unless a
  separately authorised gate decision is the subject of the review.

## Structural validation boundary

`tools/validate_evidence.py` checks the mechanically decidable parts of the
documented schemas: YAML shape, stable and unique identifiers, required fields,
enums, report attribution, source references, rights fields, registered IDs
used in research Markdown, lifecycle consistency, and retention of identifiers
allocated in a supplied Git baseline. Baseline validation also preserves
source and claim identity fields and rejects new evidence links to retired
sources.

The Markdown check covers `research/`, `experiments/`, `publishing/`, and
`docs/research-synthesis.md`, matching the planned derived dossier views.

Passing validation does not establish that a source is adequate, a claim fits
the source's scope, an attribution is causal, a contribution ranking is fair,
or a proposition has the correct epistemic kind. Those are semantic review
questions and must remain visible in the review record.
