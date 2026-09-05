# Core model: from description to running system

This is the first boundary model for review. It is an analytical map, not a
claim that Nix is a complete development-process system.

## The documented chain

| Boundary | Durable description or object | What the mechanism controls | What remains outside or contingent |
| --- | --- | --- | --- |
| Nix evaluation | Nix expressions and supplied inputs | Computes values and derivation graphs | Source selection, evaluator inputs, impure evaluation, and author intent |
| Derivation | Builder, environment, declared dependencies, outputs | Describes a build action and its dependency graph | Undeclared dependencies, builder behaviour, platform effects, and permitted nondeterminism |
| Build realisation | Build execution and produced output | Attempts to realise the derivation in a controlled environment | Kernel, hardware, remote builders, sandbox policy, clocks, entropy, and defects |
| Store | Immutable store objects and references | Preserves realised objects and their reference graph | Which objects a particular store currently contains |
| Profile or generation | A selected environment or system closure | Makes one selection current without overwriting store objects | Mutable user data and external services |
| NixOS modules | Option declarations and definitions combined into a configuration | Composes a full declarative system configuration | Whether declarations capture every operational requirement |
| Activation and runtime | Switch program, services, and running state | Attempts to move the running machine to the selected configuration | Effectful transitions, persistent data, live traffic, failures, and observation |

The source basis is C0004-C0007. Each row deliberately names a boundary where
the word "reproducible" needs a subject: description, derivation, build output,
store object, selected closure, static configuration, or running service.

## Four distinctions the series must preserve

### Description is not realisation

A Nix expression can compute a derivation graph; a derivation can describe a
build; a build can realise an object. Conflating these steps hides both the
power of the model and the remaining sources of variation. [C0004]

### Identity is not automatically bit-for-bit equality

Early Nix explains store identity using hashes of build inputs. Current Nix
has a richer store model. We must name the addressing method and the object
whose equality is at issue before claiming that "the hash is the content" or
that equal descriptions necessarily yielded identical bytes. [C0001, C0005]

### Atomic selection is not total-state rollback

Profiles and NixOS generations make it possible to select an earlier closure
without overwriting the old store objects. That is powerful and specific. It
does not on its own reverse a database migration, an external API action, a
changed secret, or arbitrary mutable state. [C0006, C0007]

### Replay is not trace

In this project, replay means invoking a generative process again from durable
descriptions and a chosen checkpoint, possibly with bounded freedom and new
steering. An execution trace may help diagnose or compare runs, but retaining
one is a separate capability. [H0003]

## Fit with the proposed replayable process

The working hypothesis is that Nix and NixOS supply several unusually strong
pieces:

- explicit dependency graphs;
- immutable realised objects;
- sharing and closure operations;
- declarative composition of static system configuration;
- selectable generations and bounded rollback; and
- a practical separation between building a candidate and selecting it.

The proposed development-process system would also need to make other things
durable and operable: evolving intent, constraints, plans, decisions, methods,
candidate generation, assessment, human and machine authority, feedback, and
the rationale for selecting or rejecting outcomes. Whether existing ecosystem
tools already provide those layers is deliberately open. [H0001]

## Candidate checkpoint model

A useful checkpoint is not merely a saved filesystem. It is a reviewable
bundle that identifies:

1. the intent and constraints accepted so far;
2. the process definition and tools to invoke;
3. selected inputs and allowable degrees of freedom;
4. decisions and authority boundaries;
5. realised artefacts and observations; and
6. unresolved questions that a later replay may steer differently.

This candidate model is a hypothesis for later examples and experiments, not
a feature description of Nix. [H0003]

## Tests before promotion into narrative

- Demonstrate which changes alter derivations, store paths, bytes, profiles,
  system closures, and runtime behaviour.
- Test a NixOS generation rollback alongside mutable service data to show the
  boundary without caricature.
- Compare input-addressed, fixed-output, and content-addressed cases using
  current terminology.
- Search flakes, lock files, Nix develop, direnv, devenv, process-compose,
  Arion, NixOps, Colmena, deploy-rs, Hydra, and related tools before making a
  claim about missing process-level capabilities.
- Record where deliberate randomness could be permitted, captured, replayed,
  or selected without weakening claims about deterministic downstream steps.
