// Simple 2D axisymmetric jet domain for SU2 Assignment 2
// Units in meters

L = 1.0; 
R = 0.5;
R_jet = 0.05;

// Mesh sizing: finer at the jet shear layer, coarse in the farfield
Point(1) = {0, 0, 0, 0.002};       
Point(2) = {0, R_jet, 0, 0.002};   
Point(3) = {0, R, 0, 0.05};        
Point(4) = {L, R, 0, 0.05};        
Point(5) = {L, 0, 0, 0.05};        

Line(1) = {1, 2}; 
Line(2) = {2, 3}; 
Line(3) = {3, 4}; 
Line(4) = {4, 5}; 
Line(5) = {5, 1}; 

Line Loop(1) = {1, 2, 3, 4, 5};
Plane Surface(1) = {1};

// SU2 boundary markers
Physical Curve("MARKER_INLET") = {1};
Physical Curve("MARKER_WALL") = {2}; 
Physical Curve("MARKER_FAR") = {3};
Physical Curve("MARKER_OUTLET") = {4};
Physical Curve("MARKER_SYM") = {5};
Physical Surface("fluid") = {1};
