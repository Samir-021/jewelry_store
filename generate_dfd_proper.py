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
    'entity': "rounded=0;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontStyle=1;",
    'process': "ellipse;whiteSpace=wrap;html=1;aspect=fixed;fillColor=#fff2cc;strokeColor=#d6b656;fontStyle=1;",
    'datastore': "shape=partialRectangle;right=0;left=1;top=1;bottom=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontStyle=1;",
    'flow': "endArrow=classic;html=1;rounded=0;labelBackgroundColor=#ffffff;",
    'flow_dual': "startArrow=classic;endArrow=classic;html=1;rounded=0;labelBackgroundColor=#ffffff;"
}

nodes = {}

# Sizing per specifications:
# Processes are strict circles (100x100)
# Open rectangles for Stores (missing right edge)
w_ent, h_ent = 120, 60
w_pro, h_pro = 100, 100
w_sto, h_sto = 120, 60

# Positioning coordinates helper (defines center geometric points to prevent overlap and cross)
def add_cent_node(value, type_, cx, cy, w, h):
    node_id = get_id()
    x = cx - (w / 2)
    y = cy - (h / 2)
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

# 1. External Entities (Rectangles)
add_cent_node("Vendor", "entity", cx=200, cy=150, w=w_ent, h=h_ent)
add_cent_node("User", "entity", cx=200, cy=550, w=w_ent, h=h_ent)
add_cent_node("eSewa", "entity", cx=1100, cy=550, w=w_ent, h=h_ent)

# 2. Processes (Circles) - strict order vertically removes all line crossings
add_cent_node("2.0\nProduct Mgt", "process", cx=500, cy=150, w=w_pro, h=h_pro)
add_cent_node("3.0\nOrder Proc", "process", cx=500, cy=350, w=w_pro, h=h_pro)
add_cent_node("4.0\nPayment Proc", "process", cx=500, cy=550, w=w_pro, h=h_pro)
add_cent_node("1.0\nUser Mgt", "process", cx=500, cy=750, w=w_pro, h=h_pro)

# 3. Data Stores (Open Rectangles)
add_cent_node("D2: Products", "datastore", cx=800, cy=250, w=w_sto, h=h_sto)
add_cent_node("D3: Orders", "datastore", cx=800, cy=450, w=w_sto, h=h_sto)
add_cent_node("D4: Payments", "datastore", cx=800, cy=650, w=w_sto, h=h_sto)
add_cent_node("D1: Users", "datastore", cx=800, cy=750, w=w_sto, h=h_sto)

# 4. Data Flows with Clear Labels
# User Connects
add_edge("User", "1.0\nUser Mgt", "register / login")
add_edge("User", "3.0\nOrder Proc", "place order")

# Vendor Connects
add_edge("Vendor", "2.0\nProduct Mgt", "add/update/\ndelete products")

# eSewa Connects
add_edge("4.0\nPayment Proc", "eSewa", "payment req\n& conf", dual=True)

# Process to Store Connections
add_edge("1.0\nUser Mgt", "D1: Users", "save/retrieve", dual=True)

add_edge("2.0\nProduct Mgt", "D2: Products", "save/update", dual=True)
add_edge("3.0\nOrder Proc", "D2: Products", "read info")

add_edge("3.0\nOrder Proc", "D3: Orders", "store order info")
add_edge("4.0\nPayment Proc", "D3: Orders", "update status")

add_edge("4.0\nPayment Proc", "D4: Payments", "store payment info")

add_edge("3.0\nOrder Proc", "4.0\nPayment Proc", "payment trigger")

# Pretty printing tree output handling
try:
    if hasattr(ET, 'indent'):
        ET.indent(root, space="\t", level=0)
except Exception:
    pass

tree = ET.ElementTree(mxfile)
tree.write('jewelry_DFD_level1.drawio', encoding='utf-8', xml_declaration=True)
print("Updated geometric DFD layout generated.")
