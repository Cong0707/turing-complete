# Turing Complete Save Lab

`tc-save-lab` is an offline laboratory for Turing Complete 2.1.x save files.
It decodes, validates, version-controls, and atomically writes current-format
circuits without starting the game.

The `examples/` tree is the reproducible source of the campaign challenge
solutions. Each level has its own directory, metadata, baseline, and candidate
circuits. Research notes are immutable Chinese Markdown files under
`docs/研究日志/`; routine progress is deliberately not appended here.

## Local setup

```powershell
cd D:\Develop\Other\turing-complete
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m tc_save_lab inspect
```

The default save root is `%APPDATA%\Turing Complete`. The tool refuses a write
while `Turing Complete.exe` is running. A write is an atomic same-directory
replace followed by a decode-and-compare verification; it leaves no backup
copy. Use the interactive `apply` command only after reviewing the generated
candidate manifest.

## Status

The first milestone implements strict v15 container support and a read-only
catalogue. Game asset compatibility, circuit synthesis, and full campaign
writeback are tracked in the Chinese research notes.
