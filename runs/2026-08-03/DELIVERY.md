# CASE No. 0003 — DELIVERY

## Download and post this

https://raw.githubusercontent.com/Talonsturgill/thebigfunny/main/runs/2026-08-03/case0003_tiktok.mp4

Public repo, so the link needs no login and downloads directly on a phone.

| | |
| --- | --- |
| file | `case0003_tiktok.mp4` |
| runtime | 53.27s |
| dimensions | 1080x1920 (9:16) |
| video | H.264 high@4.0, **yuv420p**, tv range, bt709 |
| audio | AAC 160k, 48kHz, stereo |
| streaming | faststart (moov before mdat) |
| size | 10.7MB, against a 280MB mobile cap |

Caption is `caption.txt`. Sources are `first_comment.txt` and they go in the
FIRST COMMENT, never in the body.

## The other two files, and why they are not the one to post

- `case0003_recut.mp4` — the **master**. Same picture and same audio, but it is
  `yuvj420p`, full-range JPEG YUV, which is what Remotion emits. A platform
  re-encoding that will read the range tag and lift or crush every black in the
  film. On a show made of crushed dark teal that is the most visible defect
  available, and no gate had ever looked at it before today.
- `case0003.mp4` — the ORIGINAL ship, kept byte-for-byte. It has the floating
  limbs, the ledge through Ray's head and the cropped payoff words. Do not post
  it. It is here because shipped run artifacts are not this routine's to
  overwrite.

## Verified

`scripts/delivery_check.py runs/2026-08-03/case0003_tiktok.mp4 --url <the link>`
passes every row, including a live fetch of the URL itself. A link that 404s is
worse than no link, because it is the first thing in the draft anyone acts on.
