# Jigyasa Auto Publisher

Daily Facebook publishing uses one ZIP package per date. ChatGPT creates the actual images and post copy; you upload one ZIP to GitHub, and the scheduled GitHub Actions publisher selects the matching image and JSON for each slot.

## Daily process

1. Ask ChatGPT to create one ZIP containing all four posts.
2. In this repository, create/open `content/YYYY-MM-DD/` using the India-local date.
3. Upload the single ZIP as `jigyasa-daily.zip` inside that dated folder and commit it to the default branch.
4. GitHub Actions reads the ZIP at each scheduled slot and publishes the matching image/caption to Facebook.

## Required ZIP structure

The ZIP must contain these files at its root (a README may also be included):

- `07-00.jpg` and `07-00.json`
- `10-00.jpg` and `10-00.json`
- `13-30.jpg` and `13-30.json`
- `20-30.jpg` and `20-30.json`

Each JSON must have at least a non-empty `caption` and an `image` field. Recommended fields are `date`, `slot`, `topic`, `title`, `caption`, `hashtags`, and `image`. Use the matching image filename in `image`, such as `content/YYYY-MM-DD/07-00.jpg` or `07-00.jpg`.

## Schedule (India time)

- 07:00
- 10:00
- 13:30
- 20:30

## Required GitHub secrets

Under **Settings → Secrets and variables → Actions → Secrets**, configure:

- `FACEBOOK_PAGE_ID`
- `FACEBOOK_PAGE_ACCESS_TOKEN`

Never commit access tokens or API keys.

## Important

- The ZIP must be uploaded before the first scheduled slot if you want all four posts published that day.
- The publisher checks the ZIP and matching files at runtime. A missing/corrupt ZIP or missing slot pair causes that slot to fail.
- Manual workflow dispatch publishes immediately; use it only when you intend to publish.
- The publisher also retains backwards compatibility with older separate image/JSON files.
- Successful publishing still depends on valid Facebook credentials and Page permissions.
