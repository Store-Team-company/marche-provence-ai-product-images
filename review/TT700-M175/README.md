# TT700 and M175 — five-image WebP pilot

**Actual binary files are uploaded.** The branch now contains all ten verified 800×800 WebP images under [images/](./images/), and the two-product CSV at [TT700-M175-SKU-Images-GITHUB-RAW-TEST.csv](./TT700-M175-SKU-Images-GITHUB-RAW-TEST.csv).

Products:
- TT700 — 64-inch square Cassis Jacquard Red & Turquoise tablecloth (five image roles)
- M175 — 64-inch square Cassis 6-piece ensemble with napkins and bread basket (five image roles)

Each has 5 separate WebP files: **main**, **alternate**, **infographic**, **outdoor**, and **people**. Images remain **AI-generated drafts pending close comparison with the real textile and accessories**.

## Testing GitHub image downloads

GitHub raw-image URLs in the CSV point to the **immutable image commit** `314cd2902db52f5ffa2f6089f60affaa5095ac7f` and will work anonymously **only after this repository is made public**. Before importing, open the first image URL in a private/incognito browser window and verify that the response is a WebP image, not an HTML login page.

The file `TT700-M175-SKU-Images-GITHUB-RAW-TEST.csv` contains **only `SKU,Images`**. The existing Botble *full product importer* previously rejected this two-column format, and it must not be used for testing without a dedicated image-only importer. The normal Botble update pathway can modify unrelated product fields or associations.

To verify server-side fetching without changing a product, run:
```bash
curl -L --fail --silent --show-error -o /tmp/tt700-github-image-test.webp 'https://raw.githubusercontent.com/Store-Team-company/marche-provence-ai-product-images/314cd2902db52f5ffa2f6089f60affaa5095ac7f/review/TT700-M175/images/tt700-cassis-red-turquoise-64-inch-square-jacquard-tablecloth-main.webp'
file /tmp/tt700-github-image-test.webp
```

If this returns a valid WebP from the server, GitHub download access works. A **dedicated SKU + Images importer** is still needed to apply the two-column CSV to products. Do not change your live catalog or mark generated images as faithful merchandise photographs until QA passes.

Alternative server upload CSV: `TT700-M175-SKU-Images-SERVER-READY.csv` uses your existing public server folder `public_html/public/storage/marche-provence-images/` and is not the direct-GitHub test.

Status: **GitHub images + two-column CSV pushed; public access and Botble import not yet verified.**
