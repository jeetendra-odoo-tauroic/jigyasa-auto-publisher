# Jigyasa Auto Publisher

Upload **one ZIP file** named `daily-posts.zip` to the repository root. GitHub Actions' scheduled publisher reads the correct post from inside that ZIP at each slot and sends the matching image and caption to your Facebook Page.

## Daily process

1. Ask ChatGPT to prepare today's four images, Hindi captions and JSON metadata in a single ZIP.
2. Ensure the ZIP contains this exact structure, using today's date in India time:

```text
daily-posts.zip
└── content/
    └── YYYY-MM-DD/
        ├── 07-00.jpg
        ├── 07-00.json
        ├── 10-00.jpg
        ├── 10-00.json
        ├── 13-30.jpg
        ├── 13-30.json
        ├── 20-30.jpg
        └── 20-30.json
```

3. Each JSON must contain a non-empty `caption` and `image` path. Example:

```json
{
  "date": "YYYY-MM-DD",
  "slot": "07:00",
  "topic": "A topic",
  "title": "A Hindi title",
  "caption": "Hindi caption and hashtags",
  "hashtags": "#Jigyasa #HindiThoughts",
  "image": "content/YYYY-MM-DD/07-00.jpg"
}
```

The `image` value must exactly match the image's path inside the ZIP. Image paths must stay within the ZIP's content folder. The JSON file for each slot must reference that slot's matching image.

4. Upload or replace `daily-posts.zip` at the repository root and commit the change. Do not upload four separate ZIPs.
5. GitHub Actions automatically reads the slot's JSON and image from the ZIP and publishes at **07:00, 10:00, 13:30 and 20:30 IST**.

## Required GitHub secrets

Under **Settings → Secrets and variables → Actions → Secrets**, configure:

- `FACEBOOK_PAGE_ID`
- `FACEBOOK_PAGE_ACCESS_TOKEN` with permission to publish photos to your Page

Never put tokens in the ZIP or source code.

## Important

- Replace the ZIP daily with a package containing the current India-local date. Old dated packages will not publish as today's posts.
- Scheduled runs may start a little late.
- Running the publisher manually publishes a real Facebook post immediately.
- The publisher retains backward compatibility with individual dated files if `daily-posts.zip` is absent.
- This repository code has been updated for ZIP reading, but successful publishing must still be confirmed in GitHub Actions after secrets and a valid ZIP are in place.
