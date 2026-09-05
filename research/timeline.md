# Initial research timeline

This is a source-backed spine, not yet a complete history. Dates mark
publications we have verified, not necessarily the start of the underlying
work. Community events, releases, governance, and oral histories remain to be
researched.

## 2003: construction and deployment are connected

The official Nix research index reports that Eelco Dolstra's paper
*Integrating Software Construction and Software Deployment* joins building and
deployment in one formalism while preserving the creation and deployment of
variants. [C0009]

We provisionally treat this work as an antecedent to the later Nix deployment
model. That inference neither dates the beginning of Nix work nor implies that
the current architecture was already present. [H0004]

## 2004: the deployment mechanism is presented

Dolstra, Merijn de Jonge, and Eelco Visser presented *Nix: A Safe and
Policy-Free System for Software Deployment* at LISA '04. The paper identifies
distinct store paths computed from build inputs as the mechanism that permits
side-by-side variants. It separately describes user environments as store
objects, upgrade and rollback as switching environments, and garbage
collection in terms of roots and dependency reachability. [C0001, C0011]

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

Dolstra and Armijn Hemel's *Purely Functional System Configuration Management*
presents static packages, configuration files, and control scripts as
immutable results of pure functions. The authors report implementing the model
in a small but realistic distribution called NixOS. [C0010]

## 2008: NixOS and build-farm accounts mature

Dolstra and Andres Löh's ICFP paper presents NixOS as a Linux distribution
constructed and updated from declarative specification. It explicitly extends
the model from packages to static system configuration and examines how pure
actual builds were in practice. [S0003]

The same year's Nix Build Farm paper, credited to Dolstra and Visser, reports
using Nix descriptions to produce build environments automatically and
deterministically while expressing build variants for continuous integration.
[C0012]

The project provisionally interprets this as an early bridge to the series'
broader concern with development processes. It is not evidence for the full
replay model. [H0005]

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
