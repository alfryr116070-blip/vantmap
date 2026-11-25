# Vantmap for ChatGPT (no coding tools)

1. Open `prompt.md`, replace the goal line with yours, and paste the whole prompt into ChatGPT (a model with web browsing).
2. It returns one JSON block in a **lighter, separate format** (`{vantmap:1, teams, routes, stages, …}`, defined in `prompt.md`) — not the repository's `map.json` schema.
3. Optional but recommended: paste `review.md` into a **new** chat together with that JSON. It re-opens every link and marks claims it can't confirm.
4. Open `vantmap-chatgpt.html` in a browser (double-click; no server) and paste or drop the JSON in.

Limits: a single chat can't run the two independent judges or the daily update, so treat the result as watch-list quality until it is checked. To turn a direction into a full repository map, run `/vantmap:vantmap-new-map` in Claude Code (you can give it the ChatGPT result as a starting list of teams).

`viewer_src.html` is the template; `vantmap-chatgpt.html` is built from it with the two prompts embedded (`python3 build.py`).
