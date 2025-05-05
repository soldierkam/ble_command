## Description

Home Assistant custom integration for writing data to Bluetooth Low Energy (BLE) characteristics.
Send raw byte data to BLE devices using their MAC address and characteristic UUID via the ble_write service.

## Example

```yaml
action: ble_command.write
data:
  address: A4:C1:38:AA:BB:CC
  characteristic_uuid: 00001f1f-0000-1000-8000-00805f9b34fb
  data:
    - 69
    - 0
```