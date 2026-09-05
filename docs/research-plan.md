# Research and evidence plan

Status: proposed for research-design gate D1

Issue: #2

## Purpose

This plan defines how the project will investigate Nix, NixOS, and the lessons
they may offer for replayable human-machine software development.

It governs evidence collection. It does not predetermine the conclusions or
authorise scripting, audio generation, publication, external interviews, or a
software demonstrator.

## Research principles

- Begin with questions, not a defence or criticism of Nix.
- Prefer primary evidence and record enough when evidence is secondary.
- Separate what a system promises from what it guarantees and what users
  experience.
- Treat Nix, NixOS, package collections, deployment tools, development
  environments, and surrounding services as related but distinct systems.
- State the software version, date, platform, and configuration to which a
  technical observation applies.
- Seek evidence that could contradict the working thesis.
- Preserve disagreements and changes over time instead of forcing one timeless
  account.
- Use practical experiments to test important claims that documentation alone
  cannot settle.
- Keep the evidence useful both for audio narration and deeper companion
  material.

## Principal research questions

### Q1: Origins, people, and historical development

- Which problems led to Nix, and how were they framed at the time?
- Which research traditions, earlier systems, and practical experiences
  influenced its design?
- Who made the important conceptual, implementation, institutional, and
  community contributions?
- How did NixOS arise from Nix, and how did their goals and boundaries evolve?
- Which turning points, disagreements, governance changes, or ecosystem
  developments altered the project's direction?
- Which common historical accounts are supported, incomplete, disputed, or
  retrospective simplifications?

### Q2: The architectural model

- What are the essential semantics and invariants of Nix?
- How do evaluation, derivations, builders, the store, dependency closure,
  substitution, garbage collection, profiles, generations, and rollback fit
  together?
- What do purity, reproducibility, determinism, hermeticity, immutability, and
  declarative configuration mean in this context, and where are they commonly
  conflated?
- What does NixOS add through modules, system configuration, activation, and
  service management?
- Which guarantees arise from architecture, which depend on disciplined
  packaging, and which depend on infrastructure or convention?
- Where do time, mutable state, identity, authority, secrets, hardware,
  networks, and external services cross the model's boundaries?

### Q3: Practical use and adoption

- What is the current path from first encounter to competent use?
- What makes the system difficult to learn, operate, debug, or maintain?
- How well can it provide controllable and relocatable environments for
  building, testing, and debugging real software?
- How do platform, architecture, and organisational setting affect the result?
- What operational costs accompany the architectural benefits?
- Which surrounding tools fill gaps, and do they reinforce or weaken the core
  model?
- For which tasks would adopting Nix or NixOS be proportionate, and where would
  it not be?

### Q4: Replayable development

- Which Nix ideas transfer from artefact construction to development-process
  design?
- What would a description of a generative human-machine process need to
  contain?
- How should such a description express freedom, rules, authority, evaluation,
  randomness, budgets, stopping conditions, and feedback?
- What becomes progressively more constrained as work converges?
- What constitutes a useful checkpoint, and what must be preserved to replay
  from it under different steering?
- Which forms of reproducibility apply to environments, processes, evidence,
  and final artefacts?
- What must exist above, alongside, or beyond Nix to support an evolving
  choice-making process?
- Which apparent lessons are genuinely general and which are specific to Nix?

### Q5: Communication and companion publication

- Which concepts require diagrams, timelines, examples, or demonstrations
  rather than audio alone?
- How can every episode remain intelligible without a screen?
- Which current podcast metadata and application behaviours best expose stable
  companion pages, transcripts, chapters, links, and corrections?
- How should changing web material be preserved or cited?
- Which images, recordings, quotations, logos, and historical materials may be
  used lawfully, and with what attribution?
- How should accessibility influence transcripts, diagrams, navigation, and
  alternative text?

## Source strategy

### Source classes

Use the following source classes, in descending evidential preference where
they address the same factual question:

1. Contemporary primary sources: papers, theses, specifications, manuals,
   release notes, source code, issue and commit history, talks, and archived
   project material.
2. First-person accounts: interviews, correspondence, retrospectives, and
   presentations by participants.
3. Institutional records: project, foundation, university, company, and
   conference material.
4. Independent technical analysis and reliable historical scholarship.
5. Community reports, operational accounts, discussions, surveys, and
   tutorials.
6. Project experiments and reasoned synthesis.

Precedence is not automatic. A later official description may be authoritative
about current behaviour but poor evidence of earlier intent. First-person
recollection may be valuable but incomplete. Source selection must follow the
claim being tested.

### Source record

Each retained source should have a stable identifier and record:

- title, creator, publisher or repository, and source class;
- original and archived location where lawful and practical;
- publication date, retrieval date, version, revision, or commit;
- relevant people, organisations, concepts, and time periods;
- claims for which it supplies evidence;
- brief assessment of authority, proximity, limitations, and conflicts;
- quotation or excerpt locations without unnecessary copying; and
- copyright, licence, attribution, and intended-use information.

