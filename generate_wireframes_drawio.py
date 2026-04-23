import xml.etree.ElementTree as ET

mxfile = ET.Element('mxfile', host="app.diagrams.net")
diagram = ET.SubElement(mxfile, 'diagram', id="wireframe", name="Wireframes")
mxGraphModel = ET.SubElement(diagram, 'mxGraphModel', dx="1422", dy="798", grid="1", gridSize="10", guides="1", tooltips="1", connect="1", arrows="1", fold="1", page="1", pageScale="1", pageWidth="1600", pageHeight="1200", math="0", shadow="0")
root = ET.SubElement(mxGraphModel, 'root')
ET.SubElement(root, 'mxCell', id="0")
ET.SubElement(root, 'mxCell', id="1", parent="0")

id_counter = 2
def get_id():
    global id_counter
    res = str(id_counter)
    id_counter += 1
    return res

styles = {
    'browser': "rounded=1;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;align=center;verticalAlign=top;fontStyle=1;fontSize=18;spacingTop=10;",
    'header': "rounded=0;whiteSpace=wrap;html=1;fillColor=#222222;fontColor=#ffffff;strokeColor=none;align=left;spacingLeft=20;",
    'hero': "rounded=0;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;align=center;verticalAlign=middle;fontSize=24;",
    'section_title': "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize=20;fontStyle=1;fontFamily=Georgia;",
    'box': "rounded=0;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontStyle=1;",
    'product': "rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#cccccc;align=center;verticalAlign=bottom;spacingBottom=15;",
    'sidebar': "rounded=0;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;align=left;verticalAlign=top;spacingTop=20;spacingLeft=20;",
    'dashboard_main': "rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#cccccc;align=left;verticalAlign=top;spacingTop=20;spacingLeft=20;fontSize=18;fontStyle=1;",
    'metric': "rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontStyle=1;fontSize=22;"
}

def add_rect(value, style_key, x, y, w, h):
    node_id = get_id()
    cell = ET.SubElement(root, 'mxCell', id=node_id, value=value, style=styles[style_key], vertex="1", parent="1")
    ET.SubElement(cell, 'mxGeometry', x=str(int(x)), y=str(int(y)), width=str(w), height=str(h), **{'as': 'geometry'})
    return node_id

# ------------- HOME PAGE WIREFRAME -------------
# Browser Window Outline
add_rect("Home Page Wireframe", "browser", 50, 50, 600, 1000)
# Navigation / Header
add_rect("Jewelry Store        | Home     Collections     Products     Cart (3)", "header", 50, 90, 600, 50)
# Hero Carousel Frame
add_rect("Timeless Elegance\n\n[ Shop Collection ]", "hero", 50, 140, 600, 200)

# Featured Collections Layer
add_rect("Our Collections", "section_title", 50, 360, 600, 40)
add_rect("BRIDAL", "box", 80, 410, 160, 120)
add_rect("EVERYDAY LUXURY", "box", 270, 410, 160, 120)
add_rect("GIFTS", "box", 460, 410, 160, 120)

# Why Choose Us Layer
add_rect("Why Choose Us", "section_title", 50, 560, 600, 40)
add_rect("💎 Certified Diamonds", "box", 80, 610, 160, 60)
add_rect("🚚 Free Shipping", "box", 270, 610, 160, 60)
add_rect("🛡️ Lifetime Warranty", "box", 460, 610, 160, 60)

# New Arrivals Grid
add_rect("New Arrivals", "section_title", 50, 700, 600, 40)
add_rect("[Image Placeholder]\n\nDiamond Ring\nNPR 50,000", "product", 80, 750, 160, 180)
add_rect("[Image Placeholder]\n\nGold Necklace\nNPR 80,000", "product", 270, 750, 160, 180)
add_rect("[Image Placeholder]\n\nRuby Earrings\nNPR 30,000", "product", 460, 750, 160, 180)

# ------------- VENDOR DASHBOARD WIREFRAME -------------
# Browser Window Outline
add_rect("Vendor Dashboard Wireframe", "browser", 800, 50, 700, 700)
# Authenticated Header
add_rect("Vendor Portal        | View Storefront     Logout", "header", 800, 90, 700, 50)

# Sidebar Nav
sidebar_text = "Vendor Menu\n\n- Dashboard Overview\n- Manage Products\n- Add New Product\n- Store Settings\n- Sales Reports"
add_rect(sidebar_text, "sidebar", 800, 140, 200, 610)

# Main Dashboard View Area
dashboard_titles = "Dashboard Overview\n\nWelcome, Store Owner!\nStore Name: Luxury Gems (Kathmandu)"
add_rect(dashboard_titles, "dashboard_main", 1000, 140, 500, 610)

# KPIs and Metrics
add_rect("📋\n24\nTotal Products", "metric", 1040, 250, 200, 120)
add_rect("✅\nVerified\nStatus", "metric", 1260, 250, 200, 120)

# Optional content list 
add_rect("Recent Products List Grid placed here", "box", 1040, 400, 420, 100)

try:
    if hasattr(ET, 'indent'):
        ET.indent(root, space="\t", level=0)
except Exception:
    pass

tree = ET.ElementTree(mxfile)
tree.write('ui_wireframes.drawio', encoding='utf-8', xml_declaration=True)
print("Wireframes generated successfully.")
