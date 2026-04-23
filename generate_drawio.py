import xml.etree.ElementTree as ET
import math

mxfile = ET.Element('mxfile', host="app.diagrams.net")
diagram = ET.SubElement(mxfile, 'diagram', id="er_diagram", name="ER Diagram")
mxGraphModel = ET.SubElement(diagram, 'mxGraphModel', dx="1422", dy="798", grid="1", gridSize="10", guides="1", tooltips="1", connect="1", arrows="1", fold="1", page="1", pageScale="1", pageWidth="1400", pageHeight="1400", math="0", shadow="0")
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
    'relationship': "rhombus;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;",
    'attribute': "ellipse;whiteSpace=wrap;html=1;fillColor=#f5f5f5;fontColor=#333333;strokeColor=#666666;",
    'edge': "endArrow=none;html=1;rounded=0;",
    'edge_cardinality': "endArrow=none;html=1;rounded=0;labelBackgroundColor=none;"
}

nodes = {}

def add_node(value, type_, x, y, w, h):
    node_id = get_id()
    cell = ET.SubElement(root, 'mxCell', id=node_id, value=value, style=styles[type_], vertex="1", parent="1")
    ET.SubElement(cell, 'mxGeometry', x=str(int(x)), y=str(int(y)), width=str(w), height=str(h), **{'as': 'geometry'})
    nodes[value] = node_id
    return node_id

def add_edge(source_val, target_val, label=""):
    edge_id = get_id()
    if label:
        cell = ET.SubElement(root, 'mxCell', id=edge_id, value=label, style=styles['edge_cardinality'], edge="1", parent="1", source=nodes[source_val], target=nodes[target_val])
    else:
        cell = ET.SubElement(root, 'mxCell', id=edge_id, value="", style=styles['edge'], edge="1", parent="1", source=nodes[source_val], target=nodes[target_val])
    ET.SubElement(cell, 'mxGeometry', relative="1", **{'as': 'geometry'})
    return edge_id

# Entities
add_node("User", "entity", 300, 300, 100, 40)
add_node("Order", "entity", 700, 300, 100, 40)
add_node("Payment", "entity", 1100, 300, 100, 40)
add_node("Vendor", "entity", 300, 700, 100, 40)
add_node("Product", "entity", 700, 700, 100, 40)
add_node("Inventory", "entity", 1100, 700, 100, 40)
add_node("Category", "entity", 700, 1100, 100, 40)

# Relationships
add_node("places", "relationship", 500, 300, 100, 40)
add_node("has_payment", "relationship", 900, 300, 100, 40)
add_node("manages", "relationship", 500, 700, 100, 40)
add_node("has_inventory", "relationship", 900, 700, 100, 40)
add_node("contains", "relationship", 700, 900, 100, 40)

# Connect relationships
add_edge("User", "places", "1")
add_edge("places", "Order", "N")
add_edge("Order", "has_payment", "1")
add_edge("has_payment", "Payment", "1")

add_edge("Vendor", "manages", "1")
add_edge("manages", "Product", "N")
add_edge("Product", "has_inventory", "1")
add_edge("has_inventory", "Inventory", "1")

add_edge("Category", "contains", "1")
add_edge("contains", "Product", "N")

def attach_attributes_radial(entity, attrs, entity_x, entity_y, radius=120, start_angle=0, end_angle=360):
    center_x = entity_x + 50
    center_y = entity_y + 20
    n = len(attrs)
    if n == 0: return
    angle_step = (end_angle - start_angle) / (n - 1) if n > 1 else 0
    for i, attr in enumerate(attrs):
        angle = math.radians(start_angle + i * angle_step)
        attr_center_x = center_x + radius * math.cos(angle)
        attr_center_y = center_y + radius * math.sin(angle)
        # width varies slightly based on text len for aesthetics
        width = 120
        add_node(attr, "attribute", attr_center_x - (width/2), attr_center_y - 20, width, 40)
        add_edge(entity, attr)

# 0 is right, 90 is down, 180 is left, 270 is up
attach_attributes_radial("User", ["<u>user_id (PK)</u>", "name", "email", "password", "role"], 300, 300, radius=160, start_angle=90, end_angle=270)
attach_attributes_radial("Vendor", ["<u>vendor_id (PK)</u>", "name", "email", "password"], 300, 700, radius=160, start_angle=90, end_angle=270)
attach_attributes_radial("Order", ["<u>order_id (PK)</u>", "user_id (FK)", "date", "total_amount"], 700, 300, radius=160, start_angle=200, end_angle=340)
attach_attributes_radial("Payment", ["<u>payment_id (PK)</u>", "order_id (FK)", "amount", "method (eSewa)", "status"], 1100, 300, radius=170, start_angle=-90, end_angle=90)
attach_attributes_radial("Product", ["<u>product_id (PK)</u>", "name", "price", "metal", "gender", "description", "category_id (FK)", "vendor_id (FK)"], 700, 700, radius=260, start_angle=190, end_angle=350)
attach_attributes_radial("Inventory", ["<u>inventory_id (PK)</u>", "product_id (FK)", "stock"], 1100, 700, radius=160, start_angle=-90, end_angle=90)
attach_attributes_radial("Category", ["<u>category_id (PK)</u>", "category_name"], 700, 1100, radius=170, start_angle=0, end_angle=180)

# Optional indent for pretty XML styling if supported by the Python version
try:
    if hasattr(ET, 'indent'):
        ET.indent(root, space="\t", level=0)
except Exception:
    pass

tree = ET.ElementTree(mxfile)
tree.write('jewelry_ER_diagram.drawio', encoding='utf-8', xml_declaration=True)
print("ER Diagram generated at jewelry_ER_diagram.drawio")
