import os
import requests
import time

import discord
from discord.ext import tasks, commands


TOKEN = os.getenv("TOKEN")
CHANNEL_PUBLIC = 954047687202836540  # multisig-monitor
CHANNEL_PRIVATE = 1012022586907050085  # multisig
API_CALL_LOOP_PERIOD = 30
SAFES = {
    "0xB65cef03b9B89f99517643226d76e286ee999e77": ["dev", "Mainnet", 3],
    "0xb364bAb258ad35dd83c7dd4E8AC78676b7aa1e9F": ["dev", "Arbitrum", 3],
    "0x329543f0F4BB134A3f7a826DC32532398B38a3fA": ["dev", "Binance Smart Chain", 2],
    "0x4977110Ed3CD5eC5598e88c8965951a47dd4e738": ["dev", "Polygon", 3],
    "0x4c56ee3295042f8A5dfC83e770a21c707CB46f5b": ["dev", "Fantom", 3],
    "0x86cbD0ce0c087b482782c181dA8d191De18C8275": ["techops", "Mainnet", 3],
    "0x292549E6bd5a41aE4521Bb8679aDA59631B9eD4C": ["techops", "Arbitrum", 3],
    # '0x777061674751834993bfBa2269A1F4de5B4a6E7c': ['techops', 'Binance Smart Chain', 3],
    "0xeb7341c89ba46CC7945f75Bd5dD7a04f8FA16327": ["techops", "Polygon", 3],
    "0x781E82D5D49042baB750efac91858cB65C6b0582": ["techops", "Fantom", 3],
    "0xD0A7A8B98957b9CD3cFB9c0425AbE44551158e9e": ["treasury_vault", "Mainnet", 5],
    "0x45b798384c236ef0d78311D98AcAEc222f8c6F54": ["treasury_vault", "Fantom", 3],
    "0x042B32Ac6b453485e357938bdC38e0340d4b9276": ["treasury_ops", "Mainnet", 3],
    "0xf109c50684EFa12d4dfBF501eD4858F25A4300B3": ["treasury_ops", "Fantom", 3],
    "0xA9ed98B5Fb8428d68664f3C5027c62A10d45826b": ["treasury_voter", "Mainnet", 5],
    # "0xD4868d98849a58F743787c77738D808376210292": ["fin_ops", "Mainnet", 3],
    # "0x6F76C6A1059093E21D8B1C13C4e20D8335e2909F": ["politician", "Mainnet", 3],
    "0xB76782B51BFf9C27bA69C77027e20Abd92Bcf3a8": ["ibbtc", "Mainnet", 3],
    # "0x9faA327AAF1b564B569Cb0Bc0FDAA87052e8d92c": ["recovered", "Mainnet", 3],
    "0x0D5eDB3ECbB15EF4EaD105c018fEd4e1d173B335": ["dev", "Optimism", 3],
    "0x8D05c5DA2a3Cb4BeB4C5EB500EE9e3Aa71670733": ["techops", "Optimism", 2],
}
GNOSIS_URLS = {
    "Mainnet": "https://safe-transaction-mainnet.safe.global/",
    "Binance Smart Chain": "https://safe-transaction-bsc.safe.global/",
    "Polygon": "https://safe-transaction-polygon.safe.global/",
    "Arbitrum": "https://safe-transaction-arbitrum.safe.global/",
    "Optimism": "https://safe-transaction-optimism.safe.global/",
    "Fantom": "https://safe-txservice.fantom.network",
}
GNOSIS_SLUGS = {
    "Mainnet": "eth",
    "Arbitrum": "arb1",
    "Binance Smart Chain": "bnb",
    "Polygon": "matic",
    "Optimism": "oeth",
}
EXPLORER_URLS = {
    "Mainnet": "https://etherscan.io/tx/",
    "Binance Smart Chain": "https://bscscan.com/tx/",
    "Polygon": "https://polygonscan.com/tx/",
    "Arbitrum": "https://arbiscan.io/tx/",
    "Fantom": "https://ftmscan.com/tx/",
    "Optimism": "https://optimistic.etherscan.io/tx/",
}
MENTIONS = {
    "dev": "<@766785323110891580>",
    "techops": "<@&1015337028495360040>",
    "treasury_vault": "<@&1015338392487202887>",
    "treasury_ops": "<@&1015337910268080128>",
    "treasury_voter": "<@&1015338392487202887>",
    "fin_ops": "<@&1015340237389570079>",
    # "politician": "<@&955928657388507196>",
    "ibbtc": "<@&1016649224575787019>",
    # "recovered": "<@1016649224575787019>",
}
HEADERS = {"accept": "application/json"}
BOT = commands.Bot(command_prefix=["."])


