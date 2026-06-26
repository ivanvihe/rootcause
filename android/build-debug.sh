#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ ! -f "$ROOT_DIR/local.properties" ]]; then
  echo "Missing $ROOT_DIR/local.properties"
  echo "Copy local.properties.example to local.properties and set sdk.dir"
  exit 1
fi

cd "$ROOT_DIR"
./gradlew assembleDebug

echo
echo "Debug APK:"
find "$ROOT_DIR/app/build/outputs/apk/debug" -name '*.apk' -print
