# RootCause Android

Base Android app for RootCause with:

- first-launch onboarding for `host`, `port` and `api key`
- HTTPS-only server access
- device registration against the RootCause mobile API
- dashboard bootstrap, alert listing and `ack` / `silence` / `re-run` actions
- Gradle Wrapper included

## Build

Typical next steps:

1. Copy `local.properties.example` to `local.properties` and set `sdk.dir`.
2. Open `android/` in Android Studio or run `./build-debug.sh`.
3. Build a debug APK from the `app` module.

The project includes the Gradle wrapper. In this environment, `./build-debug.sh` produces:

`app/build/outputs/apk/debug/app-debug.apk`

## Release

Release signing is wired through `keystore.properties`.

1. Copy `keystore.properties.example` to `keystore.properties`.
2. Generate or provide a keystore file, for example under `android/keystore/`.
3. Run `./build-release.sh`.

The signed release APK is written to:

`app/build/outputs/apk/release/app-release.apk`

## Security

- The mobile client assumes TLS. Do not expose `8787` directly over plain HTTP.
- Put RootCause behind HTTPS and use the public hostname, for example `https://rootcause.example.com:8567`.
- API keys are generated in the RootCause web console and stored server-side as hashes.

## Push notifications

Push is not fully wired yet. The backend is prepared for registered devices, but Firebase/FCM integration still needs to be added before production mobile notifications.
