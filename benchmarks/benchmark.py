"""Small local benchmark; it writes no files and reports this machine's timing."""

from pathlib import Path
from time import perf_counter

from questlint.core.analyzer import Analyzer
from questlint.core.source import SourceFile


def main() -> None:
    source = "\n".join(
        f"local value_{index} = {index}; print(value_{index})" for index in range(500)
    )
    files = [SourceFile(Path(f"synthetic_{index}.lua"), source) for index in range(20)]
    analyzer = Analyzer()
    started = perf_counter()
    diagnostics = sum((analyzer.analyze(file) for file in files), [])
    elapsed = perf_counter() - started
    print(f"{len(files)} files, {len(diagnostics)} diagnostics, {elapsed:.3f}s")


if __name__ == "__main__":
    main()
