//GLSL
#version 140
in vec2 p3d_MultiTexCoord0;
in vec4 p3d_Vertex;
in vec3 p3d_Normal;

uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelViewMatrix;
uniform mat4 p3d_ModelMatrix;
uniform vec4 fog;
uniform float tex_scale;

out float fog_factor;
out vec2 texUV;
out vec2 texUVrepeat;
out vec4 vpos;
out vec4 world_pos;

uniform float bias;
uniform mat4 trans_model_to_clip_of_shadowCamera;
out vec4 shadowCoord;


void main()
    { 
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;     
    vpos=p3d_ModelViewMatrix * p3d_Vertex;
    world_pos=p3d_ModelMatrix* p3d_Vertex;
    
    float distToEdge=clamp(pow(distance(world_pos.xy, vec2(256.0, 256.0))*0.004, 8.0), 0.0, 1.0);
    float distToCamera =clamp(-vpos.z*fog.a, 0.0, 0.95);
    fog_factor=clamp(distToCamera+distToEdge, 0.0, 1.0);  
      
    texUV=p3d_MultiTexCoord0;
    texUVrepeat=p3d_MultiTexCoord0*tex_scale; 
        
     // Calculate light-space clip position.
    vec4 pushed = p3d_Vertex + vec4(p3d_Normal * bias, 0);
    vec4 lightclip = trans_model_to_clip_of_shadowCamera * pushed;
    // Calculate shadow-map texture coordinates.
    shadowCoord = lightclip * vec4(0.5,0.5,0.5,1.0) + lightclip.w * vec4(0.5,0.5,0.5,0.0);    
    }
