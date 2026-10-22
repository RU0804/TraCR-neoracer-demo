#if UNITY_EDITOR
using System;
using System.IO;
using UnityEditor;
using UnityEngine;

// Editor-only, additive map import. Does not replace a scene or modify vehicle assets.
public static class TraCRMapBuilder
{
    [Serializable] class Road { public float x0, y0, x1, y1, width; }
    [Serializable] class Map { public string label; public bool measured; public float width_m, height_m; public Road[] roads; }

    [MenuItem("TraCR/Import measured road layout JSON")]
    static void Import()
    {
        var path = EditorUtility.OpenFilePanel("TraCR road layout", "", "json");
        if (String.IsNullOrEmpty(path)) return;
        var map = JsonUtility.FromJson<Map>(File.ReadAllText(path));
        if (map == null || map.roads == null || map.width_m <= 0 || map.height_m <= 0)
            throw new ArgumentException("Invalid map dimensions or roads");
        var root = new GameObject("TraCR map — " + (map.measured ? "surveyed" : "ILLUSTRATIVE ONLY"));
        Undo.RegisterCreatedObjectUndo(root,"Import TraCR map");
        var groundMaterial = MakeMaterial("Ground",new Color(.24f,.29f,.26f));
        var roadMaterial = MakeMaterial("Road",new Color(.12f,.14f,.16f));
        AddBox(root.transform, "Ground", new Vector3(-map.height_m/2,-.025f,map.width_m/2),
               new Vector3(map.height_m,.05f,map.width_m),0,groundMaterial);
        foreach (var road in map.roads) {
            var dx=road.x1-road.x0; var dy=road.y1-road.y0;
            var length=Mathf.Sqrt(dx*dx+dy*dy);
            if (length <= 0 || road.width <= 0) continue;
            AddBox(root.transform,"Road",new Vector3(-(road.y0+road.y1)/2,.003f,(road.x0+road.x1)/2),
                   new Vector3(road.width,.006f,length),-Mathf.Atan2(dy,dx)*Mathf.Rad2Deg,roadMaterial);
        }
        Selection.activeGameObject=root;
        Debug.Log("TraCR map: " + map.label + ". Verify units, origin, lane widths and vehicle footprint against the physical map.");
    }
    static Material MakeMaterial(string name,Color color) {
        Directory.CreateDirectory("Assets/TraCR/Generated");
        AssetDatabase.Refresh();
        var material=new Material(Shader.Find("Standard")); material.color=color;
        AssetDatabase.CreateAsset(material,AssetDatabase.GenerateUniqueAssetPath("Assets/TraCR/Generated/"+name+".mat"));
        AssetDatabase.SaveAssets();
        return material;
    }
    static void AddBox(Transform parent,string name,Vector3 position,Vector3 scale,float yaw,Material material) {
        var item=GameObject.CreatePrimitive(PrimitiveType.Cube);
        item.name=name; item.transform.SetParent(parent,false);
        item.transform.localPosition=position; item.transform.localScale=scale;
        item.transform.localRotation=Quaternion.Euler(0,yaw,0);
        item.GetComponent<Renderer>().sharedMaterial=material;
    }
}
#endif
