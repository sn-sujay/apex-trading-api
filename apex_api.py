#!/usr/bin/env python3
"""
APEX Trading API - Lightweight version for Render
Runs key APEX functions directly without full Hermes dependency
"""
import os
import json
from datetime import datetime
from flask import Flask, jsonify, request

app = Flask(__name__)

STATE_FILE = os.environ.get('STATE_FILE', 'state.json')

def load_state():
    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except:
        return {"error": "No state file"}

def save_state(data):
    with open(STATE_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# ============ ENDPOINTS ============

@app.route('/')
def home():
    """Landing page"""
    return jsonify({
        "service": "APEX Trading API",
        "version": "1.0",
        "status": "running",
        "endpoints": {
            "/": "This info",
            "/ping": "Health check (keep alive)",
            "/health": "Full system health",
            "/state": "Get current state",
            "/market-regime": "Get market regime",
            "/vix": "Get India VIX",
            "/signal": "Generate trade signal",
            "/trigger/<agent>": "Trigger APEX agent"
        }
    })

@app.route('/ping')
def ping():
    """Health check - Render & cron use this"""
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/health')
def health():
    """Full health check"""
    state = load_state()
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "state_exists": os.path.exists(STATE_FILE),
        "market_regime": state.get("market_regime", "UNKNOWN"),
        "india_vix": state.get("india_vix", {}).get("current", "N/A")
    })

@app.route('/state')
def get_state():
    """Get current trading state"""
    return jsonify(load_state())

@app.route('/market-regime')
def market_regime():
    """Get current market regime"""
    state = load_state()
    regime = state.get("market_regime", "UNKNOWN")
    vix_data = state.get("india_vix", {})
    
    return jsonify({
        "regime": regime,
        "india_vix": vix_data.get("current", "N/A"),
        "vix_change": vix_data.get("change_percent", "N/A"),
        "sentiment": state.get("sentiment", {}).get("label", "NEUTRAL")
    })

@app.route('/vix')
def vix():
    """Get India VIX data"""
    state = load_state()
    return jsonify(state.get("india_vix", {}))

@app.route('/signal')
def signal():
    """Generate trade signal based on current state"""
    state = load_state()
    
    regime = state.get("market_regime", "UNKNOWN")
    sentiment = state.get("sentiment", {}).get("label", "NEUTRAL")
    confidence = state.get("sentiment", {}).get("confidence", 0)
    
    # Strategy mapping
    strategy_map = {
        ("TRENDING_UP", "BULLISH"): "Bull Call Spread",
        ("TRENDING_UP", "NEUTRAL"): "Bull Call Spread",
        ("TRENDING_UP", "BEARISH"): "SKIP",
        ("TRENDING_DOWN", "BULLISH"): "SKIP",
        ("TRENDING_DOWN", "NEUTRAL"): "Bear Put Spread",
        ("TRENDING_DOWN", "BEARISH"): "Bear Put Spread",
        ("RANGING", "ANY"): "Iron Condor",
        ("VOLATILE", "ANY"): "Long Straddle",
        ("HIGH_VOLATILITY", "ANY"): "Long Strangle"
    }
    
    strategy = strategy_map.get((regime, sentiment), "IRON_CONDOR")
    
    return jsonify({
        "regime": regime,
        "sentiment": sentiment,
        "confidence": confidence,
        "recommended_strategy": strategy,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/trigger/<agent>')
def trigger(agent):
    """Trigger APEX agent (placeholder for now)"""
    valid_agents = [
        "market-regime", "vix-monitor", "sentiment",
        "option-chain", "strategy-generator", "risk-veto"
    ]
    
    if agent not in valid_agents:
        return jsonify({"error": f"Unknown agent: {agent}"}), 400
    
    return jsonify({
        "agent": agent,
        "status": "triggered",
        "message": f"Agent {agent} would execute here",
        "timestamp": datetime.now().isoformat()
    })

# ============ INIT STATE IF NEEDED ============

if not os.path.exists(STATE_FILE):
    initial_state = {
        "market_regime": "UNKNOWN",
        "india_vix": {"current": 0, "change_percent": 0},
        "sentiment": {"label": "NEUTRAL", "confidence": 0},
        "created_at": datetime.now().isoformat()
    }
    save_state(initial_state)
    print(f"Created initial state file: {STATE_FILE}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    print(f"Starting APEX API on port {port}")
    app.run(host='0.0.0.0', port=port)