import argparse
import logging
import math

import anyio
from anynet import tls
from nintendo.nex import settings, prudp, rmc
from nintendo.nex.authentication import AuthenticationServer

import config
import dashboard
import eagle
from ClientMgr import ClientMgr
from MatchMaker import MatchMaker
from MatchMakingServer import MatchMakingServerExt, MatchMakingServer
from MatchmakeExtensionServer import MatchmakeExtensionServer
from MatchmakeRefereeServer import MatchmakeRefereeServer
from MessageDeliveryServer import MessageDeliveryServer
from Ranking2Server import Ranking2Server
from SecureConnectionServer import SecureConnectionServer
from UtilityServer import UtilityServer

logging.basicConfig(level=logging.INFO)


async def main():
    parser = argparse.ArgumentParser(description='SMB35 custom server.')
    parser.add_argument('--prudpport', metavar='p', type=int, help='port for the eagle server', default=20000)
    parser.add_argument('--eagleport', metavar='e', type=int, help='port for the eagle server', default=20001)
    parser.add_argument('--dashboardport', metavar='d', type=int, help='port for the web dashboard', default=20080)

    args = parser.parse_args()
    print(args)

    s = settings.load("switch")
    s.configure("0a69c592", 40600, 0)

    chain = tls.load_certificate_chain("resources/fullchain.pem")
    key = tls.TLSPrivateKey.load("resources/privkey.pem", tls.TYPE_PEM)
    context = tls.TLSContext()
    context.set_certificate_chain(chain, key)

    async with eagle.serve("", args.eagleport, context) as eagle_mgr:
        clients = ClientMgr()
        matchmaker = MatchMaker(clients, eagle_mgr)
        async with dashboard.serve("", args.dashboardport, context, clients, matchmaker):
            servers1 = [AuthenticationServer(s)]
            servers2 = [
                SecureConnectionServer(clients),
                MessageDeliveryServer(clients, matchmaker),
                MatchmakeRefereeServer(clients, matchmaker),
                MatchmakeExtensionServer(matchmaker),
                MatchMakingServerExt(matchmaker),
                MatchMakingServer(matchmaker),
                Ranking2Server(),
                UtilityServer()
            ]

            async with prudp.serve_transport(s, "", args.prudpport, context) as transport:
                async with rmc.serve_prudp(s, servers1, transport, 1):
                    async with rmc.serve_prudp(s, servers2, transport, 2, key=config.SERVER_KEY):
                        print("Server is running!")
                        await anyio.sleep(math.inf)


anyio.run(main)
