# The needle plot

One needle per mutation call, drawn along the axis of one of the reference's sequences and
colored by mutation type. It sits on an experiment's Overview page (`/stats`), under the
counts and the sample table, and it is drawn from the mutations as they stand — there is
nothing stored to keep current, so it cannot disagree with the tables beside it.

## It draws one sequence at a time

A reference is often more than one sequence: a chromosome and one or more plasmids. The plot
shows **one of them**, with a picker above it when there is more than one.

!!! warning "Two contigs on one axis is a plot of nothing"

    Laying them end to end would need offsets the reader cannot see, and every coordinate on
    the plot would then match nothing in the mutation tables. So the axis belongs to one
    sequence and says which one.

**The default is the longest sequence** — the chromosome, on a reference that also carries
plasmids — and not the one carrying the most mutations. A small plasmid under strong selection
can outnumber the chromosome, and a page opening on the plasmid would be a surprise about the
reference dressed up as a fact about the data. Length is a property of the reference; a
mutation count moves with the data.

Every sequence in the reference is listed, with its mutation count beside it, **including one
with no mutations at all**. Selecting it draws an empty axis, which is an answer: you asked
what is on the plasmid and the plot says nothing is. A sequence left out of the menu would be
indistinguishable from one the reference does not have.

The choice is in the URL — `?experiment_id=4&contig=pXYZ` — so a particular sequence's
plot is a link you can send.

## What the axis is

The sequence's length, read from the stored reference. With **no** stored reference — an
experiment imported from bare `.gd` files — there are no lengths at all, so the axis falls back
to the largest coordinate in the data, which is still truer than a constant. That fallback is
also why the picker's order degrades to most-mutations-first there: length is the ordering when
it is known, and nothing else is available when it is not.

## What it does not do

- **It does not apply your view filter.** The Overview summarizes what the experiment holds, in
  the way the dashboard does, rather than being a table you read rows through. The mutation
  tables are where filtering applies.
- **It does subtract the ancestor**, like every other derivation: an ancestral mutation is in
  every sample by construction and would be a needle in every plot.

## Installing it

This component contributes no page and no sidebar entry — it is a panel on a page mutint-core
owns, registered through `panel_registry`. Adding it as a submodule of an assembled project is
all there is to it; a deployment without it simply has no such section on the Overview.
