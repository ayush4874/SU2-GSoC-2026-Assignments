import os
import sys
import mpi4py
mpi4py.rc.thread_level = "single" 
from mpi4py import MPI
import pysu2

def split_wall_marker(mesh_in, mesh_out):
    """
    Splits the 'wall' marker into 'wall_hot' and 'wall_cold' zones.
    This bypasses missing API hooks in certain versions of pysu2.
    """
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
                
            if "MARKER_TAG= wall" in line:
                in_wall = True
                f.write("MARKER_TAG= wall_hot\n")
                # Split the elements roughly in half
                f.write("MARKER_ELEMS= 56\n")
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
                
                # After writing the first half, switch to the cold zone
                if elems_read == 56:
                    f.write("MARKER_TAG= wall_cold\n")
                    f.write("MARKER_ELEMS= 56\n")
            else:
                f.write(line)

def prepare_config(cfg_in, cfg_out, mesh_out):
    """Updates config to use the newly split mesh and apply the varying temperatures."""
    with open(cfg_in, "r") as f:
        lines = f.readlines()
        
    with open(cfg_out, "w") as f:
        for line in lines:
            if line.startswith("MESH_FILENAME="):
                f.write(f"MESH_FILENAME= {mesh_out}\n")
            elif line.startswith("MARKER_ISOTHERMAL="):
                # Apply 400K to the hot section and 288.15K to the cold section
                f.write("MARKER_ISOTHERMAL= ( wall_hot, 400.0, wall_cold, 288.15 )\n")
            elif "wall" in line and not "MARKER_ISOTHERMAL" in line:
                # Ensure the solver tracks both new wall sections
                f.write(line.replace("wall", "wall_hot, wall_cold"))
            else:
                f.write(line)

if __name__ == "__main__":
    comm = MPI.COMM_WORLD
    
    base_mesh = "flatplate.su2"
    split_mesh = "flatplate_split.su2"
    base_cfg = "flatplate.cfg"
    run_cfg = "flatplate_split.cfg"

    if comm.Get_rank() == 0:
        print("Bypassing pysu2 API limitations by dynamically splitting mesh boundaries...")
        split_wall_marker(base_mesh, split_mesh)
        
        print("Updating configuration file with spatial temperature gradient...")
        prepare_config(base_cfg, run_cfg, split_mesh)

    # Ensure all MPI processes wait for the file I/O to finish
    comm.Barrier()

    if comm.Get_rank() == 0:
        print("Initializing SU2 solver via pysu2...")
        
    driver = pysu2.CSinglezoneDriver(run_cfg, 1, comm)
    
    if comm.Get_rank() == 0:
        print("Starting simulation...")
        
    driver.StartSolver()
    
    if comm.Get_rank() == 0:
        print("Simulation finished. Post-processing...")
        
    driver.Postprocess()
    
    # Hard exit to avoid known SWIG memory deallocation segfault
    os._exit(0)