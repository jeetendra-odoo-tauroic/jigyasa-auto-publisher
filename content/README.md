# Daily ZIP location

Upload exactly one file per day to this folder:

`content/YYYY-MM-DD/jigyasa-daily.zip`

Replace YYYY-MM-DD with the current date in India. The ZIP itself should contain all four image/JSON pairs at the ZIP root:

- 07-00.jpg + 07-00.json
- 10-00.jpg + 10-00.json
- 13-30.jpg + 13-30.json
- 20-30.jpg + 20-30.json

Commit the ZIP before the first publishing slot. The scheduled publisher opens the ZIP and chooses the matching pair for the current slot. Each JSON should include a caption and image filename/path. See the repository README for full instructions.
