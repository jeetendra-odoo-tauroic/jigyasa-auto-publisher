# AI Social Post Publisher

GitHub Actions automatically creates original social posts with the OpenAI API, saves the image and post metadata in this repository, and publishes the image and caption to a Facebook Page.

## Automated flow

1. A scheduled GitHub Actions run starts at the configured India-time slots.
2. The OpenAI text model generates the topic, title, caption, hashtags and image prompt.
3. The OpenAI image model generates the image.
4. The workflow commits the JPG and JSON metadata under `content/YYYY-MM-DD/`.
5. The workflow publishes the same image and caption to Facebook.

## Required GitHub Actions secret

In **Settings → Secrets and variables → Actions → Secrets**, add:

- `OPENAI_API_KEY`: API key for OpenAI API access.
- `FACEBOOK_PAGE_ID`: Facebook Page ID.
- `FACEBOOK_PAGE_ACCESS_TOKEN`: Page access token with the permissions required to publish photos.

A ChatGPT subscription does not include OpenAI API usage; API billing is separate.

## Optional repository variables

In **Settings → Secrets and variables → Actions → Variables**, these values are optional:

- `OPENAI_TEXT_MODEL` (default `gpt-4.1-mini`)
- `OPENAI_IMAGE_MODEL` (default `gpt-image-1`)
- `OPENAI_IMAGE_QUALITY` (default `medium`)
- `BRAND_NAME` (default `Jigyasa`)
- `CONTENT_NICHE` (default Hindi educational content, science, history, technology and everyday knowledge)
- `POST_LANGUAGE` (default `Hindi`)
- `TARGET_AUDIENCE` (default general audience in India)

## Schedule and manual test

The workflow runs on its schedule in `.github/workflows/publish.yml`. It can also be started from **Actions → AI Social Post Publisher → Run workflow**. A manual run publishes to the configured Facebook Page, so only use it when ready.

## Files

- `generate_post.py`: generates post text and image with OpenAI.
- `publish.py`: publishes the generated image and caption to Facebook.
- `.github/workflows/publish.yml`: schedules generation, commits output and publishes it.

Never commit API keys or page tokens to source control.
