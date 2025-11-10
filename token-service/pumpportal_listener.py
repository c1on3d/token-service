import asyncio
import json
import aiohttp
import websockets

# ENRICHER_URL = "https://your-service-name.onrender.com/tokens/add"  # Update this after deploying to Render
ENRICHER_URL = None  # Disabled for now

# ANSI color codes
GREEN = '\033[92m'
ORANGE = '\033[38;5;208m'
RESET = '\033[0m'

async def get_sol_price():
    """Fetch current SOL price in USD"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("solana", {}).get("usd", 0)
    except:
        pass
    return 0

async def fetch_metadata(session, uri):
    """Fetch token metadata from URI to get social links"""
    try:
        async with session.get(uri, timeout=aiohttp.ClientTimeout(total=5)) as resp:
            if resp.status == 200:
                return await resp.json()
    except:
        pass
    return {}

async def listen_tokens():
    uri = "wss://pumpportal.fun/api/data"
    
    # Get SOL price
    sol_price = await get_sol_price()
    print(f"💵 SOL Price: ${sol_price:.2f}")
    
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                print("✅ Connecting to PumpPortal...")
                async with websockets.connect(uri) as ws:
                    # Subscribe to pump.fun token creations
                    await ws.send(json.dumps({"method": "subscribeNewToken"}))
                    print("🟢 Listening for pump.fun and bonk.fun token creations...")

                    msg_count = 0
                    async for msg in ws:
                        try:
                            data = json.loads(msg)
                            msg_count += 1
                            
                            # Show first few messages for debugging
                            if msg_count <= 3:
                                print(f"📩 Message #{msg_count}: {json.dumps(data, indent=2)[:200]}...")
                            
                            # Handle token creation events
                            if data.get("txType") == "create":
                                mcap_sol = data.get('marketCapSol', 0)
                                mcap_usd = mcap_sol * sol_price
                                
                                # Fetch metadata for social links
                                metadata_uri = data.get('uri', '')
                                metadata = await fetch_metadata(session, metadata_uri) if metadata_uri else {}
                                
                                # Extract social links and image
                                twitter = metadata.get('twitter', 'N/A')
                                telegram = metadata.get('telegram', 'N/A')
                                website = metadata.get('website', 'N/A')
                                image = metadata.get('image', 'N/A')
                                
                                # Add socials and image to data
                                data['twitter'] = twitter
                                data['telegram'] = telegram
                                data['website'] = website
                                data['image'] = image
                                
                                # Determine pool type and color
                                pool = data.get('pool', 'pump')
                                color = ORANGE if pool == 'bonk' else GREEN
                                pool_name = 'BONK.FUN' if pool == 'bonk' else 'PUMP.FUN'
                                
                                print(f"\n{color}{'='*80}")
                                print(f"🆕 NEW TOKEN ({pool_name})")
                                print(f"Name:              {data.get('name', 'N/A')}")
                                print(f"Symbol:            {data.get('symbol', 'N/A')}")
                                print(f"Mint:              {data.get('mint', 'N/A')}")
                                print(f"Signature:         {data.get('signature', 'N/A')}")
                                print(f"Trader:            {data.get('traderPublicKey', 'N/A')}")
                                print(f"Initial Buy:       {data.get('initialBuy', 0):,.2f} tokens")
                                print(f"SOL Amount:        {data.get('solAmount', 0):.6f} SOL")
                                print(f"Market Cap:        ${mcap_usd:,.2f} ({mcap_sol:.2f} SOL)")
                                print(f"Bonding Curve:     {data.get('bondingCurveKey', 'N/A')}")
                                print(f"Tokens in Curve:   {data.get('vTokensInBondingCurve', 0):,.2f}")
                                print(f"SOL in Curve:      {data.get('vSolInBondingCurve', 0):.6f} SOL")
                                print(f"URI:               {data.get('uri', 'N/A')}")
                                print(f"Pool:              {data.get('pool', 'N/A')}")
                                print(f"Twitter:           {twitter}")
                                print(f"Telegram:          {telegram}")
                                print(f"Website:           {website}")
                                print(f"Image:             {image}{RESET}")

                                # Send token data to your enricher backend (disabled for now)
                                if ENRICHER_URL:
                                    print(f"🚀 Calling API...")
                                    try:
                                        async with session.post(ENRICHER_URL, json=data) as resp:
                                            response_text = await resp.text()
                                            if resp.status == 200:
                                                print(f"✅ API success: {response_text}")
                                            else:
                                                print(f"⚠️ API status {resp.status}: {response_text}")
                                    except Exception as post_error:
                                        print(f"⚠️ API error: {post_error}")
                                
                                print(f"{'='*80}{RESET}")
                        except Exception as e:
                            print(f"⚠️ Error: {e}")
            except Exception as e:
                print(f"🔄 Connection lost: {e}")
                print("⏳ Reconnecting in 5 seconds...")
                await asyncio.sleep(5)

asyncio.run(listen_tokens())
