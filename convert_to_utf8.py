# convert_to_utf8.py
with open("share_data.json", "r", encoding="utf-16") as f:
    text = f.read()

with open("share_data_utf8.json", "w", encoding="utf-8") as f:
    f.write(text)

print("✅ Converted to UTF-8 (BOMなし): share_data_utf8.json")
