from typing import List
from pydantic import BaseModel


class Branch(BaseModel):
    block: int = 0
    branch: int = 0
    line: int = 0
    taken: int = 0


class Line(BaseModel):
    line: int = 0
    hit: int = 0


class Function(Line):
    name: str = None


class Stats(BaseModel):
    br_found: int = 0
    br_hit: int = 0
    hit: int = 0
    lines: int = 0
    fn_found: int = 0
    fn_hit: int = 0


class FileCoverageReport(BaseModel):
    stats: Stats = Stats()
    branches: List[Branch] = []
    lines: List[Line] = []
    miss: List[int] = []
    functions: List[Function] = []
    file_name: str = None
    test: str = None


def lcovparse(combined):
    # clean and strip lines
    assert "end_of_record" in combined, 'lcov file is missing "end_of_record" line(s)'
    files = filter(lambda f: f != "", combined.strip().split("end_of_record"))
    coverage_data = [_part(current_file) for current_file in files]
    for f in coverage_data:
        hit_lines = [l.line for l in f.lines]
        for l in range(1, f.stats.lines + 1):
            if l not in hit_lines:
                f.miss.append(Line(line=l))
    return coverage_data


def _part(chunk):
    report = FileCoverageReport()
    for l in chunk.split("\n"):
        _line(l, report)
    return report


def _line(l, report: FileCoverageReport):
    """
    http://ltp.sourceforge.net/test/coverage/lcov.readme.php#10
    """
    if l == "":
        return None
    method, content = tuple(l.strip().split(":", 1))
    content = content.strip()
    if method == "TN":
        # test title
        report.test = content

    elif method == "SF":
        # file name
        report.file_name = content

    elif method == "LF":
        # lines found
        report.stats.lines = int(content)

    elif method == "LH":
        # line hit
        report.stats.hit = int(content)

    elif method == "DA":
        if "null" not in content:
            line, hit = map(int, content.split(",")[:2])
            report.lines.append(Line(line=line, hit=hit))

    # ---------
    # Functions
    # ---------
    elif method == "FNF":
        # functions found
        report.stats.fn_found = int(content)

    elif method == "FNH":
        report.stats.fn_hit = int(content)

    elif method == "FN":
        line, name = content.split(",", 1)
        report.functions.append(Function(line=int(line), name=name))

    elif method == "FNDA":
        # function names
        # FNDA:75,get_user
        hit, name = content.split(",", 1)
        if hit not in (None, "-", ""):
            for fn in report.functions:
                if fn.name == name:
                    fn.hit = int(hit)

    # --------
    # Branches
    # --------
    elif method == "BRF":
        report.stats.br_found = int(content)

    elif method == "BRH":
        report.stats.br_hit = int(content)

    elif method == "BRDA":
        # branch names
        # BRDA:10,1,0,1
        line, block, branch, taken = content.split(",", 3)
        report.branches.append(
            Branch(
                line=int(line),
                block=int(block),
                branch=int(branch),
                taken=0 if taken == "-" else int(taken),
            )
        )
    else:
        raise Exception(f"Unknown method name {method}")
