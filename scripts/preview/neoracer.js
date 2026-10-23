// Geometry preview only: official AutoDRIVE mesh, photo-derived road, scripted motion.
// This does not execute Unity, vehicle physics, sensor simulation, or the live bridge.
import * as THREE from 'three';
import { FBXLoader } from '/upstream/preview-assets/three/examples/jsm/loaders/FBXLoader.js';

const set = (selector, text) => document.querySelector(selector).textContent = text;
const normalize = text => text.toLowerCase().replace(/[^a-z0-9]/g, '');
const assetRoot = '/upstream/preview-assets/autodrive/Assets/Models/Vehicle/NeoRacer/';

window.previewReady = (async () => {
    set('.brand p', 'NeoRacer V1 / Poster demo preview');
    set('.thin', ' / MODEL PREVIEW');
    set('.eyebrow', 'NEORACER / OFFICIAL AUTODRIVE MODEL');
    set('.subtitle', 'Target layout: physical onboard video alongside a matching virtual vehicle.');
    set('#mode', '3D MODEL PREVIEW');
    set('#fullscreen', 'Scripted motion');
    document.querySelector('#fullscreen').disabled = true;
    set('#connection', 'NeoRacer / Photo-derived course');
    set('#map-label', '4.75 m square draft / Survey pending');
    set('#notice', 'MODEL PREVIEW - Both views are rendered in WebGL using the official NeoRacer mesh. No physical video or Unity execution.');
    const panels = document.querySelectorAll('.panel');
    panels[0].querySelector('h2').textContent = 'Onboard perspective';
    panels[0].querySelector('.tag').textContent = 'VIRTUAL CAMERA';
    panels[1].querySelector('h2').textContent = 'NeoRacer V1 model';
    panels[1].querySelector('.tag').textContent = 'AUTODRIVE GEOMETRY';
    set('#real-state', 'MODEL PREVIEW / FRONT VIEW');
    set('#sim-state', 'OFFICIAL NEORACER MESH');
    set('#camera-source', 'Target input: physical onboard video');
    set('#pose-source', 'Target renderer: AutoDRIVE / Unity');
    set('#camera-age', 'Hardware pending');
    set('#pose-age', 'Integration pending');
    for (const id of ['real-placeholder', 'sim-placeholder']) document.getElementById(id).hidden = true;
    for (const id of ['real', 'sim']) document.getElementById(id).hidden = false;
    document.querySelector('#real').alt = 'Illustrative virtual front camera, not physical footage';
    document.querySelector('#sim').alt = 'Official AutoDRIVE NeoRacer geometry rendered in WebGL';
    const titles = ['VEHICLE MODEL', 'SCRIPTED MOTION', 'ROAD LAYOUT', 'STOP LINE'];
    const notes = ['Official AutoDRIVE FBX geometry', 'Visual demonstration / No physics', '4.75 m square / Survey pending', '2 s dwell / No physical control'];
    document.querySelectorAll('.metrics > div').forEach((metric, i) => {
        metric.querySelector('p').textContent = titles[i];
        metric.querySelector('span').textContent = notes[i];
    });
    set('#skew', 'NeoRacer V1');
    set('#latency', 'Scripted path');
    set('#position', 'Photo draft');
    set('#pairs', 'S2, then S6');
    set('footer > span:first-child', 'TraCR / NeoRacer geometry from AutoDRIVE / WebGL visualization');
    set('footer > span:last-child', 'Preview only / No live vehicle connected');

    const scene = new THREE.Scene();
    scene.background = new THREE.Color('#c8c7bf');
    scene.fog = new THREE.Fog('#c8c7bf', 8, 20);
    const renderer = new THREE.WebGLRenderer({antialias: true, preserveDrawingBuffer: true});
    renderer.setSize(800, 450);
    renderer.setPixelRatio(1);
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.3;
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    scene.add(new THREE.HemisphereLight(0xf4faff, 0x526678, 2.2));
    const sunlight = new THREE.DirectionalLight(0xfff6df, 3);
    sunlight.position.set(-3, 5, -3);
    sunlight.castShadow = true;
    sunlight.shadow.mapSize.set(1024, 1024);
    Object.assign(sunlight.shadow.camera, {left: -3.5, right: 3.5, top: 3.5, bottom: -3.5, near: 0.1, far: 15});
    sunlight.shadow.bias = -0.000015;
    sunlight.shadow.normalBias = 0;
    scene.add(sunlight);
    scene.add(new THREE.DirectionalLight(0xd8f2ff, 1));
    function box(w, h, d, color, x, y, z) {
        const mesh = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), new THREE.MeshStandardMaterial({color, roughness: 0.85}));
        mesh.position.set(x, y, z); mesh.receiveShadow = true; scene.add(mesh); return mesh;
    }
    const map = await (await fetch('/configs/map.photo-v1.geometry.json')).json();
    const point = p => new THREE.Vector3(p.x - map.width_m / 2, 0, p.y - map.height_m / 2);
    box(30, 0.08, 30, '#b5a58e', 0, -0.06, 0);
    box(map.width_m, 0.02, map.height_m, map.ground_color, 0, -0.01, 0);
    // The photograph shows flat foam mat and tape, without raised track walls.
    const colors = {white: '#f5f6f0', yellow: '#f1dc25', stop: '#ff3826'};
    function strip(points, width, color, height) {
        const positions = [], indices = [];
        points.forEach((p, i) => {
            const before = points[Math.max(0, i - 1)], after = points[Math.min(points.length - 1, i + 1)];
            const tangent = after.clone().sub(before).normalize();
            const normal = new THREE.Vector3(-tangent.z, 0, tangent.x);
            for (const side of [-1, 1]) {
                const v = p.clone().addScaledVector(normal, side * width / 2);
                positions.push(v.x, height, v.z);
            }
            if (i < points.length - 1) {const k = 2*i; indices.push(k,k+2,k+1,k+1,k+2,k+3);}
        });
        const g = new THREE.BufferGeometry();
        g.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
        g.setIndex(indices); g.computeVertexNormals();
        const mesh = new THREE.Mesh(g, new THREE.MeshStandardMaterial({color, roughness: 1, side: THREE.DoubleSide}));
        mesh.receiveShadow = true; scene.add(mesh);
    }
    for (let i = 1; i < 10; i++) {
        const x = -map.width_m/2 + map.width_m*i/10;
        const z = -map.height_m/2 + map.height_m*i/10;
        strip([new THREE.Vector3(x,0,-map.height_m/2),new THREE.Vector3(x,0,map.height_m/2)],.003,'#424445',.0001);
        strip([new THREE.Vector3(-map.width_m/2,0,z),new THREE.Vector3(map.width_m/2,0,z)],.003,'#424445',.0001);
    }
    for (const line of map.strips) strip(line.points.map(point), line.width_m, colors[line.kind], .0007);
    // Use the shared sampled polyline without a second smoothing pass.
    const route = map.preview_route, routePoints = route.points.map(point), lengths = [0];
    for (let i=1; i<routePoints.length; i++) lengths.push(lengths[i-1]+routePoints[i].distanceTo(routePoints[i-1]));
    const routeLength = lengths.at(-1);
    function poseAt(s) {
        s = Math.max(0,Math.min(routeLength,s));
        let i=1; while (i<lengths.length-1 && lengths[i]<s) i++;
        const fraction=(s-lengths[i-1])/(lengths[i]-lengths[i-1]);
        const p=routePoints[i-1].clone().lerp(routePoints[i],fraction);
        // Central differences avoid visible heading jumps at polyline vertices.
        const a=routePoints[Math.max(0,i-2)], b=routePoints[Math.min(routePoints.length-1,i+1)];
        return {p,tangent:b.clone().sub(a).normalize()};
    }

    const materials = await (await fetch('/runtime/neoracer-materials.json')).json();
    const model = await new FBXLoader().loadAsync(assetRoot + 'NeoRacer.fbx');
    const sourceBox = new THREE.Box3().setFromObject(model);
    const rawSize = sourceBox.getSize(new THREE.Vector3());
    const rawCenter = sourceBox.getCenter(new THREE.Vector3());
    let frontAxle, rearAxle;
    const tires = [];
    model.traverse(object => {
        if (normalize(object.name) === 'frontaxle1') frontAxle = object;
        if (normalize(object.name) === 'rearaxle1') rearAxle = object;
        if (/^(front|rear)tire[0-9]+$/.test(normalize(object.name))) tires.push(object);
    });
    if (!frontAxle || !rearAxle) throw new Error('Cannot identify the source front/rear axles.');
    const frontCenter = new THREE.Box3().setFromObject(frontAxle).getCenter(new THREE.Vector3());
    const rearCenter = new THREE.Box3().setFromObject(rearAxle).getCenter(new THREE.Vector3());
    const sourceForward = frontCenter.clone().sub(rearCenter).normalize();
    const sourceHeading = Math.atan2(sourceForward.x, sourceForward.z);
    const materialNames = new Set(), unmatched = new Set(), meshes = [];
    model.traverse(object => {
        if (!object.isMesh) return;
        meshes.push({name: object.name, center: new THREE.Box3().setFromObject(object).getCenter(new THREE.Vector3()).toArray()});
        object.castShadow = true; object.receiveShadow = true;
        const convert = old => {
            materialNames.add(old.name);
            const saved = materials[normalize(old.name)];
            if (!saved) unmatched.add(old.name);
            return new THREE.MeshStandardMaterial({
                name: old.name,
                color: saved ? new THREE.Color(...saved.color) : old.color,
                metalness: saved ? saved.metallic : 0.1,
                roughness: saved ? Math.max(0.25, 1 - saved.smoothness) : 0.65,
                side: THREE.DoubleSide,
            });
        };
        object.material = Array.isArray(object.material) ? object.material.map(convert) : convert(object.material);
    });
    // Read source units and align the direction from rear axle to front axle to +Z.
    const settings = await (await fetch('/runtime/neoracer-model-settings.json')).json();
    model.scale.multiplyScalar(settings.metersPerUnit);
    model.rotation.y -= sourceHeading;
    const body = new THREE.Group(); body.add(model); scene.add(body);
    const size = new THREE.Box3().setFromObject(model).getSize(new THREE.Vector3());
    const center = new THREE.Box3().setFromObject(model).getCenter(new THREE.Vector3());
    if (tires.length !== 4) throw new Error(`Expected four tire groups; found ${tires.length}`);
    const floor = Math.min(...tires.map(tire => new THREE.Box3().setFromObject(tire).min.y));
    model.position.sub(new THREE.Vector3(center.x, floor, center.z));
    model.updateMatrixWorld(true);
    const alignedForward = new THREE.Box3().setFromObject(frontAxle).getCenter(new THREE.Vector3())
        .sub(new THREE.Box3().setFromObject(rearAxle).getCenter(new THREE.Vector3())).normalize();
    if (alignedForward.z < 0.99) throw new Error('Vehicle front does not align with the scripted path.');
    const tireContacts = tires.map(tire => ({name: tire.name, bottom: new THREE.Box3().setFromObject(tire).min.y}));
    if (Math.max(...tireContacts.map(t => Math.abs(t.bottom))) > .002) throw new Error('Tire contact exceeds 2 mm tolerance.');
    const frontCamera = new THREE.PerspectiveCamera(80, 16 / 9, 0.01, 25);
    const chaseCamera = new THREE.PerspectiveCamera(45, 16 / 9, 0.01, 25);
    const cross = (a,b) => a.x*b.z-a.z*b.x;
    function intersection(a,b,c,d) {
        const r=b.clone().sub(a), q=d.clone().sub(c), delta=c.clone().sub(a), denom=cross(r,q);
        if (Math.abs(denom)<1e-10) return null;
        const t=cross(delta,q)/denom, u=cross(delta,r)/denom;
        return t>=0 && t<=1 && u>=0 && u<=1 ? t : null;
    }
    const stops = route.stop_ids.map(id => {
        const line=map.markings.find(m => m.id===id), [a,b]=line.points.map(point);
        for (let i=1;i<routePoints.length;i++) {
            const fraction=intersection(routePoints[i-1],routePoints[i],a,b);
            if (fraction!==null) return {id, line, crossing:lengths[i-1]+fraction*(lengths[i]-lengths[i-1])};
        }
        throw new Error(`Route does not cross ${id}`);
    });
    // The body reference is its geometric center. Stop the front bumper before the tape.
    for (const stop of stops) stop.s=stop.crossing-size.z/2-stop.line.width_m/2-route.bumper_gap_m;
    stops.sort((a,b)=>a.s-b.s);
    const stages=[]; let clock=2, last=0;
    for (const target of [...stops,{id:'END',s:routeLength}]) {
        const distance=target.s-last, a=route.acceleration_mps2, peak=Math.min(route.max_speed_mps,Math.sqrt(distance*a));
        const ramp=peak/a, cruise=(distance-peak*peak/a)/peak;
        const duration=2*ramp+cruise;
        stages.push({start:clock,end:clock+duration,from:last,to:target.s,ramp,cruise,peak,id:target.id,kind:'drive'});
        clock+=duration;
        if (target.id!=='END') {
            stages.push({start:clock,end:clock+route.stop_dwell_s,s:target.s,id:target.id,kind:'stop'});
            clock+=route.stop_dwell_s;
        }
        last=target.s;
    }
    const duration=Math.ceil(clock+2);
    function stateAt(time) {
        if (time<2) return {s:0,speed:0,label:'Course overview',id:'S2'};
        const stage=stages.find(stage=>time>=stage.start && time<stage.end);
        if (!stage) return {s:routeLength,speed:0,label:'Pass complete / Replay',id:'Complete'};
        if (stage.kind==='stop') return {s:stage.s,speed:0,label:`Stopped at ${stage.id}`,id:stage.id};
        const t=time-stage.start, a=route.acceleration_mps2;
        let d,v;
        if (t<stage.ramp) {d=.5*a*t*t;v=a*t;}
        else if(t<stage.ramp+stage.cruise) {d=.5*stage.peak*stage.ramp+stage.peak*(t-stage.ramp);v=stage.peak;}
        else {const left=stage.end-time;d=stage.to-stage.from-.5*a*left*left;v=a*left;}
        return {s:stage.from+d,speed:v,label:v<stage.peak-.001 && t>stage.ramp ? 'Braking' : 'Driving',id:stage.id==='END'?'Finish':stage.id};
    }
    function footprint(s) {
        const {p,tangent}=poseAt(s), right=new THREE.Vector3(tangent.z,0,-tangent.x);
        return [[-1,-1],[1,-1],[1,1],[-1,1]].map(([x,z])=>p.clone().addScaledVector(right,x*size.x/2).addScaledVector(tangent,z*size.z/2));
    }
    function pointSegment(p,a,b) {
        const delta=b.clone().sub(a), t=THREE.MathUtils.clamp(p.clone().sub(a).dot(delta)/delta.lengthSq(),0,1);
        return p.distanceTo(a.clone().addScaledVector(delta,t));
    }
    function inside(p,polygon) {
        let value=false;
        for(let i=0,j=polygon.length-1;i<polygon.length;j=i++) {
            const a=polygon[i],b=polygon[j];
            if ((a.z>p.z)!==(b.z>p.z) && p.x<(b.x-a.x)*(p.z-a.z)/(b.z-a.z)+a.x) value=!value;
        }
        return value;
    }
    function clearance(corners,line) {
        const pts=line.points.map(point); let minimum=Infinity;
        for(let j=1;j<pts.length;j++) {
            if(inside(pts[j],corners)) return -line.width_m/2;
            for(let k=0;k<4;k++) {
                const a=corners[k],b=corners[(k+1)%4],c=pts[j-1],d=pts[j];
                if(intersection(a,b,c,d)!==null) return -line.width_m/2;
                minimum=Math.min(minimum,pointSegment(a,c,d),pointSegment(b,c,d),pointSegment(c,a,b),pointSegment(d,a,b));
            }
        }
        return minimum-line.width_m/2;
    }
    // Check the entire bounding rectangle, not only the center point or tire tracks.
    const boundaries=map.markings.filter(line=>line.kind!=='stop');
    const outer=map.markings.find(line=>line.id==='outer-edge').points.map(point);
    const divider=map.markings.find(line=>line.id==='main-divider').points.map(point);
    let minClearance=Infinity, worstDistance=0;
    const samples=Math.ceil(routeLength/.01);
    for(let i=0;i<=samples;i++) {
        const s=routeLength*i/samples, corners=footprint(s);
        if(!corners.every(p=>inside(p,outer)&&!inside(p,divider))) throw new Error(`Vehicle leaves the outer lane at ${s.toFixed(3)} m.`);
        for(const line of boundaries) {
            const value=clearance(corners,line);
            if(value<minClearance) {minClearance=value;worstDistance=s;}
        }
    }
    if(minClearance<.015) throw new Error(`Insufficient paint clearance: ${minClearance} m at ${worstDistance} m.`);
    const stopChecks=stops.map(stop=>({id:stop.id,route_distance_m:stop.s,front_bumper_clearance_m:clearance(footprint(stop.s),stop.line),dwell_seconds:route.stop_dwell_s}));
    if(stopChecks.some(stop=>stop.front_bumper_clearance_m<.055)) throw new Error('Front bumper is too close to a stop line.');
    window.previewInfo = {duration,routeLength,stages,minimum_paint_clearance_m:minClearance,footprint_samples:samples+1,
        sample_spacing_m:routeLength/samples,worst_clearance_route_distance_m:worstDistance,full_lap_validated:false,stops:stopChecks,tire_contacts:tireContacts,
        contact_tolerance_m:.002,map_source_sha256:map.source_sha256,map_measured:map.measured};
    window.modelInfo = {
        rawSize: rawSize.toArray(), rawCenter: rawCenter.toArray(), unitScaleFactor: settings.centimetersPerUnit,
        sourceForward: sourceForward.toArray(), alignedForward: alignedForward.toArray(),
        sizeMeters: size.toArray(), meshCount: meshes.length, meshes,
        materialNames: [...materialNames], unmatchedMaterials: [...unmatched],
        renderer: renderer.getContext().getParameter(renderer.getContext().RENDERER),
    };
    window.renderMap = async () => {
        const camera=new THREE.OrthographicCamera(-2.65,2.65,2.65,-2.65,.01,20);
        camera.position.set(0,8,0); camera.up.set(0,0,-1); camera.lookAt(0,0,0);
        const original=body.visible; body.visible=false;
        renderer.setSize(900,900); renderer.render(scene,camera);
        const image=renderer.domElement.toDataURL('image/png'); renderer.setSize(800,450); body.visible=original;
        return image;
    };
    window.renderFrame = async (seconds, probeAngle = null) => {
        const state=stateAt(seconds), {p,tangent}=poseAt(state.s);
        body.position.copy(p); body.rotation.y = Math.atan2(tangent.x, tangent.z);
        scene.updateMatrixWorld(true);
        const forward = tangent, right = new THREE.Vector3(tangent.z, 0, -tangent.x);
        frontCamera.position.copy(p).addScaledVector(forward, 0.24); frontCamera.position.y = 0.18;
        frontCamera.lookAt(frontCamera.position.clone().addScaledVector(forward, 2).add(new THREE.Vector3(0, -0.14, 0)));
        chaseCamera.position.copy(p).addScaledVector(forward, -0.85).addScaledVector(right, 0.55);
        chaseCamera.position.y = 0.55;
        chaseCamera.lookAt(p.clone().add(new THREE.Vector3(0, 0.09, 0)));
        if (seconds<2 && probeAngle===null) {
            chaseCamera.position.set(3,5,5); chaseCamera.lookAt(0,0,0);
        }
        if (probeAngle !== null) {
            body.position.set(0, 0, 0); body.rotation.set(0, 0, 0);
            const radius = Math.max(...size.toArray()) * 1.6;
            chaseCamera.position.set(radius * Math.sin(probeAngle), radius * 0.45, radius * Math.cos(probeAngle));
            chaseCamera.lookAt(0, size.y / 2, 0);
        }
        const images = [];
        for (const camera of [frontCamera, chaseCamera]) {
            renderer.render(scene, camera);
            images.push(renderer.domElement.toDataURL('image/png'));
        }
        for (const [i, id] of ['real', 'sim'].entries()) {
            const image = document.getElementById(id); image.src = images[i]; await image.decode();
        }
        set('#latency', `${state.speed.toFixed(2)} m/s`);
        set('#pairs', state.id);
        set('#frame-label', 'Virtual camera / Calibration pending');
        set('#pose-label', `${state.label} / Scripted preview`);
        return {triangles: renderer.info.render.triangles, calls: renderer.info.render.calls,state};
    };
    await window.renderFrame(0);
    return true;
})();
