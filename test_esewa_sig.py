import hmac
import hashlib
import base64
import json

def verify_signature(data_json, secret_key):
    data = json.loads(data_json)
    signed_field_names = data.get('signed_field_names', '')
    fields = signed_field_names.split(',')
    
    # Try different message formats
    formats = [
        # Format 1: key=value,key=value
        lambda d, f: ",".join([f"{field}={d[field]}" for field in f]),
        # Format 2: valuevaluevalue
        lambda d, f: "".join([str(d[field]) for field in f]),
        # Format 3: key=value&key=value (unlikely for eSewa v2 success)
        lambda d, f: "&".join([f"{field}={d[field]}" for field in f]),
    ]
    
    received_sig = data.get('signature')
    print(f"Received Signature: {received_sig}")
    print(f"Secret Key used: {secret_key}")
    
    for i, fmt in enumerate(formats):
        message = fmt(data, fields)
        print(f"Format {i+1} message: {message}")
        
        generated_sig = base64.b64encode(
            hmac.new(
                secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
        ).decode()
        
        print(f"Format {i+1} generated signature: {generated_sig}")
        if generated_sig == received_sig:
            print(f"MATCH FOUND in Format {i+1}!")
            return True
            
    return False

# Data from user
user_data = '{"transaction_code":"000EAIN","status":"COMPLETE","total_amount":"10000.0","transaction_uuid":"587bb587-2c9d-4d20-81f3-08ae6540172","product_code":"EPAYTEST","signed_field_names":"transaction_code,status,total_amount,transaction_uuid,product_code,signed_field_names","signature":"D9gQe9y4VIW+CIwxRH1qTiXFH6rlcpLx0nvzEQZ6gww="}'

print("Testing with key from views/utils: 8gBm/:&EnhH.1/q")
verify_signature(user_data, "8gBm/:&EnhH.1/q")

print("\nTesting with key from settings: 8gBm/:&EnhH.1/q(")
verify_signature(user_data, "8gBm/:&EnhH.1/q(")
