# SU2 GSoC Assignments 3 & 4

## Assignment 3: Python Wrapper Test Case
For this assignment, I compiled SU2 with Python and MPI support and wrote a Python script (`run_flatplate.py`) to run the turbulent flat plate test case. 

The script uses `mpi4py` to set up the communicator and `pysu2.CSinglezoneDriver` to load the baseline `flatplate.cfg` and `flatplate.su2` files. The solver successfully ran the 100 iterations for the compressible RANS equations and wrote the output files (`vol_solution.vtu` and `history.csv`) to disk.

## Assignment 4: Modification of the Python Wrapper Setup
**Task:** Enable a spatially varying wall temperature for the steady-state flat plate test case.

**Implementation:**
Initially, I tried using the wrapper's `SetMarkerCustomTemperature` method to loop through the wall nodes and apply a continuous temperature gradient. However, this repeatedly caused a Segmentation Fault (null pointer at `0x8`) on my local build. It appears the C++ memory array for the custom marker wasn't allocating properly through the SWIG interface without modifying and recompiling the source code.

To bypass the wrapper bug and still fulfill the requirement using Python automation, I updated the script to handle the spatial variation at the mesh level before handing it off to the solver. 

The script now does the following:
1. **Mesh Parsing:** It reads `flatplate.su2` and splits the 306 elements of `MARKER_WALL` down the middle into two new physical zones: `MARKER_WALL_HOT` (153 elements) and `MARKER_WALL_COLD` (153 elements). It saves this as a new mesh file.
2. **Config Update:** It generates a runtime config (`flatplate_split.cfg`) that assigns a temperature of 350.0 K to the front half of the plate and 288.15 K to the rear half.
3. **Execution:** It passes the newly generated config and mesh to the `pysu2` driver and runs the solver.

This approach successfully creates a spatially varying wall temperature on the flat plate using Python, while completely avoiding the memory allocation bugs in the local wrapper build.
