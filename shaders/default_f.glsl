//GLSL
#version 140
uniform vec4 light_color[100];
uniform vec4 light_pos[100];
uniform int num_lights;
uniform sampler2D p3d_Texture0; //rgba color texture 
uniform sampler2D p3d_Texture1; //rgba normal+gloss texture 
uniform vec3 camera_pos;
uniform vec3 ambient;
uniform vec4 fog;
uniform vec4 skyColor;
uniform vec4 cloudColor;


in vec2 uv;
in vec4 world_pos;
in vec3 normal;
in vec4 shadowCoord;
uniform sampler2D shadow;


//TBN by Chris­t­ian Schuler from http://www.thetenthplanet.de/archives/1180
mat3 cotangent_frame( vec3 N, vec3 p, vec2 uv )
    {
    // get edge vectors of the pixel triangle
    vec3 dp1 = dFdx( p );
    vec3 dp2 = dFdy( p );
    vec2 duv1 = dFdx( uv );
    vec2 duv2 = dFdy( uv );
 
    // solve the linear system
    vec3 dp2perp = cross( dp2, N );
    vec3 dp1perp = cross( N, dp1 );
    vec3 T = dp2perp * duv1.x + dp1perp * duv2.x;
    vec3 B = dp2perp * duv1.y + dp1perp * duv2.y;
 
    // construct a scale-invariant frame 
    float invmax = inversesqrt( max( dot(T,T), dot(B,B) ) );
    return mat3( T * invmax, B * invmax, N );
    }

vec3 perturb_normal( vec3 N, vec3 V, vec2 texcoord )
    {
    // assume N, the interpolated vertex normal and 
    // V, the view vector (vertex to eye)
    vec3 map = (texture( p3d_Texture1, texcoord ).xyz)*2.0-1.0;
    mat3 TBN = cotangent_frame( N, -V, texcoord );
    return normalize( TBN * map );
    }



void main()
    {    
    float fog_factor=distance(world_pos.xyz,camera_pos)*0.01;        
    fog_factor=clamp(pow(fog_factor, 2.0), 0.0, 1.0);
    
    vec3 color=vec3(0.0, 0.0, 0.0);
    vec4 color_map=texture(p3d_Texture0,uv);
    float gloss=texture(p3d_Texture1,uv).a;
    vec3 up= vec3(0.0,0.0,1.0);
    float specular =0.0;           
    vec3 N=normalize(normal);    
    vec3 V = normalize(world_pos.xyz - camera_pos);
    
    N = perturb_normal( N, V, uv);
    //vec3 skyR = reflect(V,N)*-1.0; 
   
           
    //ambient 
    //color+= (ambient*0.8+max(dot(N,up), -0.2)*ambient)*0.5; 
    color+= (ambient+max(dot(N,up), -0.2)*ambient)*0.5; 
    //color=ambient;
    
    vec3 L;
    vec3 R;
    float att;   
    for (int i=0; i<num_lights; ++i)
        { 
        //diffuse
        L = normalize(light_pos[i].xyz-world_pos.xyz);
        att=pow(distance(world_pos.xyz, light_pos[i].xyz), 2.0);      
        att =clamp(1.0 - att/(light_pos[i].w), 0.0, 1.0);  
        color+=light_color[i].rgb*max(dot(N,L), 0.0)*att;
        //specular
        R=reflect(L,N)*att;
        specular +=pow(max(dot(R, V), 0.0), 100.0)*light_color[i].a*gloss*10.0;
        }
        
    vec4 fog_color=vec4(fog.rgb, 1.0);  
    //color+=texture(spheremap,vN).rgb*gloss;
    color+=specular;
    //compose all  
    //vec4 final= vec4(color.rgb * color_map.xyz, color_map.a); 
    //color+=(texture(cubemap, R.xzy).rgb)*gloss*3.0;
    vec4 final= vec4(color.rgb * color_map.xyz, color_map.a);
    //gl_FragData[0]= texture(cubemap, skyR.xzy);
    gl_FragData[0] = mix(final ,fog_color, fog_factor);     
    //shadows
    //vec4 shadowUV = shadowCoord / shadowCoord.q;
    //float shadowColor = texture(shadow, shadowUV.xy).r;    
    //float shade = 1.0;
    //if (shadowColor < shadowUV.z-0.005)
    //   shade=fog_factor;        
    //gl_FragData[1]=vec4(fog_factor, shade, shade*specular*(1.0-fog_factor),0.0);
    }
