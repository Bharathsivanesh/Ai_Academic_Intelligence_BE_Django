import pandas as pd
import numpy as np
from intelligence.models import Student, StudentMarks

def generate_dataset():
    rows = []

    students = Student.objects.all()

    for student in students:
        marks = StudentMarks.objects.filter(student=student).select_related("exam")

        iat1_scores = []
        iat2_scores = []
        iat3_scores = []

        for mark in marks:
            if mark.max_marks == 0:
                continue

            pct = (mark.obtained_marks / mark.max_marks) * 100
            exam_type = mark.exam.exam_type

            if exam_type == "IAT1":
                iat1_scores.append(pct)
            elif exam_type == "IAT2":
                iat2_scores.append(pct)
            elif exam_type == "IAT3":
                iat3_scores.append(pct)

        if not iat1_scores and not iat2_scores and not iat3_scores:
            continue

        iat1 = sum(iat1_scores) / len(iat1_scores) if iat1_scores else 0
        iat2 = sum(iat2_scores) / len(iat2_scores) if iat2_scores else 0
        iat3 = sum(iat3_scores) / len(iat3_scores) if iat3_scores else 0
        avg  = (iat1 + iat2 + iat3) / 3

        fail = 1 if avg < 50 else 0

        rows.append({
            "iat1": iat1,
            "iat2": iat2,
            "iat3": iat3,
            "avg":  avg,
            "fail": fail,
        })

    real_df = pd.DataFrame(rows)

    # ✅ Synthetic balanced data so model learns both pass and fail
    np.random.seed(42)
    synthetic_rows = []

    # Failing students (avg < 50) — 100 samples
    for _ in range(100):
        iat1 = np.random.uniform(5, 49)
        iat2 = np.random.uniform(5, 49)
        iat3 = np.random.uniform(5, 49)
        avg  = (iat1 + iat2 + iat3) / 3
        synthetic_rows.append({"iat1": iat1, "iat2": iat2, "iat3": iat3, "avg": avg, "fail": 1})

    # Passing students (avg >= 50) — 100 samples
    for _ in range(100):
        iat1 = np.random.uniform(50, 100)
        iat2 = np.random.uniform(50, 100)
        iat3 = np.random.uniform(50, 100)
        avg  = (iat1 + iat2 + iat3) / 3
        synthetic_rows.append({"iat1": iat1, "iat2": iat2, "iat3": iat3, "avg": avg, "fail": 0})

    synthetic_df = pd.DataFrame(synthetic_rows)

    # Combine real + synthetic
    final_df = pd.concat([real_df, synthetic_df], ignore_index=True)

    print(f"✅ Dataset: {len(real_df)} real + {len(synthetic_df)} synthetic = {len(final_df)} total")
    print(f"✅ Class balance:\n{final_df['fail'].value_counts()}")

    return final_df