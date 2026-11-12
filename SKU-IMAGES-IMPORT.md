# CSV import contract: SKU + Images only

The lightweight CSV contains **only** `SKU,Images`, with exactly one row per product, and five URLs separated by commas inside a **quoted CSV cell**. The first URL is intended as the main image.

Public media directory (already established for the live site):
`public_html/public/storage/marche-provence-images/`

URL base:
`https://marcheprovence.com/storage/marche-provence-images/`

Example:
```csv
SKU,Images
M115,"https://marcheprovence.com/storage/marche-provence-images/m115-marat-avignon-blue-white-70-inch-round-tablecloth-main.webp,https://marcheprovence.com/storage/marche-provence-images/m115-marat-avignon-blue-white-70-inch-round-tablecloth-alternate.webp"
```

## Import limitation

**The standard Botble 15-column product importer is NOT verified to accept this minimal file.** Do not run this two-column file through the full-product importer; that could fail or unintentionally overwrite product fields.

Before importing, create or verify a dedicated image-only importer that looks up the existing product by exact unique SKU; rejects missing/duplicate SKUs; validates file existence, WebP and expected 800x800 dimensions; sets primary image to first URL and product gallery to the provided URLs; leaves all other columns and database properties untouched; and gives a dry-run report.

If the files are already available under this site's media directory, the importer should attach those paths rather than needlessly re-download them.

## Current workflow

New batch export:
`reports/sku-images-only-STAGING-DO-NOT-UPLOAD.csv`

This file is generated after 100 product sets are technically completed. It must not be imported until image upload and visual fidelity checks have passed. The separate image-alt/title metadata CSV is not imported by this two-column mapping.
