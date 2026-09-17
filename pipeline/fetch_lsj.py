import urllib.request
import os

BASE = "https://raw.githubusercontent.com/PerseusDL/lexica/master/CTS_XML_TEI/perseus/pdllex/grc/lsj/"
DEST = os.path.join(os.path.dirname(__file__), "..", "data", "lsj")
os.makedirs(DEST, exist_ok=True)

for i in range(1, 28):
    fname = f"grc.lsj.perseus-eng{i}.xml"
    dest_path = os.path.join(DEST, fname)
    if os.path.exists(dest_path) and os.path.getsize(dest_path) > 0:
        print(f"skip (exists): {fname}")
        continue
    url = BASE + fname
    urllib.request.urlretrieve(url, dest_path)
    print(f"downloaded: {fname} ({os.path.getsize(dest_path)} bytes)")

print("DONE")
