#!/bin/sh
# Migrated from the native `jellyfin_transcode` check (remote, on the mediaserver).
# Exits 0 when NVENC/CUDA transcoding works, non-zero otherwise. script_exporter
# turns the exit code into script_success{script="jellyfin_transcode"}, which the
# generated Prometheus rule alerts on; Alertmanager then forwards to RootCause.
#
# Remote: shells out over SSH. Mount an SSH key into the exporter container and
# point SSH_KEY at it (see scripts/README.md).
SSH_KEY="${SSH_KEY:-/scripts/keys/id_ed25519}"
HOST="${MEDIASERVER_SSH:-user@mediaserver.example.lan}"

ssh -i "$SSH_KEY" -o StrictHostKeyChecking=accept-new -o ConnectTimeout=10 "$HOST" -- \
  'docker exec jellyfin /usr/lib/jellyfin-ffmpeg/ffmpeg \
     -f lavfi -i testsrc=duration=1:size=320x240:rate=25 \
     -init_hw_device cuda=cu:0 -filter_hw_device cu \
     -c:v h264_nvenc -f null - >/dev/null 2>&1'
rc=$?
if [ "$rc" -ne 0 ]; then
  echo "jellyfin NVENC/CUDA transcode test failed (rc=$rc)"
  exit 1
fi
echo "jellyfin NVENC/CUDA transcode OK"
exit 0
