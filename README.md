# Jigyasa Auto Publisher

This repository publishes four prepared ChatGPT-created image posts to a Facebook Page each day. **Image creation is done in ChatGPT; GitHub does not generate or redraw the images.** You upload the generated image files and matching JSON metadata once per day, and GitHub Actions handles scheduled Facebook publishing.

## Daily workflow

1. Ask ChatGPT to create four topic-specific images, Hindi titles, captions and hashtags.
2. Upload the four image files and four matching JSON files into `content/YYYY-MM-DD/`.
3. Commit/push the files to the default branch.
4. GitHub Actions publishes the four posts at **07:00, 10:00, 13:30 and 20:30 India time**.

See [content/README.md](content/README.md) for the exact file names and JSON format.

## One-time setup

In **Settings → Secrets and variables → Actions → Secrets**, configure:

- `FACEBOOK_PAGE_ID`: Facebook Page ID.
- `FACEBOOK_PAGE_ACCESS_TOKEN`: Page access token with permission to publish photos to that Page.

Never commit tokens or API keys to the repository.

## Test carefully

The workflow's **Run workflow** option publishes to the Facebook Page; it is not a dry run. First verify the dated JSON and image file paths, and use a manual run only when you intend to publish that slot.

## Notes

- Scheduled GitHub Actions jobs can occasionally start a little late.
- GitHub Actions publishes only the post files that exist for the current India-local date and configured slot.
- Automatic image generation workflows are disabled for scheduled runs so they do not create substitute Pillow drawings. ChatGPT-generated images remain the intended image source.
