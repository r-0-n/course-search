import json

tests = json.load(open("data/test_set.json", encoding="utf-8"))
required = {"id","question","type","source","locations"}
problems = 0
for i, t in enumerate(tests, start=1):
    missing = required - set(t.keys())
    extra = set(t.keys()) - required
    bad_types = []
    if "locations" in t and not isinstance(t["locations"], list):
        bad_types.append("locations is not a list")
    if "source" in t and not str(t["source"]).strip():
        bad_types.append("source is empty")
    if missing or extra or bad_types:
        problems += 1
        print(f"Item #{1} (id={t.get('id')}): "
              f"missing={sorted(missing)} unexpected={sorted(extra)} {bad_types}")

print(f"\n{len(tests)} items checked, {problems} with problems")
