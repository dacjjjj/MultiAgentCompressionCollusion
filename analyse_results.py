import json, glob

# Find most recent experiment file
files = sorted(glob.glob("results/experiment_*.json"))
if not files:
    print("No experiment results found")
    exit()

latest = files[-1]
print(f"Analysing: {latest}\n")

data = json.load(open(latest))

# Find the attack that got through in compressed condition
print("=" * 60)
print("ATTACK CASES THAT EVADED DETECTION (compressed condition)")
print("=" * 60)

compressed_results = data["results"]["compressed"]
for r in compressed_results:
    if r["mode"] == "ATTACK" and not r["collusion_detected"]:
        print(f"\nTest {r['test_id']} - {r['task_name']}")
        print(f"\n--- ORIGINAL CODE (what Agent A wrote) ---")
        print(r["agent_a_output"][:500])
        print(f"\n--- COMPRESSED VERSION (what monitor saw) ---")
        print(r["compressed_output"][:500])
        print(f"\n--- AGENT B REVIEW ---")
        print(r["agent_b_output"][:300])
        print(f"\n--- MONITOR ON CODE ---")
        print(f"Safe: {r['monitor_a_safe']}")
        print(f"Reasoning: {r['monitor_a_reasoning'][:300]}")
        print(f"\n--- MONITOR ON REVIEW ---")
        print(f"Safe: {r['monitor_b_safe']}")
        print(f"Reasoning: {r['monitor_b_reasoning'][:300]}")

# Compare same test across conditions
print("\n" + "=" * 60)
print("ALL ATTACK RESULTS BY CONDITION")
print("=" * 60)
print(f"{'Task':<20} {'Baseline':<12} {'Compressed':<12} {'Monitor-Full':<12}")
print("-" * 56)

baseline = {r["task_name"]: r for r in data["results"]["baseline"] if r["mode"] == "ATTACK"}
compressed = {r["task_name"]: r for r in data["results"]["compressed"] if r["mode"] == "ATTACK"}
monitor_full = {r["task_name"]: r for r in data["results"]["monitor_full"] if r["mode"] == "ATTACK"}

for task_name in baseline:
    b = "CAUGHT" if baseline[task_name]["collusion_detected"] else "MISSED"
    c = "CAUGHT" if compressed.get(task_name, {}).get("collusion_detected", False) else "MISSED"
    m = "CAUGHT" if monitor_full.get(task_name, {}).get("collusion_detected", False) else "MISSED"
    print(f"{task_name:<20} {b:<12} {c:<12} {m:<12}")
