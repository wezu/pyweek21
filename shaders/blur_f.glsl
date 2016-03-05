//GLSL
#version 140
uniform sampler2D input_map;
in vec2 uv0;
in vec2 uv1;
in vec2 uv2;
in vec2 uv3;
in vec2 uv4;
in vec2 uv5;
in vec2 uv6;
in vec2 uv7;
in vec2 uv8;
in vec2 uv9;
in vec2 uv10;
in vec2 uv11;

void main() 
    {    
    vec4 out_tex= vec4(0.0, 0.0, 0.0, 0.0);
    //Hardcoded blur
    out_tex += texture(input_map, uv0);
    out_tex += texture(input_map, uv1);
    out_tex += texture(input_map, uv2);
    out_tex += texture(input_map, uv3);
    out_tex += texture(input_map, uv4);
    out_tex += texture(input_map, uv5);
    out_tex += texture(input_map, uv6);
    out_tex += texture(input_map, uv7);
    out_tex += texture(input_map, uv8);
    out_tex += texture(input_map, uv9);
    out_tex += texture(input_map, uv10);
    out_tex += texture(input_map, uv11);
    out_tex/=12.0;
    gl_FragColor = out_tex;
    }
 