A machine-readable source index should be maintained alongside readable notes.

## Claim and uncertainty model

Each material claim should be classified as one of:

- **fact**: directly supported by adequate evidence;
- **report**: attributed to a person or source without adopting it as fact;
- **inference**: a conclusion drawn explicitly from stated evidence;
- **hypothesis**: a proposition retained for investigation;
- **judgement**: the project's reasoned evaluation or recommendation.

Claim records should identify supporting and contrary sources, applicable
versions and dates, confidence, unresolved ambiguity, and where the claim may
be used.

Absence of discovered evidence is not evidence of absence. Claims that Nix or
its ecosystem lacks a capability require an explicit search boundary.

## Historical method

The historical dossier should include:

- a dated chronology with source references;
- a people and institutions map based on evidenced roles;
- the development of central concepts and terminology;
- distinctions among original intent, contemporary implementation, later
  interpretation, and present behaviour;
- competing accounts and meaningful omissions;
- governance and community developments that affected technical direction; and
- identification of people whose direct testimony might materially improve the
  account.

No person should be contacted or invited merely because they appear in the
plan. External communication requires separate approval and a reviewed brief.

## Technical analysis

Analyse the system by boundaries rather than as a single product:

- the Nix language and evaluator;
- derivations, builders, and build isolation;
- store paths, references, closure, and garbage collection;
- fetching, substitution, caching, trust, and provenance;
- profiles, generations, upgrades, rollback, and state;
- package collections and composition;
- development environments and debugging workflows;
- NixOS modules, activation, services, and mutable host state;
- deployment, orchestration, and remote execution;
- platform and architecture support; and
- surrounding tools that assume responsibility outside the core.

For each boundary, record intended properties, actual mechanism, failure modes,
observability, authority, ownership, recovery, and relevant alternatives.

## Practical experiment design

Experiments must be specified before execution. Each specification should
state:

- the question and competing hypotheses;
- platform, architecture, versions, and pinned inputs;
- setup and isolation method;
- commands or process description;
- expected observations without prescribing the result;
- evidence and logs to retain;
- safety, cleanup, and host-mutation boundaries; and
- criteria for interpreting success, failure, and uncertainty.

Candidate experiment families are:

1. Recreate an identical development environment from a pinned description.
2. Move a build and debugging workflow between materially different hosts.
3. Change one declared input and observe the resulting rebuild boundary.
4. Reproduce, inspect, and debug a failure.
5. Exercise generations, rollback, and recovery.
6. Compare declared state with mutable or externally owned state.
7. Test caching, substitution, remote execution, and trust boundaries.
8. Compare a Nix-based workflow with a conventional environment for one
   representative project.
9. Represent a development checkpoint and examine what Nix captures and what a
   higher-level replay still requires.

Run experiments only in disposable or explicitly authorised environments. Do
not mutate an important host merely because an experiment is listed.

## Companion and publishing research

Before series specification, determine:

- a stable canonical URL pattern for series and episode pages;
- how podcast applications expose episode links and formatted show notes;
- suitable current standards for transcripts and chapter metadata;
- accessible diagram, image, code, and transcript presentation;
- correction and version-history mechanisms;
- durable hosting and preservation needs;
- audio and image formats and associated metadata; and
- rights, attribution, and licence implications for every asset class.

Do not select a publishing service or licence merely by drafting this plan.

## Dossier structure

The evidence stage should produce or refine:

- research/sources.yaml: machine-readable source index;
- research/claims.yaml: material claim and uncertainty register;
- research/timeline.md: sourced chronology;
- research/people.md: evidenced people and institutions map;
- research/concepts/: architectural and terminology notes;
- research/ecosystem/: current roles and boundary map;
- experiments/: specifications, fixtures, results, and retained evidence;
- publishing/: companion, metadata, accessibility, and rights research; and
- docs/research-synthesis.md: readable findings and unresolved questions.

Schemas should be small, versioned, documented, and extended only when real
evidence requires it.

## Stopping conditions

The evidence dossier is sufficient for series specification when:

- every principal question has either adequate evidence or an explicit,
  consequential gap;
- the historical account has a sourced chronology and avoids unsupported role
  attribution;
- architectural claims are tied to mechanisms and applicable versions;
- material contrary evidence and ecosystem alternatives are represented;
- the practical claims central to the narrative have been tested or clearly
  identified as untested;
- sources and intended media uses have enough rights information for planning;
- remaining uncertainty can be communicated honestly without blocking the
  narrative; and
- further research is likely to add detail rather than change the proposed
  series architecture.

Exhaustiveness is not required. A material contradiction, unsafe experiment,
unresolved rights dependency, or expanding scope that changes the project
vision is a reason to halt and seek a decision.

## Proposed D2 entry criteria

Research design D1 may close when the owner approves:

- the principal questions and boundaries;
- the source and claim models;
- the historical and technical methods;
- the experiment families and safety rules;
- the companion and rights research;
- the dossier structure and stopping conditions; and
- any changes required to the approved project vision.

Only then may systematic evidence collection begin.
