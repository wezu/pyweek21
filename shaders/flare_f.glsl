//GLSL
#version 140
uniform sampler2D glareTex;

in vec2 uv;

void main()
    {
    int uGhosts=4;
    float uGhostDispersal=0.5;
    float uHaloWidth=0.4;
    vec2 texcoord = -uv + vec2(1.0, 1.0);    
    vec3 chroma_distort = vec3(-0.015, 0.01, 0.03);
 
    // ghost vector to image centre:
    vec2 ghostVec = (vec2(0.5, 0.5) - texcoord) * uGhostDispersal;
   
   vec2 haloVec = normalize(ghostVec) * uHaloWidth;
   
    // cromatic distort:  
    vec4 result = vec4(0.0, 0.0, 0.0, 0.0);
    result.x = texture(glareTex, texcoord + haloVec + haloVec * chroma_distort.x).x;
    result.y = texture(glareTex, texcoord + haloVec + haloVec * chroma_distort.y).y;
    result.z = texture(glareTex, texcoord + haloVec + haloVec * chroma_distort.z).z;
    // sample ghosts:  
    vec2 offset=vec2(0.0, 0.0);
    float weight=0.0;
    for (int i = 0; i < uGhosts; ++i)
        { 
        offset =texcoord + ghostVec * float(i); 
        weight = length(vec2(0.5, 0.5) - offset) / length(vec2(0.5, 0.5));
        weight = pow(1.0 - weight, 10.0);  
        result += texture(glareTex, offset)* weight; 
        } 
    // sample halo:    
    weight = length(vec2(0.5) - fract(texcoord + haloVec)) / length(vec2(0.5));
    weight = pow(1.0 - weight, 5.0);
    result += texture(glareTex, texcoord + haloVec) * weight;         
    gl_FragColor = clamp(result-0.1,0.0, 1.0);
   }
