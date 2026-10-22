using System;
using System.Collections;
using System.Text;
using UnityEngine;
using UnityEngine.Networking;

// Attach to an AutoDRIVE scene. Uses AutoDRIVE's CoSimManager and the actual NeoRacer prefab.
// This component NEVER connects to a physical-car command interface.
public class TraCRPoseFollower : MonoBehaviour
{
    public string ServerUrl = "http://127.0.0.1:8080";
    [Tooltip("Use TRACR_TOKEN environment variable; avoid saving secrets in scenes.")]
    public string TokenEnvironmentVariable = "TRACR_TOKEN";
    public CoSimManager CoSim;
    public Camera DisplayCamera;
    [Tooltip("Assign Socket and all vehicle actuator/controller behaviours. They are restored on disable.")]
    public Behaviour[] DisableWhileFollowing;
    [Tooltip("Enable only after assigning the correct virtual vehicle and disabling competing writers.")]
    public bool FollowMeasuredPose = false;
    public int Width = 960;
    public int Height = 540;
    [Range(30, 95)] public int JpegQuality = 80;
    [Range(1, 30)] public int MaximumFps = 20;
    [Tooltip("Offset from mapped vehicle reference point to this prefab rigidbody origin, in body coordinates: x forward, y left, z up.")]
    public Vector3 BodyOriginOffset;
    [Tooltip("Prefab visual forward correction; verify with cardinal headings before use.")]
    public float PrefabYawOffsetDegrees = 0;

    [Serializable] class Target {
        public string ticket, frame_id, pose_id;
        public double capture_time, pose_time;
        public float ux, uy, uz, qx, qy, qz, qw;
    }
    [Serializable] class Frame {
        public string ticket, frame_id, pose_id, jpeg;
    }
    RenderTexture output;
    Texture2D pixels;
    bool originalKinematic, originalCoSimEnabled, originalTeleport;
    Vector3 originalPosition;
    Quaternion originalRotation;
    bool[] originalEnabled;
    bool initialized;
    Coroutine worker;

    void OnEnable() { worker = StartCoroutine(Run()); }

