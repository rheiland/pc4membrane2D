Until a more streamlined workflow gets created, we do this for now:

```
python chunks.py  3.77 5.65 5 100 80 0 0   # small circle; large curvature
or,
python chunks.py  3.77 5.65 5 300 280 0 200    # large circle; smaller curvature

sh raster_chunks.sh  # need to close each plot window that appears
cat pts_chunk1.csv pts_chunk2.csv pts_chunk3.csv pts_chunk4.csv pts_chunk5.csv >cells.csv
cp cells.csv ../data
```

Note: since we hardwire the circle's center and radius for now, one would need to make edits to bin/vis_tab.py and src/custom_modules/mechanics.cpp. 

