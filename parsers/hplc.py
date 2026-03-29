import io
import re

import pandas as pd

FILE_PATH = "./fixtures/01_hplc/hplc_sequence_report.tsv"

SEP = "\t"
LINE_BREAK = "\n"

if not re.findall(r".tsv$", FILE_PATH):
    raise ValueError("Import file is not tsv")

raw_text = io.open(FILE_PATH).read()

line_split = raw_text.split(LINE_BREAK)

no_meta_lines = [line for line in line_split if not line.startswith("#")]

no_empty_lines = [line for line in no_meta_lines if not line == ""]

colnames = no_empty_lines[0].split(SEP)

no_colnames_lines = [line.split(SEP) for line in no_empty_lines[1:]]


df = pd.DataFrame(data=no_colnames_lines, columns=colnames)
df = df.apply(lambda col: pd.to_numeric(col, errors='coerce').fillna(col)) # type: ignore
df = df.fillna(value=0)



# data transformation exercises
controls = df[df["sample_id"].str.startswith("STD")]
qc = df[df["sample_id"].str.startswith("QC")]
blank = df[df["sample_id"].str.startswith("BLANK")]
samples = df[df["sample_id"].str.startswith("SMP")]


df["result_mg_ml_post_dilution"] = df["result_mg_ml"] / df["dilution_factor"]

df.loc[df["qc_flag"]!="PASS", "cave"] = "CAVE"
df.loc[df["qc_flag"]=="PASS", "cave"] = "PASS"

pass_rate = sum(df["qc_flag"] == "PASS")/len(df)

