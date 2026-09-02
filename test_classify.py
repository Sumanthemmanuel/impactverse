"""
Quick regression tests for the classification service.
Run with:  python3 test_classify.py
(No pytest required — plain asserts with printed output, so it's fast to run
mid-hackathon without extra setup.)
"""

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def post(text, lat, lng):
    return client.post("/classify", json={"text": text, "lat": lat, "lng": lng}).json()


def check(label, condition):
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {label}")
    assert condition, label


if __name__ == "__main__":
    print("Health check:", client.get("/health").json())
    print()

    # Two reports of the same problem, close together, different wording
    r1 = post("Contaminated water coming from the village handpump, several people fell sick",
               23.3441, 85.3096)
    r2 = post("Handpump water is dirty and contaminated near our village",
               23.3450, 85.3100)
    print("Report 1:", r1)
    print("Report 2:", r2)
    check("Report 1 classified as Water Resources", r1["domain"] == "Water Resources")
    check("Report 2 flagged as duplicate of report 1", r2["is_duplicate"] is True)
    print()

    # Same wording as report 1, but far away -> must NOT be treated as duplicate
    r3 = post("Contaminated water coming from the village handpump, several people fell sick",
               24.0000, 85.9000)
    print("Report 3 (same text, far away):", r3)
    check("Far-away identical report is NOT flagged as duplicate", r3["is_duplicate"] is False)
    print()

    # Unrelated domain with high-severity keywords -> should score high priority
    r4 = post("The roof of the government school classroom collapsed, urgent repair needed",
               23.6100, 85.2799)
    print("Report 4 (school, severe):", r4)
    check("Report 4 classified as Education", r4["domain"] == "Education")
    check("Report 4 has elevated priority from severity keywords", r4["priority_score"] > 5)
    print()

    print("All checks passed.")
