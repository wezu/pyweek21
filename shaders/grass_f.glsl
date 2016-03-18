//GLSL
#version 140
uniform sampler2D tex1; //rgb color texture
uniform sampler2D tex2; //rgb color texture
uniform sampler2D tex3; //rgb color texture
uniform sampler2D grass;
uniform sampler2D cut;
//uniform sampler2D p3d_Texture1; //normal map

in vec2 uv;
//in float fog_factor;
in vec3 normal;
in vec2 color_uv;
in vec4 world_pos;
//in float lod_factor;

uniform vec3 ambient;
uniform vec4 fog;
uniform vec4 light_color[100];
uniform vec4 light_pos[100];
uniform int num_lights;
uniform vec3 camera_pos;

void main()
    {    
    vec4 blend_mask=texture(grass,uv);
    blend_mask -=texture(cut,uv).r; 
    //if (lod_factor>0.7)
    //    discard; 
    if(dot(blend_mask.rgb, vec3(1.0, 1.0, 1.0)) < 0.1)        
        discard; 
    else
        {        
        //vec2 texUV=gl_TexCoord[0].xy; 
        float fog_factor=distance(world_pos.xyz,camera_pos)*0.01;       
        fog_factor=clamp(fog_factor, 0.0, 1.0);
        if(fog_factor > 0.99)        
            discard; 
        vec4 color_tex = vec4(0.0,0.0,0.0,0.0);        
        color_tex+=texture(tex1,color_uv)*blend_mask.r;
        color_tex+=texture(tex2,color_uv)*blend_mask.g;
        color_tex+=texture(tex3,color_uv)*blend_mask.b;                    
        //color_tex.a-=lod_factor;
        //if (color_tex.a<0.5)
        //    discard;    
        vec3 N = normalize(normal);  
        vec3 up= vec3(0.0,0.0,1.0);
        //vec3 V = normalize(world_pos.xyz - camera_pos);
        
        vec3 color=vec3(0.01, 0.01, 0.01);
        //ambient 
        color+= (ambient+max(dot(N,up), -0.2)*ambient)*0.5; 
        
        vec3 L;
        vec3 R;
        float att;   
        for (int i=0; i<num_lights; ++i)
            { 
            //diffuse
            L = normalize(light_pos[i].xyz-world_pos.xyz);
            att=pow(distance(world_pos.xyz, light_pos[i].xyz), 2.0);      
            att =clamp(1.0 - att/(light_pos[i].w), 0.0, 1.0);  
            //lambert
            //color+=light_color[i].rgb*max(dot(N,L), 0.0)*att;
            //half lambert
            //color+=light_color[i].rgb*pow((dot(N,L)*0.5)+0.5, 2.0)*att;
            //not lambert at all
            color+=light_color[i].rgb*max(dot(N,L), 0.3)*att;
            //specular
            //R=reflect(L,N)*att;
            //specular +=pow(max(dot(R, V), 0.0), 11.0)*light_color[i].a*gloss;
            }   
            
        vec4 final = vec4(color*color_tex.rgb,color_tex.a) ;
        
        gl_FragData[0] = mix(final,fog ,fog_factor)*fog_factor;
        gl_FragData[0].a=color_tex.a;
        gl_FragData[1]=vec4(fog_factor, 1.0,0.0,0.0);
        }
    }
    
