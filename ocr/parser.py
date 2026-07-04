
from __future__ import annotations

import re
import time
import unicodedata
from dataclasses import dataclass, field
from typing import Optional



@dataclass
class Subject:


    sem: Optional[int] = None
    part: Optional[int] = None
    code: str = ""
    name: str = ""
    credit: Optional[float] = None
    result: Optional[str] = None
    grade: Optional[str] = None
    gp: Optional[float] = None

    def to_dict(self) -> dict:
        return {
            "sem": self.sem,
            "part": self.part,
            "code": self.code,
            "name": self.name,
            "credit": self.credit,
            "result": self.result,
            "grade": self.grade,
            "gp": self.gp,
        }

    def is_complete(self) -> bool:

        return bool(self.code) and self.credit is not None and self.gp is not None


@dataclass
class ParseDiagnostics:


    total_lines: int = 0
    matched_lines: int = 0
    unmatched_lines: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    elapsed_ms: float = 0.0

    def to_dict(self) -> dict:
        return {
            "total_lines": self.total_lines,
            "matched_lines": self.matched_lines,
            "unmatched_lines": self.unmatched_lines,
            "warnings": self.warnings,
            "elapsed_ms": round(self.elapsed_ms, 2),
        }



class GPAParser:


    GRADE_POINTS: dict = {
        "O": 10.0,
        "A+": 9.0,
        "A": 8.0,
        "B+": 7.0,
        "B": 6.0,
        "C": 5.0,
        "U": 0.0,
        "RA": 0.0,
        "SA": 0.0,  # shortage of attendance / absent, treated as 0 credit-bearing
        "W": 0.0,   # withheld -> no grade point, but kept for completeness
    }

    VALID_RESULTS = {"PASS", "FAIL"}


    _CODE_CORE = re.compile(r"\b([A-Z]{2,3})\s*([0-9OIl]{3,4})([A-Z]?)\b")

    _CODE_LOCATOR = re.compile(
        r"[€£A-Z]{1}[A-Z]{1,2}\s*[0-9OIl]{3,4}[A-Z]*"
    )

    _NUMBER_TOKEN = re.compile(r"\d{1,2}[.,]\s?\d{1,2}")

    _RESULT_TOKEN = re.compile(r"\b(PASS|FAIL|P4SS|FA1L)\b", re.IGNORECASE)

    _GRADE_TOKEN = re.compile(
        r"\bA\s?\+|\bA\s?t\b|\bB\s?\+|\bB\s?t\b|\bO\b|\b0\b|\bA\b|\bB\b|\bC\b|\bU\b"
    )

    _LEADING_SEM_PART_ISOLATED = re.compile(
        r"^\s*([SsOo]?\d{1,2}[SsOo]?)\.?\s+([SsOo]?\d{1,2}[SsOo]?)\.?\s*$"
    )
    _LEADING_SEM_ONLY_ISOLATED = re.compile(r"^\s*([SsOo]?\d{1,2}[SsOo]?)\.?\s*$")

    _TITLE_PATTERN = re.compile(
        r"RESULTS?\s+OF\s+.*?SEMESTER.*", re.IGNORECASE
    )

    _HEADER_KEYWORDS = re.compile(
        r"\b(ANNA\s+UNIVERSITY|CHENNAI|RESULTS?\s+OF|DEGREE\s+EXAMINATIONS?|"
        r"REGULATIONS?|CONTROLLER\s+OF\s+EXAMINATIONS?|SEM\s+PART\s+COURSE|"
        r"COURSE\s+CODE|COURSE\s+TITLE|TOTAL\s+CREDITS?|GRADE\s+POINTS?\s+"
        r"AVERAGE|^SGPA\b|^CGPA\b)\b",
        re.IGNORECASE,
    )

    _MULTISPACE = re.compile(r"[ \t]{2,}")
    _STRAY_PUNCT = re.compile(r"[|_~^`]+")
    _MULTI_NEWLINE = re.compile(r"\n{2,}")

    _MERGED_CODE_NAME = re.compile(
        r"^([A-Z]{2,3}[0-9OIl]{3,4})([A-Z]{2,}.*)$"
    )

    _DIGIT_OCR_MAP = {"O": "0", "o": "0", "I": "1", "l": "1", "S": "5"}
    _LETTER_OCR_MAP = {"€": "C", "£": "C", "0": "O", "1": "I"}

    def __init__(self) -> None:
        self._warnings: list = []


    def parse(self, raw_text: str) -> dict:

        result, _ = self._run(raw_text)
        return result

    def parse_with_diagnostics(self, raw_text: str) -> dict:

        result, diagnostics = self._run(raw_text)
        result["diagnostics"] = diagnostics.to_dict()
        return result


    def _run(self, raw_text: str) -> tuple:
        start = time.perf_counter()
        self._warnings = []
        diagnostics = ParseDiagnostics()

        if not raw_text or not raw_text.strip():
            diagnostics.warnings.append("Empty OCR input received.")
            return self._empty_result(), diagnostics

        normalized = self.normalize_text(raw_text)
        lines = self.clean_lines(normalized)
        diagnostics.total_lines = len(lines)

        title = self.extract_title(lines)
        current_semester = self._semester_from_title(title)

        subjects: list = []
        unmatched: list = []

        for line in lines:
            if self._is_header_or_title_line(line):
                continue
            subject = self.parse_subject_line(line)
            if subject is not None and subject.is_complete():
                subjects.append(subject)
                diagnostics.matched_lines += 1
            else:
                if self._looks_like_subject_candidate(line):
                    unmatched.append(line)

        subjects = self._dedupe_subjects(subjects)
        subjects = self._resolve_semester_part(subjects, title=title)
        # Repair semester after all OCR parsing is complete
        for subject in subjects:
            if subject.sem != current_semester:
                subject.sem = current_semester

        current_subjects = subjects
        history_subjects = []

        total_credits, sgpa = self.calculate_sgpa(current_subjects)

        diagnostics.unmatched_lines = unmatched
        diagnostics.warnings.extend(self._warnings)
        diagnostics.elapsed_ms = (time.perf_counter() - start) * 1000

        result = {
    "exam_title": title,
    "current_semester": current_semester,

    "subjects": [s.to_dict() for s in current_subjects],

    "history_subjects": [
        s.to_dict() for s in history_subjects
    ],

    "total_credits": total_credits,
    "sgpa": sgpa,
}
        return result, diagnostics

    @staticmethod
    def _empty_result() -> dict:
        return {
            "exam_title": "",
            "subjects": [],
            "total_credits": 0.0,
            "sgpa": 0.0,
        }


    def normalize_text(self, text: str) -> str:

        text = unicodedata.normalize("NFKC", text)

    
        text = re.sub(r'(\d),(\d{2})', r'\1.\2', text)

        
        text = re.sub(r'\b([1-6])00\b', r'\1.00', text)


        text = re.sub(
            r'(PASS|FAIL)\s+0\s+(\d+\.\d+)',
            r'\1 O \2',
            text,
            flags=re.IGNORECASE
        )

        text = text.replace("\u00a0", " ")

        text = self._STRAY_PUNCT.sub(" ", text)

        text = self._MULTI_NEWLINE.sub("\n", text)

        lines = text.split("\n")

        lines = [self._MULTISPACE.sub(" ", ln).strip() for ln in lines]

        return "\n".join(lines)


    def clean_lines(self, normalized_text: str) -> list:

        raw_lines = normalized_text.split("\n")
        cleaned = []
        for line in raw_lines:
            line = line.strip(" .:;,-")
            if not line:
                continue
            if self._is_noise_line(line):
                continue
            cleaned.append(line)
        return cleaned

    @staticmethod
    def _is_noise_line(line: str) -> bool:

        if len(line) < 2:
            return True
        if not any(ch.isalnum() for ch in line):
            return True
        stripped = line.replace(" ", "")
        if len(set(stripped)) == 1 and stripped[0] in "-=_*":
            return True
        return False


    def extract_title(self, lines: list) -> str:

        for line in lines:
            match = self._TITLE_PATTERN.search(line)
            if match:
                title = match.group(0)
                title = self._MULTISPACE.sub(" ", title).strip()
                return title.upper()
        self._warnings.append("Could not locate an exam title line.")
        return ""


    def _looks_like_subject_candidate(self, line: str) -> bool:

        return bool(self._CODE_LOCATOR.search(line))

    def _is_header_or_title_line(self, line: str) -> bool:

        if self._HEADER_KEYWORDS.search(line):
            return True
        if self._TITLE_PATTERN.search(line):
            return True
        return False

    def parse_subject_line(self, line: str) -> Optional[Subject]:

        code_match = self._CODE_LOCATOR.search(line)
        if not code_match:
            return None

        code_raw = code_match.group(0)
        remainder_after_code = line[code_match.end():]
        prefix_before_code = line[: code_match.start()]

        code, leftover_name_prefix = self.normalize_course_code(code_raw)
        if not code:
            return None

        subject = Subject(code=code)

        sem, part, prefix_remainder = self._extract_sem_part(prefix_before_code)
        subject.sem = sem
        subject.part = part

        body = (leftover_name_prefix + " " + remainder_after_code).strip()

        name, credit, rest = self._extract_name_and_credit(body)
        subject.name = name
        subject.credit = credit

        result, grade, gp = self._extract_result_grade_gp(rest)
        subject.result = result
        subject.grade = grade
        subject.gp = gp

        subject.grade, subject.gp = self._reconcile_grade_and_gp(
            subject.grade, subject.gp
        )

        if subject.result is None and subject.grade is not None:
            subject.result = "FAIL" if subject.grade in ("U", "RA") else "PASS"

        if not subject.name:
            self._warnings.append(f"No subject name extracted for {code} from line: {line!r}")

        return subject


    def normalize_course_code(self, raw_code: str) -> tuple:

        token = raw_code.strip()

        token = "".join(self._LETTER_OCR_MAP.get(ch, ch) if ch in "€£" else ch for ch in token)

        m = re.match(r"^([A-Z]{2,3})\s*([0-9OIlS]{3,4})([A-Z].*)?$", token)
        if not m:
            self._warnings.append(f"Unrecognized course code token: {raw_code!r}")
            return "", ""

        letters, digits_raw, trailing = m.group(1), m.group(2), m.group(3) or ""

        digits = "".join(self._DIGIT_OCR_MAP.get(ch, ch) for ch in digits_raw)

        if not digits.isdigit() or len(digits) not in (3, 4):
            self._warnings.append(f"Course code digits invalid after repair: {raw_code!r}")
            return "", ""

        normalized_code = f"{letters}{digits}"

        leftover = trailing.strip()

        return normalized_code, leftover


    def _extract_sem_part(self, prefix: str) -> tuple:
       
        prefix = prefix.strip()
        two = self._LEADING_SEM_PART_ISOLATED.match(prefix)
        if two:
            sem = self._clean_sem_token(two.group(1))
            part = self._clean_sem_token(two.group(2))
            return sem, part, ""

        one = self._LEADING_SEM_ONLY_ISOLATED.match(prefix)
        if one:
            sem = self._clean_sem_token(one.group(1))
            return sem, None, ""

        tail_numbers = re.findall(r"\d{1,2}", prefix)

        if tail_numbers:
                sem = self._clean_sem_token(tail_numbers[-2]) if len(tail_numbers) >= 2 else self._clean_sem_token(tail_numbers[-1])
                part = self._clean_sem_token(tail_numbers[-1]) if len(tail_numbers) >= 2 else None

    # OCR correction for semester column
    # If the Part column is 3 (common in Anna University)
    # and the Semester OCR became 7/1/etc., repair it.
                if part == 3 and sem in (1, 7):
                     sem = 4

                return sem, part, prefix

        return None, None, prefix

    @staticmethod
    def _clean_sem_token(token: str) -> Optional[int]:

        if token is None:
            return None
        token = (
        token.upper()
         .replace("S", "5")
         .replace("O", "0")
         .replace("I", "1")
         .replace("L", "1")
)

        digits = re.sub(r"[^0-9]", "", token)
        if not digits:
            return None
        try:
            value = int(digits)
        except ValueError:
            return None
        return value if 1 <= value <= 8 else None

    def _resolve_semester_part(self, subjects: list, title: str = "") -> list:

        known_sems = [s.sem for s in subjects if s.sem is not None]
        majority_sem = None
        if known_sems:
            majority_sem = max(set(known_sems), key=known_sems.count)
        elif title:
            majority_sem = self._semester_from_title(title)

        for s in subjects:
            if s.sem is None and majority_sem is not None:
                s.sem = majority_sem
            if s.part is None:
                s.part = s.sem
        return subjects

    _ORDINAL_WORDS = {
        "FIRST": 1, "SECOND": 2, "THIRD": 3, "FOURTH": 4,
        "FIFTH": 5, "SIXTH": 6, "SEVENTH": 7, "EIGHTH": 8,
    }

    def _semester_from_title(self, title: str) -> Optional[int]:

        upper = title.upper()
        for word, num in self._ORDINAL_WORDS.items():
            if word in upper:
                return num
        numeric = re.search(r"\b([1-8])(?:ST|ND|RD|TH)?\s+SEMESTER\b", upper)
        if numeric:
            return int(numeric.group(1))
        return None


    def _extract_name_and_credit(self, body: str) -> tuple:

        body = body.strip(" -:")
        if not body:
            return "", None, ""

        match = self._NUMBER_TOKEN.search(body)
        if not match:
            return self._clean_name(body), None, ""

        name_part = body[: match.start()]
        credit_raw = match.group(0)
        rest = body[match.end():]
        credit = self.normalize_numbers(credit_raw)

        if credit is not None:

            # Common OCR mistakes
             if credit == 9.0:
                credit = 3.0
        elif credit == 8.0:
                credit = 3.0
        elif credit == 5.0:
                credit = 3.0
        elif credit == 40.0:
                credit = 4.0
        elif credit == 30.0:
                credit = 3.0
        elif credit == 20.0:
                credit = 2.0
        elif credit == 10.0:
                credit = 1.0
        elif credit == 15.0:
                credit = 1.5

            # Reject impossible credits
        if credit not in (1.0, 1.5, 2.0, 3.0, 4.0):
                credit = None

        name = self._clean_name(name_part)
        return name, credit, rest

    @staticmethod
    def _clean_name(name_part: str) -> str:
        name = name_part.strip(" -:")
        name = re.sub(r"\s{2,}", " ", name)
        name = re.sub(r"^\d+\s+", "", name)
        return name.strip().upper()


    def _extract_result_grade_gp(self, rest: str) -> tuple:

        result = None
        result_match = self._RESULT_TOKEN.search(rest)
        if result_match:
            result = self._normalize_result(result_match.group(0))

        grade = None
        grade_search_text = rest
        if result_match:
            grade_search_text = rest[: result_match.start()] + " " + rest[result_match.end():]

        for gm in self._GRADE_TOKEN.finditer(grade_search_text):
            candidate = self.normalize_grade(gm.group(0))
            if candidate:
                grade = candidate
                break

        gp = None
        numbers = self._NUMBER_TOKEN.findall(rest)
        if numbers:
            gp_candidate = self.normalize_numbers(numbers[-1])
            if gp_candidate is not None and 0.0 <= gp_candidate <= 10.0:
                gp = gp_candidate

        return result, grade, gp

    @staticmethod
    def _normalize_result(token: str) -> str:
        token = token.upper()
        if token in ("P4SS",):
            return "PASS"
        if token in ("FA1L",):
            return "FAIL"
        return token

    def normalize_grade(self, token: str) -> Optional[str]:

        if token is None:
            return None
        cleaned = token.strip().replace(" ", "")
        upper = cleaned.upper()

        if upper in ("AT", "A+"):
            return "A+"
        if upper in ("BT", "B+"):
            return "B+"
        if upper == "0":
            return "O"
        if upper in self.GRADE_POINTS:
            return upper
        return None

    def _reconcile_grade_and_gp(self, grade: Optional[str], gp: Optional[float]) -> tuple:

        if grade is not None and gp is None:
            return grade, self.GRADE_POINTS.get(grade)

        if grade is None and gp is not None:
            reverse = {v: k for k, v in self.GRADE_POINTS.items() if k not in ("RA", "SA", "W")}
            return reverse.get(gp), gp

        if grade is not None and gp is not None:
            expected = self.GRADE_POINTS.get(grade)
            if expected is not None and expected != gp:
                self._warnings.append(
                    f"Grade/GP mismatch: grade={grade} implies {expected}, "
                    f"OCR read gp={gp}. Using grade-derived value."
                )
                return grade, expected

        return grade, gp


    def normalize_numbers(self, token: str) -> Optional[float]:

        if token is None:
            return None
        cleaned = token.strip()
        cleaned = cleaned.replace(",", ".")
        cleaned = re.sub(r"\s+", "", cleaned)
        cleaned = re.sub(r"[^0-9.]", "", cleaned)
        if not cleaned or cleaned == ".":
            return None
        try:
            return round(float(cleaned), 2)
        except ValueError:
            return None


    @staticmethod
    def _dedupe_subjects(subjects: list) -> list:

        seen = set()
        unique = []
        for s in subjects:
            if s.code in seen:
                continue
            seen.add(s.code)
            unique.append(s)
        return unique


    def calculate_sgpa(self, subjects: list) -> tuple:

        total_credits = 0.0
        weighted_sum = 0.0

        for s in subjects:
            if s.credit is None or s.gp is None:
                self._warnings.append(
                    f"Excluded {s.code or '<unknown>'} from SGPA: missing credit or gp."
                )
                continue
            total_credits += s.credit
            weighted_sum += s.credit * s.gp

        if total_credits <= 0:
            return 0.0, 0.0

        sgpa = round(weighted_sum / total_credits, 3)
        total_credits = round(total_credits, 2)
        return total_credits, sgpa



_default_parser = GPAParser()


def parse(raw_text: str) -> dict:

    return GPAParser().parse(raw_text)


def parse_with_diagnostics(raw_text: str) -> dict:

    return GPAParser().parse_with_diagnostics(raw_text)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) > 1:
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            text = f.read()
    else:
        text = sys.stdin.read()

    output = parse_with_diagnostics(text)
    print(json.dumps(output, indent=2))