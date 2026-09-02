from django.apps import AppConfig


class NeedleConfig(AppConfig):
    name = 'aledb_needle'

    def ready(self):
        from aledb_common.about_registry import register_about_section
        from aledb_common.panel_registry import register_overview_panel
        from aledb_needle.panel import needle_panel_context

        # **No URLs and no nav entry**, which makes this the first component that is neither.
        # Compare, fixation and converge are each a page reached from the sidebar; this is a
        # panel on a page core already owns, and until `panel_registry` existed there was no
        # way to be one without living in core. See aledb_common/panel_registry.py.
        register_overview_panel(self, name='needle_plot',
                                title='Mutation Needle Plot',
                                template='needle/panel.html',
                                context=needle_panel_context)
        register_about_section(self, name='aledb-needle',
                               template='about/sections/aledb_needle.html')
