import java.util.Vector;
public class VHeap<E extends Comparable<E>> implements Prioridadpac<E> {
    // Este vector sostiene al Heap
    protected Vector<E> data; 
    
    // Crea un Heap vacio 
    public VHeap() {
        data = new Vector<E>();
    }
    
    // El constructor para hacer un Heap en un vector ya existente 
    public VHeap(Vector<E> v) {
        // Crea un vector de la misma capacidad
        data = new Vector<E>(v.size()); 
        for (int i = 0; i < v.size(); i++) {
            //Agrega cada heap de forma adecuada 
            add(v.get(i)); 
        }
    }
    
    // posiciones de papas e hijos "wiros"
    protected int papa(int i) {
        return (i - 1) / 2;
    }
    
    // wiro a la izquierda
    protected int left(int i) {
        return 2 * i + 1;
    }
    
    // wiro a la derecha
    protected int right(int i) {
        return 2 * i + 2;
    }
    
    //Mueve un elemento al Heap con su posicion indicada
    protected void percolateUp(int leaf) {
        int papa = papa(leaf);
        E value = data.get(leaf);
        
        while (leaf > 0 && value.compareTo(data.get(papa)) < 0) {
            data.set(leaf, data.get(papa)); // Move parent down
            leaf = papa;
            papa = papa(leaf);
        }
        
        data.set(leaf, value); // Insert value at its final position
    }
    
    // Agrega un elemento a la cola de prioridad
    @Override
    public void add(E value) {
        // Termina un vector
        data.add(value); 
        // Mueve el elemento a su posicion adecuada
        percolateUp(data.size() - 1); 
    }
    
    // Mueve el elemento a su posicion adecuada en el Heap
    protected void pushDownRoot(int root) {
        int heapSize = data.size();
        E value = data.get(root);
        
        while (root < heapSize) {
            int poswiro = left(root);
            if (poswiro >= heapSize) {
                // Ya no mas wiros "hijos"
                break;
            }
            
            // Encuentra el wiro mas chiquito
            if (right(root) < heapSize && 
                data.get(poswiro + 1).compareTo(data.get(poswiro)) < 0) {
                // Usar el hijo a la derecha 
                poswiro++; 
            }
            
            // Si el root es mas chiquito que el wiro chiquito, ahi se queda
            if (value.compareTo(data.get(poswiro)) <= 0) {
                break;
            }
            
            // Mueve al wiro
            data.set(root, data.get(poswiro));
            root = poswiro; // Continue down
        }
        
        data.set(root, value); // Store the value in its final position
    }
    
    //agarra el elemento con la mayor prioridad sin eliminarla del sistema
    @Override
    public E getFirst() {
        if (data.isEmpty()) {
            return null;
        }
        return data.get(0);
    }
    
    
    @Override
    public E remove() {
        if (data.isEmpty()) {
            return null;
        }
        /// Agarra el elemento con mas valor
        E minVal = data.get(0); 
        
        // Ajustar Heap
        data.set(0, data.get(data.size() - 1));
        data.setSize(data.size() - 1);
        
        if (data.size() > 0) {
            //Restaura Heap
            pushDownRoot(0);
        }
        
        return minVal;
    }
    
    // agarrar el numero de elementos en la cola
    @Override
    public int size() {
        return data.size();
    }
    
    // ver si la cola esta vacia
    @Override
    public boolean isEmpty() {
        return data.isEmpty();
    }
}