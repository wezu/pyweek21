//GLSL
#version 140
uniform sampler2D grass;
uniform sampler2D cut;
in vec2 uv; 

void main()
    {    
    vec4 grass_map=texture(grass,uv);
    grass_map -=texture(cut,uv).r;     
    gl_FragData[0]=grass_map;       
    }
