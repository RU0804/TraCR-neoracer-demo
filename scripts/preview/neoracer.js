// Geometry preview only: official AutoDRIVE mesh, illustrative road, scripted motion.
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
    set('#connection', 'NeoRacer / Illustrative course');
    set('#map-label', '5 m x 5 m / Not a measured map');
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
    const titles = ['VEHICLE MODEL', 'MOTION SOURCE', 'ROAD LAYOUT', 'LIVE INTEGRATION'];
    const notes = ['Official AutoDRIVE FBX geometry', 'Visual demonstration / No physics', 'Survey and calibration pending', 'Physical camera + pose + Unity'];
    document.querySelectorAll('.metrics > div').forEach((metric, i) => {
        metric.querySelector('p').textContent = titles[i];
        metric.querySelector('span').textContent = notes[i];
    });
    set('#skew', 'NeoRacer V1');
    set('#latency', 'Scripted path');
    set('#position', 'Illustrative');
    set('#pairs', 'Pending');
    set('footer > span:first-child', 'TraCR / NeoRacer geometry from AutoDRIVE / WebGL visualization');
    set('footer > span:last-child', 'Preview only / No live vehicle connected');

    const scene = new THREE.Scene();
    scene.background = new THREE.Color('#d8e5ed');
    scene.fog = new THREE.Fog('#d8e5ed', 5, 15);
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
    sunlight.shadow.bias = -0.0005;
    scene.add(sunlight);
    scene.add(new THREE.DirectionalLight(0xd8f2ff, 1));
    function box(w, h, d, color, x, y, z) {
        const mesh = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), new THREE.MeshStandardMaterial({color, roughness: 0.85}));
        mesh.position.set(x, y, z); mesh.receiveShadow = true; scene.add(mesh); return mesh;
    }
    box(30, 0.08, 30, '#c4cdd0', 0, -0.13, 0);
    box(5, 0.06, 5, '#e9e8db', 0, -0.04, 0);

    // An illustrative rounded road loop, independent of any surveyed physical map.
    const path = new THREE.CurvePath();
    const r = 0.8, a = 1.6, b = a - r;
    path.add(new THREE.LineCurve3(new THREE.Vector3(-b, 0, -a), new THREE.Vector3(b, 0, -a)));
    function arc(cx, cz, start, end) {
        class Corner extends THREE.Curve {
            getPoint(t, target = new THREE.Vector3()) {
                const angle = start + t * (end - start);
                return target.set(cx + r * Math.cos(angle), 0, cz + r * Math.sin(angle));
            }
        }
        path.add(new Corner());
    }
    arc(b, -b, -Math.PI / 2, 0);
    path.add(new THREE.LineCurve3(new THREE.Vector3(a, 0, -b), new THREE.Vector3(a, 0, b)));
    arc(b, b, 0, Math.PI / 2);
    path.add(new THREE.LineCurve3(new THREE.Vector3(b, 0, a), new THREE.Vector3(-b, 0, a)));
    arc(-b, b, Math.PI / 2, Math.PI);
    path.add(new THREE.LineCurve3(new THREE.Vector3(-a, 0, b), new THREE.Vector3(-a, 0, -b)));
    arc(-b, -b, Math.PI, Math.PI * 1.5);

    function ribbon(width, offset, color, height) {
        const positions = [], indices = [], steps = 320;
        for (let i = 0; i <= steps; i++) {
            const t = i / steps, p = path.getPointAt(t), direction = path.getTangentAt(t).normalize();
            const normal = new THREE.Vector3(-direction.z, 0, direction.x);
            for (const side of [-1, 1]) {
                const v = p.clone().addScaledVector(normal, offset + side * width / 2);
                positions.push(v.x, height, v.z);
            }
            if (i < steps) { const k = i * 2; indices.push(k, k + 2, k + 1, k + 1, k + 2, k + 3); }
        }
        const geometry = new THREE.BufferGeometry();
        geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
        geometry.setIndex(indices); geometry.computeVertexNormals();
        const mesh = new THREE.Mesh(geometry, new THREE.MeshStandardMaterial({color, side: THREE.DoubleSide, roughness: 0.95}));
        mesh.receiveShadow = true; scene.add(mesh);
    }
    ribbon(0.8, 0, '#343e46', 0.003);
    ribbon(0.018, 0.36, '#f5f5e9', 0.006);
    ribbon(0.018, -0.36, '#f5f5e9', 0.006);
    box(1.3, 0.012, 1.3, '#9cad8e', 0, -0.002, 0);
    for (let i = 0; i < 40; i++) {
        const t = i / 40, p = path.getPointAt(t), tangent = path.getTangentAt(t);
        const dash = box(0.014, 0.003, 0.13, '#e7cf83', p.x, 0.008, p.z);
        dash.rotation.y = Math.atan2(tangent.x, tangent.z);
    }
    for (const sign of [-1, 1]) {
        box(4.7, 0.10, 0.06, '#faf9f0', 0, 0.035, sign * 2.35);
        box(0.06, 0.10, 4.7, '#faf9f0', sign * 2.35, 0.035, 0);
    }
    // Simple course furniture provides depth cues without claiming a physical reconstruction.
    for (const [x, z] of [[-1.95, -1.9], [1.95, -1.9], [1.95, 1.9], [-1.95, 1.9]]) {
        const cone = new THREE.Mesh(new THREE.ConeGeometry(0.045, 0.16, 16), new THREE.MeshStandardMaterial({color: '#e8723d'}));
        cone.position.set(x, 0.08, z); scene.add(cone);
        box(0.12, 0.015, 0.12, '#373d42', x, 0.007, z);
    }

    const materials = await (await fetch('/runtime/neoracer-materials.json')).json();
    const model = await new FBXLoader().loadAsync(assetRoot + 'NeoRacer.fbx');
    const sourceBox = new THREE.Box3().setFromObject(model);
    const rawSize = sourceBox.getSize(new THREE.Vector3());
    const rawCenter = sourceBox.getCenter(new THREE.Vector3());
    let frontAxle, rearAxle;
    model.traverse(object => {
        if (normalize(object.name) === 'frontaxle1') frontAxle = object;
        if (normalize(object.name) === 'rearaxle1') rearAxle = object;
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
    const floor = new THREE.Box3().setFromObject(model).min.y;
    model.position.sub(new THREE.Vector3(center.x, floor, center.z));
    model.updateMatrixWorld(true);
    const alignedForward = new THREE.Box3().setFromObject(frontAxle).getCenter(new THREE.Vector3())
        .sub(new THREE.Box3().setFromObject(rearAxle).getCenter(new THREE.Vector3())).normalize();
    if (alignedForward.z < 0.99) throw new Error('Vehicle front does not align with the scripted path.');
    const frontCamera = new THREE.PerspectiveCamera(80, 16 / 9, 0.01, 25);
    const chaseCamera = new THREE.PerspectiveCamera(45, 16 / 9, 0.01, 25);
    window.modelInfo = {
        rawSize: rawSize.toArray(), rawCenter: rawCenter.toArray(), unitScaleFactor: settings.centimetersPerUnit,
        sourceForward: sourceForward.toArray(), alignedForward: alignedForward.toArray(),
        sizeMeters: size.toArray(), meshCount: meshes.length, meshes,
        materialNames: [...materialNames], unmatchedMaterials: [...unmatched],
        renderer: renderer.getContext().getParameter(renderer.getContext().RENDERER),
    };
    window.renderFrame = async (seconds, probeAngle = null) => {
        const progress = ((seconds / 20) % 1 + 1) % 1;
        const p = path.getPointAt(progress), tangent = path.getTangentAt(progress).normalize();
        body.position.copy(p); body.position.y = 0.012;
        body.rotation.y = Math.atan2(tangent.x, tangent.z);
        scene.updateMatrixWorld(true);
        const forward = tangent, right = new THREE.Vector3(tangent.z, 0, -tangent.x);
        frontCamera.position.copy(p).addScaledVector(forward, 0.24); frontCamera.position.y = 0.18;
        frontCamera.lookAt(frontCamera.position.clone().addScaledVector(forward, 2).add(new THREE.Vector3(0, -0.08, 0)));
        chaseCamera.position.copy(p).addScaledVector(forward, -0.8).addScaledVector(right, 0.5);
        chaseCamera.position.y = 0.46;
        chaseCamera.lookAt(p.clone().add(new THREE.Vector3(0, 0.11, 0)));
        if (probeAngle !== null) {
            body.position.set(0, 0.012, 0); body.rotation.set(0, 0, 0);
            const radius = Math.max(...size.toArray()) * 1.6;
            chaseCamera.position.set(radius * Math.sin(probeAngle), radius * 0.6, radius * Math.cos(probeAngle));
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
        set('#frame-label', 'Illustrative camera / Not calibrated');
        set('#pose-label', `NeoRacer / Scripted loop ${Math.round(progress * 100)}%`);
        return {triangles: renderer.info.render.triangles, calls: renderer.info.render.calls};
    };
    await window.renderFrame(0);
    return true;
})();
