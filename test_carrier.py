#!/usr/bin/env python3
"""
Quick test for SMS carrier configuration
"""

def test_carrier_lookup():
    # Email-to-SMS gateways for major carriers
    carrier_gateways = {
        'verizon': 'vtext.com',
        'att': 'txt.att.net',
        'at&t': 'txt.att.net',
        'tmobile': 'tmomail.net',
        't-mobile': 'tmomail.net',
        'sprint': 'messaging.sprintpcs.com',
        'boost': 'myboostmobile.com',
        'boost mobile': 'myboostmobile.com',
        'cricket': 'sms.cricketwireless.net',
        'cricket wireless': 'sms.cricketwireless.net',
        'uscellular': 'email.uscc.net',
        'us cellular': 'email.uscc.net',
        'metro': 'mymetropcs.com',
        'metropcs': 'mymetropcs.com',
        'metro pcs': 'mymetropcs.com',
        'mint': 'tmomail.net',  # Mint uses T-Mobile network
        'mint mobile': 'tmomail.net'
    }
    
    test_carrier = 't-mobile'
    carrier_normalized = test_carrier.lower().strip()
    gateway = carrier_gateways.get(carrier_normalized)
    
    print(f"Testing carrier: '{test_carrier}'")
    print(f"Normalized: '{carrier_normalized}'")
    print(f"Gateway found: {gateway}")
    
    if gateway:
        print("✅ Carrier lookup successful!")
        phone = "3475572898"
        sms_address = f"{phone}@{gateway}"
        print(f"SMS address would be: {sms_address}")
    else:
        print("❌ Carrier not found")
        print(f"Available carriers: {list(carrier_gateways.keys())}")

if __name__ == "__main__":
    test_carrier_lookup()
