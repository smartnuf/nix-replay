# Initial research timeline

This is a source-backed spine, not yet a complete history. Dates mark
publications we have verified, not necessarily the start of the underlying
work. Community events, releases, governance, and oral histories remain to be
researched.

## 2003: construction and deployment are connected

The official Nix research index lists Eelco Dolstra's paper *Integrating
Software Construction and Software Deployment*. It describes a precursor
problem: integrating build and deployment while preserving variability rather
than fixing one package variant. This is an antecedent, not evidence that the
current Nix architecture was already complete. [S0004]

## 2004: the deployment mechanism is presented

Dolstra, Merijn de Jonge, and Eelco Visser presented *Nix: A Safe and
Policy-Free System for Software Deployment* at LISA '04. The paper identifies
distinct store paths computed from build inputs as the central mechanism from
which side-by-side variants, environments, atomic selection changes, and safe
garbage collection follow. [S0001]

The project index also records *Imposing a Memory Management Discipline on
Software Deployment* in 2004. Its analogy between store references and memory
graphs supplies a useful second route into closures and garbage collection.
[S0004]

## 2006: the deployment model is consolidated

Utrecht University records publication of Eelco Dolstra's doctoral thesis,
*The Purely Functional Software Deployment Model*, on 18 January 2006. The
thesis presents the model, its Nix implementation, and applications beyond
package installation, including continuous integration, service deployment,
and build management. [S0002]

## 2007: the model reaches system configuration

The official index lists *Purely Functional System Configuration Management*
by Dolstra and Armijn Hemel. It frames static packages, configuration files,
and control scripts as results of pure functions and reports a small but
realistic NixOS implementation. [S0004]

## 2008: NixOS and build-farm accounts mature

Dolstra and Andres Löh's ICFP paper presents NixOS as a Linux distribution
constructed and updated from declarative specification. It explicitly extends
the model from packages to static system configuration and examines how pure
actual builds were in practice. [S0003]

The same year's Nix Build Farm paper, credited to Dolstra and Visser, applies
Nix descriptions to reproducible build environments for continuous
integration. This is an early bridge to the series' broader concern with
development processes, but it is not yet evidence for the full replay model.
[S0004]

## 2010: the NixOS account reaches journal form

The project index records a Journal of Functional Programming version of
*NixOS: A Purely Functional Linux Distribution* by Dolstra, Löh, and Nicolas
Pierron. Its abstract describes static system parts as immutable values built
by pure functions and NixOS as a modular functional specification. [S0004]

## Present reference point: Nix 2.35 and NixOS 26.05

The current evidence baseline uses the versioned Nix 2.35.2 manual for the
store model and the NixOS 26.05 manual for modules, rebuilds, generations, and
rollback. These manuals tell us about present documented interfaces; they must
not be read backwards as evidence that every feature existed in early Nix.
[S0005, S0006]

## Questions for the next history slice

- Which experiments, institutions, and collaborations preceded the 2003 and
  2004 publications?
- How did NixOS move from proof of concept to a community distribution?
- When did Nixpkgs, Hydra, channels, and flakes enter, and which problems were
  their authors trying to solve?
- Which contributors and maintainers changed the design after the founding
  research, including work that publication bylines do not expose?
- Which claims need interviews or archived project discussions rather than
  retrospective inference?
