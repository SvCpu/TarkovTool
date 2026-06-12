"""
Generate per-layer Leaflet HTML files for EFT interactive maps.

Reads maps.json for layout definition + maps_static.json for markers,
produces one standalone .html per layer in maps/{map_key}/{layer_name}.html.

Usage: python generate_layers.py
"""

import json
import os
import math
import webbrowser
from pathlib import Path

# ── paths (relative to this script) ──
REF = Path(__file__).resolve().parent.parent / "reference"
MAPS_JSON = REF / "tarkov-dev" / "src" / "data" / "maps.json"
STATIC_JSON = REF / "tarkov-dev" / "src" / "data" / "maps_static.json"
OUT = Path(__file__).resolve().parent / "maps"


# ── helpers ──

def load_data():
    with open(MAPS_JSON, encoding="utf-8") as f:
        return json.load(f)
    # static markers are minimal; parse on demand


def _js_quoted(v):
    """Minimal Python→JS literal converter for arrays/dicts/numbers/strings."""
    return json.dumps(v)


def _sw_ne(bounds):
    """maps.json bounds → Leaflet [[minZ, maxX], [maxZ, minX]]."""
    sw = [bounds[0][1], bounds[0][0]]
    ne = [bounds[1][1], bounds[1][0]]
    return sw, ne


def _build_crs_js(tf, rotation):
    """Return a JavaScript block that defines a custom CRS."""
    sx, ox, sy_raw, oy = tf
    sy = sy_raw * -1  # Leaflet Y-axis is inverted
    return f"""
    var crs = L.extend({{}}, L.CRS.Simple, {{
        transformation: new L.Transformation({sx}, {ox}, {sy}, {oy}),
        projection: L.extend({{}}, L.Projection.LonLat, {{
            project: function (latlng) {{
                var p = L.Projection.LonLat.project(_rotate(latlng, {rotation}));
                return p;
            }},
            unproject: function (point) {{
                return _rotate(L.Projection.LonLat.unproject(point), {rotation} * -1);
            }}
        }})
    }});
    """


# ── HTML template ──

HTML = r"""<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>{title}</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
  html, body, #map {{ height: 100%; margin: 0; }}
  #map {{ background: #1a1a1a; }}
  .hidden-layer {{ display: none; }}
  .leaflet-marker-icon.map-area-label {{
    font-family: system-ui, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    font-weight: 800; font-size: 20px;
    color: #c9a84c; text-shadow: 0 0 3px #000;
    -webkit-text-stroke: 0.5px #000; text-align: center;
    border: none; background: none;
  }}
  .leaflet-marker-icon.map-area-label .label {{
    position: absolute; width: 200px;
  }}
  .leaflet-marker-icon.map-area-label.off-level {{ display: none; }}
  #info {{
    position: fixed; top: 10px; right: 10px; z-index: 9999;
    background: rgba(0,0,0,0.8); color: #fff; padding: 10px 16px;
    border-radius: 6px; font: 14px/1.5 sans-serif;
  }}
  #info a {{ color: #8cf; }}
  .nav-links {{
    position: fixed; bottom: 10px; left: 50%; transform: translateX(-50%);
    z-index: 9999; display: flex; gap: 8px;
  }}
  .nav-links a {{
    background: rgba(0,0,0,0.8); color: #fff; padding: 6px 14px;
    border-radius: 4px; text-decoration: none; font: 14px sans-serif;
    cursor: pointer;
  }}
  .nav-links a.active {{ background: #48f; }}
  .nav-links a:hover {{ background: #46a; }}
</style>
</head>
<body>
<div id="map"></div>
<div id="info">
  <strong>{map_label}</strong> — {layer_label}
  {coords_html}
</div>
<div class="nav-links">{nav_links}</div>
<script>
var map_key = "{map_key}";
var layer_key = "{layer_key}";

{rotate_js}
{crs_js}

var map = L.map("map", {{
    crs: crs,
        minZoom: {min_zoom},
        maxZoom: {max_zoom},
        zoomSnap: 0.1,
        wheelPxPerZoomLevel: 120,
        attributionControl: false,
}});

var bounds = L.latLngBounds({bounds_sw}, {bounds_ne});

// restore saved view or fit bounds
var saved = localStorage.getItem("eft_map_view_" + map_key);
if (saved) {{
    try {{
        var state = JSON.parse(saved);
        map.setView(state.center, state.zoom);
    }} catch(e) {{
        map.fitBounds(bounds);
    }}
}} else {{
    map.fitBounds(bounds);
}}

// ── base tile layer ──
{tile_js}

// ── SVG overlay ──
{svg_js}

// ── static markers ──
{markers_js}

// ── labels ──
{labels_js}

// ── save state before leaving ──
function saveMapState() {{
    var c = map.getCenter();
    localStorage.setItem("eft_map_view_" + map_key, JSON.stringify({{
        center: [c.lat, c.lng],
        zoom: map.getZoom()
    }}));
}}
window.addEventListener("beforeunload", saveMapState);

// ── coordinate display (click) ──
map.on("click", function (e) {{
    var lat = e.latlng.lat.toFixed(2);
    var lng = e.latlng.lng.toFixed(2);
    document.getElementById("info").innerHTML =
        '<strong>{map_label}</strong> — {layer_label}<br>' +
        'Game X: ' + lng + ', Z: ' + lat;
}});
</script>
</body>
</html>"""


