public interface Prioridadpac<E extends Comparable<E>> {
    
    //agrega un elemento a la cola
    void add(E value);
    
    
    E getFirst();
    
    // retorna el elemento con mayor valor
    E remove();
    
    // ve el size de la cola
    int size();
    
    // ve si la cola esta vacia
    boolean isEmpty();
}