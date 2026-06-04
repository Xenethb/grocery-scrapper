# 🛒🇱🇰 PriceFind

**PriceFind** is a full-stack automated grocery price comparison platform developed for the **EEY4189 Software Design Group Project at the Open University of Sri Lanka**.

The application aggregates real-time consumer retail prices from major Sri Lankan supermarket chains (**Cargills Food City, Keells Super, and Softlogic Glomark**) and provides users with localized price analysis and branch-level distance routing.

---

## 🌟 Key Features

### 🤖 Automated Web Scraping

Python-based scrapers with robust error handling for dynamic web layouts and changing retail websites.

### 🔍 Fuzzy String Matching

High-accuracy product matching using **RapidFuzz token-set ratio algorithms** to identify identical products across multiple supermarket chains despite naming inconsistencies.

### 📍 Live Geo-Location Tracking

Integration with the latest **Google Maps JavaScript SDK (2026)** utilizing `searchByText` functionality to identify the nearest supermarket branch relative to a user's location.

### 💰 Instant Price Comparison

Provides real-time price analysis, product availability checks, and identifies the lowest available price across all supported supermarket chains.

### 🔐 Secure Enterprise Architecture

Implements Role-Based Access Control (RBAC) and Row Level Security (RLS) policies to ensure data integrity and secure access management.

---

# 🏗️ System Architecture

```text
grocery-scrapper/
├── backend/                  # Python Data Layer
│   ├── data/                 # Raw and aggregated JSON datasets
│   ├── scrapers/             # Supermarket scraping modules
│   ├── supabase/             # Database migration & upload scripts
│   └── utils/                # Data cleaning, fuzzy matching, geocoding
│
└── web/                      # React Frontend Layer
    ├── public/               # Static assets and SPA routing configuration
    ├── src/                  # Components, Hooks, Contexts, Pages
    └── package.json          # Frontend dependencies
```

---

# 🔐 Security Configuration (RLS & Key Isolation)

To follow the **Principle of Least Privilege**, the system separates frontend and backend privileges.

## Frontend Application (web)

Uses the restricted Supabase publishable key:

```env
VITE_SUPABASE_ANON_KEY=sb_publishable_xxxxxxxxx
```

### Security Controls

* Row Level Security (RLS) enabled
* Public users limited to SELECT operations
* No INSERT, UPDATE, or DELETE permissions
* Prevents client-side database tampering

---

## Backend Processing Engine (backend)

Uses the privileged service role key:

```env
SUPABASE_SERVICE_ROLE_KEY=sb_secret_xxxxxxxxx
```

### Administrative Capabilities

* Bypasses RLS securely
* Clears outdated datasets
* Uploads refreshed supermarket data
* Executes only in protected server-side environments

---

# ⚙️ Local Development Setup

## Prerequisites

* Node.js v18+
* Python 3.10+
* Supabase Project
* Google Cloud Platform API Key

---

## 1️⃣ Environment Variable Configuration

Create a `.env` file inside the `web/` directory:

```env
# Shared Database Configuration
VITE_SUPABASE_URL=https://your-project-id.supabase.co

# Frontend Configuration
VITE_SUPABASE_ANON_KEY=sb_publishable_your_public_key_here
VITE_GOOGLE_MAPS_API_KEY=AIzaSy_your_maps_key_here

# Backend Configuration (NEVER expose publicly)
SUPABASE_SERVICE_ROLE_KEY=sb_secret_your_admin_secret_key_here
```

---

## 2️⃣ Backend Processing Pipeline

Install required Python dependencies:

```bash
pip install supabase python-dotenv rapidfuzz
```

### Step A — Run Web Scrapers

```bash
python backend/scrapers/myscrapper.py
```

Outputs raw supermarket records into:

```text
backend/data/raw/
```

### Step B — Merge & Match Products

```bash
python backend/utils/merge_groceries.py
```

Performs fuzzy matching and entity resolution across all stores.

### Step C — Upload Data to Supabase

```bash
python backend/supabase/upload_to_supabase.py
```

Purges stale records and uploads the latest processed dataset.

---

## 3️⃣ Frontend Development Server

Navigate to the frontend directory:

```bash
cd web
npm install
npm run dev
```

Open:

```text
http://localhost:5173
```

---

# 🚀 Cloud Deployment (Netlify)

The frontend is optimized for deployment on Netlify with automated GitHub webhook integration.

## Netlify Build Configuration

| Setting           | Value           |
| ----------------- | --------------- |
| Base Directory    | `web`           |
| Build Command     | `npm run build` |
| Publish Directory | `web/dist`      |

---

## Required Environment Variables

Configure the following variables within Netlify:

```env
VITE_SUPABASE_URL
VITE_SUPABASE_ANON_KEY
VITE_GOOGLE_MAPS_API_KEY
```

### SPA Routing

Single Page Application (SPA) routing is handled using the custom:

```text
public/_redirects
```

configuration file.

---

# 🛠️ Technology Stack

## Frontend

* React
* React Native
* Vite
* Tailwind CSS
* Motion (Framer Motion)

## Backend

* Python 3.10+
* RapidFuzz
* Python-Dotenv

## Cloud Infrastructure

* Supabase (PostgreSQL)
* Netlify
* Google Maps JavaScript SDK
* Google Places API

---

# 📈 Supported Retailers

* 🛒 Cargills Food City
* 🛒 Keells Super
* 🛒 Softlogic Glomark

---

# 👨‍💻 Project Information

**Module:** EEY4189 Software Design Group Project

**Institution:** Open University of Sri Lanka (OUSL)

**Project Type:** Full-Stack Web Application

**Focus Areas:**

* Data Scraping
* Price Comparison
* Geolocation Services
* Cloud Databases
* Web Security
* User Experience Design
