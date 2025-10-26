# 🌐 Network Setup Guide for Cross-Subnet Access

## Current Situation
- **Your IP**: `10.229.64.145` (subnet: 10.229.64.x)
- **Roommate's Network**: `192.168.1.x` (main router)
- **Your Router**: Acts as a gateway between subnets

## 🔧 Solution Options

### **Option 1: Router Port Forwarding (Easiest)**

1. **Access your router's admin panel**:
   - Usually: `http://10.229.64.1` or `http://192.168.1.1`
   - Check your router's manual for the correct IP

2. **Set up port forwarding**:
   ```
   External Port 3000 → Internal IP 10.229.64.145:3000
   External Port 8000 → Internal IP 10.229.64.145:8000
   ```

3. **Your roommate accesses**:
   - `http://[YOUR_ROUTER_EXTERNAL_IP]:3000`
   - `http://[YOUR_ROUTER_EXTERNAL_IP]:8000`

### **Option 2: Router Bridge Mode**

Configure your router to bridge the networks:
1. Access router admin panel
2. Look for "Bridge Mode" or "AP Mode"
3. This allows direct communication between subnets

### **Option 3: Static Route Configuration**

Add a static route on the main router (192.168.1.1):
```
Destination: 10.229.64.0/24
Gateway: [YOUR_ROUTER_IP_ON_192.168.1.x]
```

### **Option 4: Use ngrok (Temporary Solution)**

For quick testing, use ngrok to create a public tunnel:

```bash
# Install ngrok
brew install ngrok  # macOS
# or download from https://ngrok.com/

# Create tunnels
ngrok http 3000  # For frontend
ngrok http 8000  # For backend (in separate terminal)
```

Your roommate can then use the ngrok URLs.

## 🚀 Quick Setup Script

I've created a script that will help you set up network access:

```bash
./start-network.sh
```

This script:
- Detects your current IP
- Starts both servers on all interfaces
- Provides the correct URLs for sharing

## 🔍 Troubleshooting

### Check Router IP
```bash
# Find your router's IP
route -n get default | grep gateway
# or
netstat -rn | grep default
```

### Test Connectivity
```bash
# From your roommate's machine, test:
ping 10.229.64.145
telnet 10.229.64.145 3000
telnet 10.229.64.145 8000
```

### Firewall Check
Make sure your firewall allows the ports:
```bash
# macOS
sudo pfctl -sr | grep 3000
sudo pfctl -sr | grep 8000
```

## 📋 Recommended Steps

1. **Try the network startup script first**:
   ```bash
   ./start-network.sh
   ```

2. **Share these URLs with your roommate**:
   - `http://10.229.64.145:3000` (main app)
   - `http://10.229.64.145:8000/docs` (API docs)

3. **If that doesn't work**, configure port forwarding on your router

4. **For permanent access**, set up proper routing between subnets

## 🆘 Need Help?

If you're still having issues:
1. Check your router's manual for port forwarding instructions
2. Contact your network administrator
3. Consider using ngrok for temporary access
