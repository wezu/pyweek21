//GLSL
#version 140
uniform sampler2D cut;
uniform sampler2D grass;
uniform sampler2D mask;
in vec2 uv; 

void main()
    {  
    float alpha=texture(mask,uv).r;    
    vec3 color=vec3(0.0282, 0.54,0.0165);    
    vec4 grass_map=texture(grass,uv);
    grass_map -=texture(cut,uv).r;             
    float where_is_the_grass=step(0.1, grass_map.r+grass_map.g+grass_map.b);    
    gl_FragData[0]=vec4(color*where_is_the_grass, where_is_the_grass);
    }
