# Vibes Only V11 — phone-only GitHub Actions Android build

This package is set up so GitHub Actions builds the APK with the maintained Buildozer Docker action.

## Important
Do **not** commit `.buildozer/` to GitHub. It is generated build data and can contain a large cached python-for-android tree.

The workflow uses:
- Buildozer stable
- Java/Android tooling supplied by the Buildozer container
- Android API 35
- Minimum Android API 24
- arm64-v8a only
- automatic Android SDK license acceptance

## GitHub build
Push the project to the `main` branch, or open GitHub Actions and run **Build Vibes Only APK** with **Run workflow**.

After a successful run, open the run's **Artifacts** section and get `Vibes-Only-APK`.
