"""What the Overview panel is handed.

Separate from `util.py` so the derivation can be tested without a request and without the
panel machinery -- the same split `aledb_filter` draws between the filter value and what
applies it, and for the same reason: `util` is two queries over core's models, and this is
the one place that knows a panel is rendered from a URL.
"""

from aledb_needle.util import get_needle_plot_data, needle_plot_axis


def needle_panel_context(experiment, request):
    """The context `needle/panel.html` renders from.

    `?contig=` is the sequence picker's own parameter, in the URL rather than the session so a
    plasmid's plot is a link somebody can send. An unrecognised value falls back to the
    default, which is the reference's longest sequence -- see `needle_plot_axis`.

    `ale_no` is read back out only so the picker's links preserve an ALE the reader arrived
    with, through `get_ale_id` rather than a second reading of the same parameter.
    """
    from aledb_seq.views.common import get_ale_id

    axis = needle_plot_axis(experiment.id, request.GET.get("contig"))
    return {
        "ale_experiment_id": experiment.id,
        "ale_no": get_ale_id(request),
        "needle_axis": axis,
        # Handed to the page through `json_script`, not as a Python repr interpolated into a
        # JS literal -- which is what `mark_safe(list(...))` was, and which only worked
        # because a repr of this particular shape happens to be valid JavaScript.
        "needle_plot_data": list(get_needle_plot_data(experiment.id, axis["contig"])),
    }
