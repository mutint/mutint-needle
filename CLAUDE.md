# CLAUDE.md — aledb-needle

The mutation needle plot, as a panel on aledb-core's experiment Overview page.

**The first plugin in the suite that is neither a page nor a model.** aledb-compare,
aledb-fixation and aledb-converge each own a route and a sidebar entry; aledb-phylogeny owns
those plus a stored table. This one registers a *panel* — a template and a callable that
builds its context — through `aledb_common.panel_registry`, and contributes no URL, no nav
entry, no model and no migration. It is the first consumer of that registry, and the reason it
exists: until then, something that was one panel rather than a page had no seam at all and had
to live in core.

The other plugin repos carry no `CLAUDE.md`, and this one does because the design notes below
came out of `aledb-core/CLAUDE.md` with the code. They describe why the plot is built as it
is, which is a different thing from `docs/using/needle-plot.md`, which says how to read it.

```
aledb-needle/
├── aledb_needle/
│   ├── apps.py        registers the panel and an About section, and nothing else
│   ├── panel.py       the context the panel template renders from
│   ├── util.py        needle_plot_axis + get_needle_plot_data — two queries over core's models
│   ├── templates/needle/panel.html
│   ├── static/aledb_needle/   muts_needle_plot.js + the vendored library (see VENDOR.md)
│   └── tests/
└── docs/using/needle-plot.md
```

It is a submodule of `mutint`. Edit it **here**, in the suite-root checkout, never in
`mutint/aledb-needle` — see the rules at the top of the suite `CLAUDE.md`.

## The plot knows which genome it is drawing

Its axis was a hardcoded `maxCoord: 5000000` in `muts_needle_plot.js` — roughly E. coli, and
wrong for anything else — and the data emitted a bare `coord` with **no `seq_id`**, so a
multi-contig reference drew every contig on top of itself on one axis. Both failed silently:
the plot rendered, it simply was not about this genome.

`needle_plot_axis` names the sequence to draw and reads its length from
`ExperimentReference.seq_ids`; `get_needle_plot_data(experiment_id, contig)` is scoped to it.
One sequence at a time rather than a concatenated axis, because offsets the reader cannot see
turn every coordinate into one that matches nothing in the tables.

**Which sequence is the reader's to choose, and for a while it was not.** One contig was
hardcoded as the answer rather than as the default, so on a chromosome-plus-plasmid reference
the plasmid's mutations were on **no page in the product** — and the line saying which contig
was drawn made that visible without making it fixable. `?contig=` carries the choice and
`needle_axis["contigs"]` is the menu, each entry with its own `count` and `length`. There is
deliberately no separate count of that list to disagree with it.

**The default is the longest sequence, not the busiest**, and the two rules are independent
enough that a fixture where they agree tests neither. The chromosome is what somebody opening
an experiment means by "the genome"; a small plasmid under strong selection can carry more
mutations than it, and a page opening on the plasmid would be a surprise about the reference
dressed up as a fact about the data. Length is a property of the reference. A count moves.

**The list is every sequence the reference has, mutations or none.** A plasmid with nothing on
it draws an empty axis, which is an answer — the reader asked and the page says nothing is
there. Left out, it is indistinguishable from a sequence the reference does not have, and the
count beside each name is what tells those apart.

Three more things:

- **The picker is links, not a form**, the same shape as the per-sample page's sample picker,
  so it needs no script and a plasmid's plot is a URL somebody can send. Its `.aledb-picker`
  wrapper and `.aledb-menu` list are core's, in `common.css`.
- **An unrecognised `?contig=` falls back to the default** rather than drawing an empty plot,
  as `breseq_table._selected_reseq` does with a sample its own filters exclude. An empty plot
  of a contig that does not exist reads exactly like a contig with no mutations — and that
  second thing is a state the page renders on purpose.
- **A contig a mutation names but the reference does not list is offered last.** It has no
  length to sort by, and dropping it would leave mutations the experiment holds on no axis.

**With no stored reference there are no lengths at all**, so the list is what the mutations
name and the order degrades to busiest first — the most the data alone can say. The sort's
final tie-break is the name, or two equal contigs swap places between page loads and the
default becomes whichever the database felt like.

Measured before any of this: a 160-base reference drew a **0–160** axis rather than 0–5,000,000
with every mutation in the leftmost pixel. On a 4.6 Mb one the visible ticks are unchanged,
because d3 rounds that domain up to 5,000,000 anyway — the fix is invisible exactly where the
old constant happened to be right.

## Nothing is stored

`get_needle_plot_data` was `aledb_stats.StaticData`, a JSON blob kept current by a registered
rebuilder since long before there was a rebuild registry. Reading three columns as
`values_list` tuples costs **0.05s** on the largest experiment in the dev database (52,139
observations) against **3.38s** to rebuild the stored answer, so the cache paid for a staleness
row, an `ensure_fresh` on the read path and a rebuilder, to save nothing.

It is also what removed a failure mode: `/stats` renders this beside `aledb_stats`'s counts,
and while both were stored they could disagree in the same viewport — one refreshed, the other
stale. Neither is stored now and both read the same queryset, so they cannot.

**Do not add a stored table back here.** See **Derived data and rebuilds** in the suite
`CLAUDE.md` for what one costs beyond disk.

## Two things it does not do

- **It applies no view filter.** The Overview summarises what the experiment holds, the way the
  dashboard does, rather than being a table you read rows through. `{% view_filter_summary %}`
  is deliberately absent for the same reason.
- **It subtracts the ancestor**, through `get_evolved_observation_queryset`, like every other
  derivation in the suite. That is not optional and has no toggle.

## Tests

`./mutint test aledb_needle`. There is no way to run them from aledb-core: the plot is not
installed there, which is the point of the split.

`aledb_needle/tests/test_needle_plot.py` builds its own breseq fixture through
`aledb_import.tests.breseq_fixture`, importing from core as any plugin's tests may. The
multi-sequence case puts **more mutations on the short sequence than on the long one**, so the
list rule and the default rule are tested apart — a fixture where they agree would pass under
either.
