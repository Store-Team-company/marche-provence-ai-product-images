# MP-IMAGE-01B: Unattended 100-product photography batch

This GitHub Actions job uses only OpenAI for AI image generation. It targets the first 100 published products from the user-provided 408-row catalog and creates five images per product.

## One-time setup
1. Create an OpenAI Platform API key with image-generation access, plus a sensible project spending limit. ChatGPT subscription access is not API billing.
2. Open repository Settings > Secrets and variables > Actions > New repository secret. Set **OPENAI_API_KEY** and paste the key there. Never share keys in code, issues, PRs or chat.
3. Enable GitHub Actions, and verify the GitHub Actions token can write repo contents and GitHub issues.
4. After this workflow is merged into the default branch, open Actions > Marche Provence 100-product autopilot > Run workflow. Subsequent scheduled hourly runs resume automatically.
5. Enable repository Watch notifications for Issues and Actions to receive the completion report.

## Unattended behavior
- Workflow: .github/workflows/automated-100.yml, hourly schedule and manual dispatch.
- 58-minute Actions job limit, 2,850-second generation budget, up to 35 NEW images per run, with resume across runs.
- The workflow writes only to the separate branch autopilot/staging-100; it does not deploy to the store.
- 5 roles per product: main, detail, alternate, lifestyle-garden, lifestyle-dining.
- Files in assets/<sku>/ have SEO-style filenames and exact 800x800 RGB WebP dimensions.
- Progress at reports/progress.csv and reports/summary.json.
- Proposed alt text and media title at reports/seo-image-metadata.csv.
- When 500 technically valid images exist, generate reports/images-only-import-STAGING-DO-NOT-UPLOAD.csv using the 15-column schema and changing ONLY Image and Images.
- URLs in staging import CSV are FUTURE media URLs; never import before matching images are uploaded and publicly available.
- GitHub issue MP-PHOTO-100-READY is created at technical completion.
- GitHub issue MP-PHOTO-SETUP-BLOCKED is created once if the OpenAI key is missing.

## Mandatory QA before deployment
Technical validation checks only file count, format and size. It CANNOT guarantee the print, border, color fidelity, accessory count or consistent people. Images remain NEEDS_VISUAL_QA until reviewed against original product references. AI-generated sample imagery must not misrepresent merchandise. No server upload or production import is enabled.

## Costs and rate limits
The OpenAI API is billed separately. Set a project spending cap before enabling. Image generation can take more than a few hours: network errors, provider rate limits, retries and visual corrections affect actual completion time. Partial products are checkpointed. Repeated failures are recorded in reports/failures.log.
