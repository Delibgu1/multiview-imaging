
#!/usr/bin/env python
import os
import sys
from glob import glob

# --- Bootstrap OSGeo4W (Windows) ANTES de carregar o Django ---
if os.name == "nt":
    OSGEO_ROOT = os.environ.get("OSGEO4W_ROOT") or r"C:\OSGeo4W"
    bin_dir = fr"{OSGEO_ROOT}\bin"
    try:
        # Disponível no Python 3.8+; garante que o Windows localize as DLLs
        os.add_dll_directory(bin_dir)
    except Exception:
        pass

    # Descobre a DLL real do GDAL (ex.: gdal311.dll) dinamicamente
    gdal_dll = None
    for pattern in ("gdal*.dll",):
        cand = sorted(glob(fr"{bin_dir}\{pattern}"), reverse=True)
        if cand:
            gdal_dll = cand[0]
            break

    geos_dll = None
    for pattern in ("geos_c*.dll", "geos_c.dll"):
        cand = sorted(glob(fr"{bin_dir}\{pattern}"), reverse=True)
        if cand:
            geos_dll = cand[0]
            break

    if gdal_dll:
        os.environ.setdefault("GDAL_LIBRARY_PATH", gdal_dll)
    if geos_dll:
        os.environ.setdefault("GEOS_LIBRARY_PATH", geos_dll)

    os.environ.setdefault("PROJ_LIB",  fr"{OSGEO_ROOT}\share\proj")
    os.environ.setdefault("GDAL_DATA", fr"{OSGEO_ROOT}\share\gdal")

    # Ajuda o loader do Windows a encontrar dependências em cascata
    os.environ["PATH"] = bin_dir + ";" + os.environ.get("PATH", "")


def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Is it installed and is your virtualenv active?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
