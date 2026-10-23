# Daily Facebook post files

For each India-local posting date, add exactly these four image/JSON pairs:

- `content/YYYY-MM-DD/07-00.jpg` and `07-00.json`
- `content/YYYY-MM-DD/10-00.jpg` and `10-00.json`
- `content/YYYY-MM-DD/13-30.jpg` and `13-30.json`
- `content/YYYY-MM-DD/20-30.jpg` and `20-30.json`

## JSON format

Each JSON file must contain a caption and the path to its matching image. Example for the 7 AM slot:

```json
{
  "date": "YYYY-MM-DD",
  "slot": "07:00",
  "topic": "Topic for this post",
  "title": "Short Hindi title",
  "caption": "Hindi caption followed by hashtags",
  "hashtags": "#Jigyasa #HindiThoughts",
  "image": "content/YYYY-MM-DD/07-00.jpg"
}
```

Replace the example date with the actual India-local date. The `image` path must match the exact JPG/PNG filename in the repository. Use UTF-8 for Hindi text.

## Low-work daily routine

1. Generate four images and their captions with ChatGPT.
2. Create one date folder under `content/`.
3. Upload the four JPGs and four matching JSON files together in one GitHub commit.
4. GitHub Actions publishes each slot at 07:00, 10:00, 13:30 and 20:30 IST.

Do not put Facebook tokens, API keys or other secrets in these files. Publishing requires the repository secrets `FACEBOOK_PAGE_ID` and `FACEBOOK_PAGE_ACCESS_TOKEN`.
