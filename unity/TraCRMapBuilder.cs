#if UNITY_EDITOR
using System;
using System.IO;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;

// Editor-only additive import. Does not modify vehicle assets or control a car.
public static class TraCRMapBuilder
{
    [Serializable] class Road { public float x0, y0, x1, y1, width; }
    [Serializable] class Point { public float x, y; }
    [Serializable] class Strip { public string id, kind; public float width_m; public Point[] points; }
    [Serializable] class Map {
        public string label, ground_color;
        public bool measured;
        public float width_m, height_m;
        public Road[] roads;
        public Strip[] strips;
    }

    [MenuItem("TraCR/Import road layout JSON")]
    static void Import()
    {
        var path = EditorUtility.OpenFilePanel("TraCR road layout", "", "json");
        if (String.IsNullOrEmpty(path)) return;
        var map = JsonUtility.FromJson<Map>(File.ReadAllText(path));
        if (map == null || (map.roads == null && map.strips == null) || map.width_m <= 0 || map.height_m <= 0)
            throw new ArgumentException("Invalid map. Use map.example.json or a generated .geometry.json file.");
        var root = new GameObject("TraCR map - " + (map.measured ? "surveyed" : "UNMEASURED DRAFT"));
        Undo.RegisterCreatedObjectUndo(root,"Import TraCR map");
        var groundColor = new Color(.29f,.30f,.31f);
        if (!String.IsNullOrEmpty(map.ground_color)) ColorUtility.TryParseHtmlString(map.ground_color,out groundColor);
        var groundMaterial = MakeMaterial("Ground",groundColor);
        AddBox(root.transform,"Ground",new Vector3(-map.height_m/2,-.01f,map.width_m/2),
            new Vector3(map.height_m,.02f,map.width_m),0,groundMaterial);
        if (map.roads != null) {
            var roadMaterial = MakeMaterial("Road",new Color(.12f,.14f,.16f));
            foreach (var road in map.roads) {
                var dx=road.x1-road.x0; var dy=road.y1-road.y0;
                var length=Mathf.Sqrt(dx*dx+dy*dy);
                if (length <= 0 || road.width <= 0) continue;
                AddBox(root.transform,"Road",new Vector3(-(road.y0+road.y1)/2,.003f,(road.x0+road.x1)/2),
                    new Vector3(road.width,.006f,length),-Mathf.Atan2(dy,dx)*Mathf.Rad2Deg,roadMaterial);
            }
        }
        if (map.strips != null) {
            var white=MakeMaterial("White tape",new Color(.95f,.96f,.94f));
            var yellow=MakeMaterial("Yellow tape",new Color(.95f,.86f,.08f));
            var red=MakeMaterial("Stop line",new Color(1f,.15f,.08f));
            foreach (var strip in map.strips) {
                if (strip.points == null || strip.points.Length < 2 || strip.width_m <= 0)
                    throw new ArgumentException("Invalid paint strip: " + strip.id);
                AddStrip(root.transform,strip,strip.kind=="stop"?red:strip.kind=="yellow"?yellow:white);
            }
        }
        AssetDatabase.SaveAssets();
        Selection.activeGameObject=root;
        Debug.Log("TraCR map: " + map.label + ". Verify dimensions and coordinate alignment. Stop lines are visual geometry, not control logic.");
    }

    static Material MakeMaterial(string name,Color color)
    {
        Directory.CreateDirectory("Assets/TraCR/Generated");
        AssetDatabase.Refresh();
        var shader=Shader.Find("HDRP/Lit") ?? Shader.Find("Universal Render Pipeline/Lit") ?? Shader.Find("Standard");
        if (shader == null) throw new InvalidOperationException("No supported surface shader found.");
        var material=new Material(shader);
        if(material.HasProperty("_BaseColor")) material.SetColor("_BaseColor",color);
        if(material.HasProperty("_Color")) material.SetColor("_Color",color);
        if(material.HasProperty("_Smoothness")) material.SetFloat("_Smoothness",.1f);
        AssetDatabase.CreateAsset(material,AssetDatabase.GenerateUniqueAssetPath("Assets/TraCR/Generated/"+name+".mat"));
        AssetDatabase.SaveAssets();
        return material;
    }

    static void AddStrip(Transform parent,Strip strip,Material material)
    {
        int n=strip.points.Length;
        var vertices=new Vector3[2*n]; var triangles=new int[6*(n-1)];
        bool closed=strip.points[0].x==strip.points[n-1].x && strip.points[0].y==strip.points[n-1].y;
        for(int i=0;i<n;i++) {
            var p=strip.points[i];
            var before=strip.points[closed && i==0?n-2:Math.Max(0,i-1)];
            var after=strip.points[closed && i==n-1?1:Math.Min(n-1,i+1)];
            var incoming=new Vector2(p.x-before.x,p.y-before.y).normalized;
            var outgoing=new Vector2(after.x-p.x,after.y-p.y).normalized;
            if(incoming.sqrMagnitude==0) incoming=outgoing;
            if(outgoing.sqrMagnitude==0) outgoing=incoming;
            var normalIn=new Vector2(-incoming.y,incoming.x);
            var normalOut=new Vector2(-outgoing.y,outgoing.x);
            // Match the preview's miter joins and its limit of twice the half width.
            var miter=(normalIn+normalOut).normalized;
            var normal=miter*(strip.width_m/2/Mathf.Max(.5f,Vector2.Dot(miter,normalIn)));
            vertices[2*i]=new Vector3(-(p.y-normal.y),.0007f,p.x-normal.x);
            vertices[2*i+1]=new Vector3(-(p.y+normal.y),.0007f,p.x+normal.x);
            if(i<n-1) {
                int k=2*i,j=6*i;
                triangles[j]=k; triangles[j+1]=k+1; triangles[j+2]=k+2;
                triangles[j+3]=k+1; triangles[j+4]=k+3; triangles[j+5]=k+2;
            }
        }
        var mesh=new Mesh {name=strip.id+" paint",indexFormat=IndexFormat.UInt32};
        mesh.vertices=vertices; mesh.triangles=triangles; mesh.RecalculateNormals(); mesh.RecalculateBounds();
        AssetDatabase.CreateAsset(mesh,AssetDatabase.GenerateUniqueAssetPath("Assets/TraCR/Generated/"+strip.id+".asset"));
        var item=new GameObject(strip.id+" / "+strip.kind);
        item.transform.SetParent(parent,false);
        item.AddComponent<MeshFilter>().sharedMesh=mesh;
        item.AddComponent<MeshRenderer>().sharedMaterial=material;
        // Tape has no raised collider; the shared mat supplies the flat ground.
    }

    static void AddBox(Transform parent,string name,Vector3 position,Vector3 scale,float yaw,Material material)
    {
        var item=GameObject.CreatePrimitive(PrimitiveType.Cube);
        item.name=name; item.transform.SetParent(parent,false);
        item.transform.localPosition=position; item.transform.localScale=scale;
        item.transform.localRotation=Quaternion.Euler(0,yaw,0);
        item.GetComponent<Renderer>().sharedMaterial=material;
    }
}
#endif