def _rotate_js(rotation):
    if not rotation:
        return "function _rotate(latlng,r){return latlng;}"
    return f"""
function _rotate(latlng, r) {{
    if (!r) return latlng;
    var a = r * Math.PI / 180, c = Math.cos(a), s = Math.sin(a);
    var x = latlng.lng, y = latlng.lat;
    return L.latLng(x * s + y * c, x * c - y * s);
}}
"""


def _tile_js(tile_path, tile_size, sw, ne):
    if not tile_path:
        return "// no tile layer"
    swj = _js_quoted(sw)
    nej = _js_quoted(ne)
    extra = ""
    if tile_size and tile_size != 256:
        extra = f", tileSize: {tile_size}"
    t = _js_quoted(tile_path)
    return f"var tileLayer = L.tileLayer({t}, {{bounds: L.latLngBounds({swj}, {nej}){extra}}}).addTo(map);"


def _svg_js(svg_path, base_svg_layer, target_svg_layer, sw, ne, is_ground):
    if not svg_path:
        return "// no SVG"
    s = _js_quoted(svg_path)
    base_g = _js_quoted(base_svg_layer)
    target_g = _js_quoted(target_svg_layer)
    swj = _js_quoted(sw)
    nej = _js_quoted(ne)
    if is_ground:
        # ground page: show all groups normally
        return f"""
var svgEl = document.createElementNS("http://www.w3.org/2000/svg", "svg");
svgEl.setAttribute("xmlns", "http://www.w3.org/2000/svg");
var svgOverlay = L.svgOverlay(svgEl, L.latLngBounds({swj}, {nej})).addTo(map);
var svgLoaded = fetch({s})
    .then(function(r) {{ return r.text(); }})
    .then(function(t) {{
        svgEl.innerHTML = t;
        var viewBox = svgEl.children[0].getAttribute("viewBox");
        if (viewBox) svgEl.setAttribute("viewBox", viewBox);
    }});
"""
    else:
        # non-ground: dim base layer, show target layer, hide other overlays
        return f"""
var svgEl = document.createElementNS("http://www.w3.org/2000/svg", "svg");
svgEl.setAttribute("xmlns", "http://www.w3.org/2000/svg");
var svgOverlay = L.svgOverlay(svgEl, L.latLngBounds({swj}, {nej})).addTo(map);
var svgLoaded = fetch({s})
    .then(function(r) {{ return r.text(); }})
    .then(function(t) {{
        svgEl.innerHTML = t;
        var viewBox = svgEl.children[0].getAttribute("viewBox");
        if (viewBox) svgEl.setAttribute("viewBox", viewBox);
        var groups = svgEl.children[0].children;
        for (var i = 0; i < groups.length; i++) {{
            var g = groups[i];
            if (g.nodeName !== "g" || !g.id) continue;
            if (g.id === {target_g}) {{
                // target layer: keep full opacity
            }} else if (g.id === {base_g}) {{
                // base layer: dim
                g.style.opacity = "0.15";
            }} else {{
                // other overlays: hide
                g.classList.add("hidden-layer");
            }}
        }}
    }});
"""


