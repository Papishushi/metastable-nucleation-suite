# Zenodo archival and arXiv preprint workflow

This document makes persistent software archiving and preprint publication part of the MNS release process. Zenodo and arXiv serve different purposes and neither replaces GitHub releases, scientific review or experimental replication.

## Identifier model

| Object | Persistent reference | Purpose |
|---|---|---|
| One immutable MNS release | Zenodo version DOI | Cite the exact software version used for an analysis |
| The evolving MNS software project | Zenodo concept DOI | Cite MNS independently of one release |
| Software or methods manuscript | arXiv identifier | Cite and review the public preprint version |
| Peer-reviewed manuscript | Journal DOI | Cite the accepted scholarly publication |
| Repository state | Git tag and commit SHA | Verify the exact source and integrity boundary |

Every publication must state which MNS release, tag and commit it used. A preprint identifier or software DOI is not evidence that a physical claim has been validated.

## Zenodo integration

Zenodo can ingest and archive new GitHub releases after the repository has been enabled through the maintainer's connected Zenodo account. This one-time account action cannot be performed from repository automation.

### Metadata source

`CITATION.cff` is the canonical repository metadata source for GitHub and Zenodo ingestion.

Do not add `.zenodo.json` merely to duplicate the same fields. Zenodo gives `.zenodo.json` precedence and ignores `CITATION.cff` when both are present. Introduce `.zenodo.json` only through a reviewed change that documents a field Zenodo requires and CFF cannot represent adequately.

### One-time activation

1. Sign in to Zenodo with the maintainer account.
2. Connect the corresponding GitHub account.
3. Synchronise the repository list.
4. Enable `Papishushi/metastable-nucleation-suite`.
5. Confirm that the next test or stable GitHub release creates a Zenodo software record.

Track this gate in issue #104. Do not publish a DOI badge or placeholder identifier before Zenodo has created the real record.

### Release checklist

Before creating a release intended for Zenodo:

- align `VERSION`, package versions, release notes and `CITATION.cff`;
- confirm the release commit and tag are final;
- run the complete release and scientific-contract checks;
- exclude credentials, private data, laboratory secrets and unrelated generated files;
- create the GitHub release and verify that Zenodo ingests it;
- record both the version DOI and concept DOI returned by Zenodo;
- add the real DOI badge, citation text and release links in a follow-up pull request;
- preserve the tag and release assets; never move an archived tag.

When an existing release must be corrected, publish a new release. Do not mutate the archived scientific record.

## arXiv integration

arXiv is the planned public preprint route for the MNS software or methods manuscript. Submission is an author action: the author must use a registered arXiv account, accept the submission licence and may require endorsement for a new category.

### Manuscript scope

The first arXiv manuscript should describe research software and methodology:

- the problem and intended reuse;
- architecture and source-of-truth boundaries;
- executable protocols and data contracts;
- semantic provenance and evidence-status separation;
- deterministic examples, tests and release reproducibility;
- limitations and explicit exclusion of unsupported physical conclusions.

It must not present CI, simulation, a Zenodo DOI or arXiv moderation as peer review or physical validation.

### Source layout

The arXiv-ready source should be introduced under `paper/arxiv/` through issue #105. It should contain only the files required to compile the manuscript:

```text
paper/arxiv/
  main.tex
  references.bib
  figures/
  README.md
```

The source archive must compile from a clean directory without absolute paths, private files or repository-wide assumptions. Figures must be included in the submission rather than referenced only through external URLs.

### Source-hygiene gate

Before uploading to arXiv:

- compile the exact upload archive in a clean environment;
- inspect the archive contents manually;
- remove comments, drafts, credentials, hidden metadata and unrelated files;
- verify filename case, supported characters and figure paths;
- check title, abstract, authors, affiliations, licence and categories;
- confirm every software result cites the exact MNS release DOI, tag and commit;
- preview the arXiv-generated PDF before final submission.

### After submission

Once an arXiv identifier exists:

- add the real identifier to README and the manuscript record;
- add a `preferred-citation` or manuscript identifier to `CITATION.cff` through a reviewed change;
- link the arXiv record from the corresponding Zenodo record and software-paper issue;
- record later versions and the journal DOI without deleting the preprint history;
- update issue #103 with submission, moderation and publication status.

No placeholder arXiv identifier should be committed.

## Required cross-links

After both integrations are active:

- the GitHub release links to its Zenodo version DOI;
- README exposes the Zenodo concept DOI for general software citation;
- the arXiv manuscript cites the exact Zenodo version DOI used;
- the Zenodo record links to the arXiv manuscript when available;
- the final journal record links back to the software archive and preprint;
- `CITATION.cff` remains consistent with the current software release and preferred manuscript citation.

## Operational ownership

- Zenodo activation and arXiv submission require the maintainer or an authorised author.
- Metadata, manuscript source, clean-build checks and cross-link verification can be reviewed through pull requests.
- Publication and archiving work is coordinated in #103, with implementation gates #104 and #105.
