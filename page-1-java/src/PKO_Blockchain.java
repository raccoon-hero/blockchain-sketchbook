import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;

public class PKO_Blockchain {

    public static class pko_Block {
        public String pko_previousHash;
        public String pko_hash;
        public String pko_data;
        public long pko_timeStamp;
        public int pko_nonce;

        public pko_Block(String data, String previousHash) {
            this.pko_data = data;
            this.pko_previousHash = previousHash;
            this.pko_timeStamp = new Date().getTime();
            this.pko_hash = pko_calculateHash();
        }

        public String pko_calculateHash() {
            String input = pko_previousHash + pko_timeStamp + pko_nonce + pko_data;
            return pko_applySha256(input);
        }

        // Simple proof of work: Find a hash that ends with two digits (1, 0)
        public void pko_mineBlock(int difficulty) {

            // More realistic PoW example: d-amount of zeros at the beginning & two last digits are 1, 0.
            // String target = String.format("%" + difficulty + "s", "").replace(' ', '0');
            // while (!(pko_hash.substring(0, difficulty).equals(target) && pko_hash.endsWith("10"))) {
            //     pko_nonce++;
            //     pko_hash = pko_calculateHash();
            // }
            
             while (!pko_hash.substring(pko_hash.length() - 2).equals("10")) {
                pko_nonce++;
                pko_hash = pko_calculateHash();
            }

            System.out.println("  |-> " + pko_nonce + " tries");
            System.out.println("Block mined: " + pko_hash);
        }

        public static String pko_applySha256(String input) {
            try {
                MessageDigest digest = MessageDigest.getInstance("SHA-256");
                byte[] hash = digest.digest(input.getBytes("UTF-8"));
                StringBuilder hexString = new StringBuilder();
                for (byte b : hash) {
                    String hex = Integer.toHexString(0xff & b);
                    if (hex.length() == 1) hexString.append('0');
                    hexString.append(hex);
                }
                return hexString.toString();
            } catch (Exception e) {
                throw new RuntimeException(e);
            }
        }
    }

    public static class pko_Blockchain {
        public List<pko_Block> pko_chain;

        public pko_Blockchain() {
            pko_chain = new ArrayList<>();
            pko_chain.add(pko_createGenesisBlock());
        }

        public pko_Block pko_createGenesisBlock() {
            pko_Block genesisBlock = new pko_Block("Genesis Block", "Raccoon");
            genesisBlock.pko_nonce = 10302030;
            genesisBlock.pko_hash = genesisBlock.pko_calculateHash();
            return genesisBlock;
        }

        public pko_Block pko_getLatestBlock() {
            return pko_chain.get(pko_chain.size() - 1);
        }

        public void pko_addBlock(pko_Block newBlock) {
            newBlock.pko_previousHash = pko_getLatestBlock().pko_hash;
            newBlock.pko_mineBlock(3);
            pko_chain.add(newBlock);
        }

        public void printBlockchain() {
            for (int i = 0; i < pko_chain.size(); i++) {
                pko_Block block = pko_chain.get(i);
                System.out.println("=============================================");
                System.out.println("Block #" + i);
                System.out.println("Previous Hash : " + block.pko_previousHash);
                System.out.println("Current Hash  : " + block.pko_hash);
                System.out.println("Data          : " + block.pko_data);
                System.out.println("Timestamp     : " + new Date(block.pko_timeStamp));
                System.out.println("Nonce         : " + block.pko_nonce);
                System.out.println("=============================================");
                
                if (i < pko_chain.size() - 1) {
                    System.out.println("      ||");
                    System.out.println("      ||");
                    System.out.println("      \\/");
                }
            }
        }
    }

    public static void main(String[] args) {
        pko_Blockchain blockchain = new pko_Blockchain();

        System.out.println("\n\nPKO_BLOCKHAIN\n");

        System.out.println("Mining pko_block #1...");
        blockchain.pko_addBlock(new pko_Block("Block with snacks #1", blockchain.pko_getLatestBlock().pko_hash));

        System.out.println("Mining pko_block 2...");
        blockchain.pko_addBlock(new pko_Block("Block with snacks #2", blockchain.pko_getLatestBlock().pko_hash));

        System.out.println("Mining pko_block 3...");
        blockchain.pko_addBlock(new pko_Block("Block with snacks #3", blockchain.pko_getLatestBlock().pko_hash));
        
        System.out.println("\nFULL PKO_BLOCKCHAIN VIEW");
        blockchain.printBlockchain();
    }
}
