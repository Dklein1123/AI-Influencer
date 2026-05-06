"""ElevenLabs voice synthesis wrapper.

Takes a Sierra script (the same `[start-end] TEXT` chunked format used
by the assembly pipeline, OR plain prose) and produces a .wav file ready
for `tools.assembly`. Identity comes from the cloned voice id stored in
`~/.AI-Influencer.env` as `ELEVEN_SIERRA_VOICE_ID`.

See `tools/voice_synth/README.md` for daily-use commands.
"""
