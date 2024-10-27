import 'package:flutter/material.dart';
import 'package:flutter_blue_plus/flutter_blue_plus.dart';

class setting_Page extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Setting'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: <Widget>[
            BluetoothSetting(),
            SizedBox(height: 20),
            Center(
              child: Text('A lot of settings here!'),
            ),
          ],
        ),
      ),
    );
  }
}

class BluetoothSetting extends StatefulWidget {
  @override
  _BluetoothSettingState createState() => _BluetoothSettingState();
}

class _BluetoothSettingState extends State<BluetoothSetting> {
  bool _isBluetoothEnabled = false;
  List<BluetoothDevice> _devicesList = [];

  @override
  void initState() {
    super.initState();
    FlutterBluePlus.adapterState.listen((state) {
      setState(() {
        _isBluetoothEnabled = state == BluetoothAdapterState.on;
      });
    });
  }

  void _scanForDevices() {
    FlutterBluePlus.startScan(timeout: Duration(seconds: 4));

    FlutterBluePlus.scanResults.listen((results) {
      setState(() {
        _devicesList = results.map((result) => result.device).toList();
      });
    });
  }

  void _connectToDevice(BluetoothDevice device) async {
    await device.connect();
    // 可以在這裡添加更多的連接後的處理邏輯
  }

  void _showDevicesDialog() {
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: Text('Select Bluetooth Device'),
          content: Container(
            width: double.minPositive,
            height: 200,
            child: ListView.builder(
              itemCount: _devicesList.length,
              itemBuilder: (context, index) {
                return ListTile(
                  title: Text(_devicesList[index].name),
                  onTap: () {
                    _connectToDevice(_devicesList[index]);
                    Navigator.of(context).pop();
                  },
                );
              },
            ),
          ),
          actions: [
            TextButton(
              child: Text('Scan'),
              onPressed: () {
                _scanForDevices();
              },
            ),
            TextButton(
              child: Text('Close'),
              onPressed: () {
                Navigator.of(context).pop();
              },
            ),
          ],
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: <Widget>[
        Text(
          'Bluetooth',
          style: TextStyle(fontSize: 18),
        ),
        Switch(
          value: _isBluetoothEnabled,
          onChanged: (value) {
            setState(() {
              _isBluetoothEnabled = value;
              if (value) {
                _scanForDevices();
                _showDevicesDialog();
              } else {
                // 使用平台特定的API來打開或關閉藍牙
              }
            });
          },
        ),
      ],
    );
  }
}

void main() => runApp(MaterialApp(
      home: setting_Page(),
    ));
