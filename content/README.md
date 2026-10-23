# Daily ZIP format

Upload a single file named `daily-posts.zip` at the repository root. Inside it, place the four image/JSON pairs under `content/YYYY-MM-DD/`, where the date is today's date in Asia/Kolkata.

The Python publisher reads only the matching time slot's JSON and image from the ZIP. Required slots and names:

- `07-00.jpg` / `07-00.json`
- `10-00.jpg` / `10-00.json`
- `13-30.jpg` / `13-30.json`
- `20-30.jpg` / `20-30.json`

Each JSON requires non-empty `caption` and `image` fields; `image` must be the exact ZIP member path, for example `content/YYYY-MM-DD/07-00.jpg`.

See the repository README for the full process and required Facebook secrets.
