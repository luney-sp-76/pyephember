# InfluxDB Setup Guide for Heating Analytics

## 📊 **InfluxDB Installation & Configuration**

### **Step 1: Install InfluxDB on Home Assistant**

#### **Option A: InfluxDB Add-on (Recommended for Home Assistant OS)**
1. **Go to Settings > Add-ons > Add-on Store**
2. **Search for "InfluxDB"**  
3. **Install the official InfluxDB add-on**
4. **Configure the add-on:**
   ```yaml
   # InfluxDB Add-on Configuration
   auth: true
   reporting: false
   ssl: false
   certfile: fullchain.pem
   keyfile: privkey.pem
   envvars: []
   ```
5. **Start the add-on**

#### **Option B: Docker Installation (for other systems)**
```bash
# Create InfluxDB container
docker run -d \
  --name influxdb \
  -p 8086:8086 \
  -v influxdb-storage:/var/lib/influxdb \
  -e INFLUXDB_DB=home_assistant_heating \
  -e INFLUXDB_ADMIN_USER=admin \
  -e INFLUXDB_ADMIN_PASSWORD=your_password_here \
  influxdb:1.8
```

### **Step 2: Create Database and User**

1. **Access InfluxDB CLI:**
   ```bash
   # If using add-on
   docker exec -it addon_a0d7b954_influxdb influx
   
   # If using standalone Docker
   docker exec -it influxdb influx
   ```

2. **Create database and user:**
   ```sql
   -- Create database
   CREATE DATABASE home_assistant_heating
   
   -- Create user
   CREATE USER "ha_heating" WITH PASSWORD "secure_password_here"
   
   -- Grant permissions
   GRANT ALL ON home_assistant_heating TO ha_heating
   
   -- Show databases to verify
   SHOW DATABASES
   ```

### **Step 3: Configure Home Assistant**

1. **Add to your `secrets.yaml`:**
   ```yaml
   # InfluxDB credentials
   influxdb_username: ha_heating
   influxdb_password: secure_password_here
   ```

2. **Add InfluxDB config to `configuration.yaml`:**
   ```yaml
   # Include InfluxDB configuration
   influxdb: !include influxdb_heating_config.yaml
   ```

3. **Or add directly to configuration.yaml:**
   ```yaml
   influxdb:
     host: localhost
     port: 8086
     database: home_assistant_heating
     username: !secret influxdb_username
     password: !secret influxdb_password
     include:
       entities:
         - binary_sensor.zone_one_heating_active
         - counter.zone_one_heating_cycles_today
         - sensor.zone_one_average_heating_duration
         - input_number.zone_one_total_heating_time_today
         - climate.one
   ```

### **Step 4: Install the Mobile Dashboard**

1. **Create new dashboard in Home Assistant:**
   - Go to **Settings > Dashboards**
   - Click **"+ Add Dashboard"**
   - Name: **"Heating Analytics"**
   - Icon: **mdi:fire**
   - **Enable "Show in sidebar"**

2. **Add the dashboard content:**
   - Click **"Edit Dashboard"**
   - Click **"Raw configuration editor"** 
   - **Copy and paste** the content from `heating_mobile_dashboard.yaml`
   - **Save**

### **Step 5: Verify Everything Works**

1. **Check InfluxDB data:**
   ```sql
   -- Connect to InfluxDB
   influx -database home_assistant_heating
   
   -- Show measurements
   SHOW MEASUREMENTS
   
   -- Check recent heating data
   SELECT * FROM heating_status WHERE time > now() - 1h
   SELECT * FROM heating_counters WHERE time > now() - 24h
   ```

2. **Test dashboard on mobile:**
   - **Open Home Assistant on iPhone**
   - **Navigate to "Heating Analytics" dashboard**
   - **Check all cards display correctly**
   - **Verify touch interactions work**

### **Step 6: Optional Enhancements**

#### **Grafana Integration (Advanced)**
```bash
# Install Grafana for advanced visualization
docker run -d \
  --name grafana \
  -p 3000:3000 \
  -e GF_SECURITY_ADMIN_PASSWORD=admin \
  grafana/grafana

# Add InfluxDB as data source in Grafana
# URL: http://localhost:8086
# Database: home_assistant_heating
```

#### **Custom Retention Policies**
```sql
-- Create retention policy for different data periods
CREATE RETENTION POLICY "one_year" ON "home_assistant_heating" DURATION 365d REPLICATION 1 DEFAULT
CREATE RETENTION POLICY "one_month" ON "home_assistant_heating" DURATION 30d REPLICATION 1
```

## 📱 **iPhone Dashboard Features**

### **Optimized for Mobile:**
- ✅ **Single-column layout** - Perfect for iPhone screens
- ✅ **Large touch targets** - Easy to tap buttons and cards  
- ✅ **Readable fonts** - Optimized text sizes for mobile
- ✅ **Three-tab layout** - Overview, Analytics, Controls
- ✅ **Swipe-friendly** - Smooth navigation between sections
- ✅ **Dark/Light mode** - Follows system theme
- ✅ **Real-time updates** - Live data refresh

### **Dashboard Tabs:**
1. **Overview** - Current status, today's stats, quick insights
2. **Analytics** - Historical charts, efficiency metrics, cost analysis  
3. **Controls** - Thermostat control, reset buttons, system info

### **Key Mobile Features:**
- **Live heating status** with prominent visual indicators
- **Touch-friendly charts** for viewing 24-hour and weekly data
- **Quick actions** accessible with large buttons
- **Smart insights** with efficiency tips and recommendations
- **Cost tracking** with daily and monthly projections

## 🔍 **Data Storage Benefits**

### **With InfluxDB you get:**
- 📊 **Long-term trending** - Years of heating data
- 🚀 **High performance** - Optimized for time-series data
- 📈 **Advanced analytics** - Complex queries and aggregations
- 🔗 **Grafana integration** - Professional dashboards
- 💾 **Efficient storage** - Compressed time-series format
- ⚡ **Real-time queries** - Fast data retrieval

### **Heating Metrics Stored:**
- Heating on/off events with timestamps
- Daily cycle counts and durations
- Temperature readings and setpoints
- Efficiency calculations over time
- Cost data and trends
- System performance metrics

The combination gives you a professional heating monitoring system with mobile-optimized interface and robust historical data storage! 🔥📱