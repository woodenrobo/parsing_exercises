import re
from pathlib import Path

import pandas as pd


def parse_separated_file(
    path: str, separator: str, meta_lines_prefix: str, include_meta: bool = False
) -> pd.DataFrame:

    if not re.findall(r".tsv$|.csv$", path):
        raise ValueError("Import file is not tsv or csv")

    with Path.open(Path(path), encoding="utf-8") as file:
        raw_text = file.read()

    line_split = raw_text.split("\n")

    if not include_meta:
        line_split = [
            line for line in line_split if not line.startswith(meta_lines_prefix)
        ]

    line_split = [line for line in line_split if line != ""]

    colnames = line_split[0].split(separator)

    no_colnames_lines = [line.split(separator) for line in line_split[1:]]

    out_df = pd.DataFrame(data=no_colnames_lines, columns=colnames)
    out_df = out_df.apply(lambda col: pd.to_numeric(col, errors="coerce").fillna(col))  # type: ignore
    out_df = out_df.fillna(value=0)

    return out_df


FILE_PATH = "./fixtures/01_hplc/hplc_sequence_report.tsv"
SEP = "\t"
META_PREFIX = "#"

df = parse_separated_file(FILE_PATH, SEP, META_PREFIX)

# data transformation exercises
controls = df[df["sample_id"].str.startswith("STD")]
qc = df[df["sample_id"].str.startswith("QC")]
blank = df[df["sample_id"].str.startswith("BLANK")]
samples = df[df["sample_id"].str.startswith("SMP")]


df["result_mg_ml_post_dilution"] = df["result_mg_ml"] / df["dilution_factor"]

df.loc[df["qc_flag"] != "PASS", "cave"] = "CAVE"
df.loc[df["qc_flag"] == "PASS", "cave"] = "PASS"

pass_rate = sum(df["qc_flag"] == "PASS") / len(df)
