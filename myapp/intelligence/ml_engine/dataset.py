import pandas as pd
from intelligence.models import Student, StudentMarks, StudentExam

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

        # skip student if no data at all
        if not iat1_scores and not iat2_scores and not iat3_scores:
            continue

        iat1 = sum(iat1_scores) / len(iat1_scores) if iat1_scores else 0
        iat2 = sum(iat2_scores) / len(iat2_scores) if iat2_scores else 0
        iat3 = sum(iat3_scores) / len(iat3_scores) if iat3_scores else 0
        avg  = (iat1 + iat2 + iat3) / 3

        # label: fail = 1 if average below 40%
        fail = 1 if avg < 40 else 0

        rows.append({
            "student_id": student.id,
            "iat1": iat1,
            "iat2": iat2,
            "iat3": iat3,
            "avg":  avg,
            "fail": fail,
        })

    return pd.DataFrame(rows)