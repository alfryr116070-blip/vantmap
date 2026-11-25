"""Build vantmap-chatgpt.html from viewer_src.html with prompt.md and review.md embedded."""
import json, os
d = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(d, "viewer_src.html"), encoding="utf-8").read()
for key, f in (("__PROMPT__", "prompt.md"), ("__REVIEW__", "review.md")):
    txt = open(os.path.join(d, f), encoding="utf-8").read()
    src = src.replace(key, txt.replace("</script", "<\\/script"))
open(os.path.join(d, "vantmap-chatgpt.html"), "w", encoding="utf-8").write(src)
print("wrote vantmap-chatgpt.html")
