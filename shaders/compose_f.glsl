//GLSL
#version 140
uniform sampler2D colorTex;
uniform sampler2D blurTex;
uniform sampler2D blurTex2;
uniform sampler2D auxTex;
uniform sampler2D noiseTex;
uniform sampler2D glareTex;
uniform sampler2D flareTex;
uniform sampler2D starTex;

in vec2 uv;
in vec2 time_uv;
in vec2 rotate_uv;


void main() 
    {    
    vec4 blured_aux=texture(blurTex,uv);
    vec4 blured_color=texture(blurTex2, uv);
    float shadow=blured_aux.g*0.3+0.7;
    
    vec4 aux=texture(auxTex, uv);
    float fogfactor=aux.r;    
    float specfactor=aux.b+blured_aux.b;
    float distor=clamp(aux.a-0.5, 0.0, 0.5)*2.0;  
    
    vec2 noise=texture(noiseTex,time_uv).rg*2.0 - 1.0;    
    vec4 color=texture(colorTex,uv+noise*0.01*distor);    
    
    color=mix(color, blured_color, fogfactor);       
    color+=texture(glareTex,uv);//*0.5;         
    color+=texture(flareTex,vec2(1.0, 1.0)-uv)*texture(starTex, rotate_uv)*0.5;
    
    //color.rgb = color.rgb / (1.0 + color.rgb);
    //color.rgb = pow(color.rgb, vec3(1.0 / 2.2));  
    
    color*=shadow;           
    gl_FragColor =color;
    //gl_FragColor =color;
    }