def _markers_js(static, normalized_name):
    """Build marker JS from maps_static.json."""
    parts = []
    if normalized_name not in static:
        return ""
    cats = static[normalized_name]
    for cat, items in cats.items():
        icon_url = f"https://assets.tarkov.dev/maps/interactive/{cat}.png"
        for item in items:
            x = item["position"]["x"]
            z = item["position"]["z"]
            label = item.get("name", "")
            parts.append(f"""
L.marker([{z}, {x}], {{
    icon: L.icon({{iconUrl: {_js_quoted(icon_url)}, iconSize: [24, 24], iconAnchor: [12, 12]}})
}}).bindPopup({_js_quoted(label)}).addTo(map);
""")
    return "\n".join(parts)


def _labels_js(labels, is_ground, ly):
    """Build label markers from maps.json labels array."""
    if not labels:
        return ""
    parts = []
    extents = ly.get("extents", []) if not is_ground else []
    for lbl in labels:
        x = lbl["position"][0]
        z = lbl["position"][1]
        # compute positionY
        if len(lbl["position"]) > 2:
            pos_y = lbl["position"][2]
        elif "top" in lbl and "bottom" in lbl:
            pos_y = (lbl["top"] - lbl["bottom"]) / 2 + lbl["bottom"]
        else:
            pos_y = 0
        # height filter
        if not is_ground and extents:
            fake_pos = {"x": x, "y": pos_y, "z": z}
            if not _marker_is_on_layer(fake_pos, extents):
                continue
        text = lbl["text"]
        size = lbl.get("size", 100)
        rotation = lbl.get("rotation", 0)
        top = lbl.get("top", 1000)
        bottom = lbl.get("bottom", -1000)
        parts.append(f"""
L.marker([{z}, {x}], {{
    icon: L.divIcon({{
        html: '<div class="label" style="font-size:{size}%;transform:translate3d(-50%,-50%,0) rotate({rotation}deg)">{text}</div>',
        className: "map-area-label"
    }}),
    interactive: false,
    zIndexOffset: -100000,
    position: {{x:{x}, y:{pos_y}, z:{z}}},
    top: {top},
    bottom: {bottom},
    group: "place-names"
}}).addTo(map);
""")
    return "\n".join(parts)


def _nav_links(map_key, layer_key, layers):
    links = []
    base_url = f"../{map_key}/"
    cls_on = '"nav-link active"'
    cls_off = '"nav-link"'
    onclick = ' onclick="saveMapState();location.href=this.href"'
    links.append(
        f'<a href="{base_url}ground.html" class={cls_on if layer_key == "ground" else cls_off}{onclick}>Ground</a>'
    )
    for ly in layers:
        safe = ly["name"].lower().replace(" ", "-")
        links.append(
            f'<a href="{base_url}{safe}.html" class={cls_on if layer_key == safe else cls_off}{onclick}>{ly["name"]}</a>'
        )
    return "".join(links)


def _marker_is_on_layer(marker_pos, layer_extents):
    """Filter marker by layer height/bounds (same logic as index.jsx)."""
    y = marker_pos["y"]
    for ext in layer_extents:
        h = ext["height"]
        if h[0] <= y < h[1]:
            if "bounds" in ext:
                for b in ext["bounds"]:
                    # bounds format: [[maxX, minZ], [minX, maxZ]]
                    max_x, min_z = b[0]
                    min_x, max_z = b[1]
                    x, z = marker_pos["x"], marker_pos["z"]
                    if min_x <= x <= max_x and min_z <= z <= max_z:
                        return True
                return False
            return True
    return False


# ── main ──

