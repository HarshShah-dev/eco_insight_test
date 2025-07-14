# server_api/utils.py
import base64
import struct

def parse_minew_data(raw_hex):
    """
    Parses the raw hex string from the sensor according to the Minew Connect V3 protocol.
    
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

# utils.py



def parse_mst01_ht_payload(b64_payload):
    try:
        decoded = base64.b64decode(b64_payload)
        if len(decoded) < 30:
            return {"error": "Frame too short"}

        if decoded[7] != 0xCA or decoded[8] != 0x05:
            return {"error": "Not an HT frame"}

        temp_raw = int.from_bytes(decoded[12:14], byteorder="big")
        hum_raw = int.from_bytes(decoded[14:16], byteorder="big")

        temperature = round(temp_raw / 256.0, 1)
        humidity = round(hum_raw / 256.0, 1)

        return {
            "temperature": temperature,
            "humidity": humidity,
        }
    except Exception as e:
        return {"error": str(e)}

# utils.py

# def parse_mst01_ht_payload(b64_payload):
#     try:
#         decoded = base64.b64decode(b64_payload)
#         hex_str = decoded.hex()
#         print("[DEBUG] Raw decoded bytes:", hex_str)

#         # Try multiple offset positions where temp/hum might be
#         candidates = []

#         for offset in range(len(decoded) - 2):
#             temp_raw = int.from_bytes(decoded[offset:offset+2], byteorder="big")
#             temp = round(temp_raw / 256.0, 1)
#             if 0 <= temp <= 50:  # valid temperature range
#                 hum_raw = int.from_bytes(decoded[offset+2:offset+4], byteorder="big")
#                 hum = round(hum_raw / 256.0, 1)
#                 if 0 <= hum <= 100:  # valid humidity range
#                     candidates.append((offset, temp, hum))

#         if not candidates:
#             return {"error": "No valid temperature/humidity pair found"}

#         # Return the first valid one found
#         offset, temperature, humidity = candidates[0]
#         print(f"[DEBUG] Selected offset: {offset}")
#         return {
#             "temperature": temperature,
#             "humidity": humidity
#         }

#     except Exception as e:
#         return {"error": str(e)}

import base64
import struct
import logging

logger = logging.getLogger(__name__)

def parse_lsg01_payload(frm_payload_b64):
    try:
        payload_bytes = base64.b64decode(frm_payload_b64)
        logger.debug(f"[LSG01] Raw bytes: {payload_bytes.hex()}")

        i = 0
        results = {}

        while i < len(payload_bytes):
            type_byte = payload_bytes[i]
            i += 1

            if type_byte == 0x01:  # Product ID
                model_id = payload_bytes[i]
                results["model_id"] = model_id
                i += 1

            elif type_byte == 0x52:  # PM2.5
                pm25 = int.from_bytes(payload_bytes[i:i+2], byteorder="big")
                results["pm25"] = pm25
                i += 2

            elif type_byte == 0x9F:  # HCHO
                hcho = int.from_bytes(payload_bytes[i:i+2], byteorder="big")
                results["hcho"] = hcho
                i += 2

            elif type_byte == 0x49:  # CO2
                co2 = int.from_bytes(payload_bytes[i:i+2], byteorder="big")
                results["co2"] = co2
                i += 2

            elif type_byte == 0xA0:  # TVOC
                tvoc = int.from_bytes(payload_bytes[i:i+2], byteorder="big")
                results["tvoc"] = tvoc
                i += 2

            elif type_byte == 0x10:  # Temperature
                temp_raw = int.from_bytes(payload_bytes[i:i+2], byteorder="big", signed=True)
                results["temperature"] = round(temp_raw / 100.0, 2)
                i += 2

            elif type_byte == 0x12:  # Humidity
                humidity_raw = int.from_bytes(payload_bytes[i:i+2], byteorder="big")
                results["humidity"] = round(humidity_raw / 10.0, 2)
                i += 2

            else:
                logger.warning(f"Unknown type byte: {hex(type_byte)} at index {i-1}")
                break

        return results

    except Exception as e:
        logger.exception("Failed to decode LSG01 payload")
        return {"error": str(e)}
