"""Sierra brand voice linter + AI grader.

Runs every draft caption / script / reply through the rules defined in
`personas/sierra-frost/voice-profile.md` §11. Cheap deterministic rules
catch ~80% of failures for free; optional Claude-graded mode catches the
harder "would Sierra actually say this?" cases.

CLI:
    echo "draft caption" | python -m tools.voice
    python -m tools.voice --file draft.txt
    python -m tools.voice --grade --file draft.txt    # AI grade too

Exit code 0 = passes all hard rules; 1 = at least one rule failed.
"""
