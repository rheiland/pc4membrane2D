# pc4membrane2D

Studio GUI to explore test case of PhysiCell subcell mechanics near a membrane

Compile the C++ model:
```
cd src
make

# copy the executable to where the Studio wants it:
cp myproj ..

# Change directory to the root dir and run the GUI from there
cd ..
python bin/studio.py
```

In the GUI:
* in the Run tab, click `Run Simulation`. Note: the simulation is run *from* the `tmpdir` directory and that's where all output files will be written.
* in the Plot tab, click `Play`.
* edit params if you want then repeat: Run, Play.