def fetch_thresholds(address):
    try:
        url = f"{GNOSIS_URLS[SAFES[address][1]]}/api/v1/safes/{address}/"
        r = requests.get(url, headers=HEADERS).json()
        return r["threshold"]
    except Exception as e:
        print("fetch thresholds error:", str(e))
        return -1


def gnosis_api_call(address):
    try:
        url = f"{GNOSIS_URLS[SAFES[address][1]]}/api/v1/safes/{address}/multisig-transactions/?limit=5"
        r = requests.get(url, headers=HEADERS).json()
        return r["results"]
    except Exception as e:
        print("api call error", str(e))


@BOT.event
async def on_ready():
    await BOT.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="Badger DAO's Gnosis Safes",
            status=discord.Status.online,
        )
    )


@tasks.loop(seconds=API_CALL_LOOP_PERIOD)
async def get_data():
    global first_run
    try:
        for address in SAFES:
            for safe_tx in gnosis_api_call(address):
                try:
                    creation_date = (
                        safe_tx["submissionDate"].split(".")[0].replace("T", " ")
                    )
                    modified_date = safe_tx["modified"].split(".")[0].replace("T", " ")
                    safe_tx_hash = safe_tx["safeTxHash"]
                    is_executed = safe_tx["isExecuted"]

                    if [safe_tx_hash, modified_date, is_executed] in prev_safe_tx_hash:
                        continue
                    prev_safe_tx_hash.append([safe_tx_hash, modified_date, is_executed])
                    if first_run:
                        continue

                    nonce = safe_tx["nonce"]
                    chain = SAFES[address][1]
                    if chain == "Fantom":
                        gnosis_url = f"https://safe.fantom.network/#/safes/{address}/transactions"
                    else:
                        gnosis_url = f"https://app.safe.global/{GNOSIS_SLUGS[chain]}:{address}/transactions/tx?id=multisig_{address}_{safe_tx_hash}"
                    if safe_tx["transactionHash"] is None:
                        tx_hash = "n/a"
                        tx_url = "n/a"
                    else:
                        tx_hash = safe_tx["transactionHash"]
                        tx_url = EXPLORER_URLS[chain] + tx_hash
                    confirmations = safe_tx["confirmations"]
                    confirmations_required = SAFES[address][2]

                    if safe_tx["isSuccessful"] is None:
                        is_successful = "n/a"
                    elif safe_tx["isSuccessful"] == True:
                        is_successful = "Success"
                    else:
                        is_successful = "Fail"
                    description = f"""
safe: **`{address}`**
nonce: **{nonce}**

safe_tx_hash: [`{safe_tx_hash}`]({gnosis_url})
tx_hash: [`{tx_hash}`]({tx_url})

signatures: **{len(confirmations)}/{confirmations_required}**
executed: **{is_executed}**
tx status: **{is_successful}**

'ready to sign' issue board: [https://github.com/orgs/Badger-Finance/projects/25/views/16](https://github.com/orgs/Badger-Finance/projects/25/views/16)

(modified {modified_date}, created {creation_date})
"""
                    title_suffix = f"{SAFES[address][0]} ({chain})"
                    if is_executed == False and is_successful != "n/a":
                        # some weird false positive
                        continue
                    elif is_executed == True:
                        tag = "[TX EXECUTED]"
                        public = True
                        private = True
                        mention = False
                    elif len(confirmations) == confirmations_required:
                        tag = "[READY FOR EXEC]"
                        public = True
                        private = False
                        mention = False
                    elif len(confirmations) == 0:
                        tag = "[NEW TX]"
                        public = True
                        private = True
                        mention = True
                    else:
                        continue

                    embed = discord.Embed(
                        title=f"{tag} {title_suffix}",
                        description=description,
                        color=0x00FF00,
                    )

                    if public:
                        channel = BOT.get_channel(CHANNEL_PUBLIC)
                        await channel.send(embed=embed)
                    if private:
                        channel = BOT.get_channel(CHANNEL_PRIVATE)
                        await channel.send(embed=embed)
                        if mention:
                            await channel.send(MENTIONS[SAFES[address][0]])
                except Exception as e:
                    print("parse error", str(e))
        if first_run:
            first_run = False
            # give sign of life to show bot is healthy and back online
            channel = BOT.get_channel(CHANNEL_PUBLIC)
            await channel.send("\U0001F916")
            print("\U0001F916")
    except Exception as e:
        print("main func error:", str(e))


@get_data.before_loop
async def before_name_change():
    await BOT.wait_until_ready()


if __name__ == "__main__":
    try:
        # overwrite (default) signing threshold with actual data from api
        for safe in SAFES:
            threshold = fetch_thresholds(safe)
            if threshold != -1:
                SAFES[safe][2] = threshold
            time.sleep(0.2)
    except Exception as e:
        print("update thresholds error:", str(e))

    first_run = True
    prev_safe_tx_hash = []
    get_data.start()
    BOT.run(TOKEN)
