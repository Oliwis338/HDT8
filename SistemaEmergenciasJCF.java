import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.PriorityQueue;


public class SistemaEmergenciasJCF {
    
    public static void main(String[] args) {
        // Usar la implementación de PriorityQueue del Java Collection Framework
        PriorityQueue<Paciente> colaPacientes = new PriorityQueue<>();
        
        try {
            // Leer archivo de pacientes
            BufferedReader reader = new BufferedReader(new FileReader("pacientes.txt"));
            String line;
            while ((line = reader.readLine()) != null) {
                String[] parts = line.split(", ");
                if (parts.length == 3) {
                    String nombre = parts[0];
                    String sintoma = parts[1];
                    char codigo = parts[2].charAt(0);
                    
                    Paciente paciente = new Paciente(nombre, sintoma, codigo);
                    colaPacientes.add(paciente);
                    System.out.println("Agregado: " + paciente);
                }
            }
            reader.close();
            
            System.out.println("\nOrden de atención a pacientes:");
            while (!colaPacientes.isEmpty()) {
                Paciente siguiente = colaPacientes.poll(); // poll() es igual a remove()
                System.out.println(siguiente);
            }
            
        } catch (IOException e) {
            System.err.println("Error al leer el archivo: " + e.getMessage());
        }
    }
}