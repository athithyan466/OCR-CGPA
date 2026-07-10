import json

GRADE_POINTS = {
    "O": 10,
    "A+": 9,
    "A": 8,
    "B+": 7,
    "B": 6,
    "C": 5,
    "RA": 0,
    "SA": 0,
    "U": 0,
    "W": 0
}


def parse(qwen_json: str):

    data = json.loads(qwen_json)

    subjects = data["subjects"]

    # Remove rows without semester
    subjects = [
        s for s in subjects
        if s.get("sem") not in ("", None)
    ]

    # Current semester = highest semester
    current_sem = max(int(s["sem"]) for s in subjects)

    # Keep only current semester
    subjects = [
        s for s in subjects
        if int(s["sem"]) == current_sem
    ]

    total_credit = 0
    weighted = 0

    for s in subjects:

        credit = float(s["credits"])

        grade = s["grade"].strip().upper()

        gp = GRADE_POINTS.get(grade, 0)

        total_credit += credit

        weighted += credit * gp

        s["gp"] = gp

    sgpa = round(weighted / total_credit, 3) if total_credit else 0

    return {
        "semester": current_sem,
        "subjects": subjects,
        "total_credits": total_credit,
        "sgpa": sgpa
    }