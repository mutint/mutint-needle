from django.apps import AppConfig


class NeedleConfig(AppConfig):
    name = 'mutint_needle'

    def ready(self):
        from mutint_common.about_registry import register_about_section
        from mutint_common.panel_registry import register_overview_panel
        from mutint_needle.panel import needle_panel_context
        from mutint_needle.version import __version__

        # **No URLs and no nav entry**, which makes this the first component that is neither.
        # Compare, fixation and converge are each a page reached from the sidebar; this is a
        # panel on a page core already owns, and until `panel_registry` existed there was no
        # way to be one without living in core. See mutint_common/panel_registry.py.
        register_overview_panel(self, name='needle_plot',
                                title='Mutation Needle Plot',
                                template='needle/panel.html',
                                context=needle_panel_context)
        register_about_section(self, name='mutint-needle', version=__version__,
                               template='about/sections/mutint_needle.html')
