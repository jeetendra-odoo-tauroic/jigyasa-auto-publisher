# Jigyasa Auto Publisher

Automatically creates and publishes Hindi science/knowledge image cards to the Jigyasa Facebook Page four times per day.

## What runs automatically

GitHub Actions runs at **7:00 AM, 10:00 AM, 1:30 PM and 8:30 PM India time** (UTC cron equivalents are in `.github/workflows/publish.yml`).

Each run:
1. Selects one fact from the curated offline fact bank in `generate_post.py`.
2. Creates a 1080×1350 PNG image and a caption JSON under `content/YYYY-MM-DD/`.
3. Publishes the image and caption using Facebook Graph API via `publish.py`.

## Cost and limitations

- No paid AI API is called. Generation uses Python and Pillow to render a designed image card from the local curated fact bank.
- **This does not call ChatGPT's built-in image generator**, and it does not create a new AI illustration. The image is a text-led graphic card.
- The fact bank is finite. Add and fact-check new entries in `FACTS` in `generate_post.py` periodically to keep topics fresh and reduce repetition.
- GitHub Actions is cloud-hosted; no personal computer needs to remain on.
- Scheduled workflows can be delayed by GitHub and are not a guaranteed exact-minute delivery service.

## Required GitHub Actions secrets

In **Settings → Secrets and variables → Actions**, configure:
- `FACEBOOK_PAGE_ID`: the Facebook Page ID.
- `FACEBOOK_PAGE_ACCESS_TOKEN`: a valid Page access token with the required publishing permissions.

Never put tokens in source files or commit them to the repository.

## Test manually

Open **Actions → Jigyasa Facebook Image Publisher → Run workflow**, choose a slot and run it. This will **publish a real post** to the configured Facebook Page; use only when you are ready to publish.

## Files

- `generate_post.py`: offline fact selection and image-card generation.
- `publish.py`: Facebook Graph API photo publishing.
- `.github/workflows/publish.yml`: scheduled generation and publishing workflow.
