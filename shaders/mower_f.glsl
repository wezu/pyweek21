//GLSL
#version 140
uniform sampler2D p3d_Texture0;
in vec2 uv; 

void main()
    {    
    vec4 final=texture(p3d_Texture0,uv);    
    gl_FragData[0]=final;       
    }
