# Nasreddin story coverage audit

Audited and reconciled: 2026-08-10

Canonical source:
`https://nasredin.blogspot.com/2010/12/this-reminds-me-of-story-111-teaching.html`

Local collection:
`src/content/stories/*.md`

## Result

The repository now contains the complete canonical sequence:

- Canonical source stories: **111**
- Canonical stories represented locally: **111**
- Missing story numbers: **0**
- Duplicate story numbers: **0**
- Separate foreword: **1**
- Additional Weebly story, “Excuses…”: **1**

The former `8309948.md` collection shell is retained at its historical
permalink, but is no longer tagged as a story and therefore does not appear as
a misleading collection entry.

## Reconciliation

The previous audit found 72 represented stories and 39 missing stories. The
missing set was source story **#3** and **#74–#111**. Those 39 stories have now
been added.

The text and titles of all 111 numbered stories, including the 72 that already
had individual Weebly pages, have been updated from the canonical Blogspot
collection. Existing Wisdom-site permalinks and lead images were preserved
where available.

Each canonical story now has explicit `story_number` metadata. The generated
collection is ordered by that field rather than by Weebly repost dates.

## Repeatable import

The reconciliation can be reproduced with:

```sh
python3 -m pip install -r requirements-import.txt
python3 scripts/import_nasredin.py
```

The importer:

1. Fetches the main Blogspot post body.
2. Requires exactly one foreword and 111 bold story headings.
3. Splits the long post into individual Markdown files.
4. Preserves established permalinks and existing lead media.
5. Produces concise index descriptions from each story’s introduction.
6. Is idempotent once `story_number` metadata is present.

## Verification

On 2026-08-10:

- Story numbers **1–111** were present exactly once.
- The collection contained the foreword, 111 canonical stories, and the
  additional “Excuses…” story.
- `npm run build` completed successfully.
- `npm run check` passed all expected-page, asset, figure, and local-link
  checks.
