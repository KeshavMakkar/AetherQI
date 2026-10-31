"""
AetherQI Central Cities Configuration.
Scalable single-source-of-truth registry for all 20 major Indian metropolitan cities.

Primary Cities (8): Delhi, Mumbai, Bengaluru, Hyderabad, Kolkata, Chennai, Pune, Ahmedabad
Additional Cities (12): Jaipur, Lucknow, Ludhiana, Chandigarh, Bhopal, Indore, Surat, Nagpur, Patna, Kanpur, Kochi, Bhubaneswar

Each city contains:
- City ID, Name, State
- Geographic coordinates (lat, lng, default zoom)
- Official CPCB CAAQMS Monitoring Station metadata
- Climate and seasonal atmospheric parameters for November Diwali period
- Verified local urban neighbourhoods with typology classifications and emission modifiers
"""

from typing import Dict, Any, List

CITIES_REGISTRY: Dict[str, Dict[str, Any]] = {
    "Delhi": {
        "id": "delhi",
        "city": "Delhi",
        "state": "Delhi (NCT)",
        "center": {"latitude": 28.6139, "longitude": 77.2090, "zoom": 12},
        "station_id": "CPCB_DL_001",
        "station_name": "Anand Vihar, Delhi - DPCC Live CAAQMS",
        "data_sources": ["CPCB CAAQMS Network", "data.gov.in Real-Time Feed", "IMD Safdarjung Observatory"],
        "climate_profile": {
            "base_temp": 22.0,
            "humidity": 68.0,
            "wind_speed": 2.2,
            "wind_direction": "NW",
            "base_adj": 35.0,
            "diwali_spike_adj": 45.0,
            "dispersion_rate": 11.5,
            "inversion_risk": "VERY_HIGH"
        },
        "neighbourhoods": [
            {
                "id": "delhi_anand_vihar",
                "name": "Anand Vihar",
                "city": "Delhi",
                "state": "Delhi (NCT)",
                "type": "Interstate Transit / Heavy Commercial",
                "modifier": 1.25,
                "latitude": 28.6476,
                "longitude": 77.3158,
                "description": "Interstate bus terminus, trans-Yamuna rail hub, and high vehicular density."
            },
            {
                "id": "delhi_connaught_place",
                "name": "Connaught Place",
                "city": "Delhi",
                "state": "Delhi (NCT)",
                "type": "Central Business District",
                "modifier": 1.10,
                "latitude": 28.6315,
                "longitude": 77.2167,
                "description": "Inner radial commercial plaza with regulated pedestrian and vehicle corridors."
            },
            {
                "id": "delhi_karol_bagh",
                "name": "Karol Bagh",
                "city": "Delhi",
                "state": "Delhi (NCT)",
                "type": "Dense Mixed Commercial & Retail",
                "modifier": 1.18,
                "latitude": 28.6514,
                "longitude": 77.1907,
                "description": "High shopping density, narrow street canyons, and elevated evening emissions."
            },
            {
                "id": "delhi_saket",
                "name": "Saket",
                "city": "Delhi",
                "state": "Delhi (NCT)",
                "type": "Planned Residential & Institutional",
                "modifier": 1.02,
                "latitude": 28.5244,
                "longitude": 77.2066,
                "description": "South Delhi residential blocks, district courts, and commercial mall complexes."
            },
            {
                "id": "delhi_rohini",
                "name": "Rohini",
                "city": "Delhi",
                "state": "Delhi (NCT)",
                "type": "Suburban Residential Sector",
                "modifier": 1.08,
                "latitude": 28.7180,
                "longitude": 77.1280,
                "description": "North-West Delhi planned residential sectors with wide arterial roads."
            }
        ]
    },
    "Mumbai": {
        "id": "mumbai",
        "city": "Mumbai",
        "state": "Maharashtra",
        "center": {"latitude": 19.0760, "longitude": 72.8777, "zoom": 12},
        "station_id": "CPCB_MH_001",
        "station_name": "Bandra Kurla Complex, Mumbai - MPCB Live CAAQMS",
        "data_sources": ["CPCB CAAQMS Network", "MPCB Air Portal", "IMD Santacruz Observatory"],
        "climate_profile": {
            "base_temp": 28.5,
            "humidity": 62.0,
            "wind_speed": 5.8,
            "wind_direction": "WNW",
            "base_adj": -20.0,
            "diwali_spike_adj": -15.0,
            "dispersion_rate": 18.0,
            "inversion_risk": "LOW_MODERATE"
        },
        "neighbourhoods": [
            {
                "id": "mumbai_bkc",
                "name": "Bandra Kurla Complex",
                "city": "Mumbai",
                "state": "Maharashtra",
                "type": "Financial & Commercial Hub",
                "modifier": 1.15,
                "latitude": 19.0657,
                "longitude": 72.8687,
                "description": "Major corporate district with high corporate vehicle flow and Mithi river basin."
            },
            {
                "id": "mumbai_colaba",
                "name": "Colaba",
                "city": "Mumbai",
                "state": "Maharashtra",
                "type": "Coastal / Heritage Corridor",
                "modifier": 0.88,
                "latitude": 18.9067,
                "longitude": 72.8147,
                "description": "Southern peninsula tip with strong maritime sea-breeze dispersion."
            },
            {
                "id": "mumbai_andheri_west",
                "name": "Andheri West",
                "city": "Mumbai",
                "state": "Maharashtra",
                "type": "Dense Mixed Urban / Commercial",
                "modifier": 1.12,
                "latitude": 19.1197,
                "longitude": 72.8468,
                "description": "Vibrant residential and media hub with continuous western railway corridor transit."
            },
            {
                "id": "mumbai_chembur",
                "name": "Chembur",
                "city": "Mumbai",
                "state": "Maharashtra",
                "type": "Industrial & Refinery Corridor",
                "modifier": 1.22,
                "latitude": 19.0522,
                "longitude": 72.8994,
                "description": "Proximity to eastern harbor industrial estates and petroleum refineries."
            },
            {
                "id": "mumbai_borivali",
                "name": "Borivali",
                "city": "Mumbai",
                "state": "Maharashtra",
                "type": "Suburban / Green Forest Buffer",
                "modifier": 0.94,
                "latitude": 19.2307,
                "longitude": 72.8567,
                "description": "Western suburb bordering Sanjay Gandhi National Park forest reserve."
            }
        ]
    },
    "Bengaluru": {
        "id": "bengaluru",
        "city": "Bengaluru",
        "state": "Karnataka",
        "center": {"latitude": 12.9716, "longitude": 77.5946, "zoom": 12},
        "station_id": "CPCB_KA_001",
        "station_name": "BTM Layout, Bengaluru - KSPCB Live CAAQMS",
        "data_sources": ["CPCB CAAQMS Network", "KSPCB Clean Air Feed", "IMD Bengaluru City Observatory"],
        "climate_profile": {
            "base_temp": 23.0,
            "humidity": 65.0,
            "wind_speed": 4.8,
            "wind_direction": "ENE",
            "base_adj": -35.0,
            "diwali_spike_adj": -30.0,
            "dispersion_rate": 16.5,
            "inversion_risk": "LOW"
        },
        "neighbourhoods": [
            {
                "id": "blr_btm",
                "name": "BTM Layout",
                "city": "Bengaluru",
                "state": "Karnataka",
                "type": "Residential & Transit Arterial",
                "modifier": 1.08,
                "latitude": 12.9166,
                "longitude": 77.6101,
                "description": "Key South Bengaluru connector with Silk Board junction vehicular proximity."
            },
            {
                "id": "blr_whitefield",
                "name": "Whitefield",
                "city": "Bengaluru",
                "state": "Karnataka",
                "type": "Tech Corridor & Suburb",
                "modifier": 1.14,
                "latitude": 12.9698,
                "longitude": 77.7500,
                "description": "IT export zones, major construction corridors, and high commuter vehicle density."
            },
            {
                "id": "blr_indiranagar",
                "name": "Indiranagar",
                "city": "Bengaluru",
                "state": "Karnataka",
                "type": "Commercial & Residential",
                "modifier": 1.04,
                "latitude": 12.9784,
                "longitude": 77.6408,
                "description": "Upscale dining, shopping streets, and mature tree-lined avenues."
            },
            {
                "id": "blr_jayanagar",
                "name": "Jayanagar",
                "city": "Bengaluru",
                "state": "Karnataka",
                "type": "Planned Garden Residential",
                "modifier": 0.92,
                "latitude": 12.9308,
                "longitude": 77.5838,
                "description": "Traditional planned residential layout with dense neighborhood green parks."
            },
            {
                "id": "blr_electronic_city",
                "name": "Electronic City",
                "city": "Bengaluru",
                "state": "Karnataka",
                "type": "Industrial Tech Campus",
                "modifier": 1.06,
                "latitude": 12.8399,
                "longitude": 77.6770,
                "description": "Expansive technology parks bordering Hosur highway industrial zones."
            }
        ]
    },
    "Hyderabad": {
        "id": "hyderabad",
        "city": "Hyderabad",
        "state": "Telangana",
        "center": {"latitude": 17.3850, "longitude": 78.4867, "zoom": 12},
        "station_id": "CPCB_TS_001",
        "station_name": "Sanathnagar, Hyderabad - TSPCB Live CAAQMS",
        "data_sources": ["CPCB CAAQMS Network", "TSPCB Air Monitoring", "IMD Begumpet Observatory"],
        "climate_profile": {
            "base_temp": 24.5,
            "humidity": 58.0,
            "wind_speed": 4.2,
            "wind_direction": "SE",
            "base_adj": -25.0,
            "diwali_spike_adj": -20.0,
            "dispersion_rate": 15.5,
            "inversion_risk": "MODERATE"
        },
        "neighbourhoods": [
            {
                "id": "hyd_sanathnagar",
                "name": "Sanathnagar",
                "city": "Hyderabad",
                "state": "Telangana",
                "type": "Industrial & Urban Mixed",
                "modifier": 1.18,
                "latitude": 17.4573,
                "longitude": 78.4418,
                "description": "Historic industrial estate with pharmaceutical and machinery manufacturing."
            },
            {
                "id": "hyd_hitec_city",
                "name": "HITEC City",
                "city": "Hyderabad",
                "state": "Telangana",
                "type": "Cyber IT Corridor",
                "modifier": 1.06,
                "latitude": 17.4435,
                "longitude": 78.3772,
                "description": "Modern software technology corridor with wide multi-lane arterial flyovers."
            },
            {
                "id": "hyd_banjara_hills",
                "name": "Banjara Hills",
                "city": "Hyderabad",
                "state": "Telangana",
                "type": "Elevated Residential & Commercial",
                "modifier": 0.95,
                "latitude": 17.4156,
                "longitude": 78.4350,
                "description": "Elevated topography with undulating terrain and favorable wind dispersal."
            },
            {
                "id": "hyd_charminar",
                "name": "Charminar (Old City)",
                "city": "Hyderabad",
                "state": "Telangana",
                "type": "Heritage Dense Bazaar",
                "modifier": 1.20,
                "latitude": 17.3616,
                "longitude": 78.4747,
                "description": "High pedestrian density, crowded retail markets, and narrow historic streets."
            },
            {
                "id": "hyd_gachibowli",
                "name": "Gachibowli",
                "city": "Hyderabad",
                "state": "Telangana",
                "type": "Institutional & Sports Corridor",
                "modifier": 0.98,
                "latitude": 17.4401,
                "longitude": 78.3489,
                "description": "Open sports stadiums, central university campuses, and green buffers."
            }
        ]
    },
    "Kolkata": {
        "id": "kolkata",
        "city": "Kolkata",
        "state": "West Bengal",
        "center": {"latitude": 22.5726, "longitude": 88.3639, "zoom": 12},
        "station_id": "CPCB_WB_001",
        "station_name": "Victoria Memorial, Kolkata - WBPCB Live CAAQMS",
        "data_sources": ["CPCB CAAQMS Network", "WBPCB Air Data", "IMD Alipore Observatory"],
        "climate_profile": {
            "base_temp": 25.0,
            "humidity": 72.0,
            "wind_speed": 3.5,
            "wind_direction": "NNE",
            "base_adj": 15.0,
            "diwali_spike_adj": 25.0,
            "dispersion_rate": 13.0,
            "inversion_risk": "HIGH"
        },
        "neighbourhoods": [
            {
                "id": "kol_victoria",
                "name": "Victoria Memorial Area",
                "city": "Kolkata",
                "state": "West Bengal",
                "type": "Maidan Green Buffer",
                "modifier": 0.90,
                "latitude": 22.5448,
                "longitude": 88.3426,
                "description": "Central Kolkata Maidan parkland serving as a crucial environmental air purifier."
            },
            {
                "id": "kol_saltlake",
                "name": "Salt Lake (Sector V)",
                "city": "Kolkata",
                "state": "West Bengal",
                "type": "Planned Tech Satellite",
                "modifier": 1.05,
                "latitude": 22.5804,
                "longitude": 88.4378,
                "description": "Planned IT hub bordering East Kolkata Wetlands with steady wetland breezes."
            },
            {
                "id": "kol_park_street",
                "name": "Park Street",
                "city": "Kolkata",
                "state": "West Bengal",
                "type": "Central Entertainment & Commercial",
                "modifier": 1.15,
                "latitude": 22.5510,
                "longitude": 88.3524,
                "description": "High evening festival activity, dining congestion, and concentrated traffic."
            },
            {
                "id": "kol_howrah",
                "name": "Howrah Terminal Area",
                "city": "Kolkata",
                "state": "West Bengal",
                "type": "Railway Transit & Industrial",
                "modifier": 1.25,
                "latitude": 22.5850,
                "longitude": 88.3430,
                "description": "Historic major rail terminus, Hooghly river crossings, and heavy diesel bus transit."
            },
            {
                "id": "kol_newtown",
                "name": "New Town (Rajarhat)",
                "city": "Kolkata",
                "state": "West Bengal",
                "type": "Smart City Residential",
                "modifier": 0.96,
                "latitude": 22.5898,
                "longitude": 88.4744,
                "description": "Modern planned development with wide expressways and eco-tourism parks."
            }
        ]
    },
    "Chennai": {
        "id": "chennai",
        "city": "Chennai",
        "state": "Tamil Nadu",
        "center": {"latitude": 13.0827, "longitude": 80.2707, "zoom": 12},
        "station_id": "CPCB_TN_001",
        "station_name": "Alandur, Chennai - TNPCB Live CAAQMS",
        "data_sources": ["CPCB CAAQMS Network", "TNPCB Air Monitor", "IMD Meenambakkam Observatory"],
        "climate_profile": {
            "base_temp": 27.5,
            "humidity": 78.0,
            "wind_speed": 6.2,
            "wind_direction": "NE",
            "base_adj": -30.0,
            "diwali_spike_adj": -25.0,
            "dispersion_rate": 18.5,
            "inversion_risk": "LOW"
        },
        "neighbourhoods": [
            {
                "id": "chn_alandur",
                "name": "Alandur",
                "city": "Chennai",
                "state": "Tamil Nadu",
                "type": "Transit Junction / Commercial",
                "modifier": 1.08,
                "latitude": 13.0033,
                "longitude": 80.2014,
                "description": "Metro rail junction and southern arterial gateway to Chennai airport."
            },
            {
                "id": "chn_tnagar",
                "name": "T. Nagar",
                "city": "Chennai",
                "state": "Tamil Nadu",
                "type": "Retail & Shopping Core",
                "modifier": 1.18,
                "latitude": 13.0418,
                "longitude": 80.2341,
                "description": "One of India's largest retail and gold shopping markets with intense festival footfall."
            },
            {
                "id": "chn_adyar",
                "name": "Adyar",
                "city": "Chennai",
                "state": "Tamil Nadu",
                "type": "Coastal Residential & Estuary",
                "modifier": 0.88,
                "latitude": 13.0064,
                "longitude": 80.2575,
                "description": "Adyar river estuary and Bay of Bengal maritime coastal breeze."
            },
            {
                "id": "chn_annanagar",
                "name": "Anna Nagar",
                "city": "Chennai",
                "state": "Tamil Nadu",
                "type": "Planned Grid Residential",
                "modifier": 1.02,
                "latitude": 13.0850,
                "longitude": 80.2101,
                "description": "Planned avenue grids with substantial tree canopy and roundabouts."
            },
            {
                "id": "chn_velachery",
                "name": "Velachery",
                "city": "Chennai",
                "state": "Tamil Nadu",
                "type": "Suburban Tech Corridor",
                "modifier": 1.05,
                "latitude": 12.9815,
                "longitude": 80.2180,
                "description": "Rapidly urbanized IT residential connector bordering Pallikaranai marsh."
            }
        ]
    },
    "Pune": {
        "id": "pune",
        "city": "Pune",
        "state": "Maharashtra",
        "center": {"latitude": 18.5204, "longitude": 73.8567, "zoom": 12},
        "station_id": "CPCB_MH_002",
        "station_name": "Shivajinagar, Pune - MPCB Live CAAQMS",
        "data_sources": ["CPCB CAAQMS Network", "SAFAR-Pune", "IMD Pune Shivajinagar Observatory"],
        "climate_profile": {
            "base_temp": 23.5,
            "humidity": 55.0,
            "wind_speed": 4.0,
            "wind_direction": "W",
            "base_adj": -20.0,
            "diwali_spike_adj": -15.0,
            "dispersion_rate": 16.0,
            "inversion_risk": "MODERATE"
        },
        "neighbourhoods": [
            {
                "id": "pun_shivajinagar",
                "name": "Shivajinagar",
                "city": "Pune",
                "state": "Maharashtra",
                "type": "Central Transit & Institutional",
                "modifier": 1.12,
                "latitude": 18.5314,
                "longitude": 73.8446,
                "description": "District court, university campuses, and central railway junction."
            },
            {
                "id": "pun_kothrud",
                "name": "Kothrud",
                "city": "Pune",
                "state": "Maharashtra",
                "type": "High-Density Residential",
                "modifier": 1.02,
                "latitude": 18.5074,
                "longitude": 73.8077,
                "description": "Established residential sector with foothills buffer towards Western Ghats."
            },
            {
                "id": "pun_hinjawadi",
                "name": "Hinjawadi",
                "city": "Pune",
                "state": "Maharashtra",
                "type": "Rajiv Gandhi Infotech Park",
                "modifier": 1.08,
                "latitude": 18.5912,
                "longitude": 73.7389,
                "description": "Major IT SEZ with heavy expressway vehicular traffic during rush hours."
            },
            {
                "id": "pun_koregaon",
                "name": "Koregaon Park",
                "city": "Pune",
                "state": "Maharashtra",
                "type": "Low-Density Green Residential",
                "modifier": 0.90,
                "latitude": 18.5362,
                "longitude": 73.8940,
                "description": "Lush tree-lined residential avenues bordering Mula-Mutha river."
            },
            {
                "id": "pun_hadapsar",
                "name": "Hadapsar",
                "city": "Pune",
                "state": "Maharashtra",
                "type": "Industrial & Tech Corridor",
                "modifier": 1.15,
                "latitude": 18.5089,
                "longitude": 73.9260,
                "description": "Automotive manufacturing units, fabrication plants, and Magarpatta tech city."
            }
        ]
    },
    "Ahmedabad": {
        "id": "ahmedabad",
        "city": "Ahmedabad",
        "state": "Gujarat",
        "center": {"latitude": 23.0225, "longitude": 72.5714, "zoom": 12},
        "station_id": "CPCB_GJ_001",
        "station_name": "Maninagar, Ahmedabad - GPCB Live CAAQMS",
        "data_sources": ["CPCB CAAQMS Network", "GPCB Air Network", "IMD Ahmedabad Airport"],
        "climate_profile": {
            "base_temp": 25.0,
            "humidity": 50.0,
            "wind_speed": 3.8,
            "wind_direction": "NE",
            "base_adj": 10.0,
            "diwali_spike_adj": 20.0,
            "dispersion_rate": 14.0,
            "inversion_risk": "HIGH"
        },
        "neighbourhoods": [
            {
                "id": "ahm_maninagar",
                "name": "Maninagar",
                "city": "Ahmedabad",
                "state": "Gujarat",
                "type": "South Commercial & Rail Hub",
                "modifier": 1.15,
                "latitude": 22.9978,
                "longitude": 72.6033,
                "description": "Busy commercial markets and Kankaria lake recreational zone."
            },
            {
                "id": "ahm_navrangpura",
                "name": "Navrangpura",
                "city": "Ahmedabad",
                "state": "Gujarat",
                "type": "Institutional & Commercial",
                "modifier": 1.05,
                "latitude": 23.0373,
                "longitude": 72.5613,
                "description": "Gujarat University area with banking offices and educational campuses."
            },
            {
                "id": "ahm_satellite",
                "name": "Satellite",
                "city": "Ahmedabad",
                "state": "Gujarat",
                "type": "Modern Residential & Retail",
                "modifier": 1.02,
                "latitude": 23.0304,
                "longitude": 72.5176,
                "description": "Western planned residential zones with shopping complexes along SG highway."
            },
            {
                "id": "ahm_naroda",
                "name": "Naroda Industrial Estate",
                "city": "Ahmedabad",
                "state": "Gujarat",
                "type": "Heavy Chemical & Industrial",
                "modifier": 1.28,
                "latitude": 23.0805,
                "longitude": 72.6598,
                "description": "Extensive chemical, textile, and engineering industrial estate."
            },
            {
                "id": "ahm_sabarmati",
                "name": "Sabarmati Riverfront",
                "city": "Ahmedabad",
                "state": "Gujarat",
                "type": "Riverfront Buffer",
                "modifier": 0.92,
                "latitude": 23.0583,
                "longitude": 72.5800,
                "description": "Open riverfront promenade offering natural cross-ventilation corridor."
            }
        ]
    },
    "Jaipur": {
        "id": "jaipur",
        "city": "Jaipur",
        "state": "Rajasthan",
        "center": {"latitude": 26.9124, "longitude": 75.7873, "zoom": 12},
        "station_id": "CPCB_RJ_001",
        "station_name": "Shastri Nagar, Jaipur - RSPCB Live CAAQMS",
        "data_sources": ["CPCB CAAQMS Network", "RSPCB Air Quality", "IMD Sanganer Observatory"],
        "climate_profile": {
            "base_temp": 21.5,
            "humidity": 45.0,
            "wind_speed": 3.2,
            "wind_direction": "NW",
            "base_adj": 10.0,
            "diwali_spike_adj": 20.0,
            "dispersion_rate": 13.5,
            "inversion_risk": "HIGH"
        },
        "neighbourhoods": [
            {
                "id": "jai_shastrinagar",
                "name": "Shastri Nagar",
                "city": "Jaipur",
                "state": "Rajasthan",
                "type": "Medical & Residential",
                "modifier": 1.10,
                "latitude": 26.9410,
                "longitude": 75.7950,
                "description": "Dense medical college corridor and residential colonies."
            },
            {
                "id": "jai_mansarovar",
                "name": "Mansarovar",
                "city": "Jaipur",
                "state": "Rajasthan",
                "type": "Sprawling Planned Residential",
                "modifier": 1.02,
                "latitude": 26.8620,
                "longitude": 75.7650,
                "description": "One of Asia's largest planned residential layouts with wide boulevards."
            },
            {
                "id": "jai_cscheme",
                "name": "C-Scheme",
                "city": "Jaipur",
                "state": "Rajasthan",
                "type": "Central Business & Dining",
                "modifier": 1.08,
                "latitude": 26.9110,
                "longitude": 75.8030,
                "description": "Central commercial sector with administrative offices and dining hubs."
            },
            {
                "id": "jai_walledcity",
                "name": "Walled City (Johari Bazaar)",
                "city": "Jaipur",
                "state": "Rajasthan",
                "type": "Heritage Bazaar Core",
                "modifier": 1.24,
                "latitude": 26.9230,
                "longitude": 75.8270,
                "description": "Historic pink city market with dense pedestrian festive shopping."
            }
        ]
    },
    "Lucknow": {
        "id": "lucknow",
        "city": "Lucknow",
        "state": "Uttar Pradesh",
        "center": {"latitude": 26.8467, "longitude": 80.9462, "zoom": 12},
        "station_id": "CPCB_UP_001",
        "station_name": "Lalbagh, Lucknow - UPPCB Live CAAQMS",
        "data_sources": ["CPCB CAAQMS Network", "UPPCB Environmental Data", "IMD Amausi Observatory"],
        "climate_profile": {
            "base_temp": 21.0,
            "humidity": 70.0,
            "wind_speed": 2.2,
            "wind_direction": "NW",
            "base_adj": 28.0,
            "diwali_spike_adj": 40.0,
            "dispersion_rate": 11.0,
            "inversion_risk": "VERY_HIGH"
        },
        "neighbourhoods": [
            {
                "id": "lko_lalbagh",
                "name": "Lalbagh",
                "city": "Lucknow",
                "state": "Uttar Pradesh",
                "type": "Central Market Core",
                "modifier": 1.22,
                "latitude": 26.8450,
                "longitude": 80.9380,
                "description": "High commercial traffic density in central municipal jurisdiction."
            },
            {
                "id": "lko_gomtinagar",
                "name": "Gomti Nagar",
                "city": "Lucknow",
                "state": "Uttar Pradesh",
                "type": "Planned Riverfront Residential",
                "modifier": 1.04,
                "latitude": 26.8580,
                "longitude": 81.0020,
                "description": "Extensive planned residential township with Gomti riverfront green buffer."
            },
            {
                "id": "lko_alambagh",
                "name": "Alambagh",
                "city": "Lucknow",
                "state": "Uttar Pradesh",
                "type": "Transit Bus Terminus Corridor",
                "modifier": 1.18,
                "latitude": 26.8120,
                "longitude": 80.9020,
                "description": "Intercity bus hub, railway junction, and heavy commercial vehicle movement."
            },
            {
                "id": "lko_hazratganj",
                "name": "Hazratganj",
                "city": "Lucknow",
                "state": "Uttar Pradesh",
                "type": "Heritage Promenade & Shopping",
                "modifier": 1.10,
                "latitude": 26.8530,
                "longitude": 80.9480,
                "description": "Historic downtown shopping corridor with heavy pedestrian festival shoppers."
            }
        ]
    },
    "Ludhiana": {
        "id": "ludhiana",
        "city": "Ludhiana",
        "state": "Punjab",
        "center": {"latitude": 30.8950, "longitude": 75.8250, "zoom": 13},
        "station_id": "CPCB_PB_001",
        "station_name": "Punjab Agricultural University (PAU), Ludhiana - PPCB Live CAAQMS",
        "data_sources": ["CPCB CAAQMS Network", "PPCB Air Quality", "IMD Ludhiana Observatory"],
        "climate_profile": {
            "base_temp": 20.0,
            "humidity": 75.0,
            "wind_speed": 2.5,
            "wind_direction": "NW",
            "base_adj": 15.0,
            "diwali_spike_adj": 25.0,
            "dispersion_rate": 12.0,
            "inversion_risk": "VERY_HIGH"
        },
        "neighbourhoods": [
            {
                "id": "ludhiana_model_town",
                "name": "Model Town",
                "city": "Ludhiana",
                "state": "Punjab",
                "type": "Commercial / Dense",
                "modifier": 1.15,
                "latitude": 30.8926,
                "longitude": 75.8341,
                "description": "High commercial & vehicular density with active shopping markets."
            },
            {
                "id": "ludhiana_sarabha_nagar",
                "name": "Sarabha Nagar",
                "city": "Ludhiana",
                "state": "Punjab",
                "type": "Residential",
                "modifier": 1.05,
                "latitude": 30.8906,
                "longitude": 75.8115,
                "description": "Established residential neighborhood with community market areas."
            },
            {
                "id": "ludhiana_dugri",
                "name": "Dugri",
                "city": "Ludhiana",
                "state": "Punjab",
                "type": "Residential",
                "modifier": 1.05,
                "latitude": 30.8656,
                "longitude": 75.8458,
                "description": "Expanding residential urban zone with moderate internal traffic."
            },
            {
                "id": "ludhiana_civil_lines",
                "name": "Civil Lines",
                "city": "Ludhiana",
                "state": "Punjab",
                "type": "Mixed Urban",
                "modifier": 1.10,
                "latitude": 30.9125,
                "longitude": 75.8361,
                "description": "Administrative offices, historic residential tracts, and commercial arterials."
            },
            {
                "id": "ludhiana_pau_area",
                "name": "PAU Area",
                "city": "Ludhiana",
                "state": "Punjab",
                "type": "Green / Park Buffer",
                "modifier": 0.90,
                "latitude": 30.9015,
                "longitude": 75.7954,
                "description": "Punjab Agricultural University campus with expansive green tree canopy."
            }
        ]
    },
    "Chandigarh": {
        "id": "chandigarh",
        "city": "Chandigarh",
        "state": "Chandigarh (UT)",
        "center": {"latitude": 30.7333, "longitude": 76.7794, "zoom": 13},
        "station_id": "CPCB_CH_001",
        "station_name": "Sector 22, Chandigarh - CPCC Live CAAQMS",
        "data_sources": ["CPCB CAAQMS Network", "CPCC Air Monitor", "IMD Chandigarh Airport"],
        "climate_profile": {
            "base_temp": 19.5,
            "humidity": 65.0,
            "wind_speed": 3.5,
            "wind_direction": "NW",
            "base_adj": -10.0,
            "diwali_spike_adj": -15.0,
            "dispersion_rate": 15.0,
            "inversion_risk": "MODERATE"
        },
        "neighbourhoods": [
            {
                "id": "chd_sector_17",
                "name": "Sector 17 (City Centre)",
                "city": "Chandigarh",
                "state": "Chandigarh (UT)",
                "type": "Pedestrian Commercial Plaza",
                "modifier": 1.10,
                "latitude": 30.7410,
                "longitude": 76.7850,
                "description": "Central commercial plaza and government administrative zone."
            },
            {
                "id": "chd_sector_22",
                "name": "Sector 22",
                "city": "Chandigarh",
                "state": "Chandigarh (UT)",
                "type": "Dense Market & Residential",
                "modifier": 1.15,
                "latitude": 30.7380,
                "longitude": 76.7725,
                "description": "Popular shopping market with high pedestrian and festive activity."
            },
            {
                "id": "chd_sector_35",
                "name": "Sector 35",
                "city": "Chandigarh",
                "state": "Chandigarh (UT)",
                "type": "Commercial & Hospitality",
                "modifier": 1.05,
                "latitude": 30.7250,
                "longitude": 76.7620,
                "description": "Hospitality and dining corridor with moderate vehicular movement."
            },
            {
                "id": "chd_sukhna_lake",
                "name": "Sukhna Lake Area",
                "city": "Chandigarh",
                "state": "Chandigarh (UT)",
                "type": "Eco-Sensitive Waterbody",
                "modifier": 0.85,
                "latitude": 30.7421,
                "longitude": 76.8188,
                "description": "Expansive natural reservoir and protected Shivalik foothills green belt."
            },
            {
                "id": "chd_industrial_area",
                "name": "Industrial Area Phase 1",
                "city": "Chandigarh",
                "state": "Chandigarh (UT)",
                "type": "Light Industrial",
                "modifier": 1.20,
                "latitude": 30.7060,
                "longitude": 76.8040,
                "description": "Manufacturing, auto workshops, and logistics transit corridor."
            }
        ]
    },
    "Bhopal": {
        "id": "bhopal",
        "city": "Bhopal",
        "state": "Madhya Pradesh",
        "center": {"latitude": 23.2599, "longitude": 77.4126, "zoom": 12},
        "station_id": "CPCB_MP_001",
        "station_name": "T.T. Nagar, Bhopal - MPPCB Live CAAQMS",
        "data_sources": ["CPCB CAAQMS Network", "MPPCB Air Portal", "IMD Bairagarh Observatory"],
        "climate_profile": {
            "base_temp": 22.5,
            "humidity": 56.0,
            "wind_speed": 3.6,
            "wind_direction": "ENE",
            "base_adj": -15.0,
            "diwali_spike_adj": -10.0,
            "dispersion_rate": 15.0,
            "inversion_risk": "MODERATE"
        },
        "neighbourhoods": [
            {
                "id": "bho_ttnagar",
                "name": "T.T. Nagar",
                "city": "Bhopal",
                "state": "Madhya Pradesh",
                "type": "Commercial & Stadium Area",
                "modifier": 1.10,
                "latitude": 23.2380,
                "longitude": 77.3990,
                "description": "New market shopping center and Tatya Tope sports stadium."
            },
            {
                "id": "bho_arera",
                "name": "Arera Colony",
                "city": "Bhopal",
                "state": "Madhya Pradesh",
                "type": "Planned Green Residential",
                "modifier": 0.95,
                "latitude": 23.2120,
                "longitude": 77.4330,
                "description": "Green residential sector with undulating terrain and lake breezes."
            },
            {
                "id": "bho_mpnagar",
                "name": "MP Nagar",
                "city": "Bhopal",
                "state": "Madhya Pradesh",
                "type": "Commercial Core & Offices",
                "modifier": 1.16,
                "latitude": 23.2320,
                "longitude": 77.4320,
                "description": "Maharana Pratap Nagar corporate and commercial business hub."
            },
            {
                "id": "bho_upperlake",
                "name": "Upper Lake (VIP Road)",
                "city": "Bhopal",
                "state": "Madhya Pradesh",
                "type": "Freshwater Wetland Buffer",
                "modifier": 0.88,
                "latitude": 23.2510,
                "longitude": 77.3620,
                "description": "Bhojtal lake reservoir with natural cooling and clean air buffer."
            }
        ]
    },
    "Indore": {
        "id": "indore",
        "city": "Indore",
        "state": "Madhya Pradesh",
        "center": {"latitude": 22.7196, "longitude": 75.8577, "zoom": 12},
        "station_id": "CPCB_MP_002",
        "station_name": "Chhoti Gwaltoli, Indore - MPPCB Live CAAQMS",
        "data_sources": ["CPCB CAAQMS Network", "MPPCB Monitoring", "IMD Indore Airport"],
        "climate_profile": {
            "base_temp": 23.0,
            "humidity": 52.0,
            "wind_speed": 4.0,
            "wind_direction": "NE",
            "base_adj": -5.0,
            "diwali_spike_adj": 5.0,
            "dispersion_rate": 15.5,
            "inversion_risk": "MODERATE"
        },
        "neighbourhoods": [
            {
                "id": "ind_chhoti_gwaltoli",
                "name": "Chhoti Gwaltoli",
                "city": "Indore",
                "state": "Madhya Pradesh",
                "type": "Transit & Central Station",
                "modifier": 1.18,
                "latitude": 22.7180,
                "longitude": 75.8670,
                "description": "Central Indore railway station and Sarwate bus terminus node."
            },
            {
                "id": "ind_vijaynagar",
                "name": "Vijay Nagar",
                "city": "Indore",
                "state": "Madhya Pradesh",
                "type": "Commercial & IT Corridor",
                "modifier": 1.08,
                "latitude": 22.7533,
                "longitude": 75.8937,
                "description": "Modern commercial, shopping, and hospitality hub in North Indore."
            },
            {
                "id": "ind_rajwada",
                "name": "Rajwada (Sarafa)",
                "city": "Indore",
                "state": "Madhya Pradesh",
                "type": "Heritage Market & Street Food",
                "modifier": 1.22,
                "latitude": 22.7186,
                "longitude": 75.8554,
                "description": "Historic palace district with vibrant nighttime Sarafa festival crowds."
            },
            {
                "id": "ind_palasia",
                "name": "Old Palasia",
                "city": "Indore",
                "state": "Madhya Pradesh",
                "type": "Residential & Dining",
                "modifier": 0.98,
                "latitude": 22.7240,
                "longitude": 75.8850,
                "description": "Established residential neighborhood with shaded avenues."
            }
        ]
    },
    "Surat": {
        "id": "surat",
        "city": "Surat",
        "state": "Gujarat",
        "center": {"latitude": 21.1702, "longitude": 72.8311, "zoom": 12},
        "station_id": "CPCB_GJ_002",
        "station_name": "Limbayat, Surat - GPCB Live CAAQMS",
        "data_sources": ["CPCB CAAQMS Network", "GPCB Coastal Feed", "IMD Surat Airport"],
        "climate_profile": {
            "base_temp": 27.0,
            "humidity": 60.0,
            "wind_speed": 5.0,
            "wind_direction": "W",
            "base_adj": -10.0,
            "diwali_spike_adj": 5.0,
            "dispersion_rate": 16.5,
            "inversion_risk": "MODERATE"
        },
        "neighbourhoods": [
            {
                "id": "sur_limbayat",
                "name": "Limbayat",
                "city": "Surat",
                "state": "Gujarat",
                "type": "High-Density Residential & Textile",
                "modifier": 1.15,
                "latitude": 21.1750,
                "longitude": 72.8620,
                "description": "High residential population density with textile processing units."
            },
            {
                "id": "sur_adajan",
                "name": "Adajan",
                "city": "Surat",
                "state": "Gujarat",
                "type": "Planned Residential Corridor",
                "modifier": 0.95,
                "latitude": 21.1960,
                "longitude": 72.7930,
                "description": "Western suburb across Tapi river with maritime coastal ventilation."
            },
            {
                "id": "sur_vesu",
                "name": "Vesu",
                "city": "Surat",
                "state": "Gujarat",
                "type": "Modern Institutional & Luxury Residential",
                "modifier": 0.92,
                "latitude": 21.1410,
                "longitude": 72.7750,
                "description": "University campus and airport corridor with open topography."
            },
            {
                "id": "sur_textile",
                "name": "Ring Road Textile Market",
                "city": "Surat",
                "state": "Gujarat",
                "type": "Wholesale Commercial Trade",
                "modifier": 1.24,
                "latitude": 21.1890,
                "longitude": 72.8420,
                "description": "Bustling textile wholesale complexes with high commercial vehicle density."
            }
        ]
    },
    "Nagpur": {
        "id": "nagpur",
        "city": "Nagpur",
        "state": "Maharashtra",
        "center": {"latitude": 21.1458, "longitude": 79.0882, "zoom": 12},
        "station_id": "CPCB_MH_003",
        "station_name": "Civil Lines, Nagpur - MPCB Live CAAQMS",
        "data_sources": ["CPCB CAAQMS Network", "MPCB Vidarbha Network", "IMD Sonegaon Observatory"],
        "climate_profile": {
            "base_temp": 23.0,
            "humidity": 54.0,
            "wind_speed": 3.8,
            "wind_direction": "E",
            "base_adj": -10.0,
            "diwali_spike_adj": -5.0,
            "dispersion_rate": 15.0,
            "inversion_risk": "MODERATE"
        },
        "neighbourhoods": [
            {
                "id": "nag_civillines",
                "name": "Civil Lines",
                "city": "Nagpur",
                "state": "Maharashtra",
                "type": "Administrative Green Zone",
                "modifier": 0.90,
                "latitude": 21.1530,
                "longitude": 79.0710,
                "description": "High Court, government secretariats, and extensive botanical gardens."
            },
            {
                "id": "nag_sitabuldi",
                "name": "Sitabuldi",
                "city": "Nagpur",
                "state": "Maharashtra",
                "type": "Commercial & Metro Hub",
                "modifier": 1.18,
                "latitude": 21.1460,
                "longitude": 79.0830,
                "description": "Central market square and interchange station of Nagpur Metro."
            },
            {
                "id": "nag_dharampeth",
                "name": "Dharampeth",
                "city": "Nagpur",
                "state": "Maharashtra",
                "type": "Residential & Retail",
                "modifier": 1.04,
                "latitude": 21.1420,
                "longitude": 79.0600,
                "description": "Established West Nagpur residential district with boutique shopping."
            },
            {
                "id": "nag_hingna",
                "name": "MIDC Hingna",
                "city": "Nagpur",
                "state": "Maharashtra",
                "type": "Industrial Manufacturing Zone",
                "modifier": 1.22,
                "latitude": 21.1120,
                "longitude": 78.9880,
                "description": "Heavy industrial cluster with engineering workshops and logistics transit."
            }
        ]
    },
    "Patna": {
        "id": "patna",
        "city": "Patna",
        "state": "Bihar",
        "center": {"latitude": 25.5941, "longitude": 85.1376, "zoom": 12},
        "station_id": "CPCB_BR_001",
        "station_name": "Samanpura, Patna - BSPCB Live CAAQMS",
        "data_sources": ["CPCB CAAQMS Network", "BSPCB Clean Air Portal", "IMD Patna Airport"],
        "climate_profile": {
            "base_temp": 22.0,
            "humidity": 72.0,
            "wind_speed": 2.1,
            "wind_direction": "WNW",
            "base_adj": 32.0,
            "diwali_spike_adj": 42.0,
            "dispersion_rate": 10.8,
            "inversion_risk": "VERY_HIGH"
        },
        "neighbourhoods": [
            {
                "id": "pat_samanpura",
                "name": "Samanpura (Raja Bazar)",
                "city": "Patna",
                "state": "Bihar",
                "type": "Medical & Commercial Arterial",
                "modifier": 1.24,
                "latitude": 25.6080,
                "longitude": 85.0830,
                "description": "High vehicular traffic along Bailey Road and IGIMS medical hospital node."
            },
            {
                "id": "pat_boringroad",
                "name": "Boring Road",
                "city": "Patna",
                "state": "Bihar",
                "type": "Commercial & Coaching Hub",
                "modifier": 1.16,
                "latitude": 25.6170,
                "longitude": 85.1160,
                "description": "Heavy youth and coaching institute footfall with intense commercial activity."
            },
            {
                "id": "pat_kankarbagh",
                "name": "Kankarbagh",
                "city": "Patna",
                "state": "Bihar",
                "type": "Dense Residential Township",
                "modifier": 1.12,
                "latitude": 25.5930,
                "longitude": 85.1580,
                "description": "One of Asia's largest residential colonies with high population density."
            },
            {
                "id": "pat_ganga_path",
                "name": "Ganga Marine Drive Area",
                "city": "Patna",
                "state": "Bihar",
                "type": "Riverfront Floodplain Buffer",
                "modifier": 0.92,
                "latitude": 25.6260,
                "longitude": 85.1720,
                "description": "Open riverbank along the Ganges with continuous natural riverine draft."
            }
        ]
    },
    "Kanpur": {
        "id": "kanpur",
        "city": "Kanpur",
        "state": "Uttar Pradesh",
        "center": {"latitude": 26.4499, "longitude": 80.3319, "zoom": 12},
        "station_id": "CPCB_UP_002",
        "station_name": "Nehru Nagar, Kanpur - UPPCB Live CAAQMS",
        "data_sources": ["CPCB CAAQMS Network", "UPPCB Monitoring", "IMD Kanpur Chakeri"],
        "climate_profile": {
            "base_temp": 21.0,
            "humidity": 69.0,
            "wind_speed": 2.0,
            "wind_direction": "NW",
            "base_adj": 30.0,
            "diwali_spike_adj": 40.0,
            "dispersion_rate": 11.0,
            "inversion_risk": "VERY_HIGH"
        },
        "neighbourhoods": [
            {
                "id": "kan_nehrunagar",
                "name": "Nehru Nagar",
                "city": "Kanpur",
                "state": "Uttar Pradesh",
                "type": "Central Urban Core",
                "modifier": 1.20,
                "latitude": 26.4710,
                "longitude": 80.3240,
                "description": "Central municipal zone with congested inner commercial streets."
            },
            {
                "id": "kan_civillines",
                "name": "Civil Lines",
                "city": "Kanpur",
                "state": "Uttar Pradesh",
                "type": "Administrative / Green Tract",
                "modifier": 0.98,
                "latitude": 26.4820,
                "longitude": 80.3450,
                "description": "Ganges riverfront proximity, judicial complexes, and shaded colonial avenues."
            },
            {
                "id": "kan_panki",
                "name": "Panki Industrial Area",
                "city": "Kanpur",
                "state": "Uttar Pradesh",
                "type": "Heavy Industrial & Power Corridor",
                "modifier": 1.26,
                "latitude": 26.4780,
                "longitude": 80.2390,
                "description": "Thermal power facilities, engineering factories, and heavy freight movement."
            },
            {
                "id": "kan_kalyanpur",
                "name": "Kalyanpur (IIT Area)",
                "city": "Kanpur",
                "state": "Uttar Pradesh",
                "type": "Institutional Buffer",
                "modifier": 0.92,
                "latitude": 26.5050,
                "longitude": 80.2450,
                "description": "IIT Kanpur academic campus with expansive forest and open air canopy."
            }
        ]
    },
    "Kochi": {
        "id": "kochi",
        "city": "Kochi",
        "state": "Kerala",
        "center": {"latitude": 9.9312, "longitude": 76.2673, "zoom": 12},
        "station_id": "CPCB_KL_001",
        "station_name": "Vyttila, Kochi - KPCB Live CAAQMS",
        "data_sources": ["CPCB CAAQMS Network", "Kerala PCB Air Data", "IMD Kochi Naval Base"],
        "climate_profile": {
            "base_temp": 28.0,
            "humidity": 82.0,
            "wind_speed": 6.5,
            "wind_direction": "W",
            "base_adj": -45.0,
            "diwali_spike_adj": -35.0,
            "dispersion_rate": 19.0,
            "inversion_risk": "VERY_LOW"
        },
        "neighbourhoods": [
            {
                "id": "koc_vyttila",
                "name": "Vyttila Mobility Hub",
                "city": "Kochi",
                "state": "Kerala",
                "type": "Intermodal Transit Hub",
                "modifier": 1.15,
                "latitude": 9.9678,
                "longitude": 76.3211,
                "description": "Kerala's largest transit interchange connecting buses, metro, and water ferries."
            },
            {
                "id": "koc_marine_drive",
                "name": "Marine Drive",
                "city": "Kochi",
                "state": "Kerala",
                "type": "Coastal Waterfront Promenade",
                "modifier": 0.88,
                "latitude": 9.9822,
                "longitude": 76.2755,
                "description": "Vembanad backwaters promenade with fresh Arabian Sea maritime air currents."
            },
            {
                "id": "koc_kakkanad",
                "name": "Kakkanad (InfoPark)",
                "city": "Kochi",
                "state": "Kerala",
                "type": "IT SmartCity Tech Hub",
                "modifier": 1.04,
                "latitude": 10.0120,
                "longitude": 76.3650,
                "description": "District administrative center and major software technology campus."
            },
            {
                "id": "koc_fortkochi",
                "name": "Fort Kochi",
                "city": "Kochi",
                "state": "Kerala",
                "type": "Heritage Coastal Tourism",
                "modifier": 0.85,
                "latitude": 9.9650,
                "longitude": 76.2420,
                "description": "Historic seaside peninsula with Chinese fishing nets and maritime breezes."
            }
        ]
    },
    "Bhubaneswar": {
        "id": "bhubaneswar",
        "city": "Bhubaneswar",
        "state": "Odisha",
        "center": {"latitude": 20.2961, "longitude": 85.8245, "zoom": 12},
        "station_id": "CPCB_OR_001",
        "station_name": "Patia, Bhubaneswar - SPCB Live CAAQMS",
        "data_sources": ["CPCB CAAQMS Network", "Odisha SPCB Portal", "IMD Bhubaneswar Airport"],
        "climate_profile": {
            "base_temp": 24.5,
            "humidity": 66.0,
            "wind_speed": 4.4,
            "wind_direction": "NE",
            "base_adj": -20.0,
            "diwali_spike_adj": -15.0,
            "dispersion_rate": 16.0,
            "inversion_risk": "LOW_MODERATE"
        },
        "neighbourhoods": [
            {
                "id": "bhu_patia",
                "name": "Patia",
                "city": "Bhubaneswar",
                "state": "Odisha",
                "type": "Institutional & IT Corridor",
                "modifier": 1.08,
                "latitude": 20.3550,
                "longitude": 85.8180,
                "description": "Major universities, KIIT campus, and Infocity IT export companies."
            },
            {
                "id": "bhu_saheednagar",
                "name": "Saheed Nagar",
                "city": "Bhubaneswar",
                "state": "Odisha",
                "type": "Commercial & Central Market",
                "modifier": 1.15,
                "latitude": 20.2910,
                "longitude": 85.8450,
                "description": "Commercial shopping hub along NH16 highway with active vehicular transit."
            },
            {
                "id": "bhu_chandrasekharpur",
                "name": "Chandrasekharpur",
                "city": "Bhubaneswar",
                "state": "Odisha",
                "type": "Planned Residential Sector",
                "modifier": 1.00,
                "latitude": 20.3250,
                "longitude": 85.8150,
                "description": "Extensive planned residential township with open parks and wide roads."
            },
            {
                "id": "bhu_khandagiri",
                "name": "Khandagiri Area",
                "city": "Bhubaneswar",
                "state": "Odisha",
                "type": "Heritage Foothills Buffer",
                "modifier": 0.90,
                "latitude": 20.2580,
                "longitude": 85.7860,
                "description": "Ancient rock-cut caves and protected forest hills providing clean air filtration."
            }
        ]
    }
}

def get_all_cities_list() -> List[Dict[str, Any]]:
    """Returns a lightweight summary list of all 20 configured cities for dropdowns and navigation."""
    return [
        {
            "id": data["id"],
            "city": data["city"],
            "state": data["state"],
            "center": data["center"],
            "station_id": data["station_id"],
            "station_name": data["station_name"],
            "neighbourhoods_count": len(data["neighbourhoods"])
        }
        for data in CITIES_REGISTRY.values()
    ]

def get_city_config(city_name: str) -> Dict[str, Any]:
    """Retrieves full configuration for a given city name (case-insensitive fallback to Delhi)."""
    target = (city_name or "Delhi").strip().lower()
    for name, data in CITIES_REGISTRY.items():
        if name.lower() == target or data["id"].lower() == target:
            return data
    return CITIES_REGISTRY["Delhi"]

