//GLSL
#version 140
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelViewMatrix;
uniform mat4 p3d_ModelMatrix;
//uniform mat4 p3d_ModelMatrixInverseTranspose;
uniform mat4 tpose_model_to_world; //pre 1.10 cg-style input

in vec3 p3d_Normal;
in vec4 p3d_Vertex;
in vec2 p3d_MultiTexCoord0;

out vec3 normal;
out vec4 world_pos;
out vec2 uv;
//uniform float bias;
//uniform mat4 trans_model_to_clip_of_shadowCamera;
//out vec4 shadowCoord;

void main()
    {
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;     
    uv = p3d_MultiTexCoord0;
    normal = (tpose_model_to_world * vec4(p3d_Normal, 0.0)).xyz; 
    world_pos=p3d_ModelMatrix* p3d_Vertex;      
    }
