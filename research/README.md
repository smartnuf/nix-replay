# Evidence records

This directory is the durable evidence base for D2. It keeps sources,
claims, interpretation, and unresolved questions separate so that later
outlines and scripts can be audited without pretending that all statements
have the same epistemic status.

## Identifiers

- `S####` identifies a source.
- `C####` identifies a factual or reported claim.
- `H####` identifies an inference or hypothesis to test.
- `J####` identifies a project judgement or recommendation.

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
- `snapshot_url`: optional immutable or release-specific reviewed location.
- `version`: release, edition, or `not-versioned`.
- `accessed`: date last checked.
- `source_class`: one of the six classes approved in the research plan.
- `authority`: why it is competent for those claims.
- `scope`: what we may use it to establish.
- `rights_status`: status for reuse in companion material. This is separate
  from permission to read, cite, and make short attributed quotations.
- `intended_use`: planned use under assessment, independently of rights status.
- `notes`: cautions about interpretation or currency.

## Claim records

`claims.yaml` uses this schema:

- `id`: stable claim or hypothesis identifier.
- `statement`: one proposition that could be checked or challenged.
- `kind`: `fact`, `report`, `inference`, `hypothesis`, or `judgement`.
- `status`: `supported`, `provisional`, `open`, `contested`, or `retired`.
- `confidence`: `high`, `medium`, or `low` evidential confidence.
- `scope`: boundary within which the statement is intended to hold.
- `attributed_to`: required for a `report`; omitted for other kinds.
- `evidence`: source IDs, locators, and the relation to the statement.
- `caveats`: material limits that must travel with the statement.
- `relevance`: likely use in the series; not a commitment to an episode.
- `reviewed`: date last reviewed.

### Source classes

The machine-readable values preserve the six ordered classes in D1:

1. `contemporary-primary`
2. `first-person-account`
3. `institutional-record`
4. `independent-analysis`
5. `community-report`
6. `project-experiment-or-synthesis`

The order is a preference when sources address the same factual question,
not an automatic ranking detached from a claim's date, scope, or provenance.

### Mutually exclusive claim kinds

`fact` means the project adopts the proposition as directly supported by
adequate evidence. Independent reproduction is required when the proposition
itself depends on observed behaviour, but not for a documentary fact such as
a byline or specified interface.

`report` means that a named person or source asserts the proposition and the
project records the attribution without adopting the underlying proposition
as fact. A report must set `attributed_to`. If we later adopt the proposition,
we retire or supersede the report with a distinct fact record.

`inference` is a conclusion explicitly drawn from stated evidence.
`hypothesis` is a proposition retained for investigation. `judgement` is the
project's reasoned evaluation or recommendation.

Confidence is distinct from status: status records the claim's disposition,
whereas confidence records evidential strength. `high` requires adequate,
direct, and well-scoped support; `medium` records material support with a
remaining test or qualification; `low` marks an early or weakly supported
proposition. For a report, confidence concerns the accuracy of the attribution,
not the unadopted proposition it contains.

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
