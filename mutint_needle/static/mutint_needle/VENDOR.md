# Vendored assets

Committed rather than fetched from a CDN so a deployment works with no outbound network, the
same reason `igv.min.js` is vendored in mutint-core and phylotree in mutint-phylogeny.

| file | source | sha256 |
|---|---|---|
| `muts-needle-plot/build/muts-needle-plot.js` | npm `muts-needle-plot` | `92edb206…` |
| `muts-needle-plot/build/muts-needle-plot.css` | npm `muts-needle-plot` | `474ead23…` |
| `muts-needle-plot/src/js/dependencies/d3.js` | npm `muts-needle-plot` | `48bc2f9e…` |
| `muts-needle-plot/src/js/dependencies/underscore.js` | npm `muts-needle-plot` | `53596846…` |
| `muts-needle-plot/src/js/d3-svg-legend.js` | npm `muts-needle-plot` | `624adae6…` |

**No version is recorded, and it cannot be recovered.** These arrived as an `npm install` of
[muts-needle-plot](https://github.com/bbglab/muts-needle-plot) committed into the repository
long before this file existed, under a `node_modules/` directory in mutint-core's own static
files — no `package.json` came with them and nothing anywhere says which release they are. The
hashes above are therefore of the files **as vendored**, which is drift detection and not
provenance: they were never checked against a published artifact and cannot be. Anybody
upgrading this library is choosing a version for the first time.

`d3.js` here is **3.5.1**, which the library was built against and which is not
interchangeable with a modern d3. mutint-phylogeny bundles its own d3 7 inside
`phylotree.min.js`, so the two never meet on a page; nothing else in the suite loads d3.

**One line is patched, in the build and its source alike.** `MutsNeedlePlot.prototype.drawLegend`
began `self = this;` with no `var`, which in sloppy mode assigns the plot to the **global**
`self` -- `window.self`, which every page has and which library code uses as "the window". The
next script to do so was the DataTables Buttons bundle that `base.html` loads after the page's
content: its FileSaver shim takes `self` as the window, reads `self.document`, and threw
`Cannot read properties of undefined (reading 'createElementNS')` on every page with a needle
plot. The line is `var self = this;` now, as the library's other methods already have it, and
the hash above is of the patched file. Upgrading the library must carry the patch, or check
that upstream fixed it.

Four files are vendored and not loaded: `src/js/MutsNeedlePlot.js` and
`src/css/muts-needle-plot.css` are the sources of the two `build/` files, `d3.min.js` is the
minified twin of the `d3.js` that is loaded, and `README.md` is what says where any of this
came from. They are kept because with no version recorded, the tree as it stands is the only
provenance there is.
