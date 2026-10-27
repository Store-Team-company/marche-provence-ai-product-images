# TT250 / M283 — SOURCE REFERENCE AND PHOTOGRAPHY QA
Status: **REVIEW — NOT IMPORTABLE** (2026-10-27)

This branch does not modify the website and contains no approved catalog image files. It must not be merged or used for a Botble image-only import until all 10 WebP images pass visual QA and are uploaded.

## TT250 — Tissus Toselli Cigale Blue & Yellow TIDY Bread Basket
- SKU: TT250
- Catalog source: https://marcheprovence.com/storage/magento-products/tiby_cig_blu.jpg
- 8 × 8 in, four yellow corner bows, watercolor-like blue ground, green leaves and yellow cicadas.
- Source listing confirms coated cotton and rigid panels.
- Export contains **one** original photo.
- The chat produced two *local screenshot-derived reference drafts*: studio-format source photo and infographic. These are **not** new AI-generated angles, have not been uploaded here, and are not approved.
- Missing: accurate different-angle photo, unoccupied lifestyle setting, people lifestyle setting.

## M283 — Bastide Blue Delft Jacquard Placemat
- SKU: M283
- Primary reference: https://marcheprovence.com/storage/magento-products/bast_blu_blu_delf.jpg
- 19 × 13 in rectangular placemat; blue Delft-style jacquard center; blue-and-white filigree cadre border.
- Three other gallery images in the product export are *matching runner, napkin, and bread basket*, **not** additional placemat photos:
  - https://marcheprovence.com/storage/magento-products/tab_run_60_bast_blu_wht_3.jpg
  - https://marcheprovence.com/storage/magento-products/nap_bast_blu_whit_4.jpg
  - https://marcheprovence.com/storage/magento-products/tidy_bast_blu_wht_2.jpg
- Exact original image bytes could not be retrieved in this session, so no alternate pattern was invented.

## Required gate before importer CSV
1. Use original exact product photos as visual inputs to native image generation.
2. Five standalone 800×800 RGB WebP images per SKU (main, alternate, infographic, outdoor, people).
3. Reject wrong colors, motifs, borders, construction, and unsupported claims.
4. GitHub binary upload required; verify actual Git blobs and byte signatures.
5. Only after upload: CSV with **SKU,Images** and five true commit-pinned raw.githubusercontent.com URLs per SKU.
6. Do not import any CSV without human fidelity approval.

No OpenAI API key or third-party generation services were used. No website changes were made.
