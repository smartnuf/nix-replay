# Evidence records

This directory is the durable evidence base for D2. It keeps sources,
claims, interpretation, and unresolved questions separate so that later
outlines and scripts can be audited without pretending that all statements
have the same epistemic status.

## Identifiers

- `S####` identifies a source.
- `C####` identifies a factual or reported claim.
- `H####` identifies an inference or hypothesis to test.

Identifiers are stable. Retire a record rather than reusing its identifier.

## Source records

`sources.yaml` uses this schema:

- `id`: stable source identifier.
- `title`: title as published.
- `creators`: credited authors or responsible organisation.
- `published`: publication date or year, as precisely as established.
- `kind`: paper, thesis, manual, project index, or software metadata.
- `publisher`: venue or responsible organisation.
- `url`: direct or canonical location.
- `version`: release, edition, or `not-versioned`.
- `accessed`: date last checked.
- `primary`: whether the source is primary for the claims we take from it.
- `authority`: why it is competent for those claims.
- `scope`: what we may use it to establish.
- `rights_status`: status for reuse in companion material. This is separate
  from permission to read, cite, and make short attributed quotations.
- `notes`: cautions about interpretation or currency.

## Claim records

`claims.yaml` uses this schema:

- `id`: stable claim or hypothesis identifier.
- `statement`: one proposition that could be checked or challenged.
- `kind`: `fact`, `reported`, `inference`, `hypothesis`, or `judgement`.
- `status`: `supported`, `provisional`, `open`, `contested`, or `retired`.
- `scope`: boundary within which the statement is intended to hold.
- `evidence`: source IDs, locators, and the relation to the statement.
- `caveats`: material limits that must travel with the statement.
- `relevance`: likely use in the series; not a commitment to an episode.
- `reviewed`: date last reviewed.

`fact` is reserved for directly checkable matters such as authorship or a
documented interface. `reported` means a primary source makes the technical
claim, but our research has not independently reproduced it. `inference` and
`hypothesis` make our interpretation explicit. `judgement` is an editorial
assessment.

## Working rules

1. Prefer versioned primary sources for technical claims.
2. Use publication records and original papers for chronology and credit.
3. Do not turn a source's aspiration into an independently verified result.
4. Attach qualifications at claim level, not only in surrounding prose.
5. Treat current manuals as current-state evidence, not historical evidence.
6. Record image, diagram, quotation, and redistribution rights separately
   before any companion asset is published.
7. A claim that Nix or NixOS lacks something remains a hypothesis until the
   relevant ecosystem has been searched.

## Current slice

The initial records establish only a foundation: early research history,
the present store and NixOS configuration boundaries, and hypotheses that
connect them to a replayable development process. Ecosystem coverage,
experiments, biographies, and media rights remain later D2 work.
