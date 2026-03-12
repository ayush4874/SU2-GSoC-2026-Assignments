# Assignment 2: Axisymmetric Turbulent Jet Simulation

## Motivation
The goal of this test case is to simulate a steady-state turbulent jet using RANS equations. I designed the domain to be large enough to allow the jet to develop fully without boundary interference. The axisymmetric formulation was chosen to reduce computational cost while maintaining 3D flow physics.

## Setup and Configuration
- **Geometry:** Created in Gmsh. It features a jet inlet (R=0.05m), a symmetry axis, and a far-field boundary.
- **Physics Model:** I used the Spalart-Allmaras (SA) turbulence model. It is well-suited for aerodynamic flows and jet shear layers.
- **Numerical Schemes:** JST (Jameson-Schmidt-Turkel) for convective flows to ensure stability at the shear layer interface.
- **Boundary Conditions:** - `MARKER_INLET`: Set to Mach 0.05.
    - `MARKER_SYM`: Defined as the axis of symmetry.
    - `MARKER_OUTLET`: Set to atmospheric pressure.

## Convergence History
The simulation was run for 500 iterations. As seen in the `history.csv`, the density and momentum residuals dropped significantly (below 10^-8), indicating a well-converged steady-state solution.

## Comparison with Experimental Values
Referring to the linked paper (*Mi et al., "Investigation of the Mixing Process in an Axisymmetric Turbulent Jet"*):
1. **Potential Core:** My simulation captures the potential core region where velocity remains constant for roughly 4-6 nozzle diameters downstream, which is consistent with the PIV data in the paper.
2. **Spreading Rate:** Qualitative analysis in ParaView shows a linear increase in jet width. This matches the LIF (Laser Induced Fluorescence) observations of fluid entrainment and jet spreading.
3. **Velocity Decay:** The centerline velocity shows an inverse decay ($1/x$) once past the potential core, aligning with the mean flow statistics reported in the experimental study.

## Deliverables
**Convergence History:**
The plot below shows the residual drop for the density and momentum equations.
![Convergence History](residuals.png)

**Velocity Magnitude Contour:**
The following contour shows the jet development, including the potential core and the radial spreading.
![Velocity Contour](results_contour.png)

## Mentor Review Updates

**Mesh and y+:**
Added a mesh visualization (`mesh.png`). The current mesh is a coarse unstructured grid and doesn't have any prism layers at the solid boundaries. Because of this, the y+ value is way too high for the Spalart-Allmaras turbulence model to accurately resolve the flow near the walls.

![Mesh Detail](mesh.png)

**Convergence & Residuals:**
The `1e-8` value mentioned in the above was just the target set in the config (`CONV_RESIDUAL_MINVAL`). Checking the actual `history.csv`, the density residual (`rms[Rho]`) actually flatlines around -0.025. The simulation stalled and didn't properly converge, likely due to the mesh quality and the corner singularity.

**Corner Velocity:**
The >1000 m/s velocity at the nozzle lip is completely unphysical. It is a numerical singularity caused by the sharp 90-degree corner. The solver is trying to accelerate the flow around a point with zero radius, causing an artificial supersonic spike in that specific cell.
