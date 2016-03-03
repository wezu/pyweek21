//GLSL
#version 140

uniform sampler2D tex1;//color maps....
uniform sampler2D tex2;  
uniform sampler2D tex3;
uniform sampler2D tex4;
uniform sampler2D tex5;
uniform sampler2D tex6;
uniform sampler2D tex1n;//normal maps...
uniform sampler2D tex2n;
uniform sampler2D tex3n;
uniform sampler2D tex4n;
uniform sampler2D tex5n;
uniform sampler2D tex6n;

uniform sampler2D atr1; // rgb vaules are for mapping details
uniform sampler2D atr2; // rgb vaules are for mapping details

uniform sampler2D height; // a heightmap 
//uniform sampler2D walkmap; // walkmap 

//uniform vec4 fog; //fog color + for adjust in alpha
uniform vec3 ambient; //ambient light color

uniform vec4 p3d_ClipPlane[1];

uniform float water_level;
uniform float z_scale;

uniform vec3 camera_pos;

in float fog_factor; 
in vec2 texUV; 
in vec2 texUVrepeat;
in vec4 vpos;
in vec4 world_pos;

in vec4 shadowCoord;
uniform sampler2D shadow;
uniform vec4 fog;
uniform vec4 light_color[100];
uniform vec4 light_pos[100];
uniform int num_lights;

void main()
    { 
    vec4 fog_color=vec4(fog.rgb, 1.0);
    if (dot(p3d_ClipPlane[0], vpos) < 0.0) 
        {
        discard;
        }          
    //vec4 fog_color=vec4(fog.rgb, 0.0);        
    if(fog_factor>0.996)//fog only version
        {
        gl_FragData[0] = fog_color;            
        gl_FragData[1]=vec4(fog_factor,1.0,0.0,0.0);
        }        
    else //full version
        {        
        vec3 vLeft=vec3(1.0,0.0,0.0); 
        float gloss=0.0;                
        //vec3 normal=normalize(texture(height,texUV).xyz*2.0-1.0);              
        vec3 up= vec3(0.0,0.0,1.0);
        float specular =0.0;   
        vec3 V = normalize(world_pos.xyz - camera_pos);
    
    
        //normal vector...
        vec3 norm=vec3(0.0,0.0,1.0);    
        vec4 me=texture(height,texUV);
        vec4 n=texture(height, vec2(texUV.x,texUV.y+0.001953125)); 
        vec4 s=texture(height, vec2(texUV.x,texUV.y-0.001953125));   
        vec4 e=texture(height, vec2(texUV.x+0.001953125,texUV.y));    
        vec4 w=texture(height, vec2(texUV.x-0.001953125,texUV.y));
        //find perpendicular vector to norm:        
        vec3 temp = norm; //a temporary vector that is not parallel to norm    
        temp.x+=0.5;
        //form a basis with norm being one of the axes:
        vec3 perp1 = normalize(cross(norm,temp));
        vec3 perp2 = normalize(cross(norm,perp1));
        //use the basis to move the normal in its own space by the offset                       
        norm -= 0.9*z_scale*(((n.r-me.r)-(s.r-me.r))*perp1 - ((e.r-me.r)-(w.r-me.r))*perp2);
        vec3 normal = normalize(norm); 
    
        //mix the textures
        vec4 mask1=texture2D(atr1,texUV);
        vec4 mask2=texture2D(atr2,texUV);
        //detail               
        vec4 detail = vec4(0.0,0.0,0.0,0.0);
            detail+=texture(tex1, texUVrepeat)*mask1.r;
            detail+=texture(tex2, texUVrepeat)*mask1.g;
            detail+=texture(tex3, texUVrepeat)*mask1.b;
            detail+=texture(tex4, texUVrepeat)*mask2.r;
            detail+=texture(tex5, texUVrepeat)*mask2.g;
            detail+=texture(tex6, texUVrepeat)*mask2.b;
        //normal 
        vec4 norm_map = vec4(0.0,0.0,0.0,0.0);
            norm_map+=texture(tex1n, texUVrepeat)*mask1.r;
            norm_map+=texture(tex2n, texUVrepeat)*mask1.g;
            norm_map+=texture(tex3n, texUVrepeat)*mask1.b;
            norm_map+=texture(tex4n, texUVrepeat)*mask2.r;
            norm_map+=texture(tex5n, texUVrepeat)*mask2.g;
            norm_map+=texture(tex6n, texUVrepeat)*mask2.b;        
        gloss=norm_map.a;
        norm_map=norm_map*2.0-1.0;
        vec3 tangent=  cross(normal, vLeft);  
        vec3 binormal= cross(normal, tangent); 
        normal.xyz *= norm_map.z;
        normal.xyz += tangent * norm_map.x;
        normal.xyz += binormal * norm_map.y;    
        //norm+=normal;
        vec3 N = normalize(normal);                      

        //lights   
        //ambient 
        vec3 color=vec3(0.0, 0.0, 0.0);
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
            color+=light_color[i].rgb*max(dot(N,L), 0.0)*att;
            //half lambert
            //color+=light_color[i].rgb*pow((dot(N,L)*0.5)+0.5, 2.0)*att;
            //specular
            R=reflect(L,N)*att;
            specular +=pow(max(dot(R, V), 0.0), 9.0+gloss*4.0)*clamp(light_color[i].a*gloss*4.0, 0.0, 1.0);
            }        
        color +=specular;
        vec4 final= vec4(color.rgb * detail.xyz, 1.0);             
        //vec4 final= vec4(color.rgb, 1.0);             
        float shade = 1.0;      
        vec4 shadowUV = shadowCoord / shadowCoord.q;
        float shadowColor = texture(shadow, shadowUV.xy).r;            
        if (shadowColor < shadowUV.z-0.001)
            shade=fog_factor;                    
        specular=specular*(1.0-fog_factor)*0.2;                
        gl_FragData[0] = mix(final, fog_color ,fog_factor*fog_factor);                
        //gl_FragData[0]=vec4(color.rgb, 1.0);
        //gl_FragData[0] = vec4(fog_color.rgb, 1.0);                
        //gl_FragData[1]=vec4(fog_factor, shade, shade*specular,0.0);       
        //gl_FragData[0] = vec4(1.0, 0.0, 0.0, 0.0);
        //gl_FragData[1] = vec4(1.0, 0.0, 0.0, 1.0);
        }
    }
    
