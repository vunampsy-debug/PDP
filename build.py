from pathlib import Path
import ast
import base64
import io
import re
import zipfile

wrapper = Path("api/index.py")
text = wrapper.read_text(encoding="utf-8")
match = re.search(r"PAYLOAD=('(?:[^'\\\\]|\\\\.)*')", text)
if not match:
    raise RuntimeError("Embedded application payload was not found")

payload = ast.literal_eval(match.group(1))
with zipfile.ZipFile(io.BytesIO(base64.b64decode(payload))) as archive:
    archive.extractall(Path("."))

# The extracted app.py is now the real FastAPI entrypoint.
# Remove the legacy wrapper so Vercel does not package two Python functions.
wrapper.unlink(missing_ok=True)
