# Image Agent — Workflow and acceptance

## Source of truth
Use the original 15-column Botble CSV export. Key by **ID and SKU**. The source website and original product images supplement this file. Never trust a product-title similarity match to decide image ownership.

## Five separate image roles
1. Main — clean, full product, neutral backdrop
2. Detail — genuine fabric detail, stitching and print
3. Alternate — different angle showing complete product
4. Lifestyle garden — natural use outdoors with appropriately selected people
5. Lifestyle dining — indoor or second real-life use; matching model where suitable

For sets and baskets, show all included components; never silently omit accessories. Do not fabricate a new fabric motif, printed logo, size, material, or included item. If references are insufficient, mark REVIEW and do not publish.

## Execution
Install Pillow (requirements.txt). Run `python agent.py plan --csv catalog.csv --output output`.
An image-generation service/operator MUST produce five separately reviewed source photos using original product references. Model identities and appearance should remain consistent for the two lifestyle photos when appropriate. Each image should be checked for print similarity before acceptance.

Convert approved input photos using `python agent.py convert --input staged-images --output approved-images`.
Each product folder uses the lowercase SEO-safe SKU, for example `approved-images/tt152/`. Every file must have the exact expected name shown in `output/manifest.csv`.
Only after review, place an `approved.flag` file in that SKU folder.

Upload WebP files to a **public HTTPS storage origin** with folder structure preserved, then run:
```
python agent.py export --csv catalog.csv --approved approved-images --public-base-url https://example.com/media/products --output output/images-only-import.csv
```
The output has the SAME 15 columns as the source. Only Image and Images change for approved, published products. All other values and unapproved/variation rows are preserved byte-for-byte at the cell level. Back up the store and test one SKU in a safe environment before any bulk import. Ensure the importer does not update other fields when reading this CSV.

## Not yet automated
AI image API connection, source-photo downloading, similarity QA, public-media upload, CI, and live-site importing are separate development tasks; this foundation does not claim to perform them. Store import and automatic production changes remain disabled.
