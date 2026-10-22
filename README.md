# Jigyasa Auto Publisher

Automatically creates and publishes Hindi science/knowledge posts to the Jigyasa Facebook Page using GitHub Actions.

## What runs automatically

The workflow schedules posts at 7:00 AM, 10:00 AM, 1:30 PM, and 8:30 PM India time, plus a temporary 4:10 PM test slot configured in `.github/workflows/publish.yml`.

Each run:
1. Selects a fact from the curated fact bank in `generate_post.py`.
2. If `POLLINATIONS_API_KEY` is configured, attempts to generate a rich AI illustration using Pollinations' `flux` image model.
3. Overlays the Hindi fact and Jigyasa branding, then saves a 1080×1350 JPG and caption JSON under `content/YYYY-MM-DD/`.
4. Publishes the JPG and caption using Facebook Graph API via `publish.py`.

## AI image provider: Pollinations

- Create an API key at [enter.pollinations.ai](https://enter.pollinations.ai/) and save it as the GitHub Actions secret `POLLINATIONS_API_KEY`.
- The workflow uses the `flux` model. The API reference we checked listed it at **0.001 Pollen per image**, but prices, free credits, model availability, and rate limits can change. Check your current account balance and the [Pollinations API documentation](https://gen.pollinations.ai/docs) before enabling it.
- This is a **free-tier / credit-based option, not a guarantee of unlimited free generation**. Do not add a payment method or buy credits unless you explicitly choose to.
- If the key is missing, generation fails, or the provider returns an error (including insufficient balance), the script falls back to its local Pillow background and still creates a JPG. A fallback post will not have an AI-generated illustration.
- This calls Pollinations, not ChatGPT's built-in image generator.

## Required GitHub Actions secrets

In **Settings → Secrets and variables → Actions**, configure:
- `FACEBOOK_PAGE_ID`: Facebook Page ID.
- `FACEBOOK_PAGE_ACCESS_TOKEN`: valid Page access token with the required publishing permissions.
- `POLLINATIONS_API_KEY`: optional key for AI-generated backgrounds.

Never put tokens in source files or commit them to the repository.

## Test manually

Open **Actions → Jigyasa Facebook Image Publisher → Run workflow**, choose a slot and run it. This publishes a real post to the configured Facebook Page, so use it only when you are ready to publish.

## Files

- `generate_post.py`: fact selection, optional AI background generation, and JPG creation.
- `publish.py`: Facebook Graph API photo publishing.
- `.github/workflows/publish.yml`: scheduled generation and publishing workflow.
