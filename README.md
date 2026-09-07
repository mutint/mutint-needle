# mutint-needle

The mutation needle plot for [MutInt](https://github.com/mutint/mutint-core), as a panel on the
experiment Overview.

**It is a panel and nothing else** — no URL, no sidebar entry, no model, no migration. The whole
of its integration is one registration:

```python
register_overview_panel(self, name='needle_plot', title='Mutation Needle Plot',
                        template='needle/panel.html', context=needle_panel_context)
```

`/stats` draws the heading and the rule; the panel's template is the body only, so components
cannot disagree about what a section on that page looks like. A panel that raises is dropped
with a logged warning rather than taking down the page.

Install it and the plot appears; leave it out and there is no empty section.

## Installing

```bash
git submodule add ../mutint-needle mutint-needle
```

MIT licensed. See [mutint-core](https://github.com/mutint/mutint-core) for the platform.
