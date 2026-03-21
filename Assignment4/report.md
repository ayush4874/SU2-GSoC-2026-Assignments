# Assignment 4: Implementation of a Spatially Varying Isothermal Wall Boundary

## 1. Simulation Setup and Computational Domain
The goal of this assignment was to bypass the static `.cfg` file and use the SU2 Python wrapper (`pysu2`) to dynamically inject a spatially varying isothermal wall boundary condition. 

The baseline case is a steady-state, 2D subsonic viscous flow over a flat plate. 
* **Flow Conditions:** Mach 0.2, Reynolds number of $5 \times 10^6$, and a freestream static temperature of 288.15 K.
* **Flow Solver:** Compressible RANS equations coupled with the Spalart-Allmaras (SA) turbulence model.
* **Mesh:** The standard `flatplate.su2` structured grid. To capture the turbulent boundary layer, the mesh elements are heavily refined in the y-direction immediately adjacent to the wall ($y=0$).

The computational domain is defined by the following boundary conditions:
* **Inlet:** Freestream conditions ($T = 288.15$ K).
* **Outlet:** Fixed static pressure.
* **Farfield:** The upper boundary of the domain.
* **Symmetry:** The fluid region preceding the flat plate's leading edge.
* **Isothermal Wall:** The flat plate surface. 

**The Target Trend:** Instead of a uniform wall temperature, I wanted to implement a sharp step function along the $x$-axis. The front section of the plate would be heated to 400.0 K, and the rear section would remain at the freestream temperature of 288.15 K. 

## 2. Implementing the Spatial Gradient (The API Roadblock)
My initial plan was to implement this the "clean" way: using the `pysu2` API to iterate over the boundary nodes in memory, grab their X-coordinates, and dynamically apply the temperature step using `SetVertexTemperature()`. 

However, depending on the specific SU2 version and SWIG compilation in my environment, several of these C++ memory hooks (like `GetNumberVertices` for specific markers) weren't exposed to the Python wrapper. I kept hitting `AttributeError` tracebacks when trying to query the wall nodes directly.

**The Workaround:**
Instead of fighting the API, I wrote a Python script (`run_flatplate.py`) to act as a pre-processor and modify the mesh topology *before* it gets passed to the solver:
1. It reads the raw ASCII `.su2` mesh file.
2. It geometrically splits the single `wall` marker into two distinct boundaries: `wall_hot` (the first 56 elements) and `wall_cold` (the remaining elements).
3. It creates a temporary configuration file on the fly, assigning 400.0 K to the `wall_hot` section and 288.15 K to the `wall_cold` section.
4. It initializes the `CSinglezoneDriver` with this modified setup and runs the simulation.

## 3. Verification and the Learning Process
In my initial attempts to verify the results, I tried plotting the volume solution in ParaView over a line. Because the flat plate is essentially a 1D line in a 2D mesh, ParaView's interpolation kept accidentally sampling freestream fluid nodes sitting a fraction of a millimeter above the plate, resulting in a messy scatter plot.

Following the feedback from the previous submission, the correct approach is to completely isolate the boundary data from the volume data. Evert suggested using the `PARAVIEW_MULTIBLOCK` output to generate separate boundary files. 

When I tried this, I ran into a known WSL environment bug where the resulting `.vtu`/`.vtm` XML files caused ParaView to crash. To achieve the exact same boundary isolation without the XML crashes, I updated my configuration to use `SURFACE_CSV`. This forced SU2 to export the isolated boundary nodes into a simple spreadsheet.

Since SU2 exports conservative variables to the CSV, I wrote a short Python script to read the Density ($\rho$) and Energy ($\rho E$) precisely at the wall. Because velocity is zero at the wall (no-slip condition), I was able to calculate the exact temperature mathematically using the ideal gas relation ($T = E / (\rho c_v)$) and plot it directly.

![Spatially Varying Wall Temperature Verification](wall_multiblock_verification.png)

As shown in the graph above, isolating the boundary data and extracting it mathematically completely removed the interpolation scatter. You can clearly see the exact spatial trend I programmed: the temperature holds steady at 400.0 K on the `wall_hot` boundary and then drops instantly to 288.15 K exactly where the Python script split the mesh ($x \approx 0.32$ m), extending across the rest of the 2.0-meter plate.