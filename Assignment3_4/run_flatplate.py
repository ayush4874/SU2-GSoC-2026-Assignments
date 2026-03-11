import os
import sys
import pysu2
from mpi4py import MPI

def split_wall_marker(mesh_in, mesh_out):
    """Splits MARKER_WALL into HOT and COLD zones."""
    with open(mesh_in, "r") as f:
        lines = f.readlines()
        
    with open(mesh_out, "w") as f:
        in_wall = False
        elems_read = 0
        
        for line in lines:
            if line.startswith("NMARK="):
                nmark = int(line.split("=")[1])
                f.write(f"NMARK= {nmark + 1}\n")
                continue
                
            if "MARKER_TAG= MARKER_WALL" in line:
                in_wall = True
                f.write("MARKER_TAG= MARKER_WALL_HOT\n")
                f.write("MARKER_ELEMS= 153\n")
                continue
                
            if in_wall:
                if "MARKER_TAG=" in line:
                    in_wall = False
                    f.write(line)
                    continue
                if "MARKER_ELEMS=" in line:
                    continue
                    
                f.write(line)
                elems_read += 1
                
                if elems_read == 153:
                    f.write("MARKER_TAG= MARKER_WALL_COLD\n")
                    f.write("MARKER_ELEMS= 153\n")
            else:
                f.write(line)

def prepare_config(cfg_in, cfg_out, mesh_out):
    """Updates config to use the split mesh and new BCs."""
    with open(cfg_in, "r") as f:
        lines = f.readlines()
        
    with open(cfg_out, "w") as f:
        for line in lines:
            if line.startswith("MESH_FILENAME="):
                f.write(f"MESH_FILENAME= {mesh_out}\n")
            elif line.startswith("MARKER_ISOTHERMAL="):
                f.write("MARKER_ISOTHERMAL= ( MARKER_WALL_HOT, 350.0, MARKER_WALL_COLD, 288.15 )\n")
            elif line.startswith("ITER="):
                f.write("ITER= 100\n")
            elif "MARKER_WALL" in line and not "MARKER_ISOTHERMAL" in line:
                f.write(line.replace("MARKER_WALL", "MARKER_WALL_HOT, MARKER_WALL_COLD"))
            else:
                f.write(line)

if __name__ == "__main__":
    base_mesh = "flatplate.su2"
    split_mesh = "flatplate_split.su2"
    base_cfg = "flatplate.cfg"
    run_cfg = "flatplate_split.cfg"

    print("Splitting mesh for spatially varying BCs...")
    split_wall_marker(base_mesh, split_mesh)
    
    print("Updating configuration file...")
    prepare_config(base_cfg, run_cfg, split_mesh)

    print("Initializing SU2 solver via pysu2...")
    comm = MPI.COMM_WORLD
    driver = pysu2.CSinglezoneDriver(run_cfg, 1, comm)
    
    print("Starting simulation...")
    driver.StartSolver()
    
    print("Simulation finished.")
    
    # Hard exit to avoid known SWIG memory deallocation segfault
    os._exit(0)
