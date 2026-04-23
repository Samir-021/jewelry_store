import xml.etree.ElementTree as ET
import html

mxfile = ET.Element('mxfile', host="app.diagrams.net")
diagram = ET.SubElement(mxfile, 'diagram', id="erd", name="ERD")
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
    'table': "rounded=1;whiteSpace=wrap;html=1;align=left;verticalAlign=top;fillColor=#f8cecc;strokeColor=#b85450;fontFamily=Helvetica;fontSize=12;spacingLeft=10;spacingRight=10;spacingTop=10;",
    'edge_1n': "startArrow=ERmandOne;endArrow=ERmany;html=1;rounded=0;edgeStyle=orthogonalEdgeStyle;strokeColor=#666666;strokeWidth=2;",
    'edge_11': "startArrow=ERmandOne;endArrow=ERmandOne;html=1;rounded=0;edgeStyle=orthogonalEdgeStyle;strokeColor=#666666;strokeWidth=2;"
}

nodes = {}

def add_table(name, attributes, cx, cy, w, h):
    node_id = get_id()
    
    # Simple HTML table-like layout inside the node using hr
    table_html = f"<div style='text-align:center;'><b>{name}</b></div><hr>" + "<br>".join(attributes)
    
    # Safe HTML escape handling while preserving layout tags
    val = html.escape(table_html)
    val = val.replace("&lt;b&gt;", "<b>").replace("&lt;/b&gt;", "</b>")
    val = val.replace("&lt;div style=&#x27;text-align:center;&#x27;&gt;", "<div style='text-align:center;'>").replace("&lt;/div&gt;", "</div>")
    val = val.replace("&lt;hr&gt;", "<hr>").replace("&lt;br&gt;", "<br>")
    val = val.replace("&lt;u&gt;", "<u>").replace("&lt;/u&gt;", "</u>")

    x = cx - (w / 2)
    y = cy - (h / 2)
    cell = ET.SubElement(root, 'mxCell', id=node_id, value=val, style=styles['table'], vertex="1", parent="1")
    ET.SubElement(cell, 'mxGeometry', x=str(int(x)), y=str(int(y)), width=str(w), height=str(h), **{'as': 'geometry'})
    nodes[name] = node_id
    return node_id

def add_edge(source_val, target_val, edge_type="1n"):
    edge_id = get_id()
    style = styles['edge_11'] if edge_type == '11' else styles['edge_1n']
    cell = ET.SubElement(root, 'mxCell', id=edge_id, value="", style=style, edge="1", parent="1", source=nodes[source_val], target=nodes[target_val])
    ET.SubElement(cell, 'mxGeometry', relative="1", **{'as': 'geometry'})
    return edge_id

w = 180
h = 170
h_prod = 220
h_short = 140

add_table("Users", ["<u>user_id (PK)</u>", "name", "email", "password", "role"], cx=250, cy=300, w=w, h=h)
add_table("Categories", ["<u>category_id (PK)</u>", "category_name"], cx=250, cy=550, w=w, h=h_short)
add_table("Vendors", ["<u>vendor_id (PK)</u>", "name", "email", "password"], cx=250, cy=800, w=w, h=h)

add_table("Orders", ["<u>order_id (PK)</u>", "user_id (FK)", "order_date", "total_amount"], cx=700, cy=300, w=w, h=h)
add_table("Products", ["<u>product_id (PK)</u>", "name", "price", "metal", "gender", "description", "category_id (FK)", "vendor_id (FK)"], cx=700, cy=675, w=w, h=h_prod)

add_table("Payments", ["<u>payment_id (PK)</u>", "order_id (FK)", "amount", "method", "status"], cx=1150, cy=300, w=w, h=h)
add_table("Order_Items", ["<u>order_item_id (PK)</u>", "order_id (FK)", "product_id (FK)", "quantity"], cx=700, cy=500, w=w, h=h_short)
add_table("Inventory", ["<u>inventory_id (PK)</u>", "product_id (FK)", "stock"], cx=1150, cy=675, w=w, h=h_short)

# Relationships
# Users -> Orders
add_edge("Users", "Orders", "1n")
# Orders -> Payments (1:1)
add_edge("Orders", "Payments", "11")
# Orders -> Order_Items
add_edge("Orders", "Order_Items", "1n")
# Products -> Order_Items
add_edge("Products", "Order_Items", "1n")
# Categories -> Products
add_edge("Categories", "Products", "1n")
# Vendors -> Products
add_edge("Vendors", "Products", "1n")
# Products -> Inventory (1:1)
add_edge("Products", "Inventory", "11")

try:
    if hasattr(ET, 'indent'):
        ET.indent(root, space="\t", level=0)
except Exception:
    pass

tree = ET.ElementTree(mxfile)
tree.write('database_schema_ERD.drawio', encoding='utf-8', xml_declaration=True)
print("DrawIO ERD Generated!")
