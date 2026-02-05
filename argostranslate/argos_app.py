#!/usr/bin/env python3
"""
Argos Translate App - Standalone offline translation CLI
Self-contained translation tool using Argos Translate
"""
from pathlib import Path
import sys

HOME = Path.home()
DATA_DIR = HOME / ".decyphertek.ai" / "app-store" / "argostranslate" / "data"

def setup_packages():
    """Download and install en<->es translation packages if not already installed"""
    import argostranslate.package
    import argostranslate.translate

    installed = argostranslate.translate.get_installed_languages()
    codes = [lang.code for lang in installed]

    if "en" in codes and "es" in codes:
        return

    print("[ArgosTranslate] Downloading language packages...")
    argostranslate.package.update_package_index()
    available = argostranslate.package.get_available_packages()

    for pkg in available:
        if (pkg.from_code == "en" and pkg.to_code == "es") or \
           (pkg.from_code == "es" and pkg.to_code == "en"):
            print(f"[ArgosTranslate] Installing {pkg.from_code} -> {pkg.to_code}")
            argostranslate.package.install_from_path(pkg.download())

    print("[ArgosTranslate] Language packages installed.")

def translate(text, from_code, to_code):
    """Translate text between languages"""
    import argostranslate.translate
    return argostranslate.translate.translate(text, from_code, to_code)

def interactive_mode():
    """Interactive translation REPL"""
    print("[ArgosTranslate] Interactive mode (type 'quit' to exit)")
    print("[ArgosTranslate] Commands: /en2es /es2en /quit")
    print()

    from_code, to_code = "en", "es"

    while True:
        try:
            prompt = f"[{from_code}->{to_code}] > "
            text = input(prompt).strip()

            if not text:
                continue
            if text in ("/quit", "quit", "exit"):
                break
            if text == "/en2es":
                from_code, to_code = "en", "es"
                print(f"[ArgosTranslate] Switched to {from_code} -> {to_code}")
                continue
            if text == "/es2en":
                from_code, to_code = "es", "en"
                print(f"[ArgosTranslate] Switched to {from_code} -> {to_code}")
                continue

            result = translate(text, from_code, to_code)
            print(f"  {result}")
        except KeyboardInterrupt:
            break

    print("\n[ArgosTranslate] Goodbye!")

if __name__ == "__main__":
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    print("[ArgosTranslate] Starting...")
    print(f"[ArgosTranslate] Data: {DATA_DIR}")

    setup_packages()

    if len(sys.argv) > 1:
        from_code = "en"
        to_code = "es"
        args = sys.argv[1:]
        if "--from" in args:
            idx = args.index("--from")
            from_code = args[idx + 1]
            args = args[:idx] + args[idx + 2:]
        if "--to" in args:
            idx = args.index("--to")
            to_code = args[idx + 1]
            args = args[:idx] + args[idx + 2:]
        text = " ".join(args)
        if text:
            print(translate(text, from_code, to_code))
    else:
        interactive_mode()