def main():
    groups = load_data()
    static = {}
    if STATIC_JSON.exists():
        with open(STATIC_JSON, encoding="utf-8") as f:
            static = json.load(f)

    for group in groups:
        interactive = [m for m in group["maps"] if m.get("projection") == "interactive"]
        if not interactive:
            continue
        map_cfg = interactive[0]
        key = map_cfg["key"]
        name = map_cfg.get("normalizedName", key)
        label = group.get("normalizedName", key)
        tf = map_cfg.get("transform", [1, 0, 1, 0])
        rot = map_cfg.get("coordinateRotation", 0)
        bounds = map_cfg.get("bounds")
        if not bounds:
            continue
        sw, ne = _sw_ne(bounds)
        min_z = map_cfg.get("minZoom", 1)
        max_z = max(7, map_cfg.get("maxZoom", 5))
        tile_path = map_cfg.get("tilePath", "")
        tile_size = map_cfg.get("tileSize", 256)
        svg_path = map_cfg.get("svgPath", "")
        base_svg_layer = map_cfg.get("svgLayer", "Ground_Level")
        layers = map_cfg.get("layers", [])
        map_labels = map_cfg.get("labels", [])

        out_dir = OUT / key
        out_dir.mkdir(parents=True, exist_ok=True)

        rotate_code = _rotate_js(rot)
        crs_code = _build_crs_js(tf, rot)
        bounds_sw = _js_quoted(sw)
        bounds_ne = _js_quoted(ne)

        # --- collect all marker data (from static) ---
        # static has {norm_name: {category: [{position:{x,y,z}, name}]}}
        marker_items = []
        if name in static:
            for cat, items in static[name].items():
                for item in items:
                    marker_items.append(item)

        # --- generate per-layer files ---
        all_layers = [{"name": "Ground", "svgLayer": base_svg_layer, "extents": []}] + layers

        for ly in all_layers:
            is_ground = ly["name"] == "Ground"
            layer_key = "ground" if is_ground else ly["name"].lower().replace(" ", "-")
            layer_id = ly.get("svgLayer", base_svg_layer)

            # markers filtered by layer extents
            markers_code = ""
            for mitem in marker_items:
                pos = mitem["position"]
                y = pos["y"]
                # ground: no height filter (show all)
                # other layers: filter by extents
                if not is_ground:
                    extents = ly.get("extents", [])
                    if not _marker_is_on_layer(pos, extents):
                        continue
                x, z = pos["x"], pos["z"]
                label = mitem.get("name", "")
                icon_url = "https://assets.tarkov.dev/maps/interactive/spawn_sniper_scav.png"
                markers_code += f"""
L.marker([{z}, {x}], {{
    icon: L.icon({{iconUrl: {_js_quoted(icon_url)}, iconSize: [24, 24], iconAnchor: [12, 12]}})
}}).bindPopup({_js_quoted(label)}).addTo(map);
"""

            svg_code = "// no SVG path available"
            tile_code = "// using SVG only"
            if svg_path:
                svg_code = _svg_js(svg_path, base_svg_layer, layer_id, sw, ne, is_ground)

            # labels filtered by layer extents
            labels_code = _labels_js(map_labels, is_ground, ly)

            # coords in info panel
            coords_html = ""
            if rot:
                coords_html += f"<br>Rotation: {rot}°"
            if tf:
                coords_html += f"<br>Transform: {tf}"

            nav_links = _nav_links(key, layer_key, layers)

            html_content = HTML.format(
                title=f"{label} — {ly['name']} — EFT Map",
                map_key=key,
                layer_key=layer_key,
                map_label=label,
                layer_label=ly["name"],
                coords_html=coords_html,
                nav_links=nav_links,
                rotate_js=rotate_code,
                crs_js=crs_code,
                min_zoom=min_z,
                max_zoom=max_z,
                bounds_sw=bounds_sw,
                bounds_ne=bounds_ne,
                tile_js=tile_code,
                svg_js=svg_code,
                markers_js=markers_code,
                labels_js=labels_code,
            )

            fpath = out_dir / f"{layer_key}.html"
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(html_content)
            print(f"  -> {fpath}")

    # write an index page once at the end
    _write_root_index(groups)


def _write_root_index(groups):
    links = []
    for group in groups:
        interactive = [m for m in group["maps"] if m.get("projection") == "interactive"]
        if not interactive:
            continue
        key = interactive[0]["key"]
        label = group.get("normalizedName", key)
        links.append((label, key))

    html = """<!DOCTYPE html>
<html lang="zh">
<head><meta charset="UTF-8"><title>EFT Map Layers</title>
<style>
  body { font: 16px/1.6 sans-serif; max-width: 640px; margin: 40px auto; padding: 0 20px; }
  h1 { color: #333; }
  ul { list-style: none; padding: 0; }
  li { margin: 8px 0; }
  a { color: #06c; text-decoration: none; font-size: 18px; }
  a:hover { text-decoration: underline; }
</style>
</head>
<body>
<h1>EFT interactive maps — per-layer view</h1>
<ul>
"""
    for label, key in links:
        html += f'  <li><a href="maps/{key}/ground.html">{label}</a></li>\n'
    html += """
</ul>
</body>
</html>"""
    idx = OUT.parent / "index.html"
    with open(idx, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  -> {idx} (root index)")


if __name__ == "__main__":
    main()
