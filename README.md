# Jigyasa Auto Publisher

Upload **one date-stamped ZIP file** to the repository root. The required filename format is `daily-posts-YYYY-MM-DD.zip`, where the date is the current date in India time. GitHub Actions calculates today's date in `Asia/Kolkata`, opens only that day's ZIP, and publishes the matching post for each scheduled slot.

## Daily process

1. Prepare four images, Hindi captions and JSON metadata in a single ZIP.
2. Name the ZIP using today's India-local date, for example `daily-posts-2026-10-23.zip`.
3. Ensure the ZIP contains this exact structure:

```text
daily-posts-YYYY-MM-DD.zip
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

4. Each JSON must contain a non-empty `caption` and `image` path. Example:

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

The `image` value must exactly match the image path inside the ZIP. Each slot's JSON must reference that slot's image.

5. Upload the newly dated ZIP to the repository root and commit it. You may keep older dated ZIPs; the publisher selects today's filename and does not use yesterday's ZIP.
6. GitHub Actions reads the matching JSON and image from today's ZIP and publishes at **07:00, 10:00, 13:30 and 20:30 IST**.

## Required GitHub secrets

Under **Settings → Secrets and variables → Actions → Secrets**, configure:

- `FACEBOOK_PAGE_ID`
- `FACEBOOK_PAGE_ACCESS_TOKEN` with permission to publish photos to your Page

Never put tokens in the ZIP or source code.

## Important

- Both the ZIP filename date and its internal folder date must match today's date in India time.
- If today's ZIP is missing or its expected post/image is missing, the publisher stops with an error instead of silently using an older package.
- Scheduled runs may start a little late.
- Running the publisher manually publishes a real Facebook post immediately.
- The code has been updated to require the date-stamped ZIP, but successful publishing still needs to be confirmed in GitHub Actions after secrets and a valid ZIP are in place.
