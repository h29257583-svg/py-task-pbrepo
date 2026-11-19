import base64, json, os, pathlib

val = os.environ.get("RCLONE_CONFIG_VAL", "").strip()
if not val:
    raise SystemExit("RCLONE_CONFIG_VAL is empty")

if "[" not in val:
    val = base64.b64decode(val).decode("utf-8")

out_lines = []
for line in val.splitlines():
    if line.strip().startswith("token") and "=" in line:
        k, v = line.split("=", 1)
        raw = v.strip()
        try:
            json.loads(raw)
        except Exception:
            if raw.startswith("{") and raw.endswith("}"):
                obj = {}
                for part in raw[1:-1].split(","):
                    if ":" in part:
                        pk, pv = part.split(":", 1)
                        pk = pk.strip().strip('"').strip("'")
                        pv = pv.strip().strip('"').strip("'")
                        obj[pk] = int(pv) if pv.isdigit() else pv
                line = f"{k.strip()} = {json.dumps(obj)}"
    out_lines.append(line)

cfg = pathlib.Path.home() / ".config/rclone/rclone.conf"
cfg.parent.mkdir(parents=True, exist_ok=True)
cfg.write_text("\n".join(out_lines) + "\n", encoding="utf-8")
os.chmod(cfg, 0o600)
print("rclone.conf prepared successfully")
