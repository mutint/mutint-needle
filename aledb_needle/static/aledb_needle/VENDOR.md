# Vendored assets

Committed rather than fetched from a CDN so a deployment works with no outbound network, the
same reason `igv.min.js` is vendored in aledb-core and phylotree in aledb-phylogeny.

| file | source | sha256 |
|---|---|---|
| `muts-needle-plot/build/muts-needle-plot.js` | npm `muts-needle-plot` | `57f77da9…` |
| `muts-needle-plot/build/muts-needle-plot.css` | npm `muts-needle-plot` | `474ead23…` |
| `muts-needle-plot/src/js/dependencies/d3.js` | npm `muts-needle-plot` | `48bc2f9e…` |
| `muts-needle-plot/src/js/dependencies/underscore.js` | npm `muts-needle-plot` | `53596846…` |
| `muts-needle-plot/src/js/d3-svg-legend.js` | npm `muts-needle-plot` | `624adae6…` |

**No version is recorded, and it cannot be recovered.** These arrived as an `npm install` of
[muts-needle-plot](https://github.com/bbglab/muts-needle-plot) committed into the repository
long before this file existed, under a `node_modules/` directory in aledb-core's own static
files — no `package.json` came with them and nothing anywhere says which release they are. The
hashes above are therefore of the files **as vendored**, which is drift detection and not
provenance: they were never checked against a published artifact and cannot be. Anybody
upgrading this library is choosing a version for the first time.

`d3.js` here is **3.5.1**, which the library was built against and which is not
interchangeable with a modern d3. aledb-phylogeny bundles its own d3 7 inside
`phylotree.min.js`, so the two never meet on a page; nothing else in the suite loads d3.

Four files are vendored and not loaded: `src/js/MutsNeedlePlot.js` and
`src/css/muts-needle-plot.css` are the sources of the two `build/` files, `d3.min.js` is the
minified twin of the `d3.js` that is loaded, and `README.md` is what says where any of this
came from. They are kept because with no version recorded, the tree as it stands is the only
provenance there is.
