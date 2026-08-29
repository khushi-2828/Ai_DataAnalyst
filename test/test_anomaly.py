import pandas as pd

from utils.anomaly_detection import detect_anomalies


df = pd.DataFrame({

    "Month": [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun"
    ],

    "Revenue": [
        10000,
        11000,
        10500,
        12000,
        11500,
        50000
    ]
})


anomalies = detect_anomalies(df)


print("\n==============================")
print("ANOMALIES")
print("==============================")


for anomaly in anomalies:

    print(anomaly)