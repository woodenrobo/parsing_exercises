from parsers.hplc import parse_separated_file

FILE_PATH = "./fixtures/01_hplc/hplc_sequence_report.tsv"
SEP = "\t"
META_PREFIX = "#"


def test_parse_separated_file_accepts_tsv() -> None:
    df = parse_separated_file(FILE_PATH, SEP, META_PREFIX)

    assert df is not None
