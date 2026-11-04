#!/usr/bin/env bash
# Make the header video files from the full-quality master (Banner.mp4).
#
#   tools/encode-hero-video.sh path/to/Banner.mp4
#
# Needs ffmpeg (tested with 6.1) and bc. Writes:
#   media/video/hero-v2-960.mp4  \
#   media/video/hero-v2-1280.mp4  > the same short seamless loop at three
#   media/video/hero-v2-1920.mp4 /  widths; hero.js picks the smallest one
#                                   that is sharp on the visitor's screen
#   media/images/hero.jpeg       its first frame = the poster master; then run
#                                python3 tools/build-images.py for the web sizes
#
# The master is 1920x1080, 60 fps, 46.3 s, one static shot. Never commit it.
# If you change anything here, bump the -v2 in the file names (and in
# index.html) so browsers don't keep serving the old files.
set -euo pipefail

SRC=${1:?usage: $0 path/to/Banner.mp4}
cd "$(dirname "$0")/.."

# Loop points, as frame numbers of the 60 fps master. Picked by comparing
# frames 6-8 s apart for the smallest camera drift and brightness change:
# frame 1238 (20.63 s) to 1602 (26.70 s), 6.07 s. The waves never match
# exactly, so the last second dissolves into the second BEFORE the start;
# the clip then ends on frame 1237 and wraps onto 1238 without a seam.
START=1238
END=1602
FADE=1                                     # seconds of dissolve
FPS=30
SHORT_LEN=$(echo "($END - $START) / 60" | bc -l)

# Constant quality (CRF): every width gets the same visual quality, roughly
# streaming-site 1080p. Lower = better and bigger; each -6 about doubles the
# size. The sand and water are full of fine grain, which is what costs bits.
CRF=23

X264=(-c:v libx264 -preset veryslow -profile:v high -pix_fmt yuv420p
      -g $((FPS * 2)) -an -sn -dn -map_metadata -1
      -colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv)

# $1 = output, $2 = filter graph, $3 = peak bitrate cap (keeps the rate
# steady enough to play while it downloads).
encode() {
  ffmpeg -v error -y -i "$SRC" -filter_complex "$2" -map '[v]' "${X264[@]}" \
         -crf $CRF -maxrate "$3" -bufsize "$(( ${3%k} * 2 ))k" \
         -movflags +faststart "$1"
  printf '%s  %s KiB\n' "$1" "$(( $(stat -c %s "$1") / 1024 ))"
}

# Cut [a,b) frames out of the master, at $FPS and width $W.
cut() { echo "trim=start_frame=$1:end_frame=$2,setpts=PTS-STARTPTS,fps=$FPS,scale=$W:-2:flags=lanczos"; }

# 1) Short loop: [START, END) with its last second dissolving into
#    [START - 1 s, START), at each width with its peak bitrate cap.
mkdir -p media/video
for spec in 960:4000k 1280:7000k 1920:12000k; do
  W=${spec%%:*}
  encode "media/video/hero-v2-$W.mp4" \
    "[0:v]split[a][b];[a]$(cut $START $END)[main];[b]$(cut $((START - 60 * FADE)) $START)[pre];
     [main][pre]xfade=transition=fade:duration=$FADE:offset=$(echo "$SHORT_LEN - $FADE" | bc -l),format=yuv420p[v]" \
    "${spec#*:}"
done

# 2) Poster master: frame 0 of the short loop, at full size. bt709 is the
#    video's colour matrix, so the photo and the first video frame match.
ffmpeg -v error -y -i "$SRC" -frames:v 1 \
  -vf "select=eq(n\,$START),scale=in_color_matrix=bt709:in_range=tv:out_range=pc,format=rgb24" \
  -pix_fmt yuvj444p -q:v 1 -flags +bitexact media/images/hero.jpeg

echo "Now: python3 tools/build-images.py"
