import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;

//utilixa su propia implementacion de VHeap
public class SistemaEmergencias {
    
    public static void main(String[] args) {
        VHeap<Paciente> colaPacientes = new VHeap<>();
        
        try {
            // Lee el archivo de pacientes
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
                Paciente siguiente = colaPacientes.remove();
                System.out.println(siguiente);
            }
            
        } catch (IOException e) {
            System.err.println("Error al leer el archivo: " + e.getMessage());
        }
    }
}