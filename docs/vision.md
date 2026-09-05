# Project vision

Status: working draft for review

## Purpose

Use Nix and NixOS to investigate how difficult software and systems work can
become more dependable and economical when it begins from a sound model of the
problem.

The project has three purposes, in priority order:

1. Treat Nix as an architectural case study from which generally useful
   principles may be extracted.
2. Evaluate practically whether and where Nix or NixOS should be adopted.
3. Develop enough guided understanding to use and judge them competently.

## Audience

The primary design listener is the project owner: a technically experienced
person investigating Nix and NixOS from first principles. Technically
experienced peers are the secondary audience.

The account may assume broad engineering and computing literacy, but it should
explain Nix-specific concepts from the ground up. Accessibility to a broad
audience must not dilute the architectural depth or determine the pace.

## North star

Investigate how human and machine actors can replay a configurable
software-development process that begins with ambiguous intent and substantial
creative freedom, but progressively crystallises its learning into durable
intents, plans, specifications, decisions, code, toolchains, tests,
environments, and ways of working, until the desired result becomes
controllable and reproducible.

The process is generative because neither its route nor its final design is
fully prescribed at the outset. It is directed because choices occur within
evolving rules, evidence, authority boundaries, and evaluation criteria. It
learns because each run can improve both the product and the descriptions
governing later runs.

## Replay and reproducibility

Here, replay does not mean reproducing a bit-for-bit result or retaining an
execution trace.

Replay means invoking a process from an evolving description. During a run,
human or machine actors may make choices within established rules. Randomness,
search, Monte Carlo methods, simulated annealing, judgement, and other forms of
bounded freedom may be valuable. A replay may therefore produce genuinely
novel output that people or machines can inspect, study, grade, and learn from.

Reproducibility is the broader goal. Depending on the stage and purpose, it may
mean:

- reproducing an exact released artefact;
- recreating the environment in which work occurs;
- reinvoking a governed process without requiring the same choices;
- replaying from a checkpoint under a different steer; or
- changing a description so that it predictably changes the process or its
  admissible outcomes.

Execution traces may support diagnosis, comparison, provenance, and learning,
but tracing is orthogonal to the meaning of replay used here.

## Why Nix and NixOS

Nix and NixOS appear to be important illustrations of architecture-first
thinking about software construction, deployment, configuration, and system
administration.

The project will examine what their architecture actually guarantees, where
their abstractions stop, and whether Nix can serve as part of the substrate for
reproducible and relocatable development processes and environments.

It will also ask what a Nix-based system lacks when the object being reproduced
is not merely an artefact or configured machine, but an evolving,
choice-making, human-machine development process.

## Editorial stance

This is an inquiry, not advocacy.

The work must distinguish:

- claims made for Nix;
- demonstrated architectural properties;
- behaviour dependent on convention, tooling, or ecosystem quality;
- reported experience;
- project inference and hypothesis; and
- lessons that are genuinely transferable.

History and people are part of the technical explanation. The project should
show what problems, constraints, research traditions, institutions, and
communities produced the ideas, and how those ideas changed over time.

## Companion publication

The podcast is audio-led, not audio-only. Each episode should have one stable,
easily discoverable companion page linked from podcast applications and, where
practical, identified in the audio itself.

Companion material may include:

- a transcript and chapter navigation;
- sources and further reading;
- photographs and historical material with lawful attribution;
- explanatory diagrams and timelines;
- commands, configurations, experiments, and worked examples;
- qualifications and corrections; and
- deeper technical documents that would interrupt the spoken narrative.

## Success

The project succeeds if it produces an engaging and technically trustworthy
account of Nix and NixOS, permits a competent practical judgement of them, and
extracts durable insights about replayable human-machine development without
claiming more than the evidence supports.
