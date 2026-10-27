# TT250 & M283 image redesign — QA GATE

**STATUS: INCOMPLETE — DO NOT IMPORT.** The assets directory contains **8 individual 800×800 WebP files**, not a complete 10-image batch.

| SKU | Main | Detail/alternate | Infographic | Outdoor | People |
|---|---|---|---|---|---|
| TT250 | Draft | Draft detail crop | Draft | **Missing** | **Missing** |
| M283 | Draft | Draft | Draft | Draft | Draft |

## Fidelity checks
- TT250: primary reference is the actual blue watercolor/mottled background, sparse cicada motif, slender green leaves, **yellow/orange** four corner ties. Earlier lifestyle renders were rejected for adding repeated cicadas and wrong pattern; not staged.
- TT250 detail file is a crop of the newly corrected main photo, not a distinct camera-angle generation.
- M283: blue Delft jacquard field and white-blue filigree cadre border. The manufacturer's exact print has not been established visually from its website file; 5 previous standalone concepts are staged **as drafts only**.
- Product facts from the customer CSV: TT250 = 8×8-inch acrylic-coated cotton tie-up basket (description corroborated on site); M283 = 19×13-inch jacquard woven blue Delft center placemat.

## Files
- `images/`: 8 actual WebP binary files, each 800×800, verified against Git SHA.
- `SEO-and-QA-review.csv`: image names, title and alt text.
- `M283-SKU-Images-PREVIEW-ONLY.csv`: one product row with five immutable GitHub raw URLs for testing **Preview & Verify**, never clicking Apply until visually approved.

**There is no two-SKU import-ready CSV**, because the two TT250 lifestyle views are missing. The previous collage outputs were discarded.
No live-site or server changes were made. This branch is **review only**.
