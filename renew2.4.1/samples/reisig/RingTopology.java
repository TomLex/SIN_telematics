package samples.reisig;



public class RingTopology extends AbstractTopology {
    public RingTopology(int n) {
        super(n);
    }

    public int[] neighbors(int i) {
        return new int[] { (i + 1) % n };
    }
}