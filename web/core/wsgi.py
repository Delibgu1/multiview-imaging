
import os
from glob import glob

# Bootstrap OSGeo4W (Windows) antes de o WSGI carregar o Django
if os.name == "nt":
    OSGEO_ROOT = os.environ.get("OSGEO4W_ROOT") or r"C:\OSGeo4W"
    bin_dir = fr"{OSGEO_ROOT}\bin"
    try:
        os.add_dll_directory(bin_dir)
    except Exception:
        pass

    # Ajusta envs se ainda não foram definidos
    if not os.environ.get("GDAL_LIBRARY_PATH"):
        cand = sorted(glob(fr"{bin_dir}\gdal*.dll"), reverse=True)
        if cand:
            os.environ["GDAL_LIBRARY_PATH"] = cand[0]
    if not os.environ.get("GEOS_LIBRARY_PATH"):
        cand = sorted(glob(fr"{bin_dir}\geos_c*.dll"), reverse=True)
        if not cand:
            cand = sorted(glob(fr"{bin_dir}\geos_c.dll"), reverse=True)
        if cand:
            os.environ["GEOS_LIBRARY_PATH"] = cand[0]
    os.environ.setdefault("PROJ_LIB",  fr"{OSGEO_ROOT}\share\proj")
    os.environ.setdefault("GDAL_DATA", fr"{OSGEO_ROOT}\share\gdal")

from django.core.wsgi import get_wsgi_application
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
application = get_wsgi_application()
