"""The needle plot's data and its axis.

Both were `aledb_stats.util` functions until this became its own component. Nothing about
them changed in the move except the two paragraphs of docstring that described where they
lived; they read core's models through `aledb_sample`, as any plugin's derivation does.
"""

from django.db.models import Count

from aledb_experiment.ordering import sample_order
from aledb_sample.util import get_evolved_call_queryset

#: The order `filter_mutation_calls` returns rows in. Kept here so the computed needle
#: plot is element-for-element what the stored one was, rather than the same points shuffled.
ROW_ORDER = sample_order("sample__")


def needle_plot_axis(experiment_id, contig=None):
    """Which sequence the needle plot draws, how long it is, and what else it could draw.

    The plot had **no idea what genome it was describing**. Its axis was a hardcoded
    `maxCoord: 5000000` in `muts_needle_plot.js` -- roughly E. coli, and wrong for anything
    else -- and `get_needle_plot_data` emitted a bare `coord` with no `seq_id`, so on a
    multi-contig reference every contig's positions were plotted on top of each other on one
    axis. Both failed silently: the plot rendered, it was simply not about this genome.

    One sequence at a time is the honest fix. The alternative -- laying contigs end to end on a
    concatenated axis -- needs offsets the reader cannot see and turns every coordinate into
    one that matches nothing in the tables.

    **Which one is the reader's to choose**, and that half was missing: one contig was
    hardcoded as the answer rather than as the default, so a plasmid's mutations were on no
    page in the product. `contig` is what the reader asked for, and an unrecognised one falls
    back to the default rather than drawing an empty plot -- the same posture
    `breseq_table._selected_reseq` takes with a sample id that its own filters exclude.

    Returns `{contig, length, contigs}`. `contigs` is every sequence the plot could draw,
    longest first, each carrying its own `count` and `length` -- the list the picker is built
    from, and the reason there is no separate count of it to disagree with.

    **The default is the longest sequence, not the busiest.** Those are usually the same and
    the difference matters when they are not: the chromosome is what somebody opening an
    experiment means by "the genome", while a small plasmid under strong selection can
    outnumber it and would then be what the page opened on. Length is a property of the
    reference; a mutation count is a property of this experiment's data, and it moves.

    **A sequence with no mutations is offered too.** It draws an empty axis, which is an
    answer -- the reader asked what is on the plasmid and the plot says nothing is. Left out,
    it is indistinguishable from a sequence the reference does not have. Its entry carries
    `count` 0, so the menu says which is which without a sentence beside it.

    `length` is None only when the experiment has no stored reference, and the plot then falls
    back to the largest coordinate it was given, which is still a better axis than a constant.
    That is also the one case where the sequences are not known independently of the
    mutations, so the list is what the mutations name and the busiest is the default.
    """
    from aledb_sample.models import ReferenceSequence

    counts = {row["mutation__reseq_reference"]: row["n"]
              for row in (get_evolved_call_queryset(experiment_id)
                          .values("mutation__reseq_reference")
                          .annotate(n=Count("id")))
              if row["mutation__reseq_reference"]}

    lengths = {}
    try:
        reference = ReferenceSequence.objects.get(experiment_id=experiment_id)
    except ReferenceSequence.DoesNotExist:
        reference = None
    if reference:
        for entry in reference.seq_ids or []:
            lengths[entry.get("id")] = entry.get("length")

    # The reference says what sequences there are; the mutations can only add to that, and a
    # contig named by a mutation but absent from the reference is a state worth still being
    # able to plot rather than one to drop silently.
    names = set(lengths) | set(counts)

    contigs = [{"id": name,
                "count": counts.get(name, 0),
                "length": lengths.get(name)}
               # Longest first, so the chromosome leads and the plasmids follow it. With no
               # stored reference every length is None and this degrades to busiest first,
               # which is the most the data alone can say. The name is the final tie-break, or
               # two equal contigs swap places between page loads and the default becomes
               # whichever the database felt like.
               for name in sorted(names, key=lambda n: (-(lengths.get(n) or 0),
                                                        -counts.get(n, 0), n))]

    ids = [entry["id"] for entry in contigs]
    chosen = contig if contig in ids else (ids[0] if ids else None)

    return {"contig": chosen,
            "length": lengths.get(chosen),
            "contigs": contigs}


def get_needle_plot_data(experiment_id, contig=None):
    """`{coord, category, value}` per mutation call, computed now.

    **Nothing is stored.** `StaticData` held this as a JSON blob kept current through the
    `static_data` rebuilder, and it was the oldest cache on the page -- precomputed at import
    since long before the rebuild registry existed. Reading three columns as tuples instead of
    instantiating the rows costs 0.05s on the largest experiment in the dev database, 52 139
    calls, against 3.38s for the model-instance path above.

    That number is what removes the failure mode the `ensure_fresh` here existed for. `/stats`
    renders this *and* `get_experiment_summary` from the same mutations, and while both were
    stored they could disagree in the same viewport -- one refreshed, the other stale. Neither
    is stored now and both read `get_mutation_call_queryset`, so they cannot.

    Ordered, and deliberately: the plot does not care, but "the same points in a different
    order" is a difference a reader would have to rule out by hand every time this is compared
    against the reference implementation, and the sort is free at this size.

    **Unfiltered.** It applied the shared experiment filter until that filter became a
    per-reader one, and `/stats` is not one of the pages that honours it -- this is a summary of
    what the experiment holds, like the dashboard, rather than a table you are reading through.
    Two columns rather than four: the gene and the experiment were fetched only to apply the
    ignored-gene list per row.
    """
    queryset = get_evolved_call_queryset(experiment_id)
    if contig:
        # Scoped to one contig, because `coord` carries no sequence name and two contigs'
        # positions on one axis is a plot of nothing. See `needle_plot_axis`.
        queryset = queryset.filter(mutation__reseq_reference=contig)
    rows = queryset.order_by(*ROW_ORDER).values_list(
        "mutation__position", "mutation__mutation_type",
    ).iterator(chunk_size=2000)

    return [{'coord': str(position), 'category': mutation_type, 'value': 1}
            for position, mutation_type in rows]
