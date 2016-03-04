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

in vec4 transform_weight;
in uvec4 transform_index;
uniform mat4 p3d_TransformTable[100];
uniform mat3 p3d_NormalMatrix; 

uniform float bias;
uniform mat4 trans_model_to_clip_of_shadowCamera;
out vec4 shadowCoord;

void main()
    { 
    //hardware skinning
    mat4 matrix = p3d_TransformTable[transform_index.x] * transform_weight.x
              + p3d_TransformTable[transform_index.y] * transform_weight.y
              + p3d_TransformTable[transform_index.z] * transform_weight.z
              + p3d_TransformTable[transform_index.w] * transform_weight.w;
    
    gl_Position = p3d_ModelViewProjectionMatrix * matrix * p3d_Vertex;
    
    //workaround for driver crash
    mat3 matrix3=mat3(matrix);   
    normal=matrix3*p3d_Normal;  
    normal = (tpose_model_to_world * vec4(normal, 0.0)).xyz;
    

    uv=p3d_MultiTexCoord0;
    world_pos=p3d_ModelMatrix* p3d_Vertex; 
    
        
    // Calculate light-space clip position.
    vec4 pushed = p3d_Vertex + vec4(p3d_Normal * bias, 0.0);
    vec4 lightclip = trans_model_to_clip_of_shadowCamera * pushed;
    // Calculate shadow-map texture coordinates.
    shadowCoord = lightclip * vec4(0.5,0.5,0.5,1.0) + lightclip.w * vec4(0.5,0.5,0.5,0.0);    
    }


