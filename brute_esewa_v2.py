import hmac
import hashlib
import base64
import json

user_data = '{"transaction_code":"000EAIN","status":"COMPLETE","total_amount":"10000.0","transaction_uuid":"587bb587-2c9d-4d20-81f3-08ae6540172","product_code":"EPAYTEST","signed_field_names":"transaction_code,status,total_amount,transaction_uuid,product_code,signed_field_names","signature":"D9gQe9y4VIW+CIwxRH1qTiXFH6rlcpLx0nvzEQZ6gww="}'
data = json.loads(user_data)
received_sig = data.get('signature')

all_fields = data['signed_field_names'].split(',')
request_fields = ["total_amount", "transaction_uuid", "product_code"]

keys = ["8gBm/:&EnhH.1/q", "8gBm/:&EnhH.1/q("]

def test_formats(fields_to_use, key_val):
    delimiters = [",", "&", ""]
    for sep in delimiters:
        # Format: key=value
        msg = sep.join([f"{f}={data[f]}" for f in fields_to_use])
        sig = base64.b64encode(hmac.new(key_val.encode(), msg.encode(), hashlib.sha256).digest()).decode()
        if sig == received_sig:
            return f"MATCH! fields={fields_to_use}, msg={msg}"
        
        # Format: value (no keys)
        msg_val = sep.join([str(data[f]) for f in fields_to_use])
        sig_val = base64.b64encode(hmac.new(key_val.encode(), msg_val.encode(), hashlib.sha256).digest()).decode()
        if sig_val == received_sig:
            return f"MATCH! fields={fields_to_use}, msg={msg_val}"
    return None

for key in keys:
    # Try all signed fields
    res = test_formats(all_fields, key)
    if res: print(f"Key: {key} -> {res}"); exit()
    
    # Try just request fields
    res = test_formats(request_fields, key)
    if res: print(f"Key: {key} -> {res}"); exit()

print("Still no match.")