    IEnumerator Run()
    {
        if (!FollowMeasuredPose || CoSim == null || CoSim.VehicleRigidBody == null || DisplayCamera == null) {
            Debug.LogError("TraCR: assign CoSim, rigidbody, display camera and enable FollowMeasuredPose.");
            yield break;
        }
        if (Width < 16 || Width > 1920 || Height < 16 || Height > 1080) {
            Debug.LogError("TraCR: unsupported output size."); yield break;
        }
        var body = CoSim.VehicleRigidBody;
        originalKinematic = body.isKinematic;
        originalCoSimEnabled = CoSim.enabled;
        originalTeleport = CoSim.Teleport;
        originalPosition = CoSim.CoSimPosition;
        originalRotation = CoSim.CoSimRotation;
        originalEnabled = new bool[DisableWhileFollowing == null ? 0 : DisableWhileFollowing.Length];
        for (int i=0; i<originalEnabled.Length; i++) {
            var behaviour = DisableWhileFollowing[i];
            if (behaviour == null || behaviour == this || behaviour == CoSim) continue;
            originalEnabled[i] = behaviour.enabled; behaviour.enabled = false;
        }
        body.isKinematic = true;
        CoSim.Teleport = true;
        // We apply CoSim targets explicitly once per capture; keep Update from racing the render.
        CoSim.enabled = false;
        output = new RenderTexture(Width, Height, 24, RenderTextureFormat.ARGB32);
        output.Create();
        pixels = new Texture2D(Width, Height, TextureFormat.RGB24, false);
        initialized = true;
        var throttle = new WaitForSecondsRealtime(1f / Mathf.Clamp(MaximumFps,1,30));
        while (FollowMeasuredPose) {
            using (var get = UnityWebRequest.Get(ServerUrl.TrimEnd('/') + "/api/unity/next")) {
                Authorize(get);
                yield return get.SendWebRequest();
                if (get.responseCode == 204) { yield return throttle; continue; }
                if (get.result != UnityWebRequest.Result.Success) {
                    Debug.LogWarning("TraCR: bridge unavailable or unauthorized; virtual pose held.");
                    yield return new WaitForSecondsRealtime(1); continue;
                }
                Target target = null;
                try { target = JsonUtility.FromJson<Target>(get.downloadHandler.text); }
                catch (Exception e) { Debug.LogError("TraCR target parse: " + e.Message); }
                if (target == null || String.IsNullOrEmpty(target.ticket)) { yield return throttle; continue; }
                Quaternion mapRotation = new Quaternion(target.qx,target.qy,target.qz,target.qw);
                Vector3 offset = mapRotation * new Vector3(-BodyOriginOffset.y,BodyOriginOffset.z,BodyOriginOffset.x);
                CoSim.CoSimPosition = new Vector3(target.ux,target.uy,target.uz) + offset;
                CoSim.CoSimRotation = mapRotation * Quaternion.Euler(0, PrefabYawOffsetDegrees, 0);
                CoSim.CoSimTimer = 0;
                body.position = CoSim.CoSimPosition;
                body.rotation = CoSim.CoSimRotation;
                body.transform.SetPositionAndRotation(CoSim.CoSimPosition,CoSim.CoSimRotation);
                Physics.SyncTransforms();
                // Allow chase-camera LateUpdate to observe the pose, then capture that exact target.
                yield return new WaitForEndOfFrame();
                var previousTarget = DisplayCamera.targetTexture;
                var previousActive = RenderTexture.active;
                string encoded = null;
                try {
                    DisplayCamera.targetTexture = output;
                    DisplayCamera.Render();
                    RenderTexture.active = output;
                    pixels.ReadPixels(new Rect(0,0,Width,Height),0,0);
                    pixels.Apply();
                    encoded = Convert.ToBase64String(pixels.EncodeToJPG(JpegQuality));
                } finally {
                    DisplayCamera.targetTexture = previousTarget;
                    RenderTexture.active = previousActive;
                }
                var frame = new Frame {ticket=target.ticket, frame_id=target.frame_id,
                                       pose_id=target.pose_id, jpeg=encoded};
                using (var post = new UnityWebRequest(ServerUrl.TrimEnd('/') + "/api/unity/frame", "POST")) {
                    post.uploadHandler = new UploadHandlerRaw(Encoding.UTF8.GetBytes(JsonUtility.ToJson(frame)));
                    post.downloadHandler = new DownloadHandlerBuffer();
                    post.SetRequestHeader("Content-Type", "application/json");
                    Authorize(post);
                    yield return post.SendWebRequest();
                    if (post.result != UnityWebRequest.Result.Success)
                        Debug.LogWarning("TraCR: render rejected (late, stale or mismatched); next frame will be requested.");
                }
            }
            yield return throttle;
        }
        // Unchecking follow in the inspector releases all modified state.
        enabled = false;
    }

    void Authorize(UnityWebRequest request) {
        request.timeout = 2;
        var token = Environment.GetEnvironmentVariable(TokenEnvironmentVariable);
        if (!String.IsNullOrEmpty(token)) request.SetRequestHeader("Authorization", "Bearer " + token);
    }

    void OnDisable() {
        if (worker != null) StopCoroutine(worker);
        if (!initialized) return;
        CoSim.VehicleRigidBody.isKinematic = originalKinematic;
        CoSim.Teleport = originalTeleport;
        CoSim.CoSimPosition = originalPosition;
        CoSim.CoSimRotation = originalRotation;
        CoSim.enabled = originalCoSimEnabled;
        for (int i=0; i<originalEnabled.Length; i++) {
            var behaviour = DisableWhileFollowing[i];
            if (behaviour != null && behaviour != this && behaviour != CoSim) behaviour.enabled = originalEnabled[i];
        }
        if (output != null) { output.Release(); Destroy(output); }
        if (pixels != null) Destroy(pixels);
        initialized = false;
    }
}
