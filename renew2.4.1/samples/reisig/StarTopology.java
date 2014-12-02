package samples.reisig;



public class StarTopology extends AbstractTopology {
    public StarTopology(int n) {
        super(n + 1);
    }

    public int[] neighbors(int i) {
        if (i == 0) {
            return new int[0];
        } else {
            return new int[] { 0 };
        }
    }
}