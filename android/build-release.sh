#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ ! -f "$ROOT_DIR/local.properties" ]]; then
  echo "Missing $ROOT_DIR/local.properties"
  echo "Copy local.properties.example to local.properties and set sdk.dir"
  exit 1
fi

if [[ ! -f "$ROOT_DIR/keystore.properties" ]]; then
  echo "Missing $ROOT_DIR/keystore.properties"
  echo "Copy keystore.properties.example to keystore.properties and set release signing values"
  exit 1
fi

cd "$ROOT_DIR"
./gradlew assembleRelease

echo
echo "Release APK:"
find "$ROOT_DIR/app/build/outputs/apk/release" -name '*.apk' -print
