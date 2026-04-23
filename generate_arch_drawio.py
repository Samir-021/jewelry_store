import xml.etree.ElementTree as ET

mxfile = ET.Element('mxfile', host="app.diagrams.net")
diagram = ET.SubElement(mxfile, 'diagram', id="arch", name="Architecture")
mxGraphModel = ET.SubElement(diagram, 'mxGraphModel', dx="1422", dy="798", grid="1", gridSize="10", guides="1", tooltips="1", connect="1", arrows="1", fold="1", page="1", pageScale="1", pageWidth="1400", pageHeight="1000", math="0", shadow="0")
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
    'client': "rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontStyle=1;fontSize=14;",
    'server': "rounded=1;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;fontStyle=1;fontSize=14;",
    'database': "shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;fillColor=#d5e8d4;strokeColor=#82b366;fontStyle=1;fontSize=14;",
    'cloud': "ellipse;shape=cloud;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontStyle=1;fontSize=14;",
    'edge': "endArrow=classic;startArrow=classic;html=1;rounded=0;edgeStyle=orthogonalEdgeStyle;strokeWidth=2;labelBackgroundColor=#ffffff;strokeColor=#333333;"
}

nodes = {}

def add_node(value, type_, cx, cy, w, h):
    node_id = get_id()
    x = cx - (w / 2)
    y = cy - (h / 2)
    cell = ET.SubElement(root, 'mxCell', id=node_id, value=value, style=styles[type_], vertex="1", parent="1")
    ET.SubElement(cell, 'mxGeometry', x=str(int(x)), y=str(int(y)), width=str(w), height=str(h), **{'as': 'geometry'})
    nodes[value] = node_id
    return node_id

def add_edge(source_val, target_val, label=""):
    edge_id = get_id()
    cell = ET.SubElement(root, 'mxCell', id=edge_id, value=label, style=styles['edge'], edge="1", parent="1", source=nodes[source_val], target=nodes[target_val])
    ET.SubElement(cell, 'mxGeometry', relative="1", **{'as': 'geometry'})
    return edge_id

# Width and Height values
w_rect, h_rect = 160, 80
w_db, h_db = 140, 140
w_cld, h_cld = 200, 120

# 1. Presentation Tier (Client)
add_node("Client\n(Web Browser)", "client", cx=200, cy=300, w=w_rect, h=h_rect)

# 2. Application Tier (Web Server)
add_node("Web Server\n(Django Application)", "server", cx=600, cy=300, w=w_rect, h=h_rect)

# 3. Data Tier (Database)
add_node("Database\n(Relational DB)", "database", cx=1000, cy=300, w=w_db, h=h_db)

# 4. External Services (eSewa)
add_node("eSewa Gateway\n(Payment API)", "cloud", cx=600, cy=600, w=w_cld, h=h_cld)

# Draw bidirectional connections centrally aligned
add_edge("Client\n(Web Browser)", "Web Server\n(Django Application)", "HTTP / HTTPS")
add_edge("Web Server\n(Django Application)", "Database\n(Relational DB)", "SQL Queries")
add_edge("Web Server\n(Django Application)", "eSewa Gateway\n(Payment API)", "API Requests")

try:
    if hasattr(ET, 'indent'):
        ET.indent(root, space="\t", level=0)
except Exception:
    pass

tree = ET.ElementTree(mxfile)
tree.write('architecture_design.drawio', encoding='utf-8', xml_declaration=True)
print("Architecture Draw.io Generated!")
