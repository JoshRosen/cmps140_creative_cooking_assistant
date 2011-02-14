import py4j.GatewayServer;

public class NLGServer {

    public static void main(String[] args) {
        int port;
        if (args.length == 0) {
            System.err.println("You must specify a port number.");
            System.exit(1);
        }
        port = Integer.parseInt(args[0]);
        GatewayServer gatewayServer = new GatewayServer(new NLGServer(),
                                                        port);
        gatewayServer.start();
        System.out.println("NLG Gateway Server started on port " + port);
    }
}
