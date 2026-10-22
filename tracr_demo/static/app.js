'use strict';
const $ = id => document.getElementById(id);
let socket, reconnect, lastStatus = 0, generation = 0, status, token = sessionStorage.getItem('tracr-token') || '';
let drawnTime = 0, drawnPoseTime = 0, serverOffset = 0;
const fmt = n => Number.isFinite(n) ? Math.round(n).toString() : '—';
function set(id, text) { $(id).textContent = text; }
function badge() {
  const disconnected = performance.now() - lastStatus > 1500;
  const now = Date.now()/1000 + serverOffset;
  const fresh = status && !disconnected;
  set('connection', fresh ? 'Local bridge connected' : 'Bridge disconnected · retrying');
  const videoOk = fresh && status.video_fresh && drawnTime && now-drawnTime < status.stale_s;
  const simOk = fresh && status.pose_fresh && status.render_fresh && drawnPoseTime && now-drawnPoseTime < status.stale_s;
  set('real-state', !drawnTime ? 'NO VIDEO' : !videoOk ? 'STALE VIDEO' : status.mode === 'self-test' ? 'SYNTHETIC' : 'VIDEO RECEIVED');
  set('sim-state', !drawnPoseTime ? 'NO RENDER' : !simOk ? 'STALE · NOT FOLLOWING' : status.mode === 'self-test' ? 'SYNTHETIC · NOT AUTODRIVE' : 'POSE-PAIRED RENDER');
  if(disconnected) set('notice', 'Bridge disconnected. Any visible images are frozen; they are not live.');
}
async function draw(message) {
  const thisGeneration = ++generation;
  const makeImage = async value => {
    const im = new Image(); im.src = 'data:image/jpeg;base64,'+value; await im.decode(); return im;
  };
  try {
    const frames = await Promise.all([makeImage(message.left), message.right ? makeImage(message.right) : null]);
    if(thisGeneration !== generation) return;
    requestAnimationFrame(() => {
      if(thisGeneration !== generation) return;
      $('real').src = frames[0].src; $('real').hidden = false; $('real-placeholder').hidden = true;
      drawnTime = message.capture_time;
      set('frame-label', message.frame_id);
      if(frames[1]) {
        $('sim').src = frames[1].src; $('sim').hidden = false; $('sim-placeholder').hidden = true;
        drawnPoseTime = message.pose_time;
        set('pose-label', message.pose_id);
        set('renderer-label', message.renderer === 'synthetic' ? 'SYNTHETIC SELF-TEST' : 'AUTODRIVE');
        set('skew', fmt(message.skew_ms)+' ms');
        set('position', message.x.toFixed(2)+' / '+message.y.toFixed(2)+' m');
      }
      badge();
    });
  } catch(e) { set('notice', 'Frame could not be decoded; waiting for the next frame.'); }
}
function connect() {
  clearTimeout(reconnect);
  socket = new WebSocket((location.protocol === 'https:' ? 'wss://' : 'ws://')+location.host+'/ws');
  socket.onopen = () => socket.send(JSON.stringify({token}));
  socket.onmessage = event => {
    const m = JSON.parse(event.data);
    if(m.type !== 'status') { draw(m); return; }
    status = m; lastStatus = performance.now(); serverOffset = m.server_time-Date.now()/1000;
    set('mode', m.mode === 'self-test' ? 'SYNTHETIC SELF-TEST' : 'LIVE INPUT MODE');
    set('map-label', m.map_label);
    set('camera-source', m.video_source); set('pose-source', m.pose_source);
    set('camera-age', fmt(m.video_age_ms)+' ms source age'); set('pose-age', fmt(m.pose_age_ms)+' ms pose age');
    set('latency', fmt(m.p95_ingest_to_pair_age_ms)+' ms'); set('pairs', m.accepted_pairs);
    set('quality', m.pose_quality === 'localized' ? 'Map localization reported by source' : m.pose_quality === 'odometry' ? 'Odometry only · drift expected' : m.pose_quality === 'test' ? 'Generated test trajectory' : 'Localization missing');
    set('timing', m.timing_verified ? 'Capture clocks marked calibrated' : 'Timing unverified · receipt/clock limits');
    let notice = 'Awaiting onboard camera, a measured map pose, and the AutoDRIVE Unity bridge.';
    if(m.mode === 'self-test') notice = 'SYNTHETIC SELF-TEST — both images and the trajectory are generated. No real vehicle or AutoDRIVE simulation is connected.';
    else if(!m.video_fresh) notice = 'Onboard video missing or stale. Check the camera connection.';
    else if(!m.pose_fresh) notice = 'Video available; map localization missing or stale. The virtual vehicle cannot follow yet.';
    else if(!m.render_fresh) notice = 'Video and pose available; waiting for a matching AutoDRIVE render. Check Unity and timestamp tolerance.';
    else if(!m.timing_verified) notice = 'Frames are paired by source timestamps. Capture-time synchronization and end-to-end latency remain unverified.';
    else notice = 'Camera frame paired with the pose applied in AutoDRIVE. Spatial calibration still requires field verification.';
    if(m.pose_quality === 'odometry') notice += ' Odometry is relative and can drift.';
    set('notice', notice); badge();
  };
  socket.onclose = e => {
    lastStatus = 0; badge();
    if(e.code === 1008) { $('auth').hidden = false; set('notice', 'Enter the local bridge token to connect.'); }
    else reconnect = setTimeout(connect, 1000);
  };
  socket.onerror = () => socket.close();
}
$('auth').onsubmit = e => { e.preventDefault(); token = $('token').value; sessionStorage.setItem('tracr-token',token); $('auth').hidden = true; connect(); };
$('fullscreen').onclick = async () => { try { if(document.fullscreenElement) await document.exitFullscreen(); else await document.documentElement.requestFullscreen(); } catch(e) { set('notice','Fullscreen is unavailable in this browser.'); } };
setInterval(badge, 200); connect();
