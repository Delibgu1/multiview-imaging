# Presets ODM (inicial)

## Agrícola geral (RGB)
- --orthophoto-resolution 5
- --dsm --dtm
- --pc-classify
- --optimize-disk-space --fast-orthophoto

## Vegetação densa / relevo
- --orthophoto-resolution 3
- --feature-quality ultra
- --pc-quality high
- --dem-euclidean-map

## Alta precisão (com GCPs)
- --use-exif
- --gcp gcp_list.txt
- --orthophoto-resolution 2
```