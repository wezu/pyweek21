//GLSL
#version 140

in vec4 p3d_Vertex;
in vec3 p3d_Normal;
in vec2 p3d_MultiTexCoord0;

uniform float osg_FrameTime;
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelViewMatrix;
//uniform mat4 p3d_ModelMatrixInverseTranspose;
uniform mat4 tpose_world_to_model; //pre 1.10 cg-style input
uniform mat4 p3d_ModelMatrix;
uniform sampler2D height;
uniform sampler2D grass;
uniform sampler2D cut;
uniform vec2 uv_offset;
uniform float z_scale;

out vec2 uv;
out vec3 normal;
out vec2 color_uv;
out vec4 world_pos;

uniform mat4 p3d_ViewMatrix;


void main()
    {   
    color_uv = p3d_MultiTexCoord0; 
    vec4 v = vec4(p3d_Vertex)+vec4(mod(float(gl_InstanceID), 16.0), floor((float(gl_InstanceID)*0.0625)+0.5),0.0, 0.0)*16.0;    
    uv=vec2(v.x*0.001953125, v.y*0.001953125)+uv_offset;    
    vec4 blend_mask=textureLod(grass,uv, 0.0); 
    blend_mask -=textureLod(cut,uv, 0.0).r; 
    normal = (tpose_world_to_model * vec4(p3d_Normal, 0.0)).xyz;
    
    if(dot(blend_mask.rgb, vec3(1.0, 1.0, 1.0)) < 0.1)        
        gl_Position=vec4(0.0,0.0,0.0,0.0);
    else
        {             
        v.z+=textureLod(height,uv, 0.0).r*z_scale;   
        float anim_co=step(0.75, color_uv.y);            
        float animation =sin(0.7*osg_FrameTime+float(gl_InstanceID)+v.x)*sin(1.7*osg_FrameTime+float(gl_InstanceID)+v.y)*anim_co;
        v.xy += animation*0.1; 
                        
        world_pos=p3d_ModelMatrix* v;          
        gl_Position = p3d_ModelViewProjectionMatrix * v;             
        }
    }
