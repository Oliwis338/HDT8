public class Paciente implements Comparable<Paciente> {
    private String nombre;
    private String sintoma;
    private char codigoEmergencia;
    
    
    public Paciente(String nombre, String sintoma, char codigoEmergencia) {
        this.nombre = nombre;
        this.sintoma = sintoma;
        this.codigoEmergencia = codigoEmergencia;
    }
    
    // nombre del paciente
    public String getNombre() {
        return nombre;
    }
    
    // simptomas
    public String getSintoma() {
        return sintoma;
    }
    
    // codigo de ermergencia
    public char getCodigoEmergencia() {
        return codigoEmergencia;
    }
    
    
    @Override
    public int compareTo(Paciente other) {
    // codigos de prioridad como A deben de ir antes que otros como E
        return this.codigoEmergencia - other.codigoEmergencia;
    }
    
   
    @Override
    public String toString() {
        return nombre + ", " + sintoma + ", " + codigoEmergencia;
    }
}