import pandas as pd

df = pd.read_csv("data/transactions.csv", parse_dates=["timestamp"])
df = df.sort_values(["card_id", "timestamp"])

small = df[(df["amount"] <= 3.0) & (df["merchant_category"] == "online")]

flagged = set()
for card_id, g in small.groupby("card_id"):
    times = g["timestamp"].tolist()
    ids = g["txn_id"].tolist()
    start = 0
    for end in range(len(times)):
        while times[end] - times[start] > pd.Timedelta(minutes=10):
            start += 1
        if end - start + 1 >= 5:
            flagged.update(ids[start:end + 1])

df["flagged"] = df["txn_id"].isin(flagged).astype(int)

tp = ((df["flagged"] == 1) & (df["is_fraud"] == 1)).sum()
fp = ((df["flagged"] == 1) & (df["is_fraud"] == 0)).sum()
fn = ((df["flagged"] == 0) & (df["is_fraud"] == 1)).sum()

precision = tp / (tp + fp) if (tp + fp) else 0
recall = tp / (tp + fn) if (tp + fn) else 0

print(f"Flagged: {len(flagged)} | TP: {tp} FP: {fp} FN: {fn}")
print(f"Precision: {precision:.3f}  Recall: {recall:.3f}")