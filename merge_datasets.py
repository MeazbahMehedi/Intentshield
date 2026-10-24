
import json
from pathlib import Path
from collections import Counter

DATA_DIR = Path("promptguard") / "data"
PROMPT_FILE = DATA_DIR / "prompt_cases.json"
ATTACK_FILE = DATA_DIR / "attack_payloads.json"
OUTPUT_FILE = DATA_DIR / "combined_cases.json"


def load_json(path):
    if not path.is_file():
        raise FileNotFoundError(f"Source file not found: {path}")

    with path.open("r", encoding="utf-8-sig") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError(f"{path} must contain a JSON array.")

    return data


def main():
    prompts = load_json(PROMPT_FILE)
    attacks = load_json(ATTACK_FILE)

    combined = []

    for item in prompts:
        combined.append({
            "id": str(item["id"]),
            "prompt": item["prompt"],
            "expected_label": item["expected_label"].lower(),
            "category": item["category"],
            "severity": item.get("severity"),
            "reason": item.get("reason", ""),
        })

    for item in attacks:
        combined.append({
            "id": str(item["id"]),
            "prompt": item.get("prompt", item.get("payload", "")),
            "expected_label": "attack",
            "category": item["category"],
            "severity": item.get("severity"),
            "reason": item.get(
                "reason",
                f"Attack payload from category {item['category']}"
            ),
        })

    ids = [item["id"] for item in combined]
    duplicates = [
        key for key, count in Counter(ids).items()
        if count > 1
    ]

    if duplicates:
        raise ValueError(f"Duplicate IDs found: {duplicates}")

    for item in combined:
        if item["expected_label"] not in {"attack", "safe"}:
            raise ValueError(f"Invalid label in {item['id']}")
        if not item["prompt"].strip():
            raise ValueError(f"Empty prompt in {item['id']}")

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(combined, file, indent=2, ensure_ascii=False)
        file.write("\n")

    labels = Counter(item["expected_label"] for item in combined)

    print("Dataset merged successfully.")
    print(f"Total records: {len(combined)}")
    print(f"Label counts: {dict(labels)}")
    print(f"Duplicate IDs: {duplicates}")
    print(f"Output file: {OUTPUT_FILE.resolve()}")


if __name__ == "__main__":
    main()
