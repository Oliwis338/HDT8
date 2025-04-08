import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class TestHeap {

    @Test
    public void testEmptyHeap() {
        VHeap<Integer> heap = new VHeap()<>();
        assertTrue(heap.isEmpty());
        assertEquals(0, heap.size());
        assertNull(heap.getFirst());
        assertNull(heap.remove());
    }
    
    @Test
    public void testAddSingleElement() {
        VHeap<Integer> heap = new VHeap()<>();
        heap.add(5);
        assertFalse(heap.isEmpty());
        assertEquals(1, heap.size());
        assertEquals(5, heap.getFirst());
    }
    
    @Test
    public void testAddMultipleElements() {
        VHeap<Integer> heap = new VHeap()<>();
        heap.add(10);
        heap.add(5);
        heap.add(15);
        assertEquals(3, heap.size());
        assertEquals(5, heap.getFirst()); // 5 should be the minimum
    }
    
    @Test
    public void testRemoveElements() {
        VHeap<Integer> heap = new VHeap()<>();
        heap.add(10);
        heap.add(5);
        heap.add(15);
        heap.add(2);
        
        assertEquals(2, heap.remove()); // First out is 2
        assertEquals(3, heap.size());
        assertEquals(5, heap.remove()); // Next is 5
        assertEquals(10, heap.remove()); // Next is 10
        assertEquals(15, heap.remove()); // Last is 15
        assertTrue(heap.isEmpty());
    }
    
    @Test
    public void testPatientPriority() {
        VHeap<Paciente> heap = new VHeap()<>();
        
        // Add patients with different priorities
        Paciente p1 = new Paciente("Juan Perez", "fractura de pierna", 'C');
        Paciente p2 = new Paciente("Maria Ramirez", "apendicitis", 'A');
        Paciente p3 = new Paciente("Lorenzo Toledo", "chikunguya", 'E');
        Paciente p4 = new Paciente("Carmen Sarmientos", "dolores de parto", 'B');
        
        heap.add(p1);
        heap.add(p2);
        heap.add(p3);
        heap.add(p4);
        
        // Check the order of removal
        assertEquals('A', heap.remove().getCodigoEmergencia()); // First should be Maria with code A
        assertEquals('B', heap.remove().getCodigoEmergencia()); // Second should be Carmen with code B
        assertEquals('C', heap.remove().getCodigoEmergencia()); // Third should be Juan with code C
        assertEquals('E', heap.remove().getCodigoEmergencia()); // Last should be Lorenzo with code E
        assertTrue(heap.isEmpty());
    }
}