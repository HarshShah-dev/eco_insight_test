# server_api/utils.py

def parse_minew_data(raw_hex):
    """
    Parses the raw hex string from the sensor according to the Minew Connect V3 protocol.
    
    Assumptions based on the manuals:
    - The packet begins with the constant header "0201061bff3906".
    - The next byte is "ca" (protocol indicator), then one byte frame version.
    
    If frame_version is "00": device information frame.
      • Next 6 bytes (12 hex digits) represent the MAC address.
      • Then 1 byte battery (percentage),
      • Then 2 bytes firmware version,
      • Then 8 bytes peripheral support,
      • Then 1 byte (TBD, skipped),
      • Then 2 bytes salt,
      • Then 2 bytes digital signature.
      
    If frame_version is "18": monitoring (human flow) data frame.
      • Next 1 byte usage (should be "00" for human flow data),
      • Then 1 byte serial number,
      • Then 2 bytes for number of entries (little-endian),
      • Then 2 bytes for number of exits (little-endian),
      • Then 12 bytes of undefined data (skipped),
      • Then 2 bytes random number,
      • Then 2 bytes digital signature.
    
    Returns a dict of parsed fields.
    """
    raw_hex = raw_hex.lower()
    header = "0201061bff3906"
    if not raw_hex.startswith(header):
        return {"error": "Invalid header"}
    remainder = raw_hex[len(header):]
    
    # Expect the next byte to be "ca" (protocol)
    if not remainder.startswith("ca"):
        return {"error": "Missing protocol indicator"}
    remainder = remainder[2:]
    
    if len(remainder) < 2:
        return {"error": "Incomplete packet"}
    frame_version = remainder[:2]
    remainder = remainder[2:]
    parsed = {"frame_version": frame_version}
    
    if frame_version == "00":
        # Device information frame
        if len(remainder) < 12:
            return {"error": "Incomplete device info frame"}
        mac_hex = remainder[:12]
        mac = ":".join(mac_hex[i:i+2] for i in range(0, 12, 2))
        parsed["mac"] = mac
        remainder = remainder[12:]
        
        if len(remainder) < 2:
            return parsed
        parsed["battery"] = int(remainder[:2], 16)
        remainder = remainder[2:]
        
        if len(remainder) < 4:
            return parsed
        fw_int = int(remainder[:4], 16)
        parsed["firmware_version"] = str(fw_int)
        remainder = remainder[4:]
        
        if len(remainder) < 16:
            return parsed
        parsed["peripheral_support"] = remainder[:16]
        remainder = remainder[16:]
        
        if len(remainder) < 2:
            return parsed
        remainder = remainder[2:]  # Skip TBD byte
        
        if len(remainder) < 4:
            return parsed
        parsed["salt"] = remainder[:4]
        remainder = remainder[4:]
        
        if len(remainder) < 4:
            return parsed
        parsed["digital_signature"] = remainder[:4]
        
    elif frame_version == "18":
        # Monitoring (human flow) data frame
        if len(remainder) < 2:
            return {"error": "Incomplete monitoring frame"}
        parsed["usage"] = remainder[:2]
        remainder = remainder[2:]
        
        if len(remainder) < 2:
            return parsed
        parsed["serial_number"] = int(remainder[:2], 16)
        remainder = remainder[2:]
        
        if len(remainder) < 4:
            return parsed
        entries_hex = remainder[:4]
        entries_swapped = entries_hex[2:] + entries_hex[:2]
        parsed["entries"] = int(entries_swapped, 16)
        remainder = remainder[4:]
        
        if len(remainder) < 4:
            return parsed
        exits_hex = remainder[:4]
        exits_swapped = exits_hex[2:] + exits_hex[:2]
        parsed["exits"] = int(exits_swapped, 16)
        remainder = remainder[4:]
        
        if len(remainder) < 24:
            return parsed
        remainder = remainder[24:]  # Skip 12 bytes undefined
        
        if len(remainder) < 4:
            return parsed
        parsed["random_number"] = remainder[:4]
        remainder = remainder[4:]
        
        if len(remainder) < 4:
            return parsed
        parsed["digital_signature"] = remainder[:4]
    else:
        parsed["error"] = "Unknown frame version"
    return parsed