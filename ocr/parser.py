from __future__ import annotations

import re
from turtle import left, right

from sys import prefix
import unicodedata
from dataclasses import dataclass
from typing import Optional

from pyparsing import line, nums


# ============================================================================
# DATA MODEL
# ============================================================================

@dataclass
class Subject:

    arrear_sem: Optional[int] = None
    part: Optional[int] = None

    code: str = ""
    name: str = ""

    credit: Optional[float] = None

    result: Optional[str] = None
    grade: Optional[str] = None
    gp: Optional[float] = None

    def complete(self) -> bool:

        return (
            self.code != ""
            and self.credit is not None
            and self.grade is not None
            and self.gp is not None
        )

    def to_dict(self):

        return {
            "arrear_sem": self.arrear_sem,
            "part": self.part,
            "code": self.code,
            "name": self.name,
            "credit": self.credit,
            "result": self.result,
            "grade": self.grade,
            "gp": self.gp,
        }


# ============================================================================
# MAIN PARSER
# ============================================================================

class GPAParser:

    ##########################################################################
    # GRADE TABLE
    ##########################################################################

    GRADE_POINTS = {

        "O": 10.0,
        "A+": 9.0,
        "A": 8.0,
        "B+": 7.0,
        "B": 6.0,
        "C": 5.0,
        "U": 0.0,
        "RA": 0.0

    }

    GP_TO_GRADE = {

        10.0: "O",
        9.0: "A+",
        8.0: "A",
        7.0: "B+",
        6.0: "B",
        5.0: "C",
        0.0: "U"

    }

    ##########################################################################
    # OCR FIX TABLES
    ##########################################################################

    CREDIT_FIX = {

        "400": 4.00,
        "300": 3.00,
        "200": 2.00,
        "150": 1.50,
        "100": 1.00,
        "050": 0.50,

    }

    GP_FIX = {

        "1000": 10.00,
        "900": 9.00,
        "800": 8.00,
        "700": 7.00,
        "600": 6.00,
        "500": 5.00,
        "000": 0.00,

    }

    ##########################################################################
    # SEMESTER WORDS
    ##########################################################################

    ORDINAL = {

        "FIRST": 1,
        "SECOND": 2,
        "THIRD": 3,
        "FOURTH": 4,
        "FIFTH": 5,
        "SIXTH": 6,
        "SEVENTH": 7,
        "EIGHTH": 8

    }

    ##########################################################################
    # REGEX
    ##########################################################################

    TITLE_RE = re.compile(

        r"RESULTS?.*SEMESTER",
        re.I

    )

    CODE_RE = re.compile(
    r"\b([A-Z]{2,4})\s*([0-9OILS]{3,4})(?![0-9])",
    re.I
)

    NUMBER_RE = re.compile(

        r"\d+(?:[.,]\d+)?"

    )

    RESULT_RE = re.compile(

        r"\bPASS\b|\bFAIL\b|\bP4SS\b|\bFA1L\b",
        re.I

    )

    ##########################################################################
    # CONSTRUCTOR
    ##########################################################################

    def __init__(self):

        self.current_semester = None

        self.subjects = []

        self.warnings = []

    ##########################################################################
    # PUBLIC
    ##########################################################################

    def parse(self, raw_text):

        self.subjects.clear()

        self.warnings.clear()

        text = self.normalize(raw_text)

        lines = self.make_lines(text)

        self.current_semester = self.detect_semester(lines)

        self.extract_subjects(lines)

        self.subjects = self.remove_duplicates(self.subjects)

        total_credit, sgpa = self.calculate()

        return {

            "exam_title": self.extract_title(lines),

            "subjects": [

                s.to_dict()

                for s in self.subjects

            ],

            "total_credits": total_credit,

            "sgpa": sgpa

        }

    ##########################################################################
    # NORMALIZATION
    ##########################################################################

    def normalize(self, text):

        text = unicodedata.normalize("NFKC", text)

        text = text.replace("\u00A0", " ")

        text = text.replace("|", " ")

        text = text.replace("_", " ")

        text = text.replace("—", "-")

        text = re.sub(r"[ ]{2,}", " ", text)

        return text

    ##########################################################################
    # LINES
    ##########################################################################

    def make_lines(self, text):

        lines = []

        for line in text.split("\n"):

            line = line.strip()

            if not line:

                continue

            lines.append(line)

        return lines

    ##########################################################################
    # TITLE
    ##########################################################################

    def extract_title(self, lines):

        for line in lines:

            if self.TITLE_RE.search(line):

                return line.upper()

        return ""

    ##########################################################################
    # SEMESTER
    ##########################################################################

    def detect_semester(self, lines):

        title = self.extract_title(lines)

        title = title.upper()

        for word, number in self.ORDINAL.items():

            if word in title:

                return number

        m = re.search(

            r"([1-8])(ST|ND|RD|TH)?\s+SEMESTER",

            title

        )

        if m:

            return int(m.group(1))

        return None
    def extract_subjects(self, lines):

        for line in lines:

            subject = self.parse_line(line)

            if subject is None:
                continue

            if self.current_semester is not None:

                if subject.arrear_sem is None:
                    subject.arrear_sem = self.current_semester

            self.subjects.append(subject)
    def parse_line(self, line):


        code_match = self.CODE_RE.search(line)

        if not code_match:
            print("NO CODE")
            return None

        letters = code_match.group(1)
        digits = code_match.group(2)


        raw_code = letters + digits
        code = self.fix_course_code(raw_code)

        

        prefix = line[:code_match.start()].strip()
        suffix = line[code_match.end():].strip()

        

        arrear_sem, part = self.extract_sem_part(prefix)

        name, credit, remain = self.extract_name_credit(suffix)


        result, grade, gp = self.extract_result_grade_gp(remain)

        

        grade, gp = self.reconcile_grade_gp(grade, gp)

        print("after reconcile", grade, gp)
        subject = Subject()

        subject.arrear_sem = arrear_sem
        subject.part = part
        subject.code = code
        subject.name = name
        subject.credit = credit
        subject.result = result
        subject.grade = grade
        subject.gp = gp

        if not subject.complete():
            return None

        return subject
    def fix_course_code(self, token):

        token = token.upper()

        token = token.replace("€", "C")
        token = token.replace("£", "C")

        m = re.match(r"([A-Z]{2,4})([0-9OILS]{3,4})", token)

        if not m:
            return ""

        letters = m.group(1)

        digits = (
            m.group(2)
            .replace("O", "0")
            .replace("I", "1")
            .replace("L", "1")
            .replace("S", "5")
        )

        if len(digits) not in (3, 4):
            return ""

        return letters + digits
    def extract_sem_part(self, prefix):

        nums = re.findall(r"\d+", prefix)

        arrear_sem = None
        part = None

        if len(nums) >= 2:
            arrear_sem = int(nums[-2])
            part = int(nums[-1])

        elif len(nums) == 1:
            arrear_sem = int(nums[0])

        return arrear_sem, part

    def extract_name_credit(self, text):

        text = text.strip()

        nums = list(self.NUMBER_RE.finditer(text))

        if len(nums) == 0:

            return self.clean_name(text), None, ""

        credit_match = None

        for m in nums:

            value = self.fix_credit(m.group())

            if value is not None:

                credit_match = m

                credit = value

                break

        if credit_match is None:

            return self.clean_name(text), None, ""

        name = text[:credit_match.start()].strip()

        remain = text[credit_match.end():].strip()

        return self.clean_name(name), credit, remain

    def clean_name(self, name):

        name = name.upper()

        name = re.sub(r"\s+", " ", name)

        name = re.sub(r"([A-Z])\s([A-Z]{2,})", r"\1\2", name)

        name = re.sub(r"([A-Z]{2,})\s([A-Z])$", r"\1\2", name)

        return name.strip()
    def extract_result_grade_gp(self, text):

        result = None
        grade = None
        gp = None

        m = self.RESULT_RE.search(text)

        if m:

            result = m.group().upper()

            result = result.replace("P4SS", "PASS")

            result = result.replace("FA1L", "FAIL")

        g = re.search(
            r"\b(O|0|A\+|A|AT|BT|BR|B\+|B|C|U|RA)\b",
            text,
            re.I
        )

        if g:

            grade = self.fix_grade(g.group())

        nums = self.NUMBER_RE.findall(text)

        if len(nums):

            gp = self.fix_gp(nums[-1])

        return result, grade, gp

    def fix_grade(self, grade):

        grade = grade.upper().replace(" ", "")

        if grade == "0":
            return "O"

        if grade in ("AT", "AT+", "AT"):
            return "A+"

        if grade in ("BT", "BR"):
            return "B+"

        if grade in ("A+", "A", "B+", "B", "C", "O", "U", "RA"):
            return grade

        return None

    def reconcile_grade_gp(self, grade, gp):

        if gp is not None:

            grade = self.GP_TO_GRADE.get(gp, grade)

            return grade, gp

        if grade is not None:

            gp = self.GRADE_POINTS.get(grade)

            return grade, gp

        return grade, gp
    def fix_credit(self, token):

        if token is None:
            return None

        token = token.strip()

        token = token.replace(",", ".")
        token = token.replace(" ", "")

        token = token.replace("O", "0")
        token = token.replace("o", "0")
        token = token.replace("I", "1")
        token = token.replace("l", "1")

        token = re.sub(r"[^0-9.]", "", token)

        if token == "":
            return None

        if token in self.CREDIT_FIX:
            return self.CREDIT_FIX[token]

        try:

            value = float(token)

            if 0.0 <= value <= 6.0:
                return round(value, 2)

        except:
            pass

        return None

    def fix_gp(self, token):

        if token is None:
            return None

        token = token.strip()

        token = token.replace(",", ".")
        token = token.replace(" ", "")

        token = token.replace("O", "0")
        token = token.replace("o", "0")
        token = token.replace("I", "1")
        token = token.replace("l", "1")

        token = re.sub(r"[^0-9.]", "", token)

        if token == "":
            return None

        if token in self.GP_FIX:
            return self.GP_FIX[token]

        try:

            value = float(token)

            if 0.0 <= value <= 10.0:
                return round(value, 2)

        except:
            pass

        return None

    def remove_duplicates(self, subjects):

        seen = set()

        output = []

        for s in subjects:

            if s.code in seen:
                continue

            seen.add(s.code)

            output.append(s)

        return output

    def calculate(self):

        total_credit = 0.0

        total_points = 0.0

        for s in self.subjects:

            if s.credit is None:
                continue

            if s.gp is None:
                continue

            total_credit += s.credit

            total_points += s.credit * s.gp

        if total_credit == 0:

            return 0.0, 0.0

        sgpa = round(total_points / total_credit, 3)

        return round(total_credit, 2), sgpa

    def parse_with_diagnostics(self, raw_text):

        result = self.parse(raw_text)

        result["warnings"] = self.warnings

        return result


_default_parser = GPAParser()


def parse(raw_text):

    return _default_parser.parse(raw_text)


def parse_with_diagnostics(raw_text):

    return _default_parser.parse_with_diagnostics(raw_text)


if __name__ == "__main__":

    import json
    import sys

    if len(sys.argv) > 1:

        with open(sys.argv[1], "r", encoding="utf-8") as f:

            raw = f.read()

    else:

        raw = sys.stdin.read()

    print(

        json.dumps(

            parse(raw),

            indent=4

        )

    )
