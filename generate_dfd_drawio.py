import xml.etree.ElementTree as ET

mxfile = ET.Element('mxfile', host="app.diagrams.net")
diagram = ET.SubElement(mxfile, 'diagram', id="dfd_diagram", name="Level 1 DFD")
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
    'entity': "rounded=0;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontStyle=1",
    'process': "ellipse;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontStyle=1",
    'datastore': "shape=partialRectangle;right=0;left=0;whiteSpace=wrap;html=1;top=1;bottom=1;fillColor=#d5e8d4;strokeColor=#82b366;fontStyle=1",
    'flow': "endArrow=classic;html=1;rounded=0;labelBackgroundColor=#ffffff;",
    'flow_dual': "startArrow=classic;endArrow=classic;html=1;rounded=0;labelBackgroundColor=#ffffff;"
}

nodes = {}

def add_node(value, type_, x, y, w, h):
    node_id = get_id()
    cell = ET.SubElement(root, 'mxCell', id=node_id, value=value, style=styles[type_], vertex="1", parent="1")
    ET.SubElement(cell, 'mxGeometry', x=str(int(x)), y=str(int(y)), width=str(w), height=str(h), **{'as': 'geometry'})
    nodes[value] = node_id
    return node_id

def add_edge(source_val, target_val, label="", dual=False):
    edge_id = get_id()
    style = styles['flow_dual'] if dual else styles['flow']
    
    cell = ET.SubElement(root, 'mxCell', id=edge_id, value=label, style=style, edge="1", parent="1", source=nodes[source_val], target=nodes[target_val])
    ET.SubElement(cell, 'mxGeometry', relative="1", **{'as': 'geometry'})
    return edge_id

# 1. External Entities
add_node("User", "entity", 100, 210, 120, 60)
add_node("Vendor", "entity", 100, 610, 120, 60)
add_node("eSewa", "entity", 1100, 410, 120, 60)

# 2. Processes
add_node("1.0\nUser Mgt.", "process", 400, 200, 120, 80)
add_node("2.0\nProduct Mgt.", "process", 400, 600, 120, 80)
add_node("3.0\nOrder\nProcessing", "process", 400, 400, 120, 80)
add_node("4.0\nPayment\nProcessing", "process", 800, 400, 120, 80)

# 3. Data Stores
add_node("D1: Users", "datastore", 700, 210, 120, 60)
add_node("D2: Products", "datastore", 700, 610, 120, 60)
add_node("D3: Orders", "datastore", 600, 280, 120, 60)
add_node("D4: Payments", "datastore", 800, 210, 120, 60)

# 4. Data Flows
# User connections
add_edge("User", "1.0\nUser Mgt.", "register/login")
add_edge("User", "3.0\nOrder\nProcessing", "place order")

# Vendor connections
add_edge("Vendor", "2.0\nProduct Mgt.", "add/update/delete")

# eSewa connections
add_edge("4.0\nPayment\nProcessing", "eSewa", "req & conf", dual=True)

# Process <-> Data Store connections
add_edge("1.0\nUser Mgt.", "D1: Users", "save/retrieve\nuser info", dual=True)
add_edge("2.0\nProduct Mgt.", "D2: Products", "save/update", dual=True)
add_edge("3.0\nOrder\nProcessing", "D3: Orders", "store order info")
add_edge("3.0\nOrder\nProcessing", "D2: Products", "read availability")
add_edge("4.0\nPayment\nProcessing", "D4: Payments", "store payment info")
add_edge("4.0\nPayment\nProcessing", "D3: Orders", "update status")

# Optional: Add flow from P3 to P4 to trigger payment.
add_edge("3.0\nOrder\nProcessing", "4.0\nPayment\nProcessing", "payment trigger")

try:
    if hasattr(ET, 'indent'):
        ET.indent(root, space="\t", level=0)
except Exception:
    pass

tree = ET.ElementTree(mxfile)
tree.write('jewelry_DFD_level1.drawio', encoding='utf-8', xml_declaration=True)
print("DFD Diagram generated at jewelry_DFD_level1.drawio")
