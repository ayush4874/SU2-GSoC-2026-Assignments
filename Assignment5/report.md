# Assignment 5: Addition of New Volume and Screen Output

## Objective
Add the local speed of sound to the SU2 volume output (ParaView files) and screen output, and verify the implementation using the turbulent jet test case from Assignment 2.

## Implementation

The modifications were made in the compressible flow output class: `SU2_CFD/src/output/CFlowCompOutput.cpp`.

### 1. Volume Output (`SOUND_SPEED`)
To output the local speed of sound at each grid point to the `.vtk` file, I modified the `SetVolumeOutputValue` function by pulling the variable directly from the node data:
```cpp
SetVolumeOutputValue("SOUND_SPEED", iPoint, Node_Flow->GetSoundSpeed(iPoint));
```
To ensure the configuration parser recognized the new output request, I registered the variable in the internal dictionary:

```cpp
AddVolumeOutput("SOUND_SPEED", "Sound_Speed", "PRIMITIVE", "Local speed of sound");
```
### 2. Screen Output (`AVG_SOUND_SPEED`)
To print the domain-averaged speed of sound to the terminal during the simulation, I added a calculation loop inside the `LoadHistoryData` function:

```cpp
su2double avg_sound_speed = 0.0;
unsigned long nPointDomain = geometry->GetnPointDomain();
const auto* Node_Flow = flow_solver->GetNodes();

for (unsigned long iPoint = 0; iPoint < nPointDomain; iPoint++) {
  avg_sound_speed += Node_Flow->GetSoundSpeed(iPoint);
}
avg_sound_speed /= (su2double)nPointDomain;
SetHistoryOutputValue("AVG_SOUND_SPEED", avg_sound_speed);
```
I then registered this variable so it could be called via the `.cfg` file:

```cpp
AddHistoryOutput("AVG_SOUND_SPEED", "Avg[a]", ScreenOutputFormat::SCIENTIFIC, "AERO", "Average speed of sound in the domain.");
```
Following these changes, the source code was recompiled using the Ninja build system.

## Results

The modified solver was tested using the 2D axisymmetric turbulent jet case. The configuration file was updated to include the new output keys:
* `SCREEN_OUTPUT= (..., AVG_SOUND_SPEED)`
* `VOLUME_OUTPUT= (..., SOUND_SPEED)`

### Screen Output
The terminal output correctly displays the newly registered `Avg[a]` column. The value updates every iteration, providing a real-time domain average of the speed of sound alongside standard residuals.

![Terminal output showing the Avg[a] column](screen_output.png)

### Volume Output
The resulting `vol_solution.vtk` file was post-processed in ParaView. The newly implemented `Sound_Speed` variable is successfully written to the mesh points and is available for contour plotting and further analysis.

![ParaView visualization of the Sound_Speed contour](volume_output.png)