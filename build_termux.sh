#!/data/data/com.termux/files/usr/bin/bash
set -e

echo "== Vibes Only Android/Termux build helper =="

pkg install -y git zip unzip openjdk-17 python clang make cmake pkg-config autoconf automake libtool zlib libffi openssl

python - <<'PY'
from pathlib import Path
import buildozer

p = Path(buildozer.__file__).parent / "targets" / "android.py"
s = p.read_text(encoding="utf-8")

old = """is_debian_like = which("dpkg") is not None

        if is_debian_like and \\
                not buildops.file_exists('/usr/include/zlib.h'):
            raise BuildozerException(
                'zlib headers must be installed, '
                'run: sudo apt-get install zlib1g-dev')"""

new = """is_debian_like = (
            which("dpkg") is not None
            and "com.termux" not in os.environ.get("PREFIX", "")
            and "termux" not in os.environ.get("PREFIX", "").lower()
        )

        if is_debian_like and \\
                not buildops.file_exists('/usr/include/zlib.h'):
            raise BuildozerException(
                'zlib headers must be installed, '
                'run: sudo apt-get install zlib1g-dev')"""

if old in s:
    p.write_text(s.replace(old, new), encoding="utf-8")
    print("Patched Buildozer's Debian-only zlib check for Termux.")
elif "com.termux" in s:
    print("Buildozer already appears to contain the Termux zlib adjustment.")
else:
    print("Buildozer source layout differs from the expected 1.6.0 layout.")
    raise SystemExit(2)
PY

export CPPFLAGS="-I$PREFIX/include"
export CFLAGS="-I$PREFIX/include"
export LDFLAGS="-L$PREFIX/lib"
export PKG_CONFIG_PATH="$PREFIX/lib/pkgconfig"

echo "Starting APK build..."
buildozer android debug
