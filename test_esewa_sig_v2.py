import hmac
import hashlib
import base64
import json

def test_sig(data_json, secret_key):
    data = json.loads(data_json)
    signed_field_names = data.get('signed_field_names', '')
    fields = signed_field_names.split(',')
    
    received_sig = data.get('signature')
    
    # Format 1: total_amount=100.00,transaction_uuid=11-aa,product_code=EPAYTEST
    msg1 = ",".join([f"{field}={data[field]}" for field in fields])
    
    # Format 2: total_amount=100.00&transaction_uuid=11-aa&product_code=EPAYTEST
    msg2 = "&".join([f"{field}={data[field]}" for field in fields])
    
    # Format 3: Name1=Value1, Name2=Value2 (with spaces)
    msg3 = ", ".join([f"{field}={data[field]}" for field in fields])
    
    msgs = [msg1, msg2, msg3]
    
    for i, msg in enumerate(msgs):
        sig = base64.b64encode(hmac.new(secret_key.encode(), msg.encode(), hashlib.sha256).digest()).decode()
        if sig == received_sig:
            return f"MATCH! Format {i+1}, Message: {msg}"
    return None

user_data = '{"transaction_code":"000EAIN","status":"COMPLETE","total_amount":"10000.0","transaction_uuid":"587bb587-2c9d-4d20-81f3-08ae6540172","product_code":"EPAYTEST","signed_field_names":"transaction_code,status,total_amount,transaction_uuid,product_code,signed_field_names","signature":"D9gQe9y4VIW+CIwxRH1qTiXFH6rlcpLx0nvzEQZ6gww="}'

keys = ["8gBm/:&EnhH.1/q", "8gBm/:&EnhH.1/q("]

for key in keys:
    res = test_sig(user_data, key)
    if res:
        print(f"Key: {key} -> {res}")
    else:
        print(f"Key: {key} -> No match")
